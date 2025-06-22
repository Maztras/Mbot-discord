from discord.ext import commands
from discord import app_commands, Interaction, Status

class Generales(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hola", description="Saluda al bot")
    async def hola(self, interaction: Interaction):
        await interaction.response.send_message("👋 ¡Hola! El bot está funcionando correctamente.")

    @app_commands.command(name="stats", description="Muestra cuántos miembros están en línea")
    async def stats(self, interaction: Interaction):
        guild = interaction.guild
        await guild.chunk()
        total = guild.member_count
        en_linea = sum(1 for member in guild.members if member.status == Status.online)
        await interaction.response.send_message(f"📊 Miembros conectados: {en_linea}/{total}")

async def setup(bot):
    await bot.add_cog(Generales(bot))
