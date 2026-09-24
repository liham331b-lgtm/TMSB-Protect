import discord
from discord import app_commands
from discord.ext import commands


class Clear(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="clear",
        description="Supprime un nombre de messages."
    )
    @app_commands.describe(
        nombre="Nombre de messages à supprimer"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        nombre: app_commands.Range[int, 1, 100]
    ):

        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ Cette commande doit être utilisée dans un salon textuel.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            messages = await interaction.channel.purge(
                limit=nombre
            )

            await interaction.followup.send(
                f"🧹 **{len(messages)} messages supprimés.**",
                ephemeral=True
            )

            print(
                f"[CLEAR] {interaction.user} a supprimé "
                f"{len(messages)} messages dans "
                f"#{interaction.channel.name}"
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Je n'ai pas la permission de supprimer les messages.",
                ephemeral=True
            )

        except discord.HTTPException as erreur:
            await interaction.followup.send(
                f"❌ Erreur Discord : `{erreur}`",
                ephemeral=True
            )

    @clear.error
    async def clear_error(
        self,
        interaction: discord.Interaction,
        erreur
    ):

        if isinstance(
            erreur,
            app_commands.errors.MissingPermissions
        ):
            message = (
                "🚫 **Accès refusé.**\n"
                "Cette commande est réservée aux "
                "**administrateurs** du serveur."
            )

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
    await bot.add_cog(Clear(bot))