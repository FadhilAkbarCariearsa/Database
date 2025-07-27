import discord
import logging
import sys
import os
from Bot import handle_message, init_files
from Github_push import git_push

# 🚀 Auto-push ke GitHub saat startup
git_push()

# 🔇 Minimal logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# 🎯 Intents minimum
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot aktif sebagai: {client.user}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="?help"))

@client.event
async def on_message(message):
    if not message.author.bot:
        try:
            await handle_message(message)
        except Exception as e:
            print(f"⚠️ Error: {e}")

@client.event
async def on_error(event, *args, **kwargs):
    print(f"⚠️ Error di event {event}: {sys.exc_info()}")

if __name__ == "__main__":
    init_files()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN tidak ditemukan di secrets.")
        sys.exit(1)
    client.run(token)