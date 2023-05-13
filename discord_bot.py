# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import asyncio
import time
import discord

# IMPORTS EXTENSIONS FOR COMMANDS
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from url_to_mp3 import url_to_stream, search_for


# IMPORT THE OS MODULE.
import os

# IMPORT LOAD_DOTENV FUNCTION FROM DOTENV MODULE.
from dotenv import load_dotenv

# IMPORT LOGGING

import logging


# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv()

# GRAB THE API TOKEN FROM THE .ENV FILE.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


bot = commands.Bot(command_prefix='+', intents=intents)

bot.remove_command('help')

# UNDER THIS LINE OF CODE ARE THE COMMANDS FOR THE BOT. YOU CAN ADD/CHANGE THOSE SAFELY WITHOUT DESTORYING THE CODE

@bot.command()
async def connect(ctx):
    channel = ctx.author.voice.channel
    print('Connecting to', channel)
    await channel.connect()

@bot.command()
async def disconnect(ctx):
    await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, *, keywords):
    if not ctx.voice_client:
        channel = ctx.author.voice.channel
        print('Connecting to', channel)
        await channel.connect()

    if ctx.voice_client.is_playing():
        await ctx.send("Sorry, there is a song being played and i can't handle that yet, stop the song and try again... :(")
        return

    url = search_for(keywords)

    if url ==  None:
        await ctx.send("Sorry, no results found... :( (Try using +url <url>)")
        return
    else:
        await ctx.send("Result found! :D")

    f = url_to_stream(url)
    
    if f == None:
        await ctx.send("Sorry there was an error loading the audio... :(")
        return

    try:
        await ctx.send("Playing it uwu \n" + str(url))
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable=os.getenv('FFMPEG_PATH'), source=f))
    except Exception as e:
        print(e)
        await ctx.send("Sorry there was an error loading the audio... :(")
    
@bot.command()
async def url(ctx, *, url):
    if not ctx.voice_client:
        channel = ctx.author.voice.channel
        print('Connecting to', channel)
        await channel.connect()

    if ctx.voice_client.is_playing():
        await ctx.send("Sorry, there is a song being played and i can't handle that yet, stop the song and try again... :(")
        return
    
    f = url_to_stream(url)

    if f == None:
        await ctx.send("Sorry there was an error loading the audio... :(")
        return
    
    try:
        await ctx.send("Playing it uwu \n" + str(url))
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable=os.getenv('FFMPEG_PATH'), source=f))
    except Exception as e:
        print(e)
        await ctx.send("Sorry there was an error loading the audio... :(")


@bot.command()
async def pause(ctx):
    ctx.voice_client.pause()

@bot.command()
async def resume(ctx):
    ctx.voice_client.resume()

@bot.command()
async def stop(ctx):
    ctx.voice_client.stop()

@bot.event
async def on_voice_state_update(member, before, after):
    
    if not member.id == bot.user.id:
        return

    elif before.channel is None:
        voice = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time = time + 1
            if voice.is_playing() and not voice.is_paused():
                time = 0
            if time == 60:
                await voice.disconnect()
            if not voice.is_connected():
                break

@bot.command()
async def help(ctx):
    await ctx.send("```Commands:\n\n+connect: Connects the bot to the voice channel you are currently in.\n\n+disconnect: Disconnects the bot from the voice channel.\n\n+play <keywords>: Plays the first result of the search on YouTube.\n\n+url <url>: Plays the audio of the video from the url.\n\n+pause: Pauses the audio.\n\n+resume: Resumes the audio.\n\n+stop: Stops the audio.\n\n+help: Shows this message.```")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("¿?wtf is that command?¿?, try +help")


# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. DON'T REMOVE THIS LINE OF CODE JUST CHANGE THE "DISCORD_TOKEN" PART TO YOUR DISCORD BOT TOKEN
bot.run(DISCORD_TOKEN)

