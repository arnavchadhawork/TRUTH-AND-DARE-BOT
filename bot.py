import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random

# =========================
# SETTINGS
# =========================

#TOKEN = "MTU1MzgwMzQyNDEzNzYxMzQ1Mw.GPg5RZ.WdzPT9jOlk6-T9MncgDNNVVOiu39mF1MZAaRDQ"
TOKEN = os.getenv("TOKEN_BOT")

# Optional:
# Agar sirf ek server par commands instantly chahiye,
# apne Discord Server ID ko yahan daal do.
# Example: GUILD_ID = 123456789012345678
GUILD_ID = None

DATA_FILE = "questions.json"


# =========================
# DATA FUNCTIONS
# =========================

def load_questions():
    if not os.path.exists(DATA_FILE):
        data = {
            "truth": [],
            "dare": []
        }

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if "truth" not in data:
            data["truth"] = []

        if "dare" not in data:
            data["dare"] = []

        return data

    except (json.JSONDecodeError, OSError):
        return {
            "truth": [],
            "dare": []
        }


def save_questions(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


questions = load_questions()


# =========================
# BOT SETUP
# =========================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# BOT READY
# =========================

@bot.event
async def on_ready():
    print("=" * 40)
    print(f"Bot Online: {bot.user}")
    print(f"Bot ID: {bot.user.id}")

    try:
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)

            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)

            print(f"Synced {len(synced)} commands to server.")
        else:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} global commands.")

    except Exception as e:
        print("Command sync error:", e)

    print("=" * 40)


# =========================
# TRUTH
# =========================

@bot.tree.command(
    name="truth",
    description="Get a random Truth question"
)
async def truth(interaction: discord.Interaction):

    if not questions["truth"]:
        await interaction.response.send_message(
            "❌ Abhi koi Truth question add nahi hai.\n"
            "Admin `/addtruth` se question add kar sakta hai.",
            ephemeral=True
        )
        return

    question = random.choice(questions["truth"])

    embed = discord.Embed(
        title="🟦 TRUTH",
        description=f"**{question}**",
        color=discord.Color.blue()
    )

    embed.set_footer(
        text=f"Asked to {interaction.user.display_name}"
    )

    await interaction.response.send_message(embed=embed)


# =========================
# DARE
# =========================

@bot.tree.command(
    name="dare",
    description="Get a random Dare"
)
async def dare(interaction: discord.Interaction):

    if not questions["dare"]:
        await interaction.response.send_message(
            "❌ Abhi koi Dare add nahi hai.\n"
            "Admin `/adddare` se dare add kar sakta hai.",
            ephemeral=True
        )
        return

    dare_question = random.choice(questions["dare"])

    embed = discord.Embed(
        title="🟥 DARE",
        description=f"**{dare_question}**",
        color=discord.Color.red()
    )

    embed.set_footer(
        text=f"Dare for {interaction.user.display_name}"
    )

    await interaction.response.send_message(embed=embed)


# =========================
# ADD TRUTH
# =========================

@bot.tree.command(
    name="addtruth",
    description="Add a new Truth question"
)
@app_commands.describe(
    question="Enter the Truth question"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def addtruth(
    interaction: discord.Interaction,
    question: str
):

    question = question.strip()

    if not question:
        await interaction.response.send_message(
            "❌ Question empty nahi ho sakta.",
            ephemeral=True
        )
        return

    questions["truth"].append(question)
    save_questions(questions)

    await interaction.response.send_message(
        f"✅ Truth question add ho gaya!\n\n"
        f"**Question:** {question}"
    )


# =========================
# ADD DARE
# =========================

@bot.tree.command(
    name="adddare",
    description="Add a new Dare"
)
@app_commands.describe(
    dare="Enter the Dare"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def adddare(
    interaction: discord.Interaction,
    dare: str
):

    dare = dare.strip()

    if not dare:
        await interaction.response.send_message(
            "❌ Dare empty nahi ho sakta.",
            ephemeral=True
        )
        return

    questions["dare"].append(dare)
    save_questions(questions)

    await interaction.response.send_message(
        f"✅ Dare add ho gaya!\n\n"
        f"**Dare:** {dare}"
    )


# =========================
# LIST TRUTHS
# =========================

@bot.tree.command(
    name="listtruth",
    description="Show all Truth questions"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def listtruth(interaction: discord.Interaction):

    if not questions["truth"]:
        await interaction.response.send_message(
            "❌ Koi Truth question saved nahi hai.",
            ephemeral=True
        )
        return

    text = ""

    for number, question in enumerate(questions["truth"], start=1):
        text += f"**{number}.** {question}\n"

    # Discord message limit handling
    if len(text) > 1900:
        text = text[:1900] + "\n..."

    embed = discord.Embed(
        title="🟦 Truth Questions",
        description=text,
        color=discord.Color.blue()
    )

    embed.set_footer(
        text=f"Total Truths: {len(questions['truth'])}"
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# =========================
# LIST DARES
# =========================

@bot.tree.command(
    name="listdare",
    description="Show all Dares"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def listdare(interaction: discord.Interaction):

    if not questions["dare"]:
        await interaction.response.send_message(
            "❌ Koi Dare saved nahi hai.",
            ephemeral=True
        )
        return

    text = ""

    for number, dare in enumerate(questions["dare"], start=1):
        text += f"**{number}.** {dare}\n"

    if len(text) > 1900:
        text = text[:1900] + "\n..."

    embed = discord.Embed(
        title="🟥 Dare List",
        description=text,
        color=discord.Color.red()
    )

    embed.set_footer(
        text=f"Total Dares: {len(questions['dare'])}"
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# =========================
# REMOVE TRUTH
# =========================

@bot.tree.command(
    name="removetruth",
    description="Remove a Truth question by number"
)
@app_commands.describe(
    number="Question number from /listtruth"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def removetruth(
    interaction: discord.Interaction,
    number: int
):

    if not questions["truth"]:
        await interaction.response.send_message(
            "❌ Truth list empty hai.",
            ephemeral=True
        )
        return

    if number < 1 or number > len(questions["truth"]):
        await interaction.response.send_message(
            f"❌ Invalid number.\n"
            f"Available numbers: 1-{len(questions['truth'])}",
            ephemeral=True
        )
        return

    removed = questions["truth"].pop(number - 1)
    save_questions(questions)

    await interaction.response.send_message(
        f"🗑️ Truth remove kar diya:\n\n"
        f"**{removed}**"
    )


# =========================
# REMOVE DARE
# =========================

@bot.tree.command(
    name="removedare",
    description="Remove a Dare by number"
)
@app_commands.describe(
    number="Dare number from /listdare"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def removedare(
    interaction: discord.Interaction,
    number: int
):

    if not questions["dare"]:
        await interaction.response.send_message(
            "❌ Dare list empty hai.",
            ephemeral=True
        )
        return

    if number < 1 or number > len(questions["dare"]):
        await interaction.response.send_message(
            f"❌ Invalid number.\n"
            f"Available numbers: 1-{len(questions['dare'])}",
            ephemeral=True
        )
        return

    removed = questions["dare"].pop(number - 1)
    save_questions(questions)

    await interaction.response.send_message(
        f"🗑️ Dare remove kar diya:\n\n"
        f"**{removed}**"
    )


# =========================
# TOTAL QUESTIONS
# =========================

@bot.tree.command(
    name="questioncount",
    description="Show total Truth and Dare questions"
)
async def questioncount(interaction: discord.Interaction):

    truth_count = len(questions["truth"])
    dare_count = len(questions["dare"])

    embed = discord.Embed(
        title="📊 Question Count",
        color=discord.Color.green()
    )

    embed.add_field(
        name="🟦 Truth",
        value=str(truth_count),
        inline=True
    )

    embed.add_field(
        name="🟥 Dare",
        value=str(dare_count),
        inline=True
    )

    embed.add_field(
        name="📚 Total",
        value=str(truth_count + dare_count),
        inline=True
    )

    await interaction.response.send_message(embed=embed)


# =========================
# CLEAR ALL QUESTIONS
# =========================

@bot.tree.command(
    name="clearquestions",
    description="Delete ALL Truth and Dare questions"
)
@app_commands.checks.has_permissions(administrator=True)
async def clearquestions(interaction: discord.Interaction):

    questions["truth"].clear()
    questions["dare"].clear()

    save_questions(questions)

    await interaction.response.send_message(
        "🗑️ **All Truth and Dare questions delete ho gaye.**"
    )


# =========================
# ERROR HANDLER
# =========================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(error, app_commands.MissingPermissions):
        message = (
            "❌ Tumhare paas is command ko use karne "
            "ki permission nahi hai."
        )

    else:
        print("ERROR:", error)

        message = (
            "❌ Command mein error aa gaya.\n"
            "Console check karo."
        )

    if interaction.response.is_done():
        await interaction.followup.send(
            message,
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True
        )


# =========================
# START BOT
# =========================

if TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
    print("❌ ERROR: Pehle bot.py mein apna Discord Bot Token paste karo.")
else:
    bot.run(TOKEN)
