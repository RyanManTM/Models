"""Exports a tiny probe model to check how Blender coordinates and custom properties arrive in Unity."""
import bpy
import sys

out = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)

root = bpy.data.objects.new("probe_root", None)
bpy.context.scene.collection.objects.link(root)

bpy.ops.mesh.primitive_cube_add(size=0.1, location=(1.0, 2.0, 3.0))
cube = bpy.context.active_object
cube.name = "probe_cube#plastic_black"
cube.parent = root

empty = bpy.data.objects.new("A_TEST_0", None)
empty.location = (1.0, 2.0, 3.0)
empty.rotation_euler = (0.0, 0.0, 0.0)
empty["size"] = "0.01,0.02,0.03"
empty["meta"] = "hello"
bpy.context.scene.collection.objects.link(empty)
empty.parent = root

# An empty rotated so its local +Y points along Blender +X, to see how orientations convert.
rot = bpy.data.objects.new("A_ROT_0", None)
rot.location = (0.0, 0.0, 0.0)
rot.rotation_euler = (0.0, 0.0, -1.5707963)
bpy.context.scene.collection.objects.link(rot)
rot.parent = root

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.fbx(
    filepath=out, use_selection=True, object_types={"EMPTY", "MESH"},
    apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
    bake_space_transform=True, use_custom_props=True, mesh_smooth_type="FACE", add_leaf_bones=False,
    use_mesh_modifiers=True)
print("exported", out)
