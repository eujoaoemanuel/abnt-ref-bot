"""
Ponto de entrada do bot.

- Lê o token do .env (DISCORD_TOKEN).
- Carrega os cogs listados em COGS.
- Sincroniza os slash commands ao ficar online.

Rodar direto:  python bot.py
Recomendado:   use o start.bat (Windows) ou start.sh (Linux/Mac) — eles cuidam
               do ambiente e das dependências sozinhos.
"""

from __future__ import annotations

import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Cogs carregados no boot. Adicione novos comandos aqui (roadmap).
COGS = [
    "src.cogs.referencia",
]

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("abnt-ref-bot")

# Slash commands não exigem intents privilegiados.
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info("Conectado como %s (id %s)", bot.user, bot.user.id)
    try:
        synced = await bot.tree.sync()
        log.info("Sincronizados %d slash command(s).", len(synced))
    except Exception as e:
        log.exception("Falha ao sincronizar comandos: %s", e)


async def main():
    if not TOKEN or TOKEN == "cole_seu_token_aqui":
        raise SystemExit(
            "\n[ERRO] DISCORD_TOKEN não configurado.\n"
            "Abra o arquivo .env e cole o token do bot em DISCORD_TOKEN=.\n"
        )
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
        await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot encerrado.")
