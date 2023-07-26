import asyncio
import discord
import ezcord
import os
import logging
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
intents.voice_states = True

colors = {
    logging.DEBUG: "red"
}

bot = ezcord.Bot(
    intents=intents,
    debug_guilds=os.getenv("SERVER_ID"),
    language="de"
)

embed = discord.Embed(
    color=discord.Color.yellow()
)
embed.set_footer(text="Coding Mecry")

ezcord.set_embed_templates(error_embed=embed)


def get_online_user_count():
    online_count = 0
    for guild in bot.guilds:
        online_count += sum(1 for member in guild.members if member.status == discord.Status.online)
    online_count += 1
    return online_count


@bot.event
async def status_task():
    online_count = get_online_user_count()
    await bot.change_presence(activity=discord.Game("Made by MecryTv"), status=discord.Status.online)
    await asyncio.sleep(30)
    await bot.change_presence(activity=discord.Game(f"Mit {online_count} Dc Usern"), status=discord.Status.online)
    await asyncio.sleep(30)
    await bot.change_presence(activity=discord.Game("Joint dem TestoBot.net Server"), status=discord.Status.online)
    await asyncio.sleep(30)


@bot.event
async def on_ready():
    bot.loop.create_task(status_task())


if __name__ == "__main__":
    bot.load_cogs(subdirectories=True)

load_dotenv()
bot.run(os.getenv("TOKEN"))
