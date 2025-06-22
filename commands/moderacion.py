import discord
from discord.ext import commands
from discord import app_commands, Interaction, Member, Embed
from datetime import timedelta
import re

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def crear_embed(self, tipo: str, miembro: Member, moderador: Member, razon: str, duracion: str = "", color=discord.Color.orange()):
        titulos = {
            "ban": "🔚 Usuario Baneado",
            "kick": "👢 Usuario Expulsado",
            "suspender": "⏳ Usuario Suspendido"
        }

        duracion_texto = f"\n**🕒 Tiempo:** {duracion}" if duracion else ""

        embed = Embed(
            title=titulos.get(tipo, "🔔 Moderación"),
            description=(
                f"**👤 Usuario:** {miembro.mention}"
                f"{duracion_texto}\n"
                f"**📝 Motivo:** {razon}\n"
                f"**👮 Moderador:** {moderador.mention}"
            ),
            color=color
        )
        embed.set_thumbnail(url=miembro.avatar.url if miembro.avatar else "https://cdn-icons-png.flaticon.com/512/179/179386.png")
        embed.set_footer(text="Sistema de moderación")
        return embed

    def convertir_duracion(self, texto: str) -> timedelta:
        match = re.fullmatch(r"(\d+)([smhd])", texto.lower())
        if not match:
            raise ValueError("Formato inválido. Usa '10s', '5m', '2h' o '1d'.")

        cantidad = int(match.group(1))
        unidad = match.group(2)
        factores = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        segundos = cantidad * factores[unidad]
        return timedelta(seconds=segundos)

    @app_commands.command(name="suspender", description="Suspende temporalmente a un miembro (le impide escribir)")
    @app_commands.describe(member="Miembro a suspender", duration="Duración (ej. 10s, 5m, 2h, 1d)", reason="Motivo de la suspensión")
    async def suspender(self, interaction: Interaction, member: Member, duration: str, reason: str = "Sin motivo"):
        await interaction.response.defer()
        try:
            tiempo = self.convertir_duracion(duration)
            await member.timeout(tiempo, reason=reason)
            embed = self.crear_embed("suspender", member, interaction.user, reason, duration)
            await interaction.followup.send(embed=embed)
        except ValueError as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error al suspender: {str(e)}", ephemeral=True)

    @app_commands.command(name="ban", description="Banea a un miembro")
    @app_commands.describe(member="Miembro a banear", reason="Razón del baneo")
    async def ban(self, interaction: Interaction, member: Member, reason: str = "Sin razón"):
        await interaction.response.defer()
        await member.ban(reason=reason)
        embed = self.crear_embed("ban", member, interaction.user, reason)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="kick", description="Expulsa a un miembro")
    @app_commands.describe(member="Miembro a expulsar", reason="Razón del kick")
    async def kick(self, interaction: Interaction, member: Member, reason: str = "Sin razón"):
        await interaction.response.defer()
        await member.kick(reason=reason)
        embed = self.crear_embed("kick", member, interaction.user, reason)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))
