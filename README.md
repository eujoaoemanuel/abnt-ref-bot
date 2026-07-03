# 📚 ABNT Ref Bot

Bot pessoal de Discord que transforma um **link** numa **referência formatada em ABNT (NBR 6023)**, pronta pra colar na sua lista de referências bibliográficas.

Você manda o comando, ele devolve isso:

```
ANDRADE, João Vitor. Um indicador computável de risco derivado do SINAN.
Revista Brasileira de Saúde, 2024. Disponível em: https://doi.org/10.1000/exemplo.
Acesso em: 3 jul. 2026.
```

Sem decorar comando com `!`: é **slash command** (`/`), com autocomplete do próprio Discord, resposta em cartão (embed) e botão pra copiar o texto limpo.

---

## ⚡ Começar (o jeito fácil)

> Pré-requisito único: **Python 3.10 (ou superior)** instalado ([baixe aqui](https://www.python.org/downloads/) — marque **"Add Python to PATH"**).

1. Baixe/clone este projeto.
2. Crie o bot no Discord e pegue o token (passo a passo na seção abaixo — leva 2 min).
3. **Windows:** dê duplo-clique em **`start.bat`**.
   **Linux/Mac:** rode **`./start.sh`** no terminal.

Só isso. O inicializador faz o resto sozinho:

- cria o ambiente virtual (`.venv`),
- baixa as bibliotecas necessárias,
- na primeira vez, abre o arquivo do token pra você colar,
- e sobe o bot.

Da segunda vez em diante é o mesmo duplo-clique — sem reinstalar nada.

---

## 🤖 Criar o bot no Discord (só na primeira vez)

### 1. Criar a aplicação
1. Acesse o **Discord Developer Portal**: <https://discord.com/developers/applications>
2. **New Application** → dê um nome (ex.: `ABNT Ref Bot`) → **Create**.
3. Menu lateral → **Bot** → se pedir, confirme **Add Bot**.
4. Ainda em **Bot** → **Reset Token** → **Copy**. Esse é o token — trate como senha, **não** cole em lugar público.

> Você **não** precisa ativar nenhum "Privileged Gateway Intent". Slash commands não exigem isso.

### 2. Convidar o bot pro seu servidor
1. Menu lateral → **OAuth2** → **URL Generator**.
2. Em **Scopes**, marque `bot` e `applications.commands`.
3. Em **Bot Permissions**, marque `Send Messages` e `Use Slash Commands`.
4. Copie a URL gerada no rodapé, abra no navegador, escolha seu servidor e autorize.

### 3. Colar o token
Ao rodar o `start.bat`/`start.sh` pela primeira vez, ele abre o arquivo `.env`.
Cole o token depois de `DISCORD_TOKEN=`, salve e feche. Pronto.

---

## 💬 Usar

No servidor, digite:

```
/referencia url: https://www.gov.br/saude/pt-br/algum-artigo
```

O bot responde com um cartão (título em **negrito**, como manda a ABNT) e um botão **📋 Texto puro** que reenvia só o texto limpo pra copiar. Se faltar algum dado na página, ele avisa o que revisar.

> Na 1ª vez, comandos `/` globais podem levar alguns minutos pra aparecer no Discord. Depois é instantâneo.

---

## 🧠 Como funciona (por dentro)

1. Link com **DOI** → consulta a **API Crossref** (dados estruturados e confiáveis).
2. **Página comum** → lê o HTML e extrai metadados nesta ordem: JSON-LD (schema.org) → meta tags (`og:`, `article:`, `citation_*`) → `<title>`/domínio.
3. Aplica as regras da **NBR 6023** e devolve o texto.

**Sem IA nesta versão, de propósito.** ABNT é norma fixa: é parsing + regra determinística. IA seria over-engineering aqui — ela entra no roadmap só pros casos ambíguos.

---

## 📁 Estrutura do projeto

```
abnt-ref-bot/
├── start.bat            ← Windows: duplo-clique e pronto
├── start.sh             ← Linux/Mac: ./start.sh
├── bot.py               ← entrada; lista de cogs fica aqui (COGS)
├── config.py            ← ajustes centrais (cor, formato, timeout)
├── requirements.txt
├── .env.example         ← modelo do token
├── .gitignore
└── src/
    ├── formatter.py     ← regras da ABNT (sem rede, fácil de testar)
    ├── metadata.py      ← scraping + JSON-LD + Crossref
    └── cogs/
        └── referencia.py ← o comando /referencia
```

**Onde encostar pra cada tipo de mudança:**
- Ajuste rápido (cor, timeout, formato padrão) → `config.py`
- Regra de formatação → `src/formatter.py`
- De onde vêm os dados → `src/metadata.py`
- Comando novo → novo arquivo em `src/cogs/` + registrar em `COGS` (no `bot.py`)

---

## 🗺️ Roadmap

- [ ] `/formato` pra alternar **ABNT / APA / Vancouver**
- [ ] Banco **SQLite** pra **salvar** e **buscar** referências por tema
- [ ] Validação anti-alucinação (checar se uma citação existe de verdade) — aqui sim entra IA
- [ ] Dashboard web lendo o mesmo banco

A arquitetura já foi pensada pra isso: cada item acima é um cog novo ou um módulo isolado, sem mexer no que já funciona.

---

## ⚠️ Limitações conhecidas

- Sites que **bloqueiam bots** ou não preenchem metadados vêm com campos faltando — o cartão avisa o que revisar.
- A heurística de autor assume "última palavra = sobrenome"; nomes compostos raros podem precisar de ajuste manual.
- O **negrito do título** é visual do Discord; ao copiar pro Word, reaplique lá.
- Cobre o **caso comum** de documento online. Livros e capítulos entram numa próxima versão.

---

## 🛠️ Rodar na mão (sem o inicializador)

Se preferir controlar tudo você mesmo:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # cole o token no .env
python bot.py
```

---

### Dica de dev: comandos aparecendo na hora

Comandos `/` globais demoram a propagar. Pra testar rápido num servidor só, troque no `bot.py` o `await bot.tree.sync()` por uma versão com `guild=discord.Object(id=SEU_SERVER_ID)` (pegue o ID ativando o **Modo Desenvolvedor** no Discord → botão direito no servidor → **Copiar ID**).
