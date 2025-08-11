import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="c!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s):")
        for cmd in synced:
            print(f" - /{cmd.name} {cmd.options if cmd.options else ''}")
        print("\nText commands:")
        for cmd in bot.commands:
            print(f" - {bot.command_prefix}{cmd.name} {cmd.signature}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

async def load_extensions():
    cogs_dir = "cogs"
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            ext = f"{cogs_dir}.{filename[:-3]}"
            try:
                await bot.load_extension(ext)
                print(f"Loaded extension: {ext}")
            except Exception as e:
                print(f"Failed to load extension {ext}: {e}")

async def main():
    await load_extensions()

asyncio.run(main())
bot.run(TOKEN)