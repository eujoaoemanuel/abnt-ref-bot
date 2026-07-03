"""
Extração de metadados de uma URL para montar a Referencia.

Estratégia:
  1. URL com DOI -> API Crossref (dados estruturados e confiáveis).
  2. Página comum -> baixa o HTML e tenta, nesta ordem:
       JSON-LD (schema.org) > meta tags (og:, article:, citation_*) > <title>/domínio.

Heurística: sites bem feitos preenchem esses campos, sites ruins não.
Quando falta algo, a Referencia fica com None e o formatador lida com isso.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

import config
from .formatter import Referencia

HEADERS = {"User-Agent": config.USER_AGENT}
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)


# ---------------------------------------------------------------- datas

def _parse_data(valor: str | None) -> date | None:
    if not valor:
        return None
    valor = valor.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(valor[:10], fmt).date()
        except ValueError:
            continue
    # ISO com hora/timezone -> pega só a parte da data
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    m = re.match(r"^(\d{4})", valor)  # só o ano
    if m:
        return date(int(m.group(1)), 1, 1)
    return None


# ---------------------------------------------------------------- DOI / Crossref

def extrair_doi(url: str) -> str | None:
    m = DOI_RE.search(url)
    return m.group(0).rstrip(".").rstrip("/") if m else None


def buscar_crossref(doi: str, url: str) -> Referencia:
    r = requests.get(
        f"https://api.crossref.org/works/{doi}", headers=HEADERS, timeout=config.HTTP_TIMEOUT
    )
    r.raise_for_status()
    msg = r.json()["message"]

    autores = []
    for a in msg.get("author", []):
        nome = " ".join(p for p in [a.get("given"), a.get("family")] if p)
        if nome:
            autores.append(nome)

    data_pub = None
    partes = msg.get("issued", {}).get("date-parts", [[None]])[0]
    if partes and partes[0]:
        y = partes[0]
        mth = partes[1] if len(partes) > 1 else 1
        d = partes[2] if len(partes) > 2 else 1
        data_pub = date(y, mth, d)

    return Referencia(
        url=url,
        titulo=(msg.get("title") or [None])[0],
        autores=autores,
        site=(msg.get("container-title") or [None])[0],
        data_publicacao=data_pub,
        acesso=date.today(),
    )


# ---------------------------------------------------------------- HTML scraping

def _jsonld(soup: BeautifulSoup) -> dict:
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        candidatos = data if isinstance(data, list) else [data]
        if isinstance(data, dict) and "@graph" in data:
            candidatos = data["@graph"]
        for c in candidatos:
            if isinstance(c, dict) and c.get("@type") in (
                "Article", "NewsArticle", "WebPage", "ScholarlyArticle", "Report", "BlogPosting",
            ):
                return c
    return {}


def _meta(soup: BeautifulSoup, *names: str) -> str | None:
    for n in names:
        tag = soup.find("meta", attrs={"property": n}) or soup.find("meta", attrs={"name": n})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


def _autores_do_jsonld(ld: dict) -> list[str]:
    autor = ld.get("author")
    if isinstance(autor, dict):
        autor = [autor]
    nomes: list[str] = []
    if isinstance(autor, list):
        for a in autor:
            if isinstance(a, dict) and a.get("name"):
                nomes.append(a["name"])
            elif isinstance(a, str):
                nomes.append(a)
    return nomes


def raspar_html(url: str) -> Referencia:
    r = requests.get(url, headers=HEADERS, timeout=config.HTTP_TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    ld = _jsonld(soup)

    titulo = (
        ld.get("headline")
        or _meta(soup, "og:title", "citation_title", "dc.title")
        or (soup.title.string.strip() if soup.title and soup.title.string else None)
    )

    autores = _autores_do_jsonld(ld)
    if not autores:
        m = _meta(soup, "author", "citation_author", "dc.creator")
        if m and not m.startswith("http"):
            autores = [m]

    site = (
        _meta(soup, "og:site_name")
        or (ld.get("publisher", {}).get("name") if isinstance(ld.get("publisher"), dict) else None)
        or urlparse(url).netloc.replace("www.", "")
    )

    instituicao = None
    pub = ld.get("publisher")
    if isinstance(pub, dict) and pub.get("name"):
        instituicao = pub["name"]

    data_pub = _parse_data(
        ld.get("datePublished")
        or _meta(soup, "article:published_time", "citation_publication_date", "dc.date", "date")
    )

    return Referencia(
        url=url,
        titulo=titulo,
        autores=autores,
        site=site,
        instituicao=instituicao,
        data_publicacao=data_pub,
        acesso=date.today(),
    )


# ---------------------------------------------------------------- entrada única

def extrair(url: str) -> Referencia:
    """Ponto de entrada: decide entre Crossref (DOI) e scraping de HTML."""
    doi = extrair_doi(url)
    if doi:
        try:
            return buscar_crossref(doi, url)
        except Exception:
            pass  # se o Crossref falhar, cai pro scraping
    return raspar_html(url)
