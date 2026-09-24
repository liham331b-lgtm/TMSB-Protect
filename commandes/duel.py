import random
import discord
from discord import app_commands
from discord.ext import commands


class DuelView(discord.ui.View):

    def __init__(self, joueur1, joueur2):
        super().__init__(timeout=120)

        self.joueur1 = joueur1
        self.joueur2 = joueur2

        self.score1 = 0
        self.score2 = 0

        self.tour = 1
        self.choix = {}

    async def jouer(self, interaction: discord.Interaction, choix: str):

        if interaction.user.id not in [self.joueur1.id, self.joueur2.id]:
            await interaction.response.send_message(
                "❌ Tu ne participes pas à ce duel.",
                ephemeral=True
            )
            return

        if interaction.user.id in self.choix:
            await interaction.response.send_message(
                "⏳ Tu as déjà choisi pour ce tour.",
                ephemeral=True
            )
            return

        self.choix[interaction.user.id] = choix

        await interaction.response.send_message(
            f"✅ Choix enregistré : **{choix}**",
            ephemeral=True
        )

        # On attend le deuxième joueur
        if len(self.choix) < 2:
            return

        choix1 = self.choix[self.joueur1.id]
        choix2 = self.choix[self.joueur2.id]

        # Résolution du tour
        gagnant = self.resultat(choix1, choix2)

        if gagnant == 1:
            self.score1 += 1
            resultat = f"🏆 {self.joueur1.mention} remporte le tour !"
        elif gagnant == 2:
            self.score2 += 1
            resultat = f"🏆 {self.joueur2.mention} remporte le tour !"
        else:
            resultat = "🤝 Égalité !"

        # Victoire finale
        if self.score1 >= 3 or self.score2 >= 3:

            if self.score1 > self.score2:
                vainqueur = self.joueur1
            else:
                vainqueur = self.joueur2

            embed = discord.Embed(
                title="🏆 DUEL TERMINÉ",
                description=(
                    f"🎉 **Vainqueur :** {vainqueur.mention}\n\n"
                    f"⚔️ {self.joueur1.mention} : **{self.score1}** points\n"
                    f"⚔️ {self.joueur2.mention} : **{self.score2}** points\n\n"
                    f"🥇 Félicitations {vainqueur.mention} !"
                )
            )

            for bouton in self.children:
                bouton.disabled = True

            await interaction.message.edit(
                embed=embed,
                view=self
            )

            self.stop()
            return

        # Tour suivant
        self.tour += 1
        self.choix = {}

        embed = discord.Embed(
            title=f"⚔️ DUEL — TOUR {self.tour}",
            description=(
                f"{self.joueur1.mention} **VS** {self.joueur2.mention}\n\n"
                f"🎯 Choisissez votre action !\n\n"
                f"⚔️ **Score actuel**\n"
                f"{self.joueur1.mention} : **{self.score1}**\n"
                f"{self.joueur2.mention} : **{self.score2}**\n\n"
                f"📢 {resultat}"
            )
        )

        await interaction.message.edit(
            embed=embed,
            view=self
        )

    @staticmethod
    def resultat(choix1, choix2):

        if choix1 == choix2:
            return 0

        # Pierre > Ciseaux
        # Ciseaux > Papier
        # Papier > Pierre

        victoires = {
            "🪨": "✂️",
            "✂️": "📄",
            "📄": "🪨"
        }

        if victoires[choix1] == choix2:
            return 1

        return 2

    @discord.ui.button(
        label="Pierre",
        emoji="🪨",
        style=discord.ButtonStyle.primary
    )
    async def pierre(
        self,
        interaction: discord.Interaction,
        bouton: discord.ui.Button
    ):
        await self.jouer(interaction, "🪨")

    @discord.ui.button(
        label="Papier",
        emoji="📄",
        style=discord.ButtonStyle.success
    )
    async def papier(
        self,
        interaction: discord.Interaction,
        bouton: discord.ui.Button
    ):
        await self.jouer(interaction, "📄")

    @discord.ui.button(
        label="Ciseaux",
        emoji="✂️",
        style=discord.ButtonStyle.danger
    )
    async def ciseaux(
        self,
        interaction: discord.Interaction,
        bouton: discord.ui.Button
    ):
        await self.jouer(interaction, "✂️")


class Duel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="duel",
        description="Défie un membre dans un duel !"
    )
    @app_commands.describe(
        membre="Le membre que tu veux défier"
    )
    async def duel(
        self,
        interaction: discord.Interaction,
        membre: discord.Member
    ):

        if membre.bot:
            await interaction.response.send_message(
                "❌ Tu ne peux pas défier un bot.",
                ephemeral=True
            )
            return

        if membre.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ Tu ne peux pas te défier toi-même.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚔️ DUEL !",
            description=(
                f"{interaction.user.mention} **VS** {membre.mention}\n\n"
                "🥊 Le premier à **3 points** gagne !\n\n"
                "Choisissez votre action avec les boutons ci-dessous."
            )
        )

        view = DuelView(interaction.user, membre)

        await interaction.response.send_message(
            embed=embed,
            view=view
        )


async def setup(bot):
    await bot.add_cog(Duel(bot))