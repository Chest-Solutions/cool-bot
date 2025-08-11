import bpy
import sys
import os

scene = bpy.context.scene
eevee = scene.eevee

# Parse arguments passed after "--"
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

# Ensure skin and output path are provided
if len(argv) < 2:
    print("❌ Usage: blender --python blender_render.py -- <skin_path> <output_path>")
    sys.exit(1)

eevee.taa_samples = 0
eevee.taa_render_samples = 5
eevee.volumetric_shadow_samples = 1
eevee.use_shadows = True

try:
    eevee.use_shadows = (argv[2].lower() == 'true')
except IndexError:
    pass

eevee.use_volumetric_shadows = True
eevee.use_shadow_jitter_viewport = True
eevee.use_taa_reprojection = True

eevee.shadow_resolution_scale = 1
eevee.shadow_ray_count = 1
eevee.shadow_step_count = 1

scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '16'

# Get the absolute script directory
script_dir = os.path.dirname(os.path.realpath(__file__))

# Get full paths
skin_path = os.path.abspath(os.path.join(script_dir, argv[0]))

# Set Output Path
bpy.context.scene.render.filepath = os.path.abspath(os.path.join(script_dir, argv[1]))

# Replace target image
target_name = "skin"  # or "Skinsaa" if you're sure of the name

for image in bpy.data.images:
    if target_name.lower() in image.name.lower():
        print(f"✅ Replacing: {image.name}")

        if image.packed_file:
            print("📦 Unpacking packed image...")
            try:
                image.unpack()
            except Exception as e:
                print(f"⚠️ Failed to unpack: {e}")

        image.filepath = skin_path
        image.filepath_raw = skin_path
        image.source = 'FILE'
        try:
            image.reload()
        except Exception as e:
            print(f"❌ Reload failed: {e}")
        break

# Render
print("🎬 Rendering...")
bpy.ops.render.render(write_still=True)
print(f"✅ Render saved")
