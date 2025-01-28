import discord, random
from discord.ext import tasks
from datetime import datetime
from utils.file_utils import load_last_message_times, load_questions
from utils.id_utils import generate_unique_id
from utils.sheets_utils import save_data

from config import BOT_TOKEN, INACTIVITY_THRESHOLD, INACTIVITY_LOOP_TIME

last_message_times = load_last_message_times("channels.json")
questions = load_questions("questions.json")


# checks inactivity of channels, sends random question from pool if inactive
@tasks.loop(seconds=INACTIVITY_LOOP_TIME)
async def check_inactivity(self):
    print(f"checking inactivity {datetime.utcnow()}")
    for key in last_message_times:
        if last_message_times[key] != None:
            inactivity_duration = datetime.utcnow() - last_message_times[key]
            if inactivity_duration.total_seconds() > INACTIVITY_THRESHOLD:
                print(f"{key} has been inactive for {inactivity_duration}")
                channel = self.get_channel(key)
                question = random.choice(questions[key])
                await channel.send(question)
                last_message_times[key] = datetime.utcnow()


class Client(discord.Client):
    # called when bot has finished logging in and setting up
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        check_inactivity.start(self)
    

    # Records all messages along with a unique ID representing user
    async def on_message(self, message):
        # ignore messages from self(bot)
        if message.author == self.user:
            return
        # create unique id for given user
        unique_id = generate_unique_id(message.author)
        # update time of last message in specific channel
        last_message_times[message.channel.id] = datetime.utcnow()
        # saves message to google sheets file
        save_data([unique_id, str(message.channel), message.content])


# intents allow bot to subscribe to specific bucket of events
intents = discord.Intents.default() 
# enables app to recieve actual content of newly created messages
intents.message_content = True      


client = Client(intents=intents)
client.run(BOT_TOKEN)