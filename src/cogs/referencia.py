"""
Cog do comando /referencia.

/referencia url:<link> -> extrai metadados -> formata em ABNT ->
embed (título em negrito) + botão que reenvia o texto puro pra copiar.

Pra adicionar um comando novo no futuro: crie outro arquivo aqui em src/cogs/
e registre em bot.py (COGS). É esse o ponto de extensão do roadmap.
"""

from __future__ import annotations

import functools

import discord
from discord import app_commands
from discord.ext import commands

import config
from ..formatter import formatar_abnt, formatar_para_discord
from ..metadata import extrair


class CopiarView(discord.ui.View):
    """Botão que devolve só o texto puro, pronto pra copiar."""

    def __init__(self, texto_puro: str):
        super().__init__(timeout=600)
        self.texto_puro = texto_puro

    @discord.ui.button(label="Texto puro", emoji="📋", style=discord.ButtonStyle.secondary)
    async def copiar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"```\n{self.texto_puro}\n```", ephemeral=True
        )


class Referencia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="referencia",
        description="Gera a referência ABNT (NBR 6023) de um link.",
    )
    @app_commands.describe(url="Link da página ou artigo (aceita DOI).")
    async def referencia(self, interaction: discord.Interaction, url: str):
        if not url.startswith(("http://", "https://")):
            await interaction.response.send_message(
                "❌ Manda um link começando com `http://` ou `https://`.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            loop = interaction.client.loop
            ref = await loop.run_in_executor(None, functools.partial(extrair, url))
        except Exception as e:
            await interaction.followup.send(
                f"⚠️ Não consegui ler essa página.\n`{type(e).__name__}: {e}`\n"
                "Alguns sites bloqueiam bots ou não expõem os metadados."
            )
            return

        embed = discord.Embed(
            title="Referência ABNT (NBR 6023)",
            description=formatar_para_discord(ref),
            color=config.EMBED_COLOR,
        )
        faltando = [
            nome for nome, val in [
                ("autor", ref.autores or ref.instituicao),
                ("título", ref.titulo),
                ("data", ref.data_publicacao),
            ] if not val
        ]
        if faltando:
            embed.add_field(
                name="⚠️ Revisar manualmente",
                value="Não encontrei: " + ", ".join(faltando),
                inline=False,
            )
        embed.set_footer(text="Confira antes de usar — o negrito do título não vai no copiar.")

        await interaction.followup.send(embed=embed, view=CopiarView(formatar_abnt(ref)))


async def setup(bot: commands.Bot):
    await bot.add_cog(Referencia(bot))
