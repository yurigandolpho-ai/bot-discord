import discord
from discord.ext import commands, tasks
import os
import datetime
import requests

# --------------------
# CONFIGURAÇÃO
# --------------------
TOKEN = os.getenv("TOKEN")  # Token do Discord
SCREENSHOT_KEY = "BK3486J-B9A4SKA-HEFT2AE-KSKHWAJ"  # Sua chave do ScreenshotAPI

LOJA_CANAL_ID = 1473476696970756276
RANKING_CANAL_ID = 1473011415567827218
PROVAS_CANAL_ID = 1473476696970756277
LIVE_CANAL_ID = 1473476696970756278
CARGO_VIP_ID = 1477809290608644259

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ranking = {}

# --------------------
# EVENTOS
# --------------------
@bot.event
async def on_ready():
    print("Bot online!")
    verificar_ranking.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = message.author.id

    # pontos por participar de live
    if message.channel.id == LIVE_CANAL_ID:
        ranking[uid] = ranking.get(uid, 0) + 1

    # pontos por provas
    if message.channel.id == PROVAS_CANAL_ID:
        if message.content.lower().startswith("!meta"):
            ranking[uid] = ranking.get(uid, 0) + 2
        elif message.attachments:
            ranking[uid] = ranking.get(uid, 0) + 3

    await bot.process_commands(message)

# --------------------
# COMANDO !LOJA
# --------------------
@bot.command()
async def loja(ctx):
    if ctx.channel.id != LOJA_CANAL_ID:
        return

    msg = await ctx.send("⏳ Pegando a loja do Fortnite...")

    try:
        # URL da página da loja do Fortnite
        loja_url = "https://www.fortnite.com/pt-BR/shop"

        # Requisição para ScreenshotAPI
        screenshot_url = f"https://api.screenshotapi.net/screenshot?token={SCREENSHOT_KEY}&url={loja_url}&full_page=true&output=image"

        response = requests.get(screenshot_url, timeout=30)
        response.raise_for_status()

        # Salva a imagem temporariamente
        with open("loja.png", "wb") as f:
            f.write(response.content)

        # Envia a imagem no Discord
        await ctx.send(file=discord.File("loja.png"))

    except Exception as e:
        await msg.edit(content=f"❌ Não foi possível pegar a loja: {e}")

# --------------------
# RANKING SEMANAL
# --------------------
@tasks.loop(hours=24)
async def verificar_ranking():
    hoje = datetime.datetime.utcnow()
    if hoje.weekday() != 6:  # domingo
        return

    canal = bot.get_channel(RANKING_CANAL_ID)
    if not canal:
        return

    if not ranking:
        await canal.send("🏆 Ranking semanal vazio.")
        return

    sorted_rank = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    texto = "🏆 **Ranking Semanal**\n\n"

    for i, (uid, pts) in enumerate(sorted_rank, start=1):
        user = await bot.fetch_user(uid)
        texto += f"{i}. {user.mention} — {pts} pontos\n"

    await canal.send(texto)

    top_uid = sorted_rank[0][0]
    member = canal.guild.get_member(top_uid)
    cargo = canal.guild.get_role(CARGO_VIP_ID)
    if member and cargo:
        await member.add_roles(cargo)

    ranking.clear()

# --------------------
# COMANDO OI
# --------------------
@bot.command()
async def oi(ctx):
    await ctx.send(f"Oi {ctx.author.mention}!")

bot.run(TOKEN)
