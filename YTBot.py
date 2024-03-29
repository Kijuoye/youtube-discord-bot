import discord
import pytube
import asyncio
from hugchat import hugchat
from hugchat.login import Login


class YTBot(discord.Client):
    """
    A bot that can play audio from youtube and chat with hugchat.

    Args:
        intents (discord.Intents): The intents for the bot.
        hugchat_credentials (tuple, optional): The credentials for the hugchat bot. Defaults to None.

    Attributes:
        voice_client (discord.VoiceClient): The voice client of the bot.
        queue (list): The queue of audio to be played.
        loop_audio (bool): Whether the audio should be looped.
        chatbot (hugchat.ChatBot): The chatbot for the bot.
    """

    def __init__(self, intents, hugchat_credentials=None):
        """
        Initializes the bot.

        Args:
            intents (discord.Intents): The intents for the bot.
            hugchat_credentials (tuple, optional): The credentials for the hugchat bot. Defaults to None.
        """
        super().__init__(intents=intents)
        self.voice_client = None
        self.queue = []
        self.loop_audio = False
        if hugchat_credentials:
            self.chatbot = self.create_chatbot(hugchat_credentials)
        else:
            self.chatbot = None
            print("Chatbot not created!")

    async def on_ready(self):
        """
        Called when the bot has successfully connected to the Discord server.
        """
        print("Logged in as", self.user.name)

    async def on_message(self, message):
        """
        Decides what to do when a message is received.

        Args:
            message (discord.Message): The message received.
        """
        if message.author == self.user:
            return

        if message.content.startswith("+play"):
            keywords = message.content[5:]
            await self.play_audio(message, keywords)
        elif message.content.startswith("+url"):
            url = message.content[4:]
            if (
                not str(url)
                .replace(" ", "")
                .startswith(("https://www.youtube.com/", "https://youtu.be/"))
            ):
                await message.channel.send(
                    "Invalid url! (Try using +play <keywords>)"
                )
            else:
                await self.play_url(message, url)
        elif message.content.startswith("+stop"):
            await self.stop_audio(message)
        elif message.content.startswith("+pause"):
            if self.voice_client:
                self.voice_client.pause()
                await message.channel.send("Paused!")
        elif message.content.startswith("+resume"):
            if self.voice_client:
                self.voice_client.resume()
                await message.channel.send("Resumed!")
        elif message.content.startswith("+queue"):
            if len(self.queue) == 0:
                await message.channel.send("Queue is empty!")
            else:
                await message.channel.send(
                    "Queue: "
                    + str(self.queue)
                    .replace(",", "\n")
                    .replace("[", "")
                    .replace("]", "")
                )
        elif message.content.startswith("+loop"):
            if self.loop_audio:
                self.loop_audio = False
                await message.channel.send("Looping disabled!")
            else:
                self.loop_audio = True
                await message.channel.send("Looping enabled!")
        elif message.content.startswith("+skip"):
            if self.voice_client:
                self.voice_client.stop()
                self.loop_audio = False
                self.play_next()
                await message.channel.send("Skipped!")
        elif message.content.startswith("+ramranch"):
            await message.channel.send(
                "18 naked cowboys in the showers at Ram Ranch!\n"
                "Big hard throbbing cocks wanting to be sucked!\n"
            )
            await self.play_url(
                message,
                "https://www.youtube.com/watch?v=39lPHHvkzYg&pp=ygUJcmFtIHJhbmNo",
            )
        elif message.content.startswith("+chat"):
            message.content = message.content[5:]
            await self.chat(message)
        elif message.content.startswith("+newchat"):
            await self.new_chat(message)
        # Silly command just in case...
        elif message.content.startswith("+deletechats_123321"):
            await self.delete_chats(message)
        elif message.content.startswith("+help"):
            await message.channel.send(
                "Commands:\n"
                "+play <keywords>: Plays the first result of a youtube search\n"
                "+url <url>: Plays the audio of the video from the url\n"
                "+stop: Stops the audio\n"
                "+pause: Pauses the audio\n"
                "+resume: Resumes the audio\n"
                "+queue: Shows the queue\n"
                "+skip: Skips the current song\n"
                "+help: Shows this message\n"
                "+loop: Loops the current song\n"
                "+ramranch: Plays Ram Ranch\n"
                "+chat: Starts a conversation with the chatbot\n"
                "+newchat: Starts a new conversation with the chatbot\n"
            )
        elif message.content.startswith("+"):
            await message.channel.send(
                "Was that meant to be a command? Because if that's the case, maaaan I have no idea what you are waiting for me to do :/"
            )

    async def chat(self, message):
        """
        Send a message to the chatbot and receive a response.

        Args:
            message (discord.Message): The message received.
        """
        if self.chatbot:
            try:
                response = self.chatbot.chat(message.content)
                response.wait_until_done()
            except Exception as e:
                print("Failed to chat:", e)
                response = "Sorry, I'm not feeling well... :("
            response_length = len(response.text)
            if response_length > 2000:
                messages = [
                    response.text[i : i + 2000]
                    for i in range(0, response_length, 2000)
                ]
                for m in messages:
                    await message.channel.send(m)
            else:
                await message.channel.send(response.text)
        else:
            await message.channel.send("I'm not in the mood to chat... :(")

    async def new_chat(self, message):
        """
        Starts a new chat conversation.

        Args:
            message: The message object representing the chat message.
        """
        if self.chatbot:
            chat_id = self.chatbot.new_conversation()
            self.chatbot.change_conversation(chat_id)
        else:
            await message.channel.send("I'm not in the mood to chat... :(")

    async def delete_chats(self, message):
        """
        Deletes all chat conversations.

        Args:
            message: The message object representing the chat message.
        """
        # WARNING: This will delete all conversations
        if self.chatbot:
            self.chatbot.delete_all_conversations()
        else:
            await message.channel.send("I'm not in the mood to chat... :(")

    async def on_voice_state_update(self, member, before, after):
        """
        Check if the bot should disconnect from the voice channel.

        Args:
            member (discord.Member): The member that updated their voice state.
            before (discord.VoiceState): The voice state before the update.
            after (discord.VoiceState): The voice state after the update.
        """
        if not member.id == self.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                time += 1
                await asyncio.sleep(1)
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time > 60:
                    await voice.disconnect()
                    self.voice_client = None
                if not voice.is_connected():
                    self.voice_client = None
                    break

    async def play_url(self, message, url):
        """
        Connect to the voice channel and play the audio from the url.

        Args:
            message (discord.Message): The message received.
            url (str): The url of the audio to be played.
        """
        if not self.voice_client:
            if not message.author.voice:
                await message.channel.send("You are not in a voice channel!")
                return
            channel = message.author.voice.channel
            print("Connecting to", channel)
            self.voice_client = await channel.connect()

        await message.channel.send("Added to queue! --> \n" + url)

        self.add_to_queue(url)

    async def play_audio(self, message, keywords):
        """
        Play the audio from the first result of a youtube search.

        Args:
            message (discord.Message): The message received.
            keywords (str): The keywords to search for.
        """
        url = self.search_for(keywords)

        if url is None:
            await message.channel.send(
                "Sorry, no results found... :( (Try using +url <url>)"
            )
            return
        else:
            await message.channel.send("Result found! :D")

        await self.play_url(message, url)

    async def stop_audio(self, message):
        """
        Stop the audio.

        Args:
            message (discord.Message): The message received.
        """
        if self.voice_client:
            self.voice_client.stop()
            await message.channel.send("Stopped!")

    def add_to_queue(self, url):
        """
        Add the url to the queue.

        Args:
            url (str): The url to be added to the queue.
        """
        if len(self.queue) == 0 and not self.voice_client.is_playing():
            self.queue.append(url)
            self.play_next()
        else:
            self.queue.append(url)

    def play_next(self):
        """
        Play the next audio in the queue.
        """
        if len(self.queue) == 0:
            return
        url = self.queue[0]
        self.queue = self.queue[1:]
        self.play_queue(url)

    def play_queue(self, url):
        """
        Play the audio from the url.

        Args:
            url (str): The url of the audio to be played.
        """
        if self.voice_client:
            audio = self.url_to_stream(url)
            if audio is None:
                return
            if self.loop_audio:
                self.voice_client.play(
                    discord.FFmpegPCMAudio(audio, executable="ffmpeg"),
                    after=lambda e: self.play_queue(url),
                )
            else:
                self.voice_client.play(
                    discord.FFmpegPCMAudio(audio, executable="ffmpeg"),
                    after=lambda e: self.play_next(),
                )

    def url_to_stream(self, url):
        """
        Convert the url to a stream.

        Args:
            url (str): The url of the audio to be converted.

        Returns:
            str: The name of the audio file.
        """
        try:
            yt = pytube.YouTube(url)

            stream = yt.streams.filter(only_audio=True).first()
            buff = open("aud", "wb")
            stream.stream_to_buffer(buffer=buff)

        except Exception as e:
            print(e)
            return None

        buff.close()
        return "aud"

    def search_for(self, keywords):
        """
        Search for the first result of a youtube search.

        Args:
            keywords (str): The keywords to search for.

        Returns:
            str: The url of the first result.
        """
        s = pytube.Search(keywords)
        if s is None or len(s.results) == 0:
            return None
        return str(s.results[0].watch_url)

    def create_chatbot(self, credentials):
        """
        Create a chatbot.

        Args:
            credentials (tuple): The credentials for the chatbot.

        Returns:
            hugchat.ChatBot: The chatbot.
        """
        try:
            email, passwd = credentials
            sign = Login(email, passwd)
            cookies = sign.login()
            cookie_path_dir = "./cookies_snapshot"
            sign.saveCookiesToDir(cookie_path_dir)
            chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        except Exception as e:
            print("Failed to create chatbot:", e)
            chatbot = None
        return chatbot
