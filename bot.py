import discord
from discord.ext import commands
import requests
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOJA_CANAL_ID = 1473476696970756276

@bot.event
async def on_ready():
    print("Bot online!")

@bot.command()
async def loja(ctx):

    if ctx.channel.id != LOJA_CANAL_ID:
        return

    try:

        url = "https://fortnite-api.com/v2/shop"
        response = requests.get(url, timeout=10)
        data = response.json()

        items = data.get("data", {}).get("entries", [])

        # fallback se entries vier vazio
        if not items:
            items = data.get("data", {}).get("featured", {}).get("entries", [])

        if not items:
            items = data.get("data", {}).get("daily", {}).get("entries", [])

        if not items:
            await ctx.send("Não consegui encontrar itens na loja hoje.")
            return

        mensagem = "🛒 **Loja Fortnite**\n\n"

        for entry in items[:10]:

            nome = entry["items"][0]["name"]
            preco = entry.get("finalPrice", "?")

            mensagem += f"• {nome} — {preco} V-Bucks\n"

        await ctx.send(mensagem)

    except Exception as e:
        print(e)
        await ctx.send("Erro ao acessar a loja.")

@bot.command()
async def oi(ctx):
    await ctx.send("Oi!")

bot.run(TOKEN)

