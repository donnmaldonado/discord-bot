import discord
from collections import defaultdict
from discord.ext import tasks, commands
from datetime import datetime
from utils.file_utils import load_last_message_times, load_questions
from utils.id_utils import generate_unique_id
from utils.sheets_utils import save_message_data, append_reaction, save_roles_data, save_email, verify_transfer_student
from config import BOT_TOKEN, SERVER_ID, VERIFIED_ROLE, INACTIVITY_THRESHOLD, INACTIVITY_LOOP_TIME

# Load questions and channels
last_message_times = load_last_message_times("channels.json")
questions = load_questions("questions.json")
# track the last asked question index for each channel
questions_indices = defaultdict(int)
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
                    index = questions_indices[key]
                    question = questions[key][index]
                    await channel.send(question)
                    last_message_times[key] = datetime.utcnow() # update last message time
                    # update index of question, wrap around if needed
                    questions_indices[key] = (index + 1) % len(questions[key])


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    if not check_inactivity.is_running():
        check_inactivity.start()


@bot.event
async def on_message(message):
    if message.guild is None and message.author != bot.user:
        guild = bot.get_guild(int(SERVER_ID))
        member = guild.get_member(message.author.id)
        verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE)

        if verify_transfer_student(message.content):
            save_email(generate_unique_id(message.author), message.content)
            if verified_role not in member.roles:
                await member.add_roles(verified_role)
                await message.channel.send("Thank you! Your email has been recorded.")
            else:
                await message.channel.send("Thank you! Your email has been recorded.")
        else:
            await message.channel.send("We could not find that email in our records, try again if there was a typo.")
            await member.remove_roles(verified_role)

    elif message.guild is not None:
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
async def on_member_update(before, after):
    # ask verified students for email via dm
    new_roles = set(after.roles) - set(before.roles) # detect added roles
    for role in new_roles:
        if role.name.lower() == VERIFIED_ROLE: 
            try:
                await after.send("Welcome! Please reply with your university email so we can contact you for compensation. (You must be a transfer student)")
            except discord.Forbidden:
                print(f"Could not send a DM to {after.name}. They might have DMs disabled")

    roles = [role.name for role in after.roles if role.name not in ["@everyone","verified student"]]
    member = generate_unique_id(after.name)
    save_roles_data(member, roles)


# @bot.command()
# async def test_join(ctx):
#     """Simulate a new member joining for testing."""
#     await on_member_join(ctx.author)

# Run bot
bot.run(BOT_TOKEN)
