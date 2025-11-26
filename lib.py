import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image
import torch

# Load .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# -------------- Model Loading (Option B - Vision Caption Model) --------------- #
MODEL_NAME = "nlpconnect/vit-gpt2-image-captioning"

print("Loading AI model... (First time takes 30–60 seconds)")
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)
processor = ViTImageProcessor.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print("Model loaded successfully!")

def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

    output_ids = model.generate(pixel_values, max_length=16, num_beams=4)
    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Extract 3 tags
    keywords = [w.lower() for w in caption.split() if w.isalpha()]
    tags = sorted(set(keywords), key=lambda x: len(x), reverse=True)[:3]

    return caption, tags

# -------------- Discord Bot Setup --------------- #
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is Ready! Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # If image is uploaded
    if message.attachments:
        for file in message.attachments:
            if any(file.filename.lower().endswith(ext) for ext in ["jpg", "jpeg", "png"]):
                await message.channel.send("🔍 Processing image, please wait...")

                img_path = f"./{file.filename}"
                await file.save(img_path)

                caption, tags = generate_caption(img_path)

                await message.channel.send(
                    f"📌 **Caption:** {caption}\n"
                    f"🏷 **Tags:** {', '.join(tags)}"
                )
                os.remove(img_path)
                return

    await bot.process_commands(message)

# If user types !ping (just to test bot is alive)
@bot.command()
async def ping(ctx):
    await ctx.send("Bot is running! Send an image to get caption 😊")

bot.run(TOKEN)
