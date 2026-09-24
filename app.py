import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN est absent du fichier .env"
    )

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print("====================================")
    print("       TM'SB | PROTECT")
    print("====================================")
    print(f"Bot : {bot.user}")
    print(f"Serveurs : {len(bot.guilds)}")
    print("Statut : EN LIGNE")

    try:
        synced = await bot.tree.sync()

        print(
            f"Commandes slash synchronisées : {len(synced)}"
        )

    except Exception as erreur:
        print(
            f"Erreur synchronisation : {erreur}"
        )


async def charger_commandes():

    dossier = "commandes"

    for fichier in os.listdir(dossier):

        if not fichier.endswith(".py"):
            continue

        if fichier == "__init__.py":
            continue

        nom_module = fichier[:-3]

        try:
            await bot.load_extension(
                f"commandes.{nom_module}"
            )

            print(
                f"[OK] Commande chargée : {nom_module}"
            )

        except Exception as erreur:

            print(
                f"[ERREUR] {nom_module} : {erreur}"
            )


async def main():

    async with bot:

        await charger_commandes()

        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())