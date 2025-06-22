import discord
from discord.ext import commands
from discord import app_commands, Interaction, Member
from datetime import datetime
import aiohttp 


class Utilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Muestra información de un usuario")
    @app_commands.describe(member="Miembro del que quieres ver información")
    async def userinfo(self, interaction: Interaction, member: Member = None):
        member = member or interaction.user
        user = await self.bot.fetch_user(member.id)

        embed = discord.Embed(
            title=f"📋 Información de {member.display_name}",
            color=member.color,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="👤 Nombre", value=member.name, inline=True)
        embed.add_field(name="📅 Cuenta creada", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=False)
        embed.add_field(name="📥 Entró al servidor", value=member.joined_at.strftime("%d/%m/%Y %H:%M"), inline=False)
        embed.add_field(name="📌 Roles", value=", ".join([r.mention for r in member.roles if r.name != "@everyone"]) or "Ninguno", inline=False)

        if user.banner:
            embed.set_image(url=user.banner.url)

        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="serverinfo", description="Muestra información detallada del servidor")
    async def serverinfo(self, interaction: Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"🌐 Información del servidor: {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Dueño", value=guild.owner.mention, inline=True)
        embed.add_field(name="📅 Creado el", value=guild.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name="👥 Miembros", value=guild.member_count, inline=True)
        embed.add_field(name="💬 Canales", value=len(guild.channels), inline=True)
        embed.add_field(name="🔐 Roles", value=len(guild.roles), inline=True)
        embed.set_footer(text="Información del servidor")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invitar", description="Genera un enlace para invitar a tu servidor")
    async def invitar(self, interaction: Interaction):
        # Busca un canal donde se puedan crear invitaciones
        canal = interaction.channel

        try:
            # Crea una invitación válida por 1 día y 1 uso
            invitacion = await canal.create_invite(max_age=86400, max_uses=1, unique=True)

            embed = discord.Embed(
                title="🔗 Invitación al servidor",
                description=(
                    f"Aquí tienes un enlace para unirte al servidor **{interaction.guild.name}**.\n\n"
                    f"📆 **Válido por:** 1 día\n"
                    f"🔁 **Usos permitidos:** 1\n"
                    f"🔗 **Enlace:** [Únete aquí]({invitacion.url})"
                ),
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text="Invitación generada automáticamente")
            embed.timestamp = interaction.created_at

            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permisos para crear invitaciones en este canal.", ephemeral=True)
            
    @app_commands.command(name="chiste", description="Te cuento un chiste aleatorio")
    async def chiste(self, interaction: Interaction):
        await interaction.response.defer()
        url = "https://v2.jokeapi.dev/joke/Any?lang=es&type=single"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                chiste = data.get("joke", "No encontré un chiste ahora mismo 😅")

        await interaction.followup.send(f"🤣 {chiste}")



    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        contenido = message.content.lower()

        if "hola soy nuevo" in contenido:
            await message.channel.send("👋 ¡Hola! Te damos la bienvenida. Te invitamos a leer las reglas para tener una excelente experiencia en el servidor. Si tienes dudas, no dudes en preguntar.")
        elif "gracias" in contenido:
            await message.add_reaction("❤️")
            await message.channel.send("¡De nada! Estamos aquí para ayudarte 😊")
        elif "adios" in contenido:
            await message.add_reaction("😥")
            await message.channel.send("¡Hasta luego! Esperamos verte pronto de vuelta 🫡")
        elif "hola" in contenido:
            await message.add_reaction("👋")
        elif "necesito ayuda" in contenido or "ayuda" in contenido:
            await message.channel.send("📩 Si necesitas ayuda, puedes contactar a un moderador del servidor o directamente al dueño 👑 ")

async def setup(bot):
    await bot.add_cog(Utilidades(bot))
