import discord
from discord.ext import commands
from pathlib import Path

class uploader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="uploadfile", description="Upload a file from the bot's server.")
    async def uploadfile(self, ctx, *, filepath: str):
        # Only allow certain folders for safety (optional)
        allowed_dirs = ["assets", "render_cache", "temp_skins"]
        file_path = Path(filepath).resolve()

        # Optional: Prevent access outside allowed directories
        if not any(str(file_path).startswith(str(Path(d).resolve())) for d in allowed_dirs):
            await ctx.send("❌ You can only upload files from allowed directories.")
            return

        if not file_path.exists() or not file_path.is_file():
            await ctx.send(f"❌ File not found: `{filepath}`")
            return

        try:
            await ctx.send(f"Uploading `{file_path.name}`:", file=discord.File(str(file_path)))
        except Exception as e:
            await ctx.send(f"❌ Failed to upload file: `{e}`")

async def setup(bot):
    await bot.add_cog(uploader(bot))