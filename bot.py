import discord
from discord.ext import commands
import requests
import os
import json

TOKEN = os.getenv("TOKEN")
FORTNITE_API_KEY = os.getenv("FORTNITE_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("Bot online!")

@bot.command()
async def loja(ctx):
    try:
        headers = {"Authorization": FORTNITE_API_KEY}
        r = requests.get("https://fortniteapi.io/v2/shop", headers=headers, timeout=10)
        
        if r.status_code != 200:
            await ctx.send(f"❌ Erro: {r.status_code}")
            return
        
        data = r.json()
        
        # Debug: mostra a estrutura do primeiro item
        if data.get("shop"):
            print("Primeiro item:", json.dumps(data["shop"][0], indent=2))
        
        items = data.get("shop", [])
        
        if not items:
            await ctx.send("🛒 Nenhum item encontrado")
            return
        
        embed = discord.Embed(title="🛒 Loja Fortnite", color=discord.Color.blue())
        
        for item in items[:10]:
            nome = item.get('name') or item.get('displayName') or item.get('title') or 'Item desconhecido'
            
            # Extrai só o valor final do preço
            preco_info = item.get('price', {})
            if isinstance(preco_info, dict):
                preco = preco_info.get('finalPrice', preco_info.get('regularPrice', '?'))
            else:
                preco = preco_info
            
            embed.add_field(name=nome, value=f"💰 {preco} V-Bucks", inline=False)
        
        if items and items[0].get('image'):
            embed.set_thumbnail(url=items[0].get('image'))
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"❌ Erro: {str(e)}")
        print(f"Erro: {e}")

bot.run(TOKEN)
