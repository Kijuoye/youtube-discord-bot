import os

import discord
from dotenv import load_dotenv
from YTBot import YTBot


if __name__ == "__main__":
    load_dotenv()
    intents = discord.Intents.default()
    intents.message_content = True
    bot = YTBot(intents=intents)
    try:
        bot.run(os.getenv("DISCORD_TOKEN"))
    except TypeError:
        print("Discord token is invalid! (Check .env file)")
