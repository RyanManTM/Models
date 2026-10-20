r"""
cat_cpus_unbox.py - adds the unboxing anchor A_CAP_PADS_0 to the committed server CPU FBXs without rebuilding them.

    blender -b --factory-startup -P Tools/Blender/cat_cpus_unbox.py -- [ids...]

A rebuild with build_cat_cpus.py gives the same anchor, but build_cpu-style heat-spreader prisms triangulate in a
different order on every run, so extras_compare.py could not show that only an anchor was added. This imports
Assets/Resources/Models/<id>.fbx (the importer settings undo dct_common.export's axis conversion: a plain round trip
compares SAME), adds the anchor with cat_cpus_server.cap_anchor and exports it again with dct_common.export.
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import cat_cpus_server as srv  # noqa: E402


def retrofit(cid):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(c.MODELS, cid + ".fbx"), use_custom_props=True,
                             axis_forward="-Z", axis_up="Y", bake_space_transform=True)
    root = bpy.data.objects[cid]
    if any(o.name == "A_CAP_PADS_0" for o in c.descendants(root)):
        print("UNBOX", cid, "already has A_CAP_PADS_0")
        return
    srv.cap_anchor(root, srv.SPECS[cid]["sock"])
    c.export(root, cid)
    print("UNBOX", cid, "+ A_CAP_PADS_0")


if __name__ == "__main__":
    for cid in c.args() or list(srv.SPECS):
        retrofit(cid)
