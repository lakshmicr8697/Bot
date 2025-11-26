import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")  # Optional

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------- BOT READY ----------------

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            print("Slash commands synced (guild).")
        else:
            await bot.tree.sync()
            print("Slash commands synced (global).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# ------------- /ask COMMAND ----------------

@bot.tree.command(name="ask", description="Ask a question (RAG or normal text query).")
@app_commands.describe(query="Type your question")
async def ask(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    # TODO: Replace with RAG or LLM call
    response = f"🤖 You asked: **{query}**\n(I will connect to a model here later.)"

    await interaction.followup.send(response)

# ------------- /image COMMAND ----------------

@bot.tree.command(name="image", description="Upload an image and get a description.")
@app_commands.describe(file="Upload an image")
async def image(interaction: discord.Interaction, file: discord.Attachment):

    # Validate file type
    if not file.content_type.startswith("image/"):
        await interaction.response.send_message("❌ Please upload a valid image.")
        return

    await interaction.response.defer()

    # Download image
    img_bytes = await file.read()

    # TODO: Pass img_bytes to a vision model
    description = "🖼️ (Image description will go here.)"

    await interaction.followup.send(
        f"**Image processed!**\n{description}"
    )

# ------------- /help COMMAND ----------------

@bot.tree.command(name="help", description="Show instructions.")
async def help_cmd(interaction: discord.Interaction):
    help_text = """
### 🤖 **Bot Commands**

**/ask <query>**
→ Ask any question (RAG or direct LLM).

**/image**
→ Upload an image and get a description.

**/help**
→ Shows this help menu.

---
Bot is fully ready! 🔥
    """
    await interaction.response.send_message(help_text)

# ------------- RUN BOT ----------------
bot.run(DISCORD_TOKEN)
