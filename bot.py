import discord
from collections import defaultdict
from discord.ext import tasks, commands
from datetime import datetime
from utils.file_utils import load_last_message_times, load_questions
from utils.id_utils import generate_unique_id
from utils.sheets_utils import save_message_data, append_reaction, save_roles_data, save_email, verify_transfer_student, already_verified
from config import BOT_TOKEN, SERVER_ID, VERIFIED_ROLE, TRANSFER_STUDENT_ROLE, INACTIVITY_THRESHOLD, INACTIVITY_LOOP_TIME

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


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return  # Ignore bot messages

#     if message.guild is None:
#         await handle_dm_verification(message)
#     else:
#         await handle_guild_message(message)
#         await bot.process_commands(message) 

@bot.event
async def on_message(message):
    if message.guild is None:
        if message.author == bot.user:
            return  # Ignore bot DMs
        await handle_dm_verification(message)
    else:
        await handle_guild_message(message)  # Process all guild messages, including bot's
        if message.author != bot.user:  # Only process commands for non-bot messages
            await bot.process_commands(message)


async def handle_dm_verification(message):
    """Handles verification of a user via DM."""
    guild = bot.get_guild(int(SERVER_ID))
    member = guild.get_member(message.author.id)
    transfer_student_role = discord.utils.get(guild.roles, name=TRANSFER_STUDENT_ROLE)

    if not already_verified(generate_unique_id(message.author)):
        if verify_transfer_student(message.content):
            save_email(generate_unique_id(message.author), message.content)
            if transfer_student_role and transfer_student_role not in member.roles:
                await member.add_roles(transfer_student_role)
            await message.channel.send("Thank you! Your email has been recorded.")
        else:
            await message.channel.send("We could not find that email in our records. Try again if there was a typo.")
    else:
        await message.channel.send("Your email has already been recorded. Thank you")


async def handle_guild_message(message):
    """Handles messages sent in guild channels."""
    if message.channel.id in last_message_times.keys():
        last_message_times[message.channel.id] = datetime.utcnow()

    message_data = extract_message_data(message)
    save_message_data(message_data)


def extract_message_data(message):
    """Extracts relevant data from a message."""
    author_id = generate_unique_id(message.author) if message.author != bot.user else "bot"
    reference = str(message.reference.message_id) if message.reference else ""
    sticker = str(message.stickers[0]) if message.stickers else ""
    reactions = ",".join(str(r) for r in message.reactions) if message.reactions else ""

    return [
        author_id,
        str(message.id),
        reference,
        str(message.channel),
        message.clean_content,
        sticker,
        reactions,
        message.created_at.strftime('%Y-%m-%d %H:%M:%S %Z'),
    ]

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome {member.mention} to {member.guild.name}! Introduce yourself!")


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
        if role.name == VERIFIED_ROLE: 
            try:
                await after.send("Welcome! Please reply with your university email so we can contact you for compensation. (You must be a transfer student)")
            except discord.Forbidden:
                print(f"Could not send a DM to {after.name}. They might have DMs disabled")

    roles = [role.name for role in after.roles if role.name not in ["@everyone","verified"]]
    member = generate_unique_id(after.name)
    save_roles_data(member, roles)


class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent buttons

    async def handle_role(self, interaction: discord.Interaction, role_name: str):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            await interaction.response.send_message(f"❌ Role '{role_name}' not found!", ephemeral=True)
            return

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed {role_name} role.", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Added {role_name} role.", ephemeral=True)

    @discord.ui.button(label="freshman", style=discord.ButtonStyle.primary, custom_id="freshman_role")
    async def freshman(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "freshman")

    @discord.ui.button(label="sophomore", style=discord.ButtonStyle.primary, custom_id="sophomore_role")
    async def sophomore(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "sophomore")

    @discord.ui.button(label="junior", style=discord.ButtonStyle.primary, custom_id="junior_role")
    async def junior(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "junior")

    @discord.ui.button(label="senior", style=discord.ButtonStyle.primary, custom_id="senior_role")
    async def senior(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "senior")

# Command to send role selection message
@bot.command()
async def roles(ctx):
    embed = discord.Embed(title="Select Your Role", description="Click a button below to get your class role!", color=discord.Color.blue())
    await ctx.send(embed=embed, view=RoleSelectView())
# Run bot
bot.run(BOT_TOKEN)
