import discord
from discord.ext import commands


SALON_BIENVENUE = 1552135835359514739


class Bienvenue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, membre):

        salon = membre.guild.get_channel(SALON_BIENVENUE)

        if salon is None:
            print(
                f"[BIENVENUE] Salon {SALON_BIENVENUE} introuvable."
            )
            return

        await salon.send(
            f"👋 Bienvenue {membre.mention} !"
        )

        print(
            f"[BIENVENUE] {membre} a rejoint le serveur."
        )


async def setup(bot):
    await bot.add_cog(Bienvenue(bot))