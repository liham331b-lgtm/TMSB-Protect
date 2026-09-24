import discord
from discord.ext import commands, tasks
import json
import os
import time


FICHIER_DONNEES = "voice_activity.json"

# 48 heures
DELAI = 48 * 60 * 60

MESSAGE_DM = """👋 **Hey !**

Ça fait déjà 48 heures que tu n'es pas passé en vocal sur notre serveur !

💬 On aimerait bien te revoir parmi nous.
🎙️ Viens faire un petit tour en vocal quand tu peux !

À bientôt sur le serveur ❤️
"""


def charger_donnees():
    if not os.path.exists(FICHIER_DONNEES):
        return {}

    try:
        with open(FICHIER_DONNEES, "r", encoding="utf-8") as fichier:
            return json.load(fichier)
    except (json.JSONDecodeError, OSError):
        return {}


def sauvegarder_donnees(donnees):
    with open(FICHIER_DONNEES, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, indent=4)


class ActiviteVocal(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.donnees = charger_donnees()
        self.verification.start()

    def cog_unload(self):
        self.verification.cancel()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        membre,
        avant,
        apres
    ):
        # On vérifie uniquement si la personne vient d'entrer dans un vocal
        if avant.channel is None and apres.channel is not None:

            maintenant = time.time()

            # Dernière présence en vocal
            self.donnees[str(membre.id)] = {
                "last_voice": maintenant,
                "last_dm": maintenant
            }

            sauvegarder_donnees(self.donnees)

            print(
                f"[VOCAL] {membre} est entré en vocal."
            )

    @tasks.loop(hours=1)
    async def verification(self):

        maintenant = time.time()

        for serveur in self.bot.guilds:

            for membre in serveur.members:

                # Ignore les bots
                if membre.bot:
                    continue

                identifiant = str(membre.id)

                # Si la personne n'existe pas encore dans nos données,
                # on commence son suivi maintenant.
                if identifiant not in self.donnees:

                    self.donnees[identifiant] = {
                        "last_voice": maintenant,
                        "last_dm": maintenant
                    }

                    continue

                donnees_membre = self.donnees[identifiant]

                dernier_vocal = donnees_membre.get(
                    "last_voice",
                    maintenant
                )

                dernier_dm = donnees_membre.get(
                    "last_dm",
                    dernier_vocal
                )

                temps_sans_vocal = maintenant - dernier_vocal
                temps_depuis_dm = maintenant - dernier_dm

                # 48h sans vocal ET 48h depuis le dernier DM
                if (
                    temps_sans_vocal >= DELAI
                    and temps_depuis_dm >= DELAI
                ):

                    try:
                        await membre.send(MESSAGE_DM)

                        donnees_membre["last_dm"] = maintenant

                        print(
                            f"[VOCAL] DM envoyé à {membre}."
                        )

                    except discord.Forbidden:
                        print(
                            f"[VOCAL] Impossible de DM {membre} "
                            "(DM fermés)."
                        )

                    except discord.HTTPException as erreur:
                        print(
                            f"[VOCAL] Erreur DM {membre}: {erreur}"
                        )

        sauvegarder_donnees(self.donnees)

    @verification.before_loop
    async def avant_verification(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ActiviteVocal(bot))