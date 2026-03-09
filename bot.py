import discord
from discord.ext import commands, tasks
import os
import datetime

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDS
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

    if message.channel.id == LIVE_CANAL_ID:
        ranking[user_id] = ranking.get(user_id, 0) + 1

    if message.channel.id == PROVAS_CANAL_ID:

        if message.content.lower().startswith("!meta"):
            ranking[user_id] = ranking.get(user_id, 0) + 2

        elif message.attachments:
            ranking[user_id] = ranking.get(user_id, 0) + 3

    # IMPORTANTE (permite comandos funcionar)
    await bot.process_commands(message)

# COMANDO LOJA
@bot.command()
async def loja(ctx):

    print("Comando loja usado")  # aparece no log do Railway

    if ctx.channel.id != LOJA_CANAL_ID:
        await ctx.send("Use o comando apenas no canal da loja.")
        return

    await ctx.send(
        "🛒 Loja Fortnite\n\n"
        "Veja a loja atual aqui:\n"
        "https://fortnite.gg/shop"
    )

@tasks.loop(hours=24)
async def verificar_ranking():

    hoje = datetime.datetime.utcnow()

    if hoje.weekday() != 6:
        return

    canal = bot.get_channel(RANKING_CANAL_ID)

    if not canal:
        return

    if not ranking:
        await canal.send("Ranking semanal vazio.")
        return

    ranking_ordenado = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    texto = "🏆 Ranking Semanal\n\n"

    for pos, (user_id, pontos) in enumerate(ranking_ordenado, start=1):

        user = await bot.fetch_user(user_id)
        texto += f"{pos}. {user.mention} — {pontos} pontos\n"

    await canal.send(texto)

    ranking.clear()

@bot.command()
async def oi(ctx):
    await ctx.send("Oi!")

bot.run(TOKEN)



