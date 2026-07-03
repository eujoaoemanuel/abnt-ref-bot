"""
Formatação de referências no padrão ABNT NBR 6023 (documentos online).

Regra do caso comum:
  SOBRENOME, Nome. Título. Nome do site, ano. Disponível em: URL. Acesso em: data.

Sem autor pessoal -> entra a instituição (caixa alta) no lugar do autor.
Código determinístico de propósito: ABNT é norma fixa, não precisa de IA.

Este módulo não depende de rede nem do Discord -> fácil de testar isolado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

# Meses abreviados conforme ABNT (maio não abrevia).
MESES_ABNT = {
    1: "jan.", 2: "fev.", 3: "mar.", 4: "abr.", 5: "maio", 6: "jun.",
    7: "jul.", 8: "ago.", 9: "set.", 10: "out.", 11: "nov.", 12: "dez.",
}

# Sufixos que não são sobrenome (não vão pra caixa alta sozinhos).
SUFIXOS = {"filho", "neto", "júnior", "junior", "jr", "sobrinho"}


@dataclass
class Referencia:
    """Metadados normalizados de uma fonte, prontos pra formatar."""
    url: str
    titulo: str | None = None
    autores: list[str] = field(default_factory=list)  # nomes crus: "João Silva"
    site: str | None = None          # nome do veículo/site
    instituicao: str | None = None   # autor institucional (quando não há pessoa)
    data_publicacao: date | None = None
    acesso: date | None = None       # default: hoje


def _abnt_data(d: date, completa: bool = True) -> str:
    """Data no padrão ABNT: '3 jul. 2026' (completa) ou '2026' (só ano)."""
    if not completa:
        return str(d.year)
    return f"{d.day} {MESES_ABNT[d.month]} {d.year}"


def _formata_autor(nome: str) -> str:
    """
    'João da Silva' -> 'SILVA, João da'
    Heurística: última palavra é o sobrenome, salvo se for sufixo (Filho, Neto...),
    quando puxa a penúltima junto. Casos raros o usuário ajusta na mão.
    """
    partes = nome.strip().split()
    if len(partes) == 1:
        return partes[0].upper()

    if partes[-1].lower().strip(".") in SUFIXOS and len(partes) >= 3:
        sobrenome = f"{partes[-2]} {partes[-1]}"
        nomes = " ".join(partes[:-2])
    else:
        sobrenome = partes[-1]
        nomes = " ".join(partes[:-1])
    return f"{sobrenome.upper()}, {nomes}"


def _bloco_autoria(ref: Referencia) -> str | None:
    """Monta a entrada de autoria: pessoas, instituição, ou nada."""
    if ref.autores:
        formatados = [_formata_autor(a) for a in ref.autores if a.strip()]
        if len(formatados) > 3:  # ABNT permite "et al." a partir de 4 autores
            return f"{formatados[0]} et al."
        return "; ".join(formatados)
    if ref.instituicao:
        return ref.instituicao.upper()
    return None


def formatar_abnt(ref: Referencia) -> str:
    """Referência completa em texto plano, pronta pra colar."""
    acesso = ref.acesso or date.today()
    partes: list[str] = []

    autoria = _bloco_autoria(ref)
    if autoria:
        partes.append(autoria if autoria.endswith(".") else autoria + ".")

    titulo = (ref.titulo or "[Título não identificado]").strip().rstrip(".")
    partes.append(titulo + ".")

    if ref.site and ref.site.lower() != (autoria or "").lower():
        partes.append(ref.site.strip().rstrip(".") + ",")

    if ref.data_publicacao:
        partes.append(_abnt_data(ref.data_publicacao, completa=False) + ".")

    partes.append(f"Disponível em: {ref.url}.")
    partes.append(f"Acesso em: {_abnt_data(acesso)}.")

    return " ".join(partes)


def formatar_para_discord(ref: Referencia) -> str:
    """
    Versão pro embed: título em negrito (markdown), como manda a ABNT.
    OBS: ao copiar pro Word o negrito não vai junto — reaplicar lá.
    """
    texto = formatar_abnt(ref)
    titulo = (ref.titulo or "[Título não identificado]").strip().rstrip(".")
    if titulo in texto:
        texto = texto.replace(titulo + ".", f"**{titulo}**.", 1)
    return texto
