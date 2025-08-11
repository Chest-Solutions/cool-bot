import logging

import discord
import psutil
from discord import ext, app_commands
from discord.ext import commands

import functions
import random


class Misc(ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="sayas", description="Say stuff as other users")
    @app_commands.describe(user="User mention or ID", message="Message to send")
    async def sayas(self, ctx: commands.Context, user: str, *, message: str):
        # Try to get the user by mention, ID, or name
        user_id = None
        if user.isdigit():
            user_id = int(user)
        else:
            user = user.replace("<", "").replace(">", "").replace("@", "").replace("&", "")
            if user.isdigit():
                user_id = int(user)
        
        member = None
        if user_id:
            member = ctx.guild.get_member(user_id)
        if not member:
            # Try by name
            member = discord.utils.find(lambda m: m.name == user or m.display_name == user, ctx.guild.members)
        if not member:
            msg = await ctx.send("Please provide a valid user (mention or ID).")
            await msg.delete(delay=3)
            return

        # Create or get a webhook
        webhooks = await ctx.channel.webhooks()
        webhook = None
        for wh in webhooks:
            if wh.user == ctx.me:
                webhook = wh
                break
        if not webhook:
            webhook = await ctx.channel.create_webhook(name=f"SayAsWebhook{random.randint(1, 9999)}")

        # Send the message as the user
        await webhook.send(
            content=message,
            username=member.display_name,
            avatar_url=member.display_avatar.url if hasattr(member, "display_avatar") else member.avatar_url,
            wait=True
        )
    @commands.hybrid_command()
    @app_commands.allowed_contexts(True, True, True)
    async def cmds(self, ctx: commands.Context):
        if ctx.author == self.user: return
        commands_list = []  # "\n".join([f"/{command.name}," for command in bot.tree.get_commands()])
        for command in self.bot.tree.get_commands():
            if command.name == "scramblerrestart" or command.name == "scramblerstop": continue
            commands_list.append(command.name)
        commands_list.append("help")
        str_commands_list = ",\n".join(commands_list)
        await ctx.send(f"Here are all the available commands:\n{str_commands_list}")

    @commands.hybrid_command()
    @app_commands.allowed_contexts(True, True, True)
    async def sudo(self, ctx: commands.Context, *, command: str):
        pass
        if not ctx.author.id in self.bot.allowedUsers and not await self.bot.is_owner(ctx.author):
            await functions.sendMessage(ctx.channel, self.bot.user, True, "Error: No permission", f"ScramberWebhook{random.randint(1, 4)}")
            return
        if command == "tasks":
            processes = []
            for process in psutil.process_iter():
                if process.pid >= 75: continue
                processes.append(f"PID: {process.pid}, Name: {process.name()}")
            str_processes = ",\n".join(processes)
            await ctx.send(f"Processes:\n```{str_processes}\n...Truncated```")
        else:
            await ctx.send("Invalid command")

    @commands.hybrid_command()
    async def forwardmessage(self, ctx: commands.Context, svr: int, cnl: int):
        try:
            guild = self.bot.get_guild(svr)
            if not guild:
                await ctx.send(f"Error: Could not find a guild with ID {svr}.", ephemeral=True)
                return

            target_channel = await guild.fetch_channel(cnl)
            if not target_channel:
                await ctx.send(f"Error: Could not find a channel with ID {cnl} in that guild.", ephemeral=True)
                return

        except discord.NotFound:
            await ctx.send("Error: Guild or channel not found.", ephemeral=True)
            return
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}", ephemeral=True)
            return

            # Store the channel objects themselves in the dictionary,
            # using channel IDs as the keys.
        self.bot.forwardingChannels[ctx.channel.id] = target_channel
        self.bot.forwardingChannels[target_channel.id] = ctx.channel

        await ctx.send(f"Messages will now be forwarded between <#{ctx.channel.id}> and <#{target_channel.id}>.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Misc(bot))