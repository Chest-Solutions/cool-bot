import asyncio
import logging
import time

import discord
from aiofiles import os
from aiohttp import ClientPayloadError
from discord import TextChannel, User, Member, utils, File
from discord.ext import commands


async def sendMessage(channel: TextChannel, user: User or Member, wait: bool, message: str, attachments=[], embeds=[], name="ScramberWebhook"):
    webhook = utils.get(await channel.webhooks(), name=name) or await channel.create_webhook(name=name)

    await webhook.send(
        content=message,
        username=user.display_name,
        avatar_url=user.display_avatar.url,
        files=[await attachment.to_file() for attachment in attachments],
        embeds=embeds,
        wait=wait
    )

async def safe_send(ctx: commands.Context, message: str = None, file_path: str = None, filename: str = None):
    if not (message or file_path):
        return

    try:
        file_obj = File(file_path, filename=filename) if file_path else None
        await ctx.send(content=message, file=file_obj)
    except ClientPayloadError:
        logging.info("Client Payload Error, Trying again")
        await asyncio.sleep(5)
        file_obj = File(file_path, filename=filename) if file_path else None
        await ctx.send(content=message, file=file_obj)
    except FileNotFoundError:
        await ctx.send(f"❌ Error: File not found at {file_path}")

async def is_file_older_than_x_days(file, minutes=1):
    file_time = await os.path.getmtime(file)
    # Check against 24 hours
    return (time.time() - file_time) / 60 > 1*minutes
