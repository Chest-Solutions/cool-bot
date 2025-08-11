import discord
from discord.ext import commands

ALLOWED_USER_IDS = {926199368518864966, 1043959796778405950}  # Replace with your IDs

class Cooloff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.disabled_cogs = set()
        self.cooloff_active = False

    async def cog_check(self, ctx):
        # Only the bot owner or allowed users can use these commands
        return ctx.author.id in ALLOWED_USER_IDS or await self.bot.is_owner(ctx.author)

    @commands.hybrid_command(name="turnoff", description="Disable all cogs except Cooloff (owner only).")
    async def turnoff(self, ctx):
        if self.cooloff_active:
            await ctx.send("Cooloff is already active.", ephemeral=True)
            return

        self.disabled_cogs.clear()
        failed = []
        for cog_name in list(self.bot.cogs):
            if cog_name != "Cooloff":
                try:
                    await self.bot.remove_cog(cog_name)
                    self.disabled_cogs.add(cog_name)
                except Exception as e:
                    failed.append((cog_name, str(e)))

        self.cooloff_active = True
        await self.bot.change_presence(status=discord.Status.offline)

        msg = f"All cogs have been turned off and status set to offline. Use `c!turnon` to turn them back on."
        if failed:
            msg += "\n❌ Failed to disable:\n"
            for cog, err in failed:
                msg += f"- {cog}: {err}\n"
        await ctx.send(msg)

    @commands.hybrid_command(name="turnon", description="Re-enable all previously disabled cogs (owner only).")
    async def turnon(self, ctx):
        if not self.cooloff_active:
            await ctx.send("Cooloff is not active.", ephemeral=True)
            return

        reloaded = []
        failed = []
        for cog_name in self.disabled_cogs:
            ext_path = f"cogs.{cog_name.lower()}"
            try:
                if ext_path in self.bot.extensions:
                    await self.bot.reload_extension(ext_path)
                else:
                    await self.bot.load_extension(ext_path)
                reloaded.append(cog_name)
            except Exception as e:
                failed.append((cog_name, str(e)))

        self.disabled_cogs.clear()
        self.cooloff_active = False
        await self.bot.change_presence(status=discord.Status.online)

        msg = "All cogs have been turned back on and status set to online."
        if reloaded:
            msg += f"\n✅ Reloaded: {', '.join(reloaded)}"
        if failed:
            msg += "\n❌ Failed to reload:\n"
            for cog, err in failed:
                msg += f"- {cog}: {err}\n"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Cooloff(bot))