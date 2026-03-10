import discord
from discord.ext import commands
from pyppeteer import launch
import asyncio

LOJA_CANAL_ID = 1473476696970756276

@commands.command()
async def loja(ctx):
    # Só funciona no canal correto
    if ctx.channel.id != LOJA_CANAL_ID:
        return

    # Mensagem inicial
    msg = await ctx.send("⏳ Pegando a loja do Fortnite, aguarde...")

    try:
        # Inicia navegador invisível
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})

        # Abre o site da loja
        await page.goto("https://www.fortnite.com/pt-BR/shop", {'waitUntil': 'networkidle2'})
        await asyncio.sleep(3)  # espera itens carregarem completamente

        # Tira screenshot da página inteira
        screenshot_path = "loja.png"
        await page.screenshot({'path': screenshot_path, 'fullPage': True})
        await browser.close()

        # Cria embed
        embed = discord.Embed(
            title="🛒 Loja do Fortnite de Hoje",
            description="Atualizada automaticamente",
            color=discord.Color.blue()
        )
        embed.set_image(url="attachment://loja.png")

        # Envia embed com imagem
        await ctx.send(embed=embed, file=discord.File(screenshot_path))

        # Deleta a mensagem de carregando
        await msg.delete()

    except Exception as e:
        await msg.edit(content=f"❌ Erro ao pegar a loja: {e}")
        print("Erro ao pegar loja:", e)
