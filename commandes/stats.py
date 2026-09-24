import discord
from discord.ext import commands
from collections import defaultdict
import time


class Stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.messages = defaultdict(int)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if message.guild:
            self.messages[message.guild.id] += 1

    @discord.app_commands.command(
        name="stats",
        description="Affiche les statistiques du serveur."
    )
    async def stats(self, interaction: discord.Interaction):

        serveur = interaction.guild

        if serveur is None:
            await interaction.response.send_message(
                "❌ Cette commande doit être utilisée dans un serveur.",
                ephemeral=True
            )
            return

        # Membres humains
        membres = [
            membre
            for membre in serveur.members
            if not membre.bot
        ]

        # Bots
        bots = [
            membre
            for membre in serveur.members
            if membre.bot
        ]

        # Membres actuellement en vocal
        vocal = [
            membre
            for membre in serveur.members
            if membre.voice is not None
            and membre.voice.channel is not None
            and not membre.bot
        ]

        # Membres en ligne
        en_ligne = [
            membre
            for membre in membres
            if membre.status != discord.Status.offline
        ]

        # Salons
        salons_textuels = [
            salon
            for salon in serveur.channels
            if isinstance(salon, discord.TextChannel)
        ]

        salons_vocaux = [
            salon
            for salon in serveur.channels
            if isinstance(salon, discord.VoiceChannel)
        ]

        categories = [
            salon
            for salon in serveur.channels
            if isinstance(salon, discord.CategoryChannel)
        ]

        total_global = len(serveur.members)

        # Création de l'embed
        embed = discord.Embed(
            title=f"📊 Statistiques — {serveur.name}",
            description=(
                "Voici les statistiques actuelles "
                "de ce serveur."
            ),
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="👥 Membres",
            value=f"**{len(membres)}**",
            inline=True
        )

        embed.add_field(
            name="🤖 Bots",
            value=f"**{len(bots)}**",
            inline=True
        )

        embed.add_field(
            name="🌍 Global",
            value=f"**{total_global}**",
            inline=True
        )

        embed.add_field(
            name="🟢 En ligne",
            value=f"**{len(en_ligne)}**",
            inline=True
        )

        embed.add_field(
            name="🎙️ En vocal",
            value=f"**{len(vocal)}**",
            inline=True
        )

        embed.add_field(
            name="💬 Messages",
            value=f"**{self.messages[serveur.id]}**",
            inline=True
        )

        embed.add_field(
            name="💬 Salons textuels",
            value=f"**{len(salons_textuels)}**",
            inline=True
        )

        embed.add_field(
            name="🔊 Salons vocaux",
            value=f"**{len(salons_vocaux)}**",
            inline=True
        )

        embed.add_field(
            name="📁 Catégories",
            value=f"**{len(categories)}**",
            inline=True
        )

        embed.add_field(
            name="🚀 Boosts",
            value=f"**{serveur.premium_subscription_count}**",
            inline=True
        )

        embed.add_field(
            name="📅 Créé le",
            value=discord.utils.format_dt(
                serveur.created_at,
                style="D"
            ),
            inline=True
        )

        embed.set_thumbnail(
            url=serveur.icon.url
            if serveur.icon
            else discord.Embed.Empty
        )

        embed.set_footer(
            text="TM'SB | PROTECT"
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Stats(bot))