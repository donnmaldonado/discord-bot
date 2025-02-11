import discord
import random
from discord.ext import tasks, commands
from datetime import datetime
from utils.file_utils import load_last_message_times, load_questions
from utils.id_utils import generate_unique_id
from utils.sheets_utils import save_message_data, append_reaction, save_roles_data
from config import BOT_TOKEN, INACTIVITY_THRESHOLD, INACTIVITY_LOOP_TIME

# Load questions and channels
last_message_times = load_last_message_times("channels.json")
questions = load_questions("questions.json")

# Enable intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Task to check inactivity and send a random question
@tasks.loop(seconds=INACTIVITY_LOOP_TIME)
async def check_inactivity():
    print(f"Checking inactivity at {datetime.utcnow()}")

    for key in last_message_times:
        if last_message_times[key] is not None:
            inactivity_duration = datetime.utcnow() - last_message_times[key]
            
            if inactivity_duration.total_seconds() > INACTIVITY_THRESHOLD:
                print(f"Channel {key} has been inactive for {inactivity_duration}")

                channel = bot.get_channel(key)  # Use bot instance
                if channel and key in questions and questions[key]:  # Ensure key exists in questions
                    question = random.choice(questions[key])
                    await channel.send(question)
                    last_message_times[key] = datetime.utcnow()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    check_inactivity.start()


@bot.event
async def on_message(message):
    # update last message time
    last_message_times[message.channel.id] = datetime.utcnow()

    timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S %Z')
    reference = message.reference
    sticker = message.stickers
    reactions = message.reactions

    if message.author != bot.user:
        author = generate_unique_id(message.author)
    else:
        author = "bot"

    if reference is not None:                    
        reference = str(reference.message_id)
    else:
        reference = ""

    if sticker:    # checks if stickers list is empty
        sticker = sticker[0]
    else:
        sticker = ""

    if not reactions:
        reactions = ""
    else:
        reactions = ",".join(reactions)
            
    save_message_data([author, str(message.id), reference, str(message.channel), message.clean_content, str(sticker), reactions, timestamp])
    await bot.process_commands(message)  # Allow command processing


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome {member.mention} to {member.guild.name}! Introduce yourself!")
        # FIX ME: needs template on how to introduce self


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    message = reaction.message
    if isinstance(reaction.emoji, str): # checks if string, aka unicode emoji
        emoji_name = reaction.emoji
    else:
        emoji_name = reaction.emoji.name
    append_reaction(str(message.id), emoji_name)


@bot.event
async def on_member_update(before,after):
    roles = [role.name for role in after.roles if role.name not in ["@everyone","verified student"]]
    member = generate_unique_id(after.name)
    save_roles_data(member, roles)


# @bot.command()
# async def test_join(ctx):
#     """Simulate a new member joining for testing."""
#     await on_member_join(ctx.author)


# Run bot
bot.run(BOT_TOKEN)
