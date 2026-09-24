import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
import time
from datetime import timedelta

SALON_AUTORISE = 1552800697928519730
ROLE_AUTORISE = 1552786859858595872

DUREE_TIMEOUT_MINUTES = 10
MAX_TIMEOUTS_PAR_HEURE = 2

FICHIER = "timeout_data.json"

SANCTIONS = {
    "trolling": "Trolling",
    "spam": "Spam",
    "soundbord": "Soundbord",
    "publiciter": "Publicité",
    "propos": "Propos",
    "deplacer": "Déplacer",
    "insult": "Insulte",
    "double compte": "Double compte",
    "discrimination": "Discrimination",
    "comportement extreme": "Comportement extrême"
}


def charger():
    if not os.path.exists(FICHIER):
        return {"utilisations": [], "timeouts": {}}

    try:
        with open(FICHIER, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"utilisations": [], "timeouts": {}}


def sauvegarder(data):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


class TimeoutSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.data = charger()
        self.verification_timeouts.start()

    def cog_unload(self):
        self.verification_timeouts.cancel()

    timeout_choices = [
        app_commands.Choice(name="Trolling", value="trolling"),
        app_commands.Choice(name="Spam", value="spam"),
        app_commands.Choice(name="Soundbord", value="soundbord"),
        app_commands.Choice(name="Publicité", value="publiciter"),
        app_commands.Choice(name="Propos", value="propos"),
        app_commands.Choice(name="Déplacer", value="deplacer"),
        app_commands.Choice(name="Insulte", value="insult"),
        app_commands.Choice(name="Double compte", value="double compte"),
        app_commands.Choice(name="Discrimination", value="discrimination"),
        app_commands.Choice(name="Comportement extrême", value="comportement extreme"),
    ]

    @app_commands.command(
        name="timeout",
        description="Timeout un membre pendant 10 minutes."
    )
    @app_commands.describe(
        user="Utilisateur à sanctionner",
        sanction="Raison de la sanction"
    )
    @app_commands.choices(sanction=timeout_choices)
    async def timeout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        sanction: app_commands.Choice[str]
    ):

        # Vérification du salon
        if interaction.channel_id != SALON_AUTORISE:
            await interaction.response.send_message(
                f"❌ Cette commande est utilisable uniquement dans <#{SALON_AUTORISE}>.",
                ephemeral=True
            )
            return

        # Vérification du rôle
        if ROLE_AUTORISE not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                "❌ Tu n'as pas le rôle nécessaire pour utiliser cette commande.",
                ephemeral=True
            )
            return

        # Impossible de sanctionner un bot
        if user.bot:
            await interaction.response.send_message(
                "❌ Tu ne peux pas timeout un bot.",
                ephemeral=True
            )
            return

        # Impossible de se sanctionner soi-même
        if user.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ Tu ne peux pas te timeout toi-même.",
                ephemeral=True
            )
            return

        # Vérification hiérarchie des rôles
        if user.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Tu ne peux pas sanctionner un membre ayant un rôle égal ou supérieur au tien.",
                ephemeral=True
            )
            return

        # Vérification permission du bot
        me = interaction.guild.me

        if me is None or not me.guild_permissions.moderate_members:
            await interaction.response.send_message(
                "❌ Le bot n'a pas la permission **Modérer les membres**.",
                ephemeral=True
            )
            return

        if user.top_role >= me.top_role:
            await interaction.response.send_message(
                "❌ Je ne peux pas timeout ce membre car son rôle est égal ou supérieur au mien.",
                ephemeral=True
            )
            return

        maintenant = time.time()

        # Nettoyage des utilisations datant de plus d'une heure
        self.data["utilisations"] = [
            timestamp
            for timestamp in self.data["utilisations"]
            if maintenant - timestamp < 3600
        ]

        # Limite de 2 timeouts par heure
        if len(self.data["utilisations"]) >= MAX_TIMEOUTS_PAR_HEURE:
            await interaction.response.send_message(
                "⏳ La limite de **2 timeouts par heure** a été atteinte.",
                ephemeral=True
            )
            sauvegarder(self.data)
            return

        raison = SANCTIONS[sanction.value]

        try:
            # Timeout de 10 minutes
            await user.timeout(
                timedelta(minutes=DUREE_TIMEOUT_MINUTES),
                reason=f"{raison} | Modérateur : {interaction.user}"
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Discord a refusé le timeout. Vérifie les permissions du bot.",
                ephemeral=True
            )
            return

        except discord.HTTPException as erreur:
            await interaction.response.send_message(
                f"❌ Erreur Discord : `{erreur}`",
                ephemeral=True
            )
            return

        # Enregistrement
        self.data["utilisations"].append(maintenant)

        fin = maintenant + (DUREE_TIMEOUT_MINUTES * 60)

        self.data["timeouts"][str(user.id)] = {
            "guild_id": interaction.guild.id,
            "fin": fin,
            "raison": raison
        }

        sauvegarder(self.data)

        # Réponse dans le salon
        embed = discord.Embed(
            title="🔇 Timeout appliqué",
            description=(
                f"**Utilisateur :** {user.mention}\n"
                f"**Sanction :** {raison}\n"
                f"**Durée :** {DUREE_TIMEOUT_MINUTES} minutes\n"
                f"**Modérateur :** {interaction.user.mention}"
            )
        )

        await interaction.response.send_message(embed=embed)

        # MP au membre sanctionné
        try:
            await user.send(
                f"🔇 **Tu as été timeout sur {interaction.guild.name}.**\n\n"
                f"**Raison :** {raison}\n"
                f"**Durée :** {DUREE_TIMEOUT_MINUTES} minutes\n\n"
                f"⏳ Ton timeout prendra fin automatiquement dans 10 minutes."
            )
        except discord.Forbidden:
            print(f"[TIMEOUT] Impossible d'envoyer un MP à {user}.")

    @tasks.loop(seconds=10)
    async def verification_timeouts(self):

        maintenant = time.time()
        changements = False

        for user_id, infos in list(self.data["timeouts"].items()):

            if maintenant < infos["fin"]:
                continue

            guild = self.bot.get_guild(infos["guild_id"])

            if guild is None:
                del self.data["timeouts"][user_id]
                changements = True
                continue

            membre = guild.get_member(int(user_id))

            if membre is not None:

                try:
                    await membre.send(
                        f"✅ **Ton timeout est terminé sur {guild.name}.**\n\n"
                        f"Tu peux de nouveau participer normalement au serveur."
                    )
                except discord.Forbidden:
                    print(f"[TIMEOUT] Impossible d'envoyer le MP de fin à {membre}.")

            del self.data["timeouts"][user_id]
            changements = True

        if changements:
            sauvegarder(self.data)

    @verification_timeouts.before_loop
    async def avant_verification(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(TimeoutSystem(bot))