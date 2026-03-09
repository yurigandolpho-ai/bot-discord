@bot.command()
async def loja(ctx):

    try:
        url = "https://fortnite-api.com/v2/shop"
        response = requests.get(url, timeout=10)
        data = response.json()

        print("DATA RECEBIDA:")
        print(data)

        entries = data.get("data", {}).get("entries", [])

        await ctx.send(f"Itens encontrados: {len(entries)}")

    except Exception as e:
        print("ERRO:", e)
        await ctx.send("Erro ao acessar a loja.")
