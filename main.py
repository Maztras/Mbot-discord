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

@tasks.loop(minutes=1)
async def actualizar_estado():
    for guild in bot.guilds:
        await guild.chunk()
        total = guild.member_count
        en_linea = sum(1 for m in guild.members if m.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd])
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"en línea: {en_linea}/{total} miembros 👀"
            )
        )
        break

@bot.command()
async def hola(ctx):
    await ctx.send("¡Hola! El bot está funcionando correctamente.")

@bot.command()
async def stats(ctx):
    for guild in bot.guilds:
        await guild.chunk()
        total = guild.member_count
        en_linea = sum(1 for member in guild.members if member.status == discord.Status.online)
        await ctx.send(f"👥 Miembros conectados: {en_linea}/{total}")
        break

bot.run(TOKEN)
