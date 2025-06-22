import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
APP_ID = int(os.getenv("APPLICATION_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=APP_ID
        )

    async def setup_hook(self):
        await self.load_extension("commands.generales")
        await self.load_extension("commands.moderacion")
        await self.load_extension("commands.utilidades")
        await self.load_extension("commands.musica")
        await self.tree.sync()
        print("✅ Comandos slash sincronizados")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ El bot está conectado como {bot.user}")
    actualizar_estado.start()

ID_SERVIDOR_PRINCIPAL = 1087474975830704189  # Reemplaza con el ID de tu servidor

@tasks.loop(minutes=1)
async def actualizar_estado():
    guild = bot.get_guild(ID_SERVIDOR_PRINCIPAL)
    if guild:
        await guild.chunk()  # Esto asegura que el caché se llene
        total = guild.member_count
        en_linea = sum(
            1 for m in guild.members
            if m.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd]
        )
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f" en línea a {en_linea}/{total} 👀"
            )
        )


@bot.command()
async def hola(ctx):
    await ctx.send("¡Hola! El bot está funcionando correctamente.")

@bot.command()
async def stats(ctx):
    guild = ctx.guild
    members = [m async for m in guild.fetch_members(limit=None)]
    total = len(members)
    en_linea = sum(1 for m in members if m.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd])
    await ctx.send(f"👥 {guild.name}: {en_linea}/{total} miembros conectados.")


bot.run(TOKEN)
