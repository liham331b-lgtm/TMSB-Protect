import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import time
import math

FICHIER = "timeout_data.json"


def charger():
    if not os.path.exists(FICHIER):
        return {"utilisations": [], "timeouts": {}, "historique": []}

    try:
        with open(FICHIER, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.setdefault("utilisations", [])
        data.setdefault("timeouts", {})
        data.setdefault("historique", [])

        return data

    except Exception:
        return {"utilisations": [], "timeouts": {}, "historique": []}


class TimeoutInfoView(discord.ui.View):

    def __init__(self, interaction, data):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.data = data
        self.page = 0

    def pages(self):
        historique = self.data.get("historique", [])

        par_page = 5
        total = max(1, math.ceil(len(historique) / par_page))

        debut = self.page * par_page
        fin = debut + par_page

        return historique[debut:fin], total

    def creer_embed(self):

        serveur = self.interaction.guild
        actifs = self.data.get("timeouts", {})
        historique = self.data.get("historique", [])

        page_items, total_pages = self.pages()

        embed = discord.Embed(
            title="🔇 PANEL DES TIMEOUTS",
            description=(
                f"📊 **Timeouts actuellement actifs :** `{len(actifs)}`\n"
                f"📜 **Sanctions enregistrées :** `{len(historique)}`\n"
                f"👑 **Serveur :** {serveur.name}\n\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
        )

        # TIMEOUTS ACTIFS
        if actifs:

            texte = ""

            for user_id, infos in list(actifs.items())[:10]:

                membre = serveur.get_member(int(user_id))

                nom = membre.mention if membre else f"<@{user_id}>"

                restant = max(0, int(infos["fin"] - time.time()))
                minutes = restant // 60
                secondes = restant % 60

                raison = infos.get("raison", "Non renseignée")
                modo = infos.get("moderateur", "Inconnu")

                texte += (
                    f"🔇 {nom}\n"
                    f"📝 **Raison :** {raison}\n"
                    f"🛡️ **Modérateur :** <@{modo}>\n"
                    f"⏳ **Temps restant :** {minutes}m {secondes}s\n\n"
                )

            embed.add_field(
                name="🔴 TIMEOUTS ACTIFS",
                value=texte[:1024],
                inline=False
            )

        else:
            embed.add_field(
                name="🔴 TIMEOUTS ACTIFS",
                value="Aucun timeout actuellement.",
                inline=False
            )

        # HISTORIQUE
        if page_items:

            texte = ""

            for sanction in page_items:

                membre_id = sanction.get("membre_id", "Inconnu")
                modo_id = sanction.get("moderateur_id", "Inconnu")

                raison = sanction.get("raison", "Inconnue")
                date = sanction.get("date", "Inconnue")
                duree = sanction.get("duree", "10 minutes")

                texte += (
                    f"👤 <@{membre_id}>\n"
                    f"📝 **Raison :** {raison}\n"
                    f"🛡️ **Modérateur :** <@{modo_id}>\n"
                    f"⏱️ **Durée :** {duree}\n"
                    f"🕐 **Date :** {date}\n\n"
                )

            embed.add_field(
                name=f"📜 HISTORIQUE — PAGE {self.page + 1}/{total_pages}",
                value=texte[:1024],
                inline=False
            )

        else:
            embed.add_field(
                name="📜 HISTORIQUE",
                value="Aucune sanction enregistrée.",
                inline=False
            )

        embed.set_footer(
            text="TM'SB | PROTECT • Panel réservé aux administrateurs"
        )

        return embed

    def mettre_a_jour_boutons(self):

        historique = self.data.get("historique", [])
        total_pages = max(1, math.ceil(len(historique) / 5))

        self.precedent.disabled = self.page <= 0
        self.suivant.disabled = self.page >= total_pages - 1

    @discord.ui.button(
        label="◀️",
        style=discord.ButtonStyle.secondary
    )
    async def precedent(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Administrateurs uniquement.",
                ephemeral=True
            )
            return

        if self.page > 0:
            self.page -= 1

        self.mettre_a_jour_boutons()

        await interaction.response.edit_message(
            embed=self.creer_embed(),
            view=self
        )

    @discord.ui.button(
        label="🔄 Actualiser",
        style=discord.ButtonStyle.primary
    )
    async def actualiser(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Administrateurs uniquement.",
                ephemeral=True
            )
            return

        self.data = charger()

        total_pages = max(
            1,
            math.ceil(len(self.data.get("historique", [])) / 5)
        )

        if self.page >= total_pages:
            self.page = total_pages - 1

        self.mettre_a_jour_boutons()

        await interaction.response.edit_message(
            embed=self.creer_embed(),
            view=self
        )

    @discord.ui.button(
        label="▶️",
        style=discord.ButtonStyle.secondary
    )
    async def suivant(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Administrateurs uniquement.",
                ephemeral=True
            )
            return

        total_pages = max(
            1,
            math.ceil(len(self.data.get("historique", [])) / 5)
        )

        if self.page < total_pages - 1:
            self.page += 1

        self.mettre_a_jour_boutons()

        await interaction.response.edit_message(
            embed=self.creer_embed(),
            view=self
        )


class TimeoutInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="timeoutinfo",
        description="Affiche le panel complet des timeouts."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def timeoutinfo(self, interaction: discord.Interaction):

        data = charger()

        view = TimeoutInfoView(interaction, data)
        view.mettre_a_jour_boutons()

        await interaction.response.send_message(
            embed=view.creer_embed(),
            view=view,
            ephemeral=True
        )

    @timeoutinfo.error
    async def timeoutinfo_error(
        self,
        interaction: discord.Interaction,
        error
    ):

        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            message = "❌ Cette commande est réservée aux administrateurs."
        else:
            message = f"❌ Erreur : `{error}`"

        if interaction.response.is_done():
            await interaction.followup.send(
                message,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                message,
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(TimeoutInfo(bot))