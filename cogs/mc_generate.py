import os

from discord.ext import commands
import aiohttp
import asyncio
import base64
import json
import time
from aiofiles import os as asyncos
import aiopathlib as pathlib
import aiofiles
import subprocess

import functions

YOUR_USER_ID = 1401958406662783188  # <-- Replace with your Discord user ID

class mc_generate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.root_dir = pathlib.AsyncPath(__file__).resolve().parent.parent
        self.assets_dir = self.root_dir / "assets"
        self.cache_dir = self.root_dir / "render_cache"
        self.blender_script = self.root_dir / "blender_render.py"
        self.blender_exec = "blender"

    @commands.hybrid_command(name="mcgenerate")
    async def mcgenerate(self, ctx, username: str, pose: str = "pose1", nocache: bool = False):
        veryStartTime = time.time()

        """Render a Minecraft skin using Blender."""
        await functions.safe_send(ctx, f"⏳ Rendering for **{username}**...")

        if nocache and ctx.author.id != 926199368518864966:
            await functions.safe_send(ctx, "❌ Only the bot owner can use the `nocache` option.")
            return

        # Step 1: Get UUID
        async with aiohttp.ClientSession() as session:
            uuid_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
            async with session.get(uuid_url) as uuid_resp:
                if uuid_resp.status != 200:
                    await functions.safe_send(ctx, "❌ Username not found.")
                    return
                uuid_data = await uuid_resp.json()
                uuid_str = uuid_data['id']

            # Step 2: Check Cache
            await self.cache_dir.mkdir(exist_ok=True)

            cached_filename = f"{uuid_str}_{pose}.png"
            cached_path = self.cache_dir / cached_filename

            for img in list(self.cache_dir.glob("*.png")):
                cached_file = self.cache_dir / img

                if not await functions.is_file_older_than_x_days(cached_file, 60): continue
                if cached_path == cached_file: continue
                await asyncos.remove(cached_file)

            if not nocache and await cached_path.exists():
                await functions.safe_send(
                    ctx,
                    f"✅ Found a cached render for **{username}** (took {time.time() - veryStartTime:.2f} seconds)!",
                    filepath=cached_path,
                    filename="render.png"
                )
                return

            # Step 3: Get model type (Alex/Steve) and skin URL
            model_is_alex = False
            profile_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid_str}"
            async with session.get(profile_url) as profile_resp:
                if profile_resp.status != 200:
                    await functions.safe_send(ctx, f"❌ An error occurred (Status Code: {profile_resp.status}). Please try again.")
                    return
                encoded = (await profile_resp.json())["properties"][0]["value"]
                skin_data = json.loads(base64.b64decode(encoded).decode())
                model = skin_data.get("textures", {}).get("SKIN", {}).get("metadata", {}).get("model")
                if model == "slim":
                    model_is_alex = True
                skin_url = skin_data["textures"]["SKIN"]["url"]

        # Step 4: Prepare blend file
        pose_name = f"{pose}_alex" if model_is_alex else pose
        blend_path = self.assets_dir / "blends" / f"{pose_name}.blend"
        if not await blend_path.exists():
            blend_path = self.assets_dir / "blends" / f"{pose}.blend"
            if not blend_path.exists():
                await functions.safe_send(ctx, f"❌ Pose `{pose}` not found.")
                return

        # Step 5: Download skin to temp file (RAM disk if possible)
        ramdisk_dir = "/dev/shm" if os.name == "posix" and await asyncos.path.exists("/dev/shm") else None
        temp_dir = ramdisk_dir or self.root_dir / "temp_skins"
        await asyncos.makedirs(temp_dir, exist_ok=True)
        skin_path = temp_dir / f"{uuid_str}.png"
        async with aiohttp.ClientSession() as session:
            async with session.get(skin_url) as skin_resp:
                async with aiofiles.open(skin_path, "wb") as f:
                    await f.write(await skin_resp.read())

        # Step 6: Run Blender in a thread
        blender_cmd = [
            self.blender_exec,
            "-noaudio",
            "--factory-startup",
            "-b", blend_path,
            "-E", "BLENDER_EEVEE_NEXT",
            #"--gpu-backend", "vulkan",
            "--python", self.blender_script,
            "--",
            skin_path,
            cached_path,
            "false" if pose == "pose3" else "true"
        ]


        def run_blender():
            try:
                start_time = time.time()
                process = subprocess.run(
                    blender_cmd, capture_output=True, text=True, check=True, encoding="utf-8"
                )

                return time.time() - start_time, process.stdout + process.stderr
            except subprocess.CalledProcessError as e:
                return -1, None, e.stdout + e.stderr
            except Exception as e:
                return -1, None, str(e)


        render_time, logs = await asyncio.to_thread(run_blender)

        print("\n--- Blender Process Output ---")
        print(logs)
        print("\n------------------------------")

        # Step 7: Clean up temp skin file
        try:
            await asyncos.remove(skin_path)
        except Exception:
            pass

        # Step 8: Send result
        await functions.safe_send(ctx, f"✅ Render complete for **{username}**!\nRender time: `{render_time:.3f}` seconds.", filepath=cached_path, filename="render.png")
        await functions.safe_send(ctx, f"Blender logs: ```{logs}```")

async def setup(bot):
    await bot.add_cog(mc_generate(bot))