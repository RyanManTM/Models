r"""
datacenter_fit.py - a fit check of the data-centre gear: imports the exported racks and installs the devices at their
anchors exactly as the game would (a device's origin on A_RACKU_n, the zero-U PDUs on A_PDU_n), checks that nothing
overlaps the rack's rails and that every ear hole meets a rack hole, then renders
Logs/ModelPreviews/datacentre_fit_<n>.png.

Run (after build_datacenter.py):  blender -b --factory-startup -P Tools/Blender/datacenter_fit.py -- [--nopreview]
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402

# (model, anchor in the rack); U numbers are A_RACKU_<U-1>
LAYOUT_42 = [("ups_2u", "A_RACKU_0"), ("ups_2u", "A_RACKU_2"), ("server_2u", "A_RACKU_8"), ("server_2u", "A_RACKU_10"),
             ("server_1u", "A_RACKU_14"), ("server_1u", "A_RACKU_15"), ("server_1u", "A_RACKU_16"), ("pdu_1u", "A_RACKU_30"),
             ("switch_24", "A_RACKU_38"), ("patch_panel_24", "A_RACKU_39"), ("pdu_0u", "A_PDU_0"), ("pdu_0u", "A_PDU_1")]
LAYOUT_12 = [("ups_2u", "A_RACKU_0"), ("server_1u", "A_RACKU_4"), ("switch_24", "A_RACKU_9"), ("patch_panel_24", "A_RACKU_10")]


def import_fbx(mid):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(c.MODELS, mid + ".fbx"), use_custom_props=True)
    return [o for o in bpy.data.objects if o not in before]


def pbr_all(objs):
    for o in objs:
        if o.type == "MESH" and "#" in o.name:
            tag = P._tag_of(o.name)
            o.data.materials.clear()
            o.data.materials.append(P.pbr_material(tag))


def place(objs, target_matrix):
    roots = [o for o in objs if o.parent is None]
    root = next(o for o in roots if o.type == "EMPTY" and not o.name.startswith("A_")) if any(
        o.type == "EMPTY" and not o.name.startswith("A_") for o in roots) else roots[0]
    M = target_matrix @ root.matrix_world.inverted()
    for o in roots:
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()   # children's world matrices follow only after an update


def unity(v):
    return Vector((-v.x, v.z, -v.y))


def check_holes(rack_objs, placed):
    """Every A_SCREW_RACK / A_SCREW_THUMB of a placed device must sit on a rack hole (same x, y within 1 mm)."""
    # the rack's hole centres from its rails: EIA-310 at the A_RACKU anchors
    racku = {o.name.split(".")[0]: o for o in rack_objs if o.name.startswith("A_RACKU_")}
    ys = []
    for nm, a in racku.items():
        p = unity(a.matrix_world.translation)
        for h in (0.00635, 0.022225, 0.0381):
            ys.append(p.y + h)
    x_hole = 0.23255
    bad = 0
    for mid, objs in placed:
        for o in objs:
            if o.type == "EMPTY" and (o.name.startswith("A_SCREW_RACK_") or o.name.startswith("A_SCREW_THUMB_")):
                p = unity(o.matrix_world.translation)
                dy = min(abs(p.y - y) for y in ys)
                dx = abs(abs(p.x) - x_hole)
                ok = dy < 0.001 and dx < 0.001
                bad += 0 if ok else 1
                if not ok:
                    print(f"FIT {mid} {o.name}: off the rack holes by dx={dx * 1000:.2f} mm dy={dy * 1000:.2f} mm")
    return bad


def bbox(objs):
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != "MESH":
            continue
        for v in o.bound_box:
            u = unity(o.matrix_world @ Vector(v))
            lo = Vector((min(lo.x, u.x), min(lo.y, u.y), min(lo.z, u.z)))
            hi = Vector((max(hi.x, u.x), max(hi.y, u.y), max(hi.z, u.z)))
    return lo, hi


def scene_for(rack_id, layout):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rack = import_fbx(rack_id)
    anchors = {o.name.split(".")[0]: o for o in rack if o.type == "EMPTY" and o.name.startswith("A_")}
    placed = []
    for mid, an in layout:
        objs = import_fbx(mid)
        place(objs, anchors[an].matrix_world)
        placed.append((mid, objs))
        lo, hi = bbox(objs)
        print(f"FIT {rack_id} {mid}@{an}: x {lo.x:.4f}..{hi.x:.4f} y {lo.y:.4f}..{hi.y:.4f} z {lo.z:.4f}..{hi.z:.4f}")
    bad = check_holes(rack, placed)
    # devices must not overlap each other in y (same rack face)
    spans = []
    for mid, objs in placed:
        if mid == "pdu_0u":
            continue
        lo, hi = bbox([o for o in objs if "@A_RAIL" not in o.name])
        spans.append((lo.y, hi.y, mid))
    spans.sort()
    for (a0, a1, ma), (b0, b1, mb) in zip(spans, spans[1:]):
        if b0 < a1 - 1e-4:
            bad += 1
            print(f"FIT {rack_id}: {ma} and {mb} overlap in height by {(a1 - b0) * 1000:.2f} mm")
    print(f"FIT {rack_id}: {'OK' if bad == 0 else str(bad) + ' problems'} ({len(placed)} devices)")
    return rack, placed, bad


def render(rack, placed, prefix, views, hide=()):
    sc = bpy.context.scene
    allobjs = rack + [o for _, objs in placed for o in objs]
    pbr_all(allobjs)
    for o in allobjs:
        if any(h in o.name for h in hide):
            o.hide_render = True
    P._gpu_cycles(sc, 48)
    P._setup_world(sc)
    sc.render.resolution_x, sc.render.resolution_y = 1000, 1200
    for k, d in enumerate(((0.4, -0.8, -0.6), (-0.6, -0.4, 0.5))):
        ld = bpy.data.lights.new(f"fill{k}", "SUN")
        ld.energy = 2.5 if k == 0 else 1.2
        ob = c.link(bpy.data.objects.new(f"fill{k}", ld))
        ob.rotation_euler = c.conv(d).to_track_quat("-Z", "Y").to_euler()
    camd = bpy.data.cameras.new("fit_cam")
    camd.lens = 50
    cam = c.link(bpy.data.objects.new("fit_cam", camd))
    sc.camera = cam
    lo, hi = bbox(rack)
    out = []
    for i, (yaw, pitch, target, dist) in enumerate(views):
        tgt = c.conv(target)
        y, p = math.radians(yaw), math.radians(pitch)
        u = Vector((math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)))
        cam.location = tgt + c.conv(u) * dist
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
        path = os.path.join(c.PREVIEWS, f"{prefix}_{i}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
    return out


def main(argv):
    total = 0
    rack, placed, bad = scene_for("rack_42u", LAYOUT_42)
    total += bad
    if "--nopreview" not in argv:
        render(rack, placed, "datacentre_fit", [(28, 10, (0, 1.0, 0.2), 4.2), (-35, 5, (0.1, 0.55, 0.35), 1.4)],
               hide=("@A_DOOR_FRONT_0", "@A_PANEL_SIDE_1"))
    rack, placed, bad = scene_for("rack_42u", LAYOUT_42)
    if "--nopreview" not in argv:
        render(rack, placed, "datacentre_fit_rear", [(150, 12, (0, 1.0, -0.2), 4.2)], hide=("@A_DOOR_REAR_0", "@A_DOOR_REAR_1", "@A_PANEL_SIDE_0"))
    rack, placed, bad = scene_for("rack_12u_open", LAYOUT_12)
    total += bad
    if "--nopreview" not in argv:
        render(rack, placed, "datacentre_fit_12u", [(30, 18, (0, 0.38, 0.0), 2.4)])
    print("FIT TOTAL:", "OK" if total == 0 else f"{total} problems")


if __name__ == "__main__":
    main(c.args())
