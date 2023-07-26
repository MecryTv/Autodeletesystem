import discord
from discord import slash_command
from discord.ext import commands
import asyncio
import sqlite3


class Autodelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autodelete_channels = []

        self.create_db()

    def create_db(self):
        conn = sqlite3.connect("database/autodelete.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS autodelete_settings (channel_id INTEGER, time INTEGER)")
        conn.commit()
        conn.close()

    def save_settings(self):
        conn = sqlite3.connect("database/autodelete.db")
        c = conn.cursor()
        c.execute("DELETE FROM autodelete_settings")
        for channel_id, time in self.autodelete_channels:
            c.execute("INSERT INTO autodelete_settings VALUES (?, ?)", (channel_id, time))
        conn.commit()
        conn.close()

    def load_settings(self):
        conn = sqlite3.connect("database/autodelete.db")
        c = conn.cursor()
        c.execute("SELECT * FROM autodelete_settings")
        results = c.fetchall()
        self.autodelete_channels = results
        conn.close()

    def remove_channel_from_db(self, channel_id):
        conn = sqlite3.connect("database/autodelete.db")
        c = conn.cursor()
        c.execute("DELETE FROM autodelete_settings WHERE channel_id=?", (channel_id,))
        conn.commit()
        conn.close()

    def get_autodelete_channels(self):
        autodelete_channel_ids = [channel_id for channel_id, _ in self.autodelete_channels]
        autodelete_channels = [self.bot.get_channel(channel_id) for channel_id in autodelete_channel_ids]
        return autodelete_channels

    @slash_command(description="Füge einem Channel die Autodelete Funktion hinzu")
    async def autodelset(self, ctx, time: int, channel: discord.TextChannel):
        if channel.id in self.get_autodelete_channels():
            embed = discord.Embed(
                title="💣 | Autodelete Settings",
                description="Der ausgewählte Channel hat keine Autodelete Funktion.",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Mülleimer.png", filename="Muelleimer.png")
            embed.set_thumbnail(url="attachment://Muelleimer.png")
            embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)

            await ctx.respond(embed=embed, file=file)
            return

        self.autodelete_channels.append((channel.id, time))
        self.save_settings()

        embed = discord.Embed(
            title="💣 | Autodelete Settings",
            description=f"Die Autodelete Funktion wurde in dem Channel {channel.mention} mit einer Zeit von {time} Sekunden gesetzt.",
            color=discord.Color.red()
        )
        file = discord.File(f"img/Mülleimer.png", filename="Muelleimer.png")
        embed.set_thumbnail(url="attachment://Muelleimer.png")
        embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)

        await ctx.respond(embed=embed, file=file)

    @slash_command(description="Entferne einen Channel mit Autodelete Funktion")
    async def autodelremove(self, ctx, channel: discord.TextChannel):
        if channel.id not in [channel_id for channel_id, _ in self.autodelete_channels]:
            embed = discord.Embed(
                title="💣 | Autodelete Settings",
                description="Der ausgewählte Channel hat keine Autodelete Funktion.",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Mülleimer.png", filename="Muelleimer.png")
            embed.set_thumbnail(url="attachment://Muelleimer.png")
            embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)

            await ctx.respond(embed=embed, file=file)
            return

        removed_channels = []
        for i, (channel_id, time) in enumerate(self.autodelete_channels):
            if channel.id == channel_id:
                removed_channels.append((channel, time))
                self.autodelete_channels.pop(i)
                self.remove_channel_from_db(channel_id)
                break
        self.save_settings()

        if removed_channels:
            embed = discord.Embed(
                title="💣 | Autodelete Settings",
                description="Der Channel mit der Autodelete Funktion wurde entfernt.",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Mülleimer.png", filename="Muelleimer.png")
            embed.set_thumbnail(url="attachment://Muelleimer.png")
            embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)

            for channel, time in removed_channels:
                embed.add_field(name="Channel / Time", value=f"{channel.mention} / {time}", inline=True)
            await ctx.respond(embed=embed, file=file)
        else:
            embed = discord.Embed(
                title="💣 | Autodelete Settings",
                description="Der ausgewählte Channel hat keine Autodelete Funktion.",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Mülleimer.png", filename="Muelleimer.png")
            embed.set_thumbnail(url="attachment://Muelleimer.png")
            embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)

            await ctx.respond(embed=embed, file=file)

    @slash_command(description="Zeige die Channels mit Autodelete Funktion an")
    async def autodelcheck(self, ctx):
        autodelete_channels = self.get_autodelete_channels()
        if autodelete_channels:
            embed = discord.Embed(
                title="💣 | Autodelete Settings",
                description="Aktive Autodelete Funktionen",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Mülleimer.png", filename="Muelleimer.png")
            embed.set_thumbnail(url="attachment://Muelleimer.png")
            embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)

            for channel_id, time in self.autodelete_channels:
                channel = self.bot.get_channel(channel_id)
                if channel is not None:
                    embed.add_field(name="Channel / Time", value=f"{channel.mention} / {time}", inline=True)
                    file = discord.File(f"img/Mülleimer.png", filename="Muelleimer.png")
                    embed.set_thumbnail(url="attachment://Muelleimer.png")
                    embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)
            await ctx.respond(embed=embed, file=file)
        else:
            embed = discord.Embed(
                title="💣 | Autodelete Settings",
                description="Es sind keine Channels mit Autodelete Funktion gesetzt. Bitte füge mit </autodelset:1122892417687896095> einen Channel und eine Zeit hinzu.",
                color=discord.Color.red()
            )
            file = discord.File(f"img/Mülleimer.png", filename="Muelleimer.png")
            embed.set_thumbnail(url="attachment://Muelleimer.png")
            embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)

            await ctx.respond(embed=embed, file=file)

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    @commands.Cog.listener()
    async def on_message(self, message):
        for channel_id, time in self.autodelete_channels:
            if (
                message.channel.id == channel_id
                and not message.pinned
            ):
                await asyncio.sleep(time)
                await message.delete()


def setup(bot):
    bot.add_cog(Autodelete(bot))
