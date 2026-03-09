import discord
from discord.ext import commands, tasks
import datetime
import os

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

# BOT ONLINE
@bot.event
async def on_ready():
    print(f"{bot.user} está online!")
    verificar_ranking.start()

# SISTEMA DE PONTOS
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

    await bot.process_commands(message)

# COMANDO LOJA (NUNCA DÁ ERRO)
@bot.command()
async def loja(ctx):

    if ctx.channel.id != LOJA_CANAL_ID:
        return

    embed = discord.Embed(
        title="🛒 Loja de Itens Fortnite",
        description="Loja atual",
        color=discord.Color.blue()
    )

    embed.set_image(url="https://fortnite-api.com/images/shop.png")

    await ctx.send(embed=embed)

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

    mensagem = "🏆 **Ranking Semanal**\n\n"

    for pos, (user_id, pontos) in enumerate(ranking_ordenado, start=1):

        user = await bot.fetch_user(user_id)
        mensagem += f"{pos}. {user.mention} — {pontos} pontos\n"

    await canal.send(mensagem)

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
    await ctx.send(f"Oi {ctx.author.mention}!")

bot.run(TOKEN)




