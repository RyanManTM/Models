r"""
cat_server_fit.py - the fit check of catalogue 18's rack gear (datacenter_fit.py's method, with this family's layout):
imports the exported rack_42u and installs the devices exactly as the game would (a device's origin on A_RACKU_n; the
cable management arm at the same A_RACKU_n as the 1U server whose rails it clips on), then checks
  * every A_SCREW_RACK_n / A_SCREW_THUMB_n lands on a rack hole (datacenter_fit.check_holes, within 1 mm);
  * no two devices overlap in height (the arm shares its server's U and is checked separately);
  * no vertex of the arm is inside its server's chassis (A_HIT_0, plus the 16 mm the PSU handles stand out at the
    rear), and its outer connector sits inside the server's outer slide channel;
then renders Logs/ModelPreviews/cat_server_fit_<n>.png.

Run (after build_cat_server.py and build_datacenter.py):
    blender -b --factory-startup -P Tools/Blender/cat_server_fit.py -- [--nopreview]
"""
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import datacenter_fit as F  # noqa: E402

# (model, anchor in the rack); U numbers are A_RACKU_<U-1>
LAYOUT = [("srv_strata_sr224_2u", "A_RACKU_0"), ("srv_strata_blank_1u", "A_RACKU_2"), ("srv_strata_sg840_4u", "A_RACKU_3"),
          ("srv_strata_blank_2u", "A_RACKU_7"), ("server_1u", "A_RACKU_9"), ("srv_strata_cma", "A_RACKU_9"),
          ("srv_strata_kvm_1u", "A_RACKU_10"), ("srv_strata_shelf_1u", "A_RACKU_11"), ("srv_linkwave_ls4804x", "A_RACKU_13"),
          ("srv_linkwave_ls1600x", "A_RACKU_14"), ("patch_panel_24", "A_RACKU_15"), ("srv_strata_blank_1u", "A_RACKU_16")]
SHARED_U = ("srv_strata_cma",)


def anchor_box(objs, name):
    """(centre, half size) of an anchor's hitbox in Unity space (axis-aligned anchors only)."""
    a = next(o for o in objs if o.name.split(".")[0] == name)
    p = F.unity(a.matrix_world.translation)
    s = [float(t) / 2 for t in a["size"].split(",")]
    return p, Vector(s)


def check_cma(placed, origin):
    bad = 0
    srv = next(objs for mid, objs in placed if mid == "server_1u")
    cma = next(objs for mid, objs in placed if mid == "srv_strata_cma")
    p, s = anchor_box(srv, "A_HIT_0")
    lo = p - s - Vector((0, 0, 0.016))
    hi = p + s
    inside = 0
    for o in cma:
        if o.type != "MESH":
            continue
        for v in o.data.vertices:
            u = F.unity(o.matrix_world @ v.co)
            if all(lo[i] + 1e-4 < u[i] < hi[i] - 1e-4 for i in range(3)):
                inside += 1
    if inside:
        bad += 1
        print(f"FIT cma: {inside} vertices inside the server_1u chassis")
    # the outer connector must sit in the +x outer rail's channel (x 0.2190..0.2236 between the rail's flanges)
    mo = next(o for o in cma if o.name.split(".")[0] == "A_MOUNT_OUTER_0")
    rr = next(o for o in srv if o.name.split(".")[0] == "A_RAIL_R_0")
    pm, pr = F.unity(mo.matrix_world.translation), F.unity(rr.matrix_world.translation)
    rs = [float(t) for t in rr["size"].split(",")]
    z = pm.z - origin.z           # in the device frame
    ok = 0.2186 < pm.x - origin.x < 0.2245 and abs(pm.y - pr.y) < rs[1] / 2 - 0.012 and -0.7385 < z < -0.70
    if not ok:
        bad += 1
    print(f"FIT cma: outer connector at x {pm.x - origin.x:.4f}, y {pm.y:.4f}, z {z:.4f} (device frame z), rail centre y {pr.y:.4f}: {'OK' if ok else 'OFF THE RAIL'}; "
          f"{inside} vertices in the chassis")
    return bad


def main(argv):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rack = F.import_fbx("rack_42u")
    anchors = {o.name.split(".")[0]: o for o in rack if o.type == "EMPTY" and o.name.startswith("A_")}
    placed = []
    for mid, an in LAYOUT:
        objs = F.import_fbx(mid)
        F.place(objs, anchors[an].matrix_world)
        placed.append((mid, objs))
        lo, hi = F.bbox(objs)
        print(f"FIT rack_42u {mid}@{an}: x {lo.x:.4f}..{hi.x:.4f} y {lo.y:.4f}..{hi.y:.4f} z {lo.z:.4f}..{hi.z:.4f}")
    bad = F.check_holes(rack, placed)
    spans = []
    for mid, objs in placed:
        if mid in SHARED_U:
            continue
        lo, hi = F.bbox([o for o in objs if "@A_RAIL" not in o.name])
        spans.append((lo.y, hi.y, mid))
    spans.sort()
    for (a0, a1, ma), (b0, b1, mb) in zip(spans, spans[1:]):
        if b0 < a1 - 1e-4:
            bad += 1
            print(f"FIT rack_42u: {ma} and {mb} overlap in height by {(a1 - b0) * 1000:.2f} mm")
    bad += check_cma(placed, F.unity(anchors[dict(LAYOUT)['srv_strata_cma']].matrix_world.translation))
    n_screws = sum(1 for _, objs in placed for o in objs if o.type == "EMPTY" and o.name.startswith(("A_SCREW_RACK_", "A_SCREW_THUMB_")))
    print(f"FIT rack_42u: {'OK' if bad == 0 else str(bad) + ' problems'} ({len(placed)} devices, {n_screws} rack screws checked)")
    if "--nopreview" not in argv:
        F.render(rack, placed, "cat_server_fit", [(28, 8, (0, 0.55, 0.3), 2.2), (-30, 4, (0.05, 0.42, 0.40), 1.1)],
                 hide=("@A_DOOR_FRONT_0", "@A_PANEL_SIDE_1"))
        bpy.ops.wm.read_factory_settings(use_empty=True)
        rack = F.import_fbx("rack_42u")
        anchors = {o.name.split(".")[0]: o for o in rack if o.type == "EMPTY" and o.name.startswith("A_")}
        placed2 = []
        for mid, an in LAYOUT:
            objs = F.import_fbx(mid)
            F.place(objs, anchors[an].matrix_world)
            placed2.append((mid, objs))
        F.render(rack, placed2, "cat_server_fit_rear", [(160, 10, (0, 0.55, -0.3), 2.2), (150, 15, (0.05, 0.55, -0.35), 1.0)],
                 hide=("@A_DOOR_REAR_0", "@A_DOOR_REAR_1", "@A_PANEL_SIDE_0"))
    print("FIT TOTAL:", "OK" if bad == 0 else f"{bad} problems")


if __name__ == "__main__":
    main(c.args())
