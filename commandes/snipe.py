import discord
from discord import app_commands
from discord.ext import commands
from collections import defaultdict, deque


MAX_MESSAGES = 100


class Snipe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Messages supprimés par salon
        self.deleted_messages = defaultdict(lambda: deque(maxlen=MAX_MESSAGES))

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        # On ignore les messages du bot
        if message.author.bot:
            return

        self.deleted_messages[message.channel.id].append({
            "author": message.author,
            "content": message.content,
            "created_at": message.created_at,
            "attachments": [
                attachment.url
                for attachment in message.attachments
            ]
        })

    @app_commands.command(
        name="snipe",
        description="Affiche les derniers messages supprimés."
    )
    @app_commands.describe(
        nombre="Nombre de messages à afficher (1 à 5)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def snipe(
        self,
        interaction: discord.Interaction,
        nombre: app_commands.Range[int, 1, 5] = 1
    ):

        messages = list(
            self.deleted_messages[interaction.channel.id]
        )

        if not messages:
            await interaction.response.send_message(
                "❌ Aucun message supprimé récent dans ce salon.",
                ephemeral=True
            )
            return

        messages = messages[-nombre:]
        messages.reverse()

        embeds = []

        for message in messages:

            contenu = message["content"]

            if not contenu:
                contenu = "*(Aucun texte — pièce jointe uniquement)*"

            if len(contenu) > 1000:
                contenu = contenu[:997] + "..."

            embed = discord.Embed(
                description=contenu,
                timestamp=message["created_at"]
            )

            embed.set_author(
                name=str(message["author"]),
                icon_url=message["author"].display_avatar.url
            )

            embed.set_footer(
                text="Message supprimé"
            )

            if message["attachments"]:
                embed.add_field(
                    name="📎 Pièce jointe",
                    value=message["attachments"][0],
                    inline=False
                )

            embeds.append(embed)

        await interaction.response.send_message(
            content=f"🕵️ **Snipe — {len(embeds)} message(s) supprimé(s)**",
            embeds=embeds,
            ephemeral=True
        )

    @snipe.error
    async def snipe_error(
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
            message = f"❌ Une erreur est survenue : `{error}`"

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
    await bot.add_cog(Snipe(bot))