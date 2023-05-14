import os
import discord
from dotenv import load_dotenv
import pytube


class MyBot(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.voice_client = None
        self.queue = []

    async def on_ready(self):
        print('Logged in as', self.user.name)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('+play'):
            keywords = message.content[5:]
            await self.play_audio(message, keywords)

        if message.content.startswith('+url'):
            url = message.content[4:]
            await self.play_url(message, url)

        if message.content.startswith('+stop'):
            await self.stop_audio(message)

    async def play_url(self, message, url):
        if not self.voice_client:
            channel = message.author.voice.channel
            print('Connecting to', channel)
            self.voice_client = await channel.connect()

        if self.voice_client.is_playing():
            await message.channel.send("Sorry, there is a song being played and I can't handle that yet, stop the song and try again... :(")
            return

        f = self.url_to_stream(url)

        if f is None:
            await message.channel.send("Sorry there was an error loading the audio... :(")
            return

        try:
            await message.channel.send("Playing it uwu \n" + str(url))
            self.voice_client.play(discord.FFmpegPCMAudio(executable=os.getenv('FFMPEG_PATH'), source=f))
        except Exception as e:
            print(e)
            await message.channel.send("Sorry there was an error loading the audio... :(")

    async def play_audio(self, message, keywords):
        if not self.voice_client:
            channel = message.author.voice.channel
            print('Connecting to', channel)
            self.voice_client = await channel.connect()

        if self.voice_client.is_playing():
            await message.channel.send("Sorry, there is a song being played and I can't handle that yet, stop the song and try again... :(")
            return

        url = self.search_for(keywords)

        if url is None:
            await message.channel.send("Sorry, no results found... :( (Try using +url <url>)")
            return
        else:
            await message.channel.send("Result found! :D")

        await self.play_url(message, url)

    async def stop_audio(self, message):
        if self.voice_client:
            self.voice_client.stop()
            await message.channel.send("Stopped!")

    def url_to_stream(self, url):
        try:
            yt = pytube.YouTube(url)
        except Exception as e:
            print(e)
            return None
        stream = yt.streams.filter(only_audio=True).first()
        if stream == None:
            return None
        try:
            buff = open("aud", "wb")
        except Exception as e:
            print(e)
            return None
        stream.stream_to_buffer(buffer=buff)
        return "aud"

    def search_for(self, keywords):
        s = pytube.Search(keywords)
        if s == None or len(s.results) == 0:
            return None
        return s.results[0].watch_url

if __name__ == '__main__':
    load_dotenv()
    intents = discord.Intents.default()
    intents.message_content = True
    bot = MyBot(intents=intents)
    bot.run(os.getenv('DISCORD_TOKEN'))