import discord
from discord.ext import commands

ALLOWED_USER_IDS = {926199368518864966, 1043959796778405950}  # Replace with your IDs

class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="reloadall")
    async def reload_all_cogs(self, ctx):
        if ctx.author.id not in ALLOWED_USER_IDS:
            await ctx.send("You do not have permission to use this command.")
            return

        await ctx.send("Restarting.")

        reloaded = []
        failed = []
        for ext in list(self.bot.extensions):
            try:
                await self.bot.reload_extension(ext)
                reloaded.append(ext.split('.')[-1])  # Show only the cog name, not the full path
            except Exception as e:
                failed.append((ext.split('.')[-1], str(e)))

        if reloaded:
            msg = f"Reloaded {len(reloaded)} cogs:\n✅ {', '.join(reloaded)}"
        else:
            msg = "No cogs reloaded."

        if failed:
            msg += "\n❌ Failed to reload:\n"
            for ext, err in failed:
                msg += f"- {ext}: {err}\n"

        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Reload(bot))