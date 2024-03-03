import os

import discord
from dotenv import load_dotenv
from YTBot import YTBot


def main():
    """
    Main function to run the bot.

    Load the environment variables and run the bot.
    """
    load_dotenv()
    intents = discord.Intents.default()
    intents.message_content = True
    bot = YTBot(
        intents=intents,
        hugchat_credentials=(
            os.getenv("EMAIL_HUGGINGFACE"),
            os.getenv("PASS_HUGGINGFACE"),
        ),
    )
    try:
        bot.run(os.getenv("DISCORD_TOKEN"))
    except TypeError:
        print("Discord token is invalid! (Check .env file)")

if __name__ == "__main__":
    main()
