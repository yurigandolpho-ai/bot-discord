import discord
from discord.ext import commands, tasks
import requests
import os
import datetime

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDS DOS CANAIS
LOJA_CANAL_ID = 1473476696970756276
RANKING_CANAL_ID = 1473011415567827218
PROVAS_CANAL_ID = 1473476696970756277
LIVE_CANAL_ID = 1473476696970756278
CARGO_VIP_ID = 1477809290608644259

ranking = {}

@bot.event
async def on_ready():
    print("Bot online!")
    verificar_ranking.start()

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = message.author.id

    # pontos nas lives
    if message.channel.id == LIVE_CANAL_ID:
        ranking[user_id] = ranking.get(user_id, 0) + 1

    # pontos nas provas
    if message.channel.id == PROVAS_CANAL_ID:

        if message.content.lower().startswith("!meta"):
            ranking[user_id] = ranking.get(user_id, 0) + 2

        elif message.attachments:
            ranking[user_id] = ranking.get(user_id, 0) + 3

    await bot.process_commands(message)

# COMANDO LOJA
import requests

@bot.command()
async def loja(ctx):

    try:
        r = requests.get("https://fortnite-api.com/v2/shop?language=pt-BR", timeout=10)
        data = r.json()

        entries = data["data"]["featured"]["entries"]

        mensagem = "🛒 **LOJA DO FORTNITE**\n\n"

        for item in entries[:5]:
            nome = item["items"][0]["name"]
            preco = item["finalPrice"]

            mensagem += f"{nome} — {preco} V-Bucks\n"

        await ctx.send(mensagem)

    except Exception as erro:
        print("ERRO LOJA:", erro)
        await ctx.send("❌ Erro ao pegar a loja.")
# RANKING SEMANAL
@tasks.loop(hours=24)
async def verificar_ranking():

    hoje = datetime.datetime.utcnow()

    if hoje.weekday() != 6:
        return

    canal = bot.get_channel(RANKING_CANAL_ID)

    if not canal:
        return

    if not ranking:
        await canal.send("🏆 Ranking semanal vazio.")
        return

    ranking_ordenado = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    texto = "🏆 **Ranking Semanal**\n\n"

    for pos, (user_id, pontos) in enumerate(ranking_ordenado, start=1):

        user = await bot.fetch_user(user_id)
        texto += f"{pos}. {user.mention} — {pontos} pontos\n"

    await canal.send(texto)

    # dar VIP ao top 1
    top_user_id = ranking_ordenado[0][0]

    guild = canal.guild
    member = guild.get_member(top_user_id)
    cargo = guild.get_role(CARGO_VIP_ID)

    if member and cargo:
        await member.add_roles(cargo)

    ranking.clear()

# COMANDO TESTE
@bot.command()
async def oi(ctx):
    await ctx.send("Oi!")

bot.run(TOKEN)




