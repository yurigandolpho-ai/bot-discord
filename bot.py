import discord
from discord.ext import commands, tasks
import requests
import datetime
import os

# TOKEN seguro (vem da variável de ambiente)
TOKEN = os.getenv("TOKEN")

# INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# CONFIGURAÇÕES (SEUS IDS)
LOJA_CANAL_ID = 1473476696970756276
RANKING_CANAL_ID = 1473011415567827218
PROVAS_CANAL_ID = 1473476696970756277
LIVE_CANAL_ID = 1473476696970756278
CARGO_VIP_ID = 1477809290608644259

ranking = {}

@bot.event
async def on_ready():
    print(f"{bot.user} está online!")
    enviar_loja.start()
    verificar_ranking.start()

# SISTEMA DE PONTOS
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id

    # +1 ponto interação live
    if message.channel.id == LIVE_CANAL_ID:
        ranking[user_id] = ranking.get(user_id, 0) + 1

    # canal de provas
    if message.channel.id == PROVAS_CANAL_ID:

        # +2 meta
        if message.content.lower().startswith("!meta"):
            ranking[user_id] = ranking.get(user_id, 0) + 2

        # +3 prova com imagem
        elif message.attachments:
            ranking[user_id] = ranking.get(user_id, 0) + 3

    await bot.process_commands(message)

# LOJA AUTOMATICA
@tasks.loop(hours=24)
async def enviar_loja():

    canal = bot.get_channel(LOJA_CANAL_ID)

    if not canal:
        return

    try:

        api = "https://fortnite-api.com/v2/shop"
        r = requests.get(api).json()

        items = r.get("data", {}).get("featured", [])

        if not items:
            await canal.send("🛒 Loja não encontrada hoje.")
            return

        await canal.send("🛒 **Loja do Fortnite Atualizada**")

        for item in items[:5]:

            nome = item.get("name", "Item")
            preco = item.get("price", "?")
            img = item.get("images", {}).get("icon")

            if img:
                await canal.send(f"{nome} — {preco} V-Bucks\n{img}")

    except:
        await canal.send("❌ Erro ao pegar loja.")

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

    # TOP 1 ganha cargo
    top_user_id = ranking_ordenado[0][0]

    guild = bot.guilds[0]
    member = guild.get_member(top_user_id)
    cargo = guild.get_role(CARGO_VIP_ID)

    if member and cargo:
        await member.add_roles(cargo)

        bot.loop.create_task(remover_cargo(member, cargo))

    ranking.clear()

async def remover_cargo(member, cargo):

    await discord.utils.sleep_until(
        datetime.datetime.utcnow() + datetime.timedelta(days=7)
    )

    await member.remove_roles(cargo)

@bot.command()
async def oi(ctx):
    await ctx.send(f"Oi {ctx.author.mention}!")

bot.run(TOKEN)