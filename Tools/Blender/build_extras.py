r"""
build_extras.py - agent C's models for the real unboxing (Logs/UNBOXING.md sections 2.3 and 2.5):

  papers   doc_leaflet, doc_booklet, doc_card, doc_sticker_sheet, doc_slip           (extras_docs.py)
  caps     cap_pcie16, cap_dp, cap_hdmi, guard_ram_ddr5, guard_ram_ddr4, cap_paste,
           sticker_psu_voltage                                                       (extras_caps.py)

Run:  "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_extras.py -- [--nopreview] [ids...]

Outputs: Assets/Resources/Models/<id>.fbx; textures tex_doc_badges and tex_sticker_psu in
Assets/Resources/Models/Textures; previews Logs/ModelPreviews/<id>_<n>.png; the report
Logs/ModelPreviews/extras_report.txt (meshes, triangles, anchors, the cap placement table, the fit checks against
the real part FBX files and the film data the game can derive from the part meshes).

The caps are checked against the part models (imported from Assets/Resources/Models, never exported here): a
triangle-overlap test and the smallest gap, on every placement listed in extras_caps.PLACEMENTS.
"""
import math
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import dct_common as c  # noqa: E402
import parts_b as pb  # noqa: E402
import extras_common as xc  # noqa: E402
import extras_docs as xd  # noqa: E402
import extras_caps as xk  # noqa: E402
from mathutils import Vector as V  # noqa: E402

DOCS = ["doc_leaflet", "doc_booklet", "doc_card", "doc_sticker_sheet", "doc_slip"]
CAPS = ["cap_pcie16", "cap_dp", "cap_hdmi", "guard_ram_ddr5", "guard_ram_ddr4", "cap_paste", "sticker_psu_voltage"]
PAGES = os.path.join(tempfile.gettempdir(), "dct_extras_pages")
PREVIEW = [True]


# ====================================================================== papers

def doc_builders():
    return {
        "doc_leaflet": (lambda: xd.build_trifold("doc_leaflet", 0.100, 0.210, False, 0.0026,
                                                 "doc=guide,fold=tri,panels=3"), "leaflet"),
        "doc_slip": (lambda: xd.build_trifold("doc_slip", 0.100, 0.210, True, 0.0020, "doc=slip,fold=tri,a4=1"),
                     "slip"),
        "doc_booklet": (xd.build_booklet, "booklet"),
        "doc_card": (xd.build_card, "card"),
        "doc_sticker_sheet": (xd.build_sticker_sheet, "sticker"),
    }


def doc_previews(pid, m, kind):
    xc.DOC_IMAGES.clear()
    for side, tag in (("front", "doc_cover"), ("back", "doc_back")):
        path = os.path.join(PAGES, f"preview_{kind}_{side}.png")
        if os.path.exists(path):
            xc.DOC_IMAGES[tag] = bpy.data.images.load(path, check_existing=True)
    lo, hi = xc.bounds(m.root)
    tgt = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2)
    span = max(hi.x - lo.x, hi.z - lo.z)
    tb = xc.table(0.8, -0.00002)
    views = [dict(target=tgt, yaw=205, pitch=48, dist=0.35 if span > 0.12 else 0.24),
             dict(target=(hi.x * 0.6, tgt[1], tgt[2]), yaw=75, pitch=10, dist=0.16 if span > 0.12 else 0.11),
             dict(target=(lo.x * 0.6, tgt[1], lo.z * 0.6), yaw=-130, pitch=16, dist=0.16 if span > 0.12 else 0.11)]
    xc.preview(pid, views)
    # the back: the paper turned over (about Z), seen from above
    bpy.data.objects.remove(tb)
    xc.place(m.root, (0.0, hi.y, 0.0), (0, 0, 1), (0, -1, 0))
    xc.table(0.8, -0.00002)
    xc.preview(pid, [dict(target=(0.0, hi.y / 2, 0.0), yaw=160, pitch=55, dist=0.35 if span > 0.12 else 0.24,
                          index=3)])


# ====================================================================== caps

def cap_builders():
    return {
        "cap_pcie16": xk.build_cap_pcie16,
        "cap_dp": lambda: xk.build_port_cap("cap_dp"),
        "cap_hdmi": lambda: xk.build_port_cap("cap_hdmi"),
        "guard_ram_ddr5": lambda: xk.build_guard_ram("guard_ram_ddr5", -0.0039),
        "guard_ram_ddr4": lambda: xk.build_guard_ram("guard_ram_ddr4", 0.0043),
        "cap_paste": xk.build_cap_paste,
        "sticker_psu_voltage": xk.build_sticker_psu_voltage,
    }


def imported_pose(obj):
    """Unity pose of an empty imported from one of our FBX files (the importer adds a local axis swap)."""
    mw = obj.matrix_world
    return pb.to_unity(mw.translation), pb.to_unity(mw.col[2].xyz).normalized(), pb.to_unity(mw.col[1].xyz).normalized()


def _euler_from(fwd, up):
    """Unity Euler angles (degrees, ZXY order as Quaternion.Euler) of LookRotation(fwd, up)."""
    R = pb.frame(fwd, up)  # columns right, up, forward
    # Unity: R = Ry * Rx * Rz ; extract
    m = R
    sx = -m[1][2]
    sx = max(-1.0, min(1.0, sx))
    x = math.asin(sx)
    if abs(math.cos(x)) > 1e-6:
        y = math.atan2(m[0][2], m[2][2])
        z = math.atan2(m[1][0], m[1][1])
    else:
        y = math.atan2(-m[2][0], m[0][0])
        z = 0.0
    return tuple(round(math.degrees(a), 3) % 360.0 for a in (x, y, z))


def rocker_off(objs, deg=9.0):
    """Tilts the imported PSU rocker (and its I/O marks) to the shipped OFF pose: the game's PsuSwitch sets
    localRotation = AngleAxis(off=+9, hinge=y) on the anchor's pieces (a positive Unity angle about +y is a
    negative Blender angle about the converted axis)."""
    from mathutils import Matrix
    a = next((o for o in objs if o.name == "A_SWITCH_PSU_0"), None)
    if a is None:
        return
    p, f, u = imported_pose(a)
    piv = c.conv(p)
    axis = c.conv(u)
    R = Matrix.Rotation(-deg * xc.DEG, 4, axis)
    for o in objs:
        if o.type == "MESH" and "@A_SWITCH_PSU_0" in o.name:
            o.matrix_world = Matrix.Translation(piv) @ R @ Matrix.Translation(-piv) @ o.matrix_world
    bpy.context.view_layer.update()


def check_caps(pid, m, previews):
    """Fit checks on every placement (overlaps and smallest gap) and, for the first one, the previews."""
    lines = []
    done_parts = {}
    for k, (part, parent, pos, fwd, up) in enumerate(xk.PLACEMENTS[pid]):
        # one import per part model
        if part not in done_parts:
            for o in [o for o in bpy.data.objects if o.get("dct_imported")]:
                bpy.data.objects.remove(o)
            done_parts[part] = xc.import_part(part)
            if pid == "sticker_psu_voltage":
                rocker_off(done_parts[part])
            # verify the anchors we rely on against the FBX
            for (pp_, an), (apos, afwd, aup) in xk.PART_ANCHORS.items():
                if pp_ != part:
                    continue
                e = next((o for o in done_parts[part] if o.name == an), None)
                if e is None:
                    lines.append(f"!! {part} has no {an}")
                    continue
                p, f, u = imported_pose(e)
                if (p - V(apos)).length > 2e-5 or (f - V(afwd)).length > 1e-3 or (u - V(aup)).length > 1e-3:
                    lines.append(f"!! {part} {an} moved: pos={tuple(round(x, 5) for x in p)} fwd={tuple(round(x, 3) for x in f)}")
        objs = done_parts[part]
        wp, wf, wu = xk.world_pose(part, parent, pos, fwd, up)
        xc.place(m.root, wp, wf, wu)
        ov, gap, gmesh = xc.fit_check(m.root, objs)
        ov_txt = "none" if not ov else ", ".join(f"{a}x{b}:{n}" for (a, b), n in ov.items())
        gap_txt = f"{gap * 1000:.2f} mm to {gmesh}" if gap < 1e8 else "> 4 mm"
        lines.append(f"fit {part} @{parent}: overlaps={ov_txt}; smallest gap {gap_txt}")
        if previews and k == 0:
            cap_previews(pid, m, part, parent, wp, wf, wu)
    for o in [o for o in bpy.data.objects if o.get("dct_imported")]:
        bpy.data.objects.remove(o)
    return lines


def cap_previews(pid, m, part, parent, wp, wf, wu):
    """Fit views with the part, a close-up, then the loose cap on a table."""
    lo, hi = xc.bounds(m.root)
    ctr = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2)
    R = pb.frame(tuple(wf), tuple(wu))
    out = R @ V((0, 0, 1))          # the pull direction in the part frame
    Z, Y = (0, 0, 1), (0, 1, 0)
    views = {
        "cap_pcie16": [dict(target=(-0.005, 0.0, 0.03), dir=(0.3, 0.45, -0.85), dist=0.32, up=Z),
                       dict(target=(0.03, -0.001, -0.003), dir=(0.25, 0.6, -0.75), dist=0.07, up=Z),
                       dict(target=(-0.047, -0.001, -0.004), dir=(-0.6, 0.45, -0.65), dist=0.07, up=Z)],
        "cap_dp": [dict(target=(0.0965, -0.0046, 0.046), dir=(1.0, -0.45, 0.3), dist=0.16, up=Z),
                   dict(target=(0.097, -0.0046, 0.027), dir=(1.0, -0.5, 0.5), dist=0.06, up=Z)],
        "cap_hdmi": [dict(target=(0.0965, -0.0046, 0.046), dir=(1.0, -0.45, -0.3), dist=0.16, up=Z),
                     dict(target=(0.097, -0.0046, 0.075), dir=(1.0, -0.5, -0.35), dist=0.06, up=Z)],
        "guard_ram_ddr5": [dict(target=(0.0, 0.0, 0.016), dir=(1.0, 0.3, -0.4), dist=0.3, up=Z),
                           dict(target=(0.0, -0.0039, 0.001), dir=(1.0, 0.45, -0.7), dist=0.045, up=Z)],
        "guard_ram_ddr4": [dict(target=(0.0, 0.0, 0.016), dir=(1.0, 0.3, -0.4), dist=0.3, up=Z),
                           dict(target=(0.0, 0.0043, 0.001), dir=(1.0, 0.45, -0.7), dist=0.045, up=Z)],
        "cap_paste": [dict(target=(0.0, 0.0, 0.0), dir=(0.45, 0.3, -0.85), dist=0.26, up=Y),
                      dict(target=(0.0, 0.0, -0.001), dir=(0.55, 0.35, -0.75), dist=0.1, up=Y)],
        "sticker_psu_voltage": [dict(target=(0.07, 0.005, 0.02), dir=(1.0, 0.35, 0.5), dist=0.3, up=Y),
                                dict(target=(0.071, 0.026, 0.047), dir=(1.0, 0.3, -0.2), dist=0.07, up=Y)],
    }[pid]
    # Unity yaw/pitch are about +Y; for z-up parts the dicts give up=(0,0,1) and the camera orbits as usual
    xc.preview(pid, views)
    # the loose piece, lying on a table
    for o in [o for o in bpy.data.objects if o.get("dct_imported")]:
        o.hide_render = True
    loose = {"cap_pcie16": ((0, -1, 0), (1, 0, 0)), "cap_dp": ((1, 0, 0), (0, 1, 0)), "cap_hdmi": ((1, 0, 0), (0, 1, 0)),
             "guard_ram_ddr5": ((0, -1, 0), (0, 0, 1)), "guard_ram_ddr4": ((0, -1, 0), (0, 0, 1)),
             "cap_paste": ((0, 1, 0), (0, 0, 1)), "sticker_psu_voltage": ((0, 1, 0), (0, 0, 1))}[pid]
    xc.place(m.root, (0, 0, 0), *loose)
    lo, hi = xc.bounds(m.root)
    xc.place(m.root, (-(lo.x + hi.x) / 2, -lo.y, -(lo.z + hi.z) / 2), *loose)
    lo, hi = xc.bounds(m.root)
    ctr = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2)
    span = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z)
    xc.table(0.6, lo.y - 0.00001)
    n0 = len(views)
    xc.preview(pid, [dict(target=ctr, yaw=30, pitch=40, dist=max(0.06, span * 2.0), index=n0),
                     dict(target=ctr, yaw=-120, pitch=28, dist=max(0.045, span * 1.1), index=n0 + 1)])
    for o in [o for o in bpy.data.objects if o.get("dct_imported")]:
        o.hide_render = False


# ====================================================================== film data the game derives from the parts

def film_data():
    """Fan hub stickers (for the hub films) and the side-panel glass (for the glass films), measured on the FBX."""
    lines = ["FILM DATA DERIVED FROM THE PART MESHES (no new anchors needed; hard-code if preferred)",
             "  hub film: a disc on the fan's sticker, in the A_FAN_<n> frame (local +z = the fan's front, where the",
             "  sticker faces): centre (x, y), radius, and z = the sticker surface (put the film 0.05 mm above it).",
             "  It belongs on the rotor: parent it to A_FAN_<n> so it spins with the hub."]
    for pid in ("gpu_rx66", "gpu_rx88", "cooler_stock", "cooler_tower", "case_breeze", "case_brickhouse"):
        c.reset()
        objs = xc.import_part(pid)
        for o in sorted(objs, key=lambda o: o.name):
            is_sticker = "_sticker@A_FAN_" in o.name or ("@A_FAN_" in o.name and "fanhub" in o.name)
            if o.type != "MESH" or not is_sticker:
                continue
            an = o.name.split("@", 1)[1].split("#", 1)[0]
            a = next((e for e in objs if e.name == an), None)
            if a is None:
                continue
            ap, af, au = imported_pose(a)
            R = pb.frame(tuple(af), tuple(au))
            Ri = R.transposed()
            pts = [Ri @ (pb.to_unity(o.matrix_world @ v.co) - ap) for v in o.data.vertices]
            cx = (max(p.x for p in pts) + min(p.x for p in pts)) / 2
            cy = (max(p.y for p in pts) + min(p.y for p in pts)) / 2
            rad = max(math.hypot(p.x - cx, p.y - cy) for p in pts)
            zz = max(p.z for p in pts)
            lines.append(f"  {pid:16s} {an:8s} centre=({cx + 0.0:.4f},{cy + 0.0:.4f}) r={rad:.4f} z={zz:.4f}  "
                         f"(fan at {tuple(round(x, 4) + 0.0 for x in ap)}, fwd {tuple(int(round(x)) for x in af)})")
    lines.append("  RAM spreader film: the +x face of the stick's A_HIT_0 (x = +size.x/2: 0.00385 DDR5, 0.00360 DDR4; it")
    lines.append("  clears the relief panel and the label), y +-0.0646, z 0.007 .. 0.038 (DDR5) / 0.0336 (DDR4), facing +x.")
    lines.append("  glass films: in the A_PANEL_SIDE_0 frame (pos (0, 0.225, 0.1), fwd +z, up +y, x = case +x),")
    lines.append("  from the glass mesh panel_side_0@A_PANEL_SIDE_0#glass:")
    for pid in ("case_breeze", "case_brickhouse"):
        c.reset()
        objs = xc.import_part(pid)
        g = next((o for o in objs if o.name.startswith("panel_side_0@A_PANEL_SIDE_0#glass")), None)
        a = next((o for o in objs if o.name == "A_PANEL_SIDE_0"), None)
        if g is None or a is None:
            lines.append(f"  {pid}: glass or panel anchor missing")
            continue
        ap, af, au = imported_pose(a)
        Ri = pb.frame(tuple(af), tuple(au)).transposed()
        pts = [Ri @ (pb.to_unity(g.matrix_world @ v.co) - ap) for v in g.data.vertices]
        lo = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        lines.append(f"  {pid:16s} glass x {lo.x:.4f}..{hi.x:.4f}  y {lo.y:.4f}..{hi.y:.4f}  z {lo.z:.4f}..{hi.z:.4f}")
        lines.append(f"  {'':16s} outer film: centre ({(lo.x + hi.x) / 2:.4f}, {(lo.y + hi.y) / 2:.4f}, {hi.z + 0.00005:.5f}) "
                     f"facing +z, size {hi.x - lo.x:.4f} x {hi.y - lo.y:.4f}")
        lines.append(f"  {'':16s} inner film: centre ({(lo.x + hi.x) / 2:.4f}, {(lo.y + hi.y) / 2:.4f}, {lo.z - 0.00005:.5f}) "
                     f"facing -z, size {hi.x - lo.x:.4f} x {hi.y - lo.y:.4f}")
    return lines


# ====================================================================== new anchors on the part models

def part_anchor_lines():
    """The film anchors agent C added to the part build scripts: read back from the re-exported FBX files (GPUs,
    tower cooler), and the values to hard-code for the boards (whose build is not reproducible, so not re-exported)."""
    lines = ["NEW ANCHORS ON PART MODELS (films, Logs/UNBOXING.md 1.4; the game builds the peel meshes on them)",
             "  Re-exported (build_parts_b.py; extras_compare.py proved every existing object unchanged, only these",
             "  anchors added; textures pixel-identical):"]
    for pid in ("gpu_rx66", "gpu_rx88", "cooler_tower"):
        c.reset()
        objs = xc.import_part(pid)
        for o in sorted(objs, key=lambda o: o.name):
            if o.type == "EMPTY" and o.name.startswith("A_FILM_") and o.name != "A_FILM_0":
                p, f, u = imported_pose(o)
                fi, ui = [int(round(x)) for x in f], [int(round(x)) for x in u]
                lines.append(f"  {pid:13s} {o.name}: pos=({p.x:.5f},{p.y:.5f},{p.z:.5f}) fwd=({fi[0]},{fi[1]},{fi[2]}) "
                             f"up=({ui[0]},{ui[1]},{ui[2]}) size={o.get('size')} meta={o.get('meta')}")
    import build_board as bb
    xr = bb.IO_FACE - 1.7
    lines += ["  NOT re-exported: mb_ridge_b5, mb_ridge_z4. build_board.py does not rebuild them identically (two clean",
              "  runs of the unchanged script differ from each other and from the committed FBX in the triangulation",
              "  of a few n-gons). The anchors are in build_board.py (Board.films) for the next rebuild; until then",
              "  hard-code them (board frame, metres; fwd = film normal, up; size = x, y, thickness in the anchor's axes):"]
    for bid, y0 in (("mb_ridge_b5", 22.0), ("mb_ridge_z4", 30.0)):
        io = ((99.8 + xr) / 2 + 0.6, (y0 + 151.5) / 2 + 6.0, 37.12)
        lines.append(f"  {bid:13s} A_FILM_IO_0: pos=({io[0] / 1000:.5f},{io[1] / 1000:.5f},{io[2] / 1000:.5f}) fwd=(0,0,1) "
                     f"up=(0,1,0) size=0.01800,0.07700,0.00100 meta=film=clear,on=io_cover_logo,peel_from=-y")
        lines.append(f"  {bid:13s} A_FILM_CHIPSET_0: pos=(-0.08000,-0.08800,{(bb.PT + 9.52) / 1000:.5f}) fwd=(0,0,1) "
                     f"up=(0,1,0) size=0.03100,0.02700,0.00100 meta=film=clear,on=chipset_logo,peel_from=+x")
    lines += ["  Not needed (placed from what exists): A_EDGE_PCIE_0 (cap_pcie16 sits on the GPU frame origin; A_HIT_2",
              "  covers the fingers), A_EDGE_0 on the RAM (the guards sit on the RAM frame origin), A_STICKER_PSU_0 (the",
              "  sticker sits on A_SWITCH_PSU_0), A_FILM_HUB_<n> and A_FILM_GLASS_0/1 (derived from the sticker and glass",
              "  meshes below, as UNBOXING.md 2.4 describes)."]
    return lines


# ====================================================================== main

def main(argv):
    t0 = time.time()
    previews = "--nopreview" not in argv and PREVIEW[0]
    ids = [a for a in argv if not a.startswith("--")] or DOCS + CAPS
    os.makedirs(PAGES, exist_ok=True)
    if previews and any(i in DOCS for i in ids):
        c.reset()
        xd.preview_pages(PAGES)
    blocks, placements, failed = [], [], []
    dbs, cbs = doc_builders(), cap_builders()
    for pid in ids:
        t = time.time()
        try:
            if pid in dbs:
                fn, kind = dbs[pid]
                m = fn()
                block = xc.report(m)
                if previews:
                    doc_previews(pid, m, kind)
            elif pid in cbs:
                m = cbs[pid]()
                m.finish()
                xc.triangulate(m.root)
                xc.validate(m.root)
                m.export()
                block = xc.report(m)
                fit = check_caps(pid, m, previews)
                block += "\n" + "\n".join("   " + x for x in fit)
                for (part, parent, pos, fwd, up) in xk.PLACEMENTS[pid]:
                    placements.append((pid, part, parent, pos, fwd, up))
            else:
                print("UNKNOWN", pid)
                continue
            blocks.append(block + f"\n   built in {time.time() - t:.1f} s")
            print(block)
        except Exception as e:  # keep going, report at the end
            import traceback
            traceback.print_exc()
            failed.append(f"{pid}: {e}")
    write_report(blocks, placements, failed, ids)
    print(f"BUILD_EXTRAS done: {len(blocks)} models in {time.time() - t0:.1f} s; failed: {failed or 'none'}")
    if failed:
        sys.exit(1)


def write_report(blocks, placements, failed, ids):
    path = os.path.join(c.PREVIEWS, "extras_report.txt")
    head = [
        "EXTRAS - REPORT (agent C: papers, part caps, guards, stickers; Logs/UNBOXING.md 2.3 and 2.5)",
        "=" * 100,
        r'Run: "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_extras.py -- [--nopreview] [ids]',
        "Scripts: Tools/Blender/build_extras.py (runner, fit checks, report), extras_common.py, extras_docs.py,",
        "         extras_caps.py.  Textures: doc_badges.png (badge atlas), sticker_psu.png.",
        "",
        "CONVENTIONS",
        "  Papers: origin at the bottom centre, lying flat, front +Y, page top +Z, reading right +X. doc_cover = the",
        "  visible front face, UV 0..1 over it (u +X, v +Z); doc_back = the visible back face, UV 0..1 (u -X, v +Z:",
        "  the paper turned over about Z, like turning a page). Edges, folds, inner pages: paper_white.",
        "  To lay a paper into an A_ITEM_DOC_<n> anchor (paper in the anchor's XY plane, front = anchor +Z):",
        "  localRotation = Quaternion.Euler(-90, 180, 0) (paper +Y -> anchor +Z, paper +Z -> anchor +Y); the paper's",
        "  origin is its back face, so if the anchor is the paper's centre, add localPosition (0, 0, -t/2).",
        "  Caps / guards / sticker: local +Z = the direction it is pulled off; origin = its seat reference.",
        "  A_HIT_0 = the cap's bounds (meta remove=+z,travel=...,blocks=...), A_GRIP_0 = the pull tab (forward = pull).",
        "",
    ]
    table = ["CAP PLACEMENT TABLE (Unity, in the parent's axes; rotation = Quaternion.LookRotation(fwd, up) =",
             "Quaternion.Euler(x, y, z) as given; remove = the pull direction in the PARENT's axes)"]
    seen = set()
    for (pid, part, parent, pos, fwd, up) in placements:
        e = _euler_from(fwd, up)
        R = pb.frame(fwd, up)
        rem = R @ V((0, 0, 1))
        key = (pid, part, parent)
        if key in seen:
            continue
        seen.add(key)
        table.append(f"  {pid:20s} {part:13s} parent={parent:15s} pos={tuple(pos)} fwd={tuple(fwd)} up={tuple(up)} "
                     f"euler={e} remove={tuple(round(x, 3) + 0.0 for x in rem)}")
    table += [
        "  Notes: cap_dp / cap_hdmi: one cap per port anchor (3 DP + 1 HDMI per card). sticker_psu_voltage: parent it",
        "  to the A_SWITCH_PSU_0 transform itself, not to its Rocker group, so it does not tilt with the rocker; it is",
        "  draped over the rocker's shipped OFF pose (PsuSwitch offAngle +9 about y). Pullable: hold/drag along the",
        "  cap's local +Z (travel 1.5 mm, then it pops); the GPU and RAM caps block installing, the DP/HDMI caps block",
        "  plugging that port, cap_paste blocks installing the cooler.",
        "",
        "BADGE ATLAS (tex_doc_badges = Models/Textures/doc_badges.png, 1024 x 1024, 4 x 4 cells of 256 px, row 0 at the",
        "top). The badges' UVs map the default cell; to show another cell add a UV offset (_BaseMap_ST zw) of",
        "(dcol * 0.25, -drow * 0.25). Defaults: badge_0@A_STICKER_0 = cell 0, badge_1@A_STICKER_1 = cell 5.",
    ]
    for i, (col, row, text) in enumerate(xd.BADGE_CELLS):
        u0, v0, u1, v1 = xd.cell_uv(col, row, 0.0)
        table.append(f"  cell {i}: col {col} row {row}  uv ({u0:.3f},{v0:.3f})..({u1:.3f},{v1:.3f})  {text}")
    table.append("  Per product: cpu_arc5 0+5, cpu_arc7 1+5, cpu_tiron5 2+6, mb_ridge_* 3+7, gpu_rx* 4+8 "
                 "(main + small); the rims use the silver swatch at col 1 row 2.")
    lines = head + table + [""] + blocks
    if failed:
        lines += ["", "FAILED:"] + failed
    try:
        lines += [""] + part_anchor_lines()
    except Exception as ex:
        lines += ["", f"part anchor listing failed: {ex}"]
    try:
        lines += [""] + film_data()
    except Exception as ex:  # the report must still be written
        lines += ["", f"film data failed: {ex}"]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("REPORT", path)


if __name__ == "__main__":
    main(c.args())
