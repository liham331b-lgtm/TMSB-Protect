import discord
from discord import app_commands
from discord.ext import commands


class UnTimeoutAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="untimeoutall",
        description="Retire le timeout de tous les membres."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def untimeoutall(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        membres_timeout = []

        # Vérifie les membres du serveur en utilisant les données Discord
        for membre in interaction.guild.members:
            try:
                fetched = await interaction.guild.fetch_member(membre.id)

                # Dans les versions récentes de discord.py,
                # le timeout peut être récupéré via le champ raw.
                timeout_until = getattr(
                    fetched,
                    "communication_disabled_until",
                    None
                )

                if timeout_until is not None:
                    membres_timeout.append(fetched)

            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                continue

        if not membres_timeout:
            await interaction.followup.send(
                "ℹ️ Aucun membre actuellement timeout trouvé.",
                ephemeral=True
            )
            return

        reussis = 0
        echecs = 0

        for membre in membres_timeout:
            try:
                await interaction.guild.edit_member(
                    membre,
                    communication_disabled_until=None,
                    reason=f"/untimeoutall par {interaction.user}"
                )
                reussis += 1

            except (discord.Forbidden, discord.HTTPException):
                echecs += 1

        await interaction.followup.send(
            "🔓 **UNTIMEOUT ALL TERMINÉ**\n\n"
            f"👥 Membres détimeout : **{reussis}**\n"
            f"❌ Échecs : **{echecs}**",
            ephemeral=True
        )

    @untimeoutall.error
    async def untimeoutall_error(self, interaction, error):

        if isinstance(error, app_commands.errors.MissingPermissions):
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
    await bot.add_cog(UnTimeoutAll(bot))