import discord
from discord import app_commands
from discord.ext import commands
import wavelink
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class Musica(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
        ))

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await wavelink.Pool.connect(
                client=self.bot,
                nodes=[
                    wavelink.Node(uri="http://127.0.0.1:2344", password="youshallnotpass")
                ]
            )
            print("✅ Nodo de Wavelink conectado")
        except Exception as e:
            print(f"⚠️ Error al conectar el nodo: {e}")

    async def get_player(self, interaction: discord.Interaction) -> wavelink.Player | None:
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("⛔ Debes estar en un canal de voz para usar este comando.", ephemeral=True)
            return None

        channel = interaction.user.voice.channel
        player = wavelink.Pool.get_node().get_player(interaction.guild)

        if not player:
            player = await channel.connect(cls=wavelink.Player)
        elif not player.is_connected:
            await player.connect(channel.id)
        return player

    @app_commands.command(name="play", description="Reproduce una canción desde YouTube o Spotify")
    @app_commands.describe(query="El nombre o enlace de la canción que quieres reproducir")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        player = await self.get_player(interaction)
        if not player:
            return

        if "open.spotify.com/track" in query:
            try:
                results = self.spotify.track(query)
                query = f"{results['name']} {results['artists'][0]['name']}"
            except Exception as e:
                await interaction.followup.send("❌ Error al procesar el enlace de Spotify.")
                print(f"Spotify error: {e}")
                return

        try:
            tracks = await wavelink.Playable.search(f"ytsearch:{query}")
        except Exception as e:
            await interaction.followup.send("❌ Ocurrió un error al buscar la canción.")
            print(f"Error al buscar: {e}")
            return

        if not tracks:
            await interaction.followup.send("❌ No se encontraron resultados.")
            return

        await player.play(tracks[0])
        await interaction.followup.send(f"▶ Reproduciendo: **{tracks[0].title}**")

    @app_commands.command(name="pause", description="Pausa la canción actual")
    async def pause(self, interaction: discord.Interaction):
        player = wavelink.Pool.get_node().get_player(interaction.guild)
        if player and player.is_playing():
            await player.pause()
            await interaction.response.send_message("⏸ Música en pausa.")

    @app_commands.command(name="resume", description="Reanuda la canción pausada")
    async def resume(self, interaction: discord.Interaction):
        player = wavelink.Pool.get_node().get_player(interaction.guild)
        if player and player.is_paused():
            await player.resume()
            await interaction.response.send_message("▶ Música reanudada.")

    @app_commands.command(name="stop", description="Detiene la música")
    async def stop(self, interaction: discord.Interaction):
        player = wavelink.Pool.get_node().get_player(interaction.guild)
        if player:
            await player.stop()
            await interaction.response.send_message("⏹ Música detenida.")

    @app_commands.command(name="skip", description="Salta la canción actual")
    async def skip(self, interaction: discord.Interaction):
        player = wavelink.Pool.get_node().get_player(interaction.guild)
        if player:
            await player.stop()
            await interaction.response.send_message("⏭ Cancion saltada.")

    @app_commands.command(name="disconnect", description="Desconecta al bot del canal de voz")
    async def disconnect(self, interaction: discord.Interaction):
        player = wavelink.Pool.get_node().get_player(interaction.guild)
        if player:
            await player.disconnect()
            await interaction.response.send_message("❌ Desconectado del canal de voz.")

    @app_commands.command(name="modo_24_7", description="Activa el modo 24/7")
    async def modo_247(self, interaction: discord.Interaction):
        player = await self.get_player(interaction)
        if not player:
            return
        await player.set_auto_play(True)
        await interaction.response.send_message("⏰ Modo 24/7 activado.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Musica(bot))
