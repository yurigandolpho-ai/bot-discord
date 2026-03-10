import discord
from discord.ext import commands, tasks
import os
import datetime
import requests
from io import BytesIO

# ----- Configurações -----
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ----- IDs dos canais e cargos -----
LOJA_CANAL_ID = 1473476696970756276
RANKING_CANAL_ID = 1473011415567827218
PROVAS_CANAL_ID = 1473476696970756277
LIVE_CANAL_ID = 1473476696970756278
CARGO_VIP_ID = 1477809290608644259

# ----- Sistema de ranking -----
ranking = {}

# ----- Eventos -----
@bot.event
async def on_ready():
    print("Bot online!")
    verificar_ranking.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = message.author.id

    if message.channel.id == LIVE_CANAL_ID:
        ranking[uid] = ranking.get(uid, 0) + 1

    if message.channel.id == PROVAS_CANAL_ID:
        if message.content.lower().startswith("!meta"):
            ranking[uid] = ranking.get(uid, 0) + 2
        elif message.attachments:
            ranking[uid] = ranking.get(uid, 0) + 3

    await bot.process_commands(message)

# ----- Comando !loja com ScreenshotAPI -----
@bot.command()
async def loja(ctx):
    if ctx.channel.id != LOJA_CANAL_ID:
        return

    msg = await ctx.send("⏳ Pegando a loja do Fortnite...")

    try:
        api_key = "
BK3486J-B9A4SKA-HEFT2AE-KSKHWAJ"  # Substitua pela sua API key do ScreenshotAPI.net
        url_to_capture = "https://www.fortnite.com/pt-BR/shop"
        api_url = f"https://api.screenshotapi.net/screenshot?token={api_key}&url={url_to_capture}&full_page=true"

        response = requests.get(api_url)
        response.raise_for_status()

        image_bytes = BytesIO(response.content)

        embed = discord.Embed(
            title="🛒 Loja do Fortnite de Hoje",
            description="Atualizada automaticamente",
            color=discord.Color.blue()
        )
        embed.set_image(url="attachment://loja.png")

        await ctx.send(embed=embed, file=discord.File(fp=image_bytes, filename="loja.png"))
        await msg.delete()

    except Exception as e:
        await msg.edit(content=f"❌ Erro ao pegar a loja: {e}")
        print("Erro loja:", e)

# ----- Ranking semanal -----
@tasks.loop(hours=24)
async def verificar_ranking():
    hoje = datetime.datetime.utcnow()
    if hoje.weekday() != 6:  # 6 = domingo UTC
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

# ----- Comando teste -----
@bot.command()
async def oi(ctx):
    await ctx.send(f"Oi {ctx.author.mention}!")

# ----- Rodar bot -----
bot.run(TOKEN)
