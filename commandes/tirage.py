import random
import discord
from discord import app_commands
from discord.ext import commands


class Tirage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="tirage",
        description="Tire au sort un membre du serveur."
    )
    async def tirage(self, interaction: discord.Interaction):

        # Récupération des membres humains
        membres = [
            membre
            for membre in interaction.guild.members
            if not membre.bot
        ]

        # Aucun membre disponible
        if not membres:
            await interaction.response.send_message(
                "❌ Aucun membre disponible pour le tirage.",
                ephemeral=True
            )
            return

        # Tirage aléatoire
        gagnant = random.choice(membres)

        embed = discord.Embed(
            title="🎉 TIRAGE AU SORT",
            description=(
                "🎯 Le tirage au sort vient de se terminer !\n\n"
                f"🏆 **Gagnant :** {gagnant.mention}\n\n"
                "Félicitations ! 🎊"
            )
        )

        embed.set_footer(
            text=f"Tirage organisé sur {interaction.guild.name}"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Tirage(bot))