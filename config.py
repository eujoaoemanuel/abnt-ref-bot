"""
Configurações centrais do bot.

Mexa AQUI pra ajustar o comportamento sem precisar caçar nada no resto do código.
É o primeiro lugar onde os upgrades do roadmap vão encostar.
"""

# Cor da barra lateral dos embeds (hex).
EMBED_COLOR = 0x2ECC71

# Formato padrão das referências. Futuro: "APA", "VANCOUVER".
FORMATO_PADRAO = "ABNT"

# Timeout (segundos) das requisições de rede ao ler uma página.
HTTP_TIMEOUT = 15

# User-Agent enviado ao raspar páginas. Alguns sites bloqueiam bots sem isso.
USER_AGENT = (
    "Mozilla/5.0 (compatible; ABNTRefBot/1.0; "
    "+https://github.com/seu-usuario/abnt-ref-bot)"
)
