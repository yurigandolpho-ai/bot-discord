@bot.command()
async def loja(ctx):

    try:

        url = "https://fortnite-api.com/v2/shop"
        response = requests.get(url, timeout=10)

        print("STATUS:", response.status_code)

        data = response.json()

        print("DATA OK")

        entries = data["data"]["entries"]

        print("ENTRIES:", len(entries))

        mensagem = "🛒 Loja Fortnite\n\n"

        for entry in entries[:5]:

            nome = entry["items"][0]["name"]
            preco = entry["finalPrice"]

            mensagem += f"{nome} — {preco} V-Bucks\n"

        await ctx.send(mensagem)

    except Exception as e:

        print("ERRO REAL:", e)

        await ctx.send("Erro ao pegar a loja.")
