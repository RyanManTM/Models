"""
build_cat_coolers.py - the catalogue CPU coolers (docs/tasks/catalog/16-coolers.md): air towers on the cooler_tower
contract, a stock cooler on the cooler_stock contract, AIO liquid coolers and server heatsinks (new contracts, see
docs/reports/cat_coolers.md).

Run: blender -b --factory-startup -P Tools/Blender/build_cat_coolers.py -- [ids] [--nopreview]

Air towers (cooler_tower frame): origin at the centre of the base contact face, +z away from the board, x towards
the board's rear I/O edge (the air flows -x -> +x), y towards its top edge. The X bracket, its four spring screws
A_SCREW_PH2_0..3 on (+-0.033, +-0.033) and the base film A_FILM_0 are exactly cooler_tower's; the fin stacks,
heat pipes, fans (A_FAN_n with A_PLUG_FAN_n) and the top cover (A_FILM_TOP_0) vary.
Coloured plastics that no plain tag covers (Noctis brown, beige) are swatches in tex_<id>_col.
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_b as pb  # noqa: E402
import parts_fan as pf  # noqa: E402
import build_cooler as bc  # noqa: E402
from mathutils import Vector as V  # noqa: E402

PREVIEW = [True]
REPORT = []
HOLES = bc.HOLES


# ====================================================================== shared helpers

def tint(objs, uv_rect):
    """Points every UV of the objects at the centre of uv_rect (a solid swatch of a tex_ atlas)."""
    u = (uv_rect[0] + uv_rect[2]) / 2
    v = (uv_rect[1] + uv_rect[3]) / 2
    for o in objs:
        if o is None:
            continue
        for d in o.data.uv_layers.active.data:
            d.uv = (u, v)


def fan(m, anchor, size, thickness, scheme, sticker, sticker_uv, name, blades=7, rgb=False, col=None):
    """make_fan with a colour scheme: (frame, blades) as plain tags, or 'col:<cell>' swatches of tex_<id>_col
    (col = (file, atlas)). Returns make_fan's return_all dict."""
    fr, bl = scheme

    def tag(t):
        return "tex_" + col[0] if t.startswith("col:") else t

    r = pf.make_fan(anchor, diameter=size, thickness=thickness, blades=blades, frame=True, rgb=rgb, sticker=sticker,
                    sticker_uv=sticker_uv, name=name, frame_tag=tag(fr), blade_tag=tag(bl), return_all=True)
    if fr.startswith("col:"):
        tint([o for o in r["static"] if o.name.endswith("#" + tag(fr))], col[1].uv(fr[4:]))
    if bl.startswith("col:"):
        tint([r["rotor"]], col[1].uv(bl[4:]))
    hub_film(m, anchor, r["sticker"])
    return r


def hub_film(m, anchor, sticker):
    """A_FILM_HUB_<n>: the clear film disc on a fan's hub sticker, an anchor in (and parented to) the fan's anchor
    frame so it spins with the rotor; n is the fan's index. Centre, radius and height come from the sticker mesh."""
    n = int(re.match(r"A_(?:RAD_)?FAN_(\d+)", anchor.name).group(1))
    p0, fwd, up = pb.unity_pose(anchor)
    pts = [pb.to_unity(sticker.matrix_world @ v.co) for v in sticker.data.vertices]
    z = max((q - p0).dot(fwd) for q in pts)
    r = max(((q - p0) - fwd * (q - p0).dot(fwd)).length for q in pts)
    return m.anchor(f"A_FILM_HUB_{n}", tuple(p0 + fwd * (z + 0.00005)), (2 * r, 2 * r, 0.0001), forward=tuple(fwd),
                    up=tuple(up), meta=f"film=clear,on=fan_hub,shape=disc,radius={r:.4f},peel=+x,tab=+x", parent=anchor)


def plug(m, idx, face, back_dir, up, cable_from, cable_pts, kind="fan4", target="CPU_FAN", tag="connector_black",
         cable_tag="black_plastic", name="FAN"):
    """build_cooler.fan_plug with an index and a kind: fan4 (4-pin PWM) or argb3 (5 V 3-pin ARGB, 4 positions with
    one blanked)."""
    a = m.anchor(f"A_PLUG_{name}_{idx}", face, (0.012, 0.008, 0.016), forward=back_dir, up=up,
                 meta=f"kind={kind},frame=plug,target={target}")
    M = pb.frame(back_dir, up)
    t = V(face)
    pl = m.piece(a, tag, "plug")
    if kind == "fan4":
        holes = [pb.rect2((k - 1.5) * 0.00254, -0.0004, 0.0012, 0.0012) for k in range(4)]
        pl.add(pb.g_slab(pb.rrect2(0, 0, 0.0101, 0.0058, 0.0005, 2), holes, 0.0025, 0.0), M, t)
        pl.add(pb.g_box((0.0101, 0.0058, 0.0110), 0.0003), M, t + M @ V((0, 0, 0.0080)))
        pl.add(pb.g_box((0.0050, 0.0012, 0.0045)), M, t + M @ V((0, 0.0034, 0.0035)))
        for k in (-1, 1):
            pl.add(pb.g_box((0.0007, 0.0010, 0.0115)), M, t + M @ V((k * 0.0042, 0.0033, 0.0075)))
        for k in range(4):
            pl.add(pb.g_box((0.0007, 0.0007, 0.0018)), M, t + M @ V(((k - 1.5) * 0.00254, -0.0004, 0.0012)))
    else:  # ARGB 3-pin (5V, D, -, G): a slim housing with an arrow, one blanked hole
        holes = [pb.rect2((k - 1.5) * 0.00254, 0, 0.0011, 0.0011) for k in range(4) if k != 2]
        pl.add(pb.g_slab(pb.rrect2(0, 0, 0.0108, 0.0034, 0.0004, 2), holes, 0.0020, 0.0), M, t)
        pl.add(pb.g_box((0.0108, 0.0034, 0.0090), 0.0003), M, t + M @ V((0, 0, 0.0065)))
        pl.add(pb.g_box((0.0016, 0.0008, 0.0016)), M, t + M @ V((-0.0040, 0.0019, 0.0050)))  # 5V arrow mark
    pts = [V(cable_from)] + [V(p) for p in cable_pts] + [t + M @ V((0, 0, 0.0185)), t + M @ V((0, 0, 0.0105))]
    m.add(cable_tag, pb.g_sweep(pb.fillet_path(pts, 0.006, 6), 0.0013 if kind == "fan4" else 0.0011, 10))
    return a


def finish(m, pid, views, extra=""):
    m.finish()
    txt = m.report()
    lo, hi = bounds(m.root)
    line = f"   BOUNDS x {lo.x:.4f}..{hi.x:.4f}  y {lo.y:.4f}..{hi.y:.4f}  z {lo.z:.4f}..{hi.z:.4f}"
    print(line)
    REPORT.append(txt + "\n" + line + (("\n" + extra) if extra else ""))
    m.export()
    if PREVIEW[0]:
        pb.preview_textures()
        pb.shots(m.root, pid, views)


def bounds(root):
    pts = []
    for o in c.descendants(root):
        if o.type == "MESH":
            pts += [pb.to_unity(o.matrix_world @ V(cc)) for cc in o.bound_box]
    lo = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


# ====================================================================== textures

def tex_tower(pid, cfg):
    """The label atlas: top cover insert, fan hub sticker, base film and tab, plain swatches."""
    br = cfg["brand"]
    at = pb.Atlas(2048, 1024)
    at.add("top", 0, 0, 1024, 256)
    at.add("hub", 1024, 0, 512, 512)
    at.add("film", 1536, 0, 512, 512)
    at.add("tab", 1536, 512, 256, 128)
    at.add("blue", 1792, 512, 64, 64)
    at.add("top2", 0, 256, 1024, 256)
    cv = pb.Canvas(2048, 1024, bg="#0d0d0e")
    cfg["draw_top"](cv, 0, 0, cfg)
    cfg["draw_top2"](cv, 0, 256, cfg)
    cfg["draw_hub"](cv, 1024 + 256, 256, cfg)
    fx, fy = 1536, 0
    fc = cfg.get("film_col", "#3d8ee6")
    cv.rect(fx, fy, 512, 512, fc)
    for k in range(9):
        cv.line(fx, fy + 40 + k * 60, fx + 512, fy - 60 + k * 60, 14, cfg.get("film_stripe", "#4a98ec"))
    cv.text("REMOVE", fx + 256, fy + 180, 64, "#ffffff", "arialb", "center", "center")
    cv.text("BEFORE USE", fx + 256, fy + 270, 52, "#ffffff", "arialb", "center", "center")
    cv.text(br.upper(), fx + 256, fy + 380, 30, "#e8f2ff", cfg.get("font", "eras"), "center", "center", spacing=1.3)
    cv.rect(1536, 512, 256, 128, fc)
    cv.text("PEEL >", 1536 + 128, 512 + 64, 40, "#ffffff", "arialb", "center", "center")
    cv.rect(1792, 512, 64, 64, fc)
    cv.render(pid)
    return at


def tex_col(pid, cells):
    """tex_<id>_col: solid swatches {name: '#rrggbb'} in 64 px cells."""
    at = pb.Atlas(64 * len(cells), 64)
    cv = pb.Canvas(64 * len(cells), 64, bg="#808080")
    for k, (nm, col) in enumerate(cells.items()):
        at.add(nm, 64 * k, 0, 64, 64)
        cv.rect(64 * k, 0, 64, 64, col)
    cv.render(pid + "_col")
    return (pid + "_col", at)


# ---------------------------------------------------------------- brand art (top inserts, hub stickers)

def hub_ring(cv, x, y, bg, ring, brand, fg, font="eras", sub=None, sub_col=None, size=46):
    cv.circle(x, y, 252, bg)
    cv.ring(x, y, 226, 236, ring)
    cv.text(brand, x, y - (14 if sub else 0), size, fg, font, "center", "center", spacing=1.15, maxw=380)
    if sub:
        cv.text(sub, x, y + 52, 22, sub_col or ring, "arialb", "center", "center", spacing=1.6, maxw=300)


def arctiq_top(cv, x, y, cfg):
    bg, fg, acc = cfg["top_bg"], cfg["top_fg"], cfg["accent"]
    cv.rect(x, y, 1024, 256, bg)
    # a snowflake-ish star mark and the wordmark
    cx, cy = x + 150, y + 128
    for k in range(3):
        a = k * math.pi / 3
        cv.line(cx - 64 * math.cos(a), cy - 64 * math.sin(a), cx + 64 * math.cos(a), cy + 64 * math.sin(a), 14, acc)
    cv.circle(cx, cy, 18, bg)
    cv.text("ARCTIQ", x + 250, y + 112, 92, fg, "arialb", "left", "center", spacing=1.25, maxw=640)
    cv.text(cfg["model_line"], x + 254, y + 196, 30, acc, "arialb", "left", "center", spacing=1.6, maxw=640)


def arctiq_hub(cv, x, y, cfg):
    hub_ring(cv, x, y, cfg["hub_bg"], cfg["accent"], "ARCTIQ", cfg["hub_fg"], "arialb", size=52)


def glacier_top(cv, x, y, cfg):
    bg, fg, acc = cfg["top_bg"], cfg["top_fg"], cfg["accent"]
    cv.rect(x, y, 1024, 256, bg)
    for k in range(7):  # the diagonal brushed stripes either side of the badge
        cv.line(x + 30 + k * 26, y + 236, x + 120 + k * 26, y + 20, 8, acc)
        cv.line(x + 994 - k * 26, y + 236, x + 904 - k * 26, y + 20, 8, acc)
    cv.text("GLACIER", x + 512, y + 104, 86, fg, "arialb", "center", "center", spacing=1.35, maxw=560)
    cv.text(cfg["model_line"], x + 512, y + 190, 30, acc, "arialb", "center", "center", spacing=2.0, maxw=560)


def glacier_hub(cv, x, y, cfg):
    hub_ring(cv, x, y, cfg["hub_bg"], cfg["accent"], "GLACIER", cfg["hub_fg"], "arialb", size=44)


def noctis_top(cv, x, y, cfg):
    bg, fg, acc = cfg["top_bg"], cfg["top_fg"], cfg["accent"]
    cv.rect(x, y, 1024, 256, bg)
    # an owl-eye style mark: two rings
    for dx in (-36, 36):
        cv.ring(x + 150 + dx, y + 128, 22, 36, fg)
    cv.text("NOCTIS", x + 250, y + 128, 96, fg, "arialb", "left", "center", spacing=1.45, maxw=680)


def noctis_top2(cv, x, y, cfg):
    cv.rect(x, y, 1024, 256, cfg["top_bg"])
    cv.text(cfg["model_line"], x + 512, y + 128, 80, cfg["top_fg"], "arialb", "center", "center", spacing=1.3)


def noctis_hub(cv, x, y, cfg):
    cv.circle(x, y, 252, cfg["hub_bg"])
    for dx in (-30, 30):
        cv.ring(x + dx, y - 40, 18, 30, cfg["hub_fg"])
    cv.text("NOCTIS", x, y + 50, 52, cfg["hub_fg"], "arialb", "center", "center", spacing=1.3)


def frostpeak_top(cv, x, y, cfg):
    cv.rect(x, y, 1024, 256, "#121315")
    cv.poly([(x + 70, y + 196), (x + 150, y + 66), (x + 192, y + 130), (x + 222, y + 96), (x + 296, y + 196)],
            "#dfe6ee")
    cv.text("FROSTPEAK", x + 330, y + 120, 74, "#eef1f5", "eras", "left", "center", spacing=1.2, maxw=640)
    cv.text(cfg["model_line"], x + 334, y + 196, 30, "#c070ff", "arialb", "left", "center", spacing=1.8, maxw=640)


def frostpeak_hub(cv, x, y, cfg):
    cv.circle(x, y, 252, "#141518")
    cv.ring(x, y, 226, 236, "#c070ff")
    cv.poly([(x - 120, y + 50), (x - 40, y - 90), (x + 2, y - 20), (x + 34, y - 60), (x + 120, y + 50)], "#e6ecf2")
    cv.text("FROSTPEAK", x, y + 110, 40, "#e6ecf2", "eras", "center", "center", spacing=1.2)


def plain_top2(cv, x, y, cfg):
    cv.rect(x, y, 1024, 256, cfg["top_bg"])


# ====================================================================== air tower

def fin_outline(D, W, teeth=10, amp=0.004, rear_teeth=0, notch=True):
    """One fin in (x, y) about its tower centre: depth 2D along x (air -x -> +x), width 2W along y; a sawtooth
    intake edge (-x), an optional sawtooth exhaust edge, clip notches near the intake on both sides."""
    pts = []
    xi = -D + amp  # the intake teeth's roots
    if notch:
        pts += [(xi, -W), (-D + 0.0050, -W), (-D + 0.0050, -W + 0.0022), (-D + 0.0080, -W + 0.0022),
                (-D + 0.0080, -W)]
    else:
        pts += [(xi, -W)]
    if rear_teeth:
        pts.append((D - amp, -W))
        for k in range(1, 2 * rear_teeth):
            y = -W + k * (2 * W) / (2 * rear_teeth)
            pts.append((D if k % 2 == 1 else D - amp, y))
        pts.append((D - amp, W))
    else:
        pts += [(D, -W), (D, W)]
    if notch:
        pts += [(-D + 0.0080, W), (-D + 0.0080, W - 0.0022), (-D + 0.0050, W - 0.0022), (-D + 0.0050, W), (xi, W)]
    else:
        pts.append((xi, W))
    for k in range(1, 2 * teeth):
        y = W - k * (2 * W) / (2 * teeth)
        pts.append((-D if k % 2 == 1 else xi, y))
    return pts


def base_and_bracket(m, base_tag="nickel", cap_tag="alu", groove_tag="alu_dark", bracket_tag="steel",
                     base_w=0.040):
    """cooler_tower's base plate, pipe cap and X bracket with the four spring screws (the contract anchors)."""
    bc.box(m, base_tag, (-0.019, -base_w / 2, 0.0), (0.019, base_w / 2, 0.0042), bevel=0.0004)
    bc.box(m, base_tag, (-0.0150, -base_w / 2 + 0.0005, 0.0042), (0.0150, base_w / 2 - 0.0005, 0.0068), bevel=0.0003)
    m.add(cap_tag, pb.g_slab(pb.chamfer2(0, 0, 0.040, 0.034, 0.003), [], 0.0058, 0.0068, bevel=0.0004))
    for k in range(5):
        bc.box(m, groove_tag, (-0.0195, -0.0150 + k * 0.0075, 0.0124), (0.0195, -0.0143 + k * 0.0075, 0.01265))
    xb_poly = []
    arm = 0.0045
    for (hx, hy) in [(0.033, 0.033), (-0.033, 0.033), (-0.033, -0.033), (0.033, -0.033)]:
        d = V((hx, hy, 0)).normalized()
        p = V((-d.y, d.x, 0))
        tip = V((hx, hy, 0)) + d * 0.004
        xb_poly += [tuple(tip - p * arm)[:2], tuple(tip + p * arm)[:2]]
        nxt = math.atan2(hy, hx) + math.pi / 4
        xb_poly.append((math.cos(nxt) * 0.0120, math.sin(nxt) * 0.0120))
    xbh = [pb.circle2(x, y, 0.0018, 16) for (x, y) in HOLES]
    m.add(bracket_tag, pb.g_slab(xb_poly, xbh, 0.0015, 0.0126, bevel=0.0003))
    for i, (x, y) in enumerate(HOLES):
        bc.spring_screw(m, i, x, y, 0.0141, 0.0196, head_r=0.0036, spring_r=0.0030)


def base_film(m, at, TEX):
    """cooler_tower's protective base film (A_FILM_0, same pose, size and meta)."""
    fa_ = m.anchor("A_FILM_0", (0, 0, 0), (0.044, 0.044, 0.003), forward=(0, 0, -1), up=(0, 1, 0),
                   meta="peel_from=+x,text=REMOVE BEFORE USE")
    fp = m.piece(fa_, TEX, "film")
    fp.add(pb.solid(pb.g_slab(pb.rect2(0, 0, 0.040, 0.042), [], 0.00012, -0.00013, back=False), at.uv("blue")))
    fp.add(pb.g_quad(0.040, 0.042, at.uv("film")), pb.label_frame((0, 0, -1), (0, 1, 0)), (0, 0, -0.000135))
    tab = [(0.0198, -0.006), (0.0235, -0.006), (0.0305, -0.004), (0.0305, 0.004), (0.0235, 0.006), (0.0198, 0.006)]
    fp.add(pb.solid(pb.g_slab(tab, [], 0.00012, -0.00013, back=False), at.uv("blue")))
    fp.add(pb.g_quad(0.010, 0.010, at.uv("tab")), pb.label_frame((0, 0, -1), (0, 1, 0)), (0.0252, 0, -0.000135))


def pipe_layout(cfg):
    """[(path points)] for the heat pipes. Single tower: U pipes across the base along y, legs at +-w in the
    stack. Dual: pipes across the base along x, one leg in each tower."""
    zb = 0.0090
    z0 = cfg["fin_z0"]
    z_top = z0 + (cfg["fin_n"] - 1) * cfg["pitch"] + 0.0030
    paths = []
    if len(cfg["towers"]) == 1:
        tx = cfg["towers"][0]
        n = cfg["pipes"]
        for k in range(n):
            xb = (k - (n - 1) / 2) * (0.028 / max(1, n - 1)) if n > 1 else 0.0
            xl = tx + (-0.0105 if k < n / 2 else 0.0105) * (cfg["D"] / 0.025)
            w = cfg["W"] * (0.40 + 0.52 * ((k * 0.618) % 1.0))
            half = [(xl, w, z_top), (xl, w, z0 - 0.004), (xb, w * 0.62, z0 - 0.016), (xb, 0.016, zb)]
            pts = [(p[0], -p[1], p[2]) for p in half] + list(reversed(half))
            paths.append((pts, (xl, w)))
    else:
        tf, tr = cfg["towers"]
        n = cfg["pipes"]
        for k in range(n):
            yb = (k - (n - 1) / 2) * (0.030 / max(1, n - 1))
            yl = (k - (n - 1) / 2) * (2 * cfg["W"] * 0.80 / max(1, n - 1))
            dx = (0.0085 if k % 2 else -0.0085) * (cfg["D"] / 0.025)
            pts = [(tf + dx, yl, z_top), (tf + dx, yl, z0 - 0.004), (-0.017, yb, zb + 0.004), (-0.012, yb, zb),
                   (0.012, yb, zb), (0.017, yb, zb + 0.004), (tr - dx, yl, z0 - 0.004), (tr - dx, yl, z_top)]
            paths.append((pts, None))
    return paths, z_top


def build_tower_model(pid, cfg):
    """A tower cooler from a config (see TOWERS)."""
    at = cfg["tex"](pid, cfg)
    col = tex_col(pid, cfg["col"]) if cfg.get("col") else None
    m = pb.Model(pid)
    TEX = "tex_" + pid
    D, W = cfg["D"], cfg["W"]
    z0, pitch, n = cfg["fin_z0"], cfg["pitch"], cfg["fin_n"]
    zt = z0 + (n - 1) * pitch
    pipe_tag = cfg.get("pipe_tag", "nickel")
    fin_tag = cfg.get("fin_tag", "alu")
    base_and_bracket(m, base_tag=cfg.get("base_tag", "nickel"), cap_tag=cfg.get("cap_tag", "alu"),
                     groove_tag=cfg.get("groove_tag", "alu_dark"))
    # heat pipes (6 mm, U-bent) with crimped tips under the covers
    paths, z_top = pipe_layout(cfg)
    legs = []
    for pts, _ in paths:
        m.add(pipe_tag, pb.g_sweep(pb.fillet_path(pts, 0.0095, 10), 0.0030, 16))
        for p in (pts[0], pts[-1]):
            legs.append((p[0], p[1]))
            m.add(pipe_tag, pb.g_cyl(0.0024, 0.0016, 16, r2=0.0012), None, (p[0], p[1], z_top + 0.0008))
    # fins, per tower
    outline = fin_outline(D, W, cfg.get("teeth", 10), cfg.get("amp", 0.004), cfg.get("rear_teeth", 0))
    for tx in cfg["towers"]:
        ol = [(x + tx, y) for (x, y) in outline]
        for k in range(n):
            m.add(fin_tag, pb.g_slab(ol, [], 0.0004, z0 + k * pitch - 0.0002))
        for (lx, ly) in legs:  # pipe collars on the top and bottom fins
            if abs(lx - tx) < D:
                for z in (z0 - 0.0004, zt + 0.0004):
                    m.add(fin_tag, pb.g_ring(0.0030, 0.0036, 0.0008, 16), None, (lx, ly, z))
    # top covers, with the brand insert on the label tower
    zc = zt + 0.0018
    cover_tag = cfg.get("cover_tag", "paint_black")
    film_top = None
    for i, tx in enumerate(cfg["towers"]):
        cover = pb.chamfer2(tx + 0.0005, 0, 2 * D + 0.002, 2 * W + 0.002, 0.006)
        holes = [pb.circle2(lx, ly, 0.0026, 16) for (lx, ly) in legs if abs(lx - tx) < D]
        m.add(cover_tag, pb.g_slab(cover, holes, 0.0030, zc, bevel=0.0005))
        trim = cfg.get("trim_tag", "alu")
        m.add(trim, pb.g_slab(pb.chamfer2(tx + 0.0005, 0, 2 * D - 0.004, 2 * W - 0.004, 0.004),
                              [pb.chamfer2(tx + 0.0005, 0, 2 * D - 0.006, 2 * W - 0.006, 0.0035)], 0.0004, zc + 0.0030))
        if cfg.get("rgb_top"):
            m.add("rgb", pb.g_slab(pb.chamfer2(tx + 0.0005, 0, 2 * D - 0.0075, 2 * W - 0.0075, 0.0032),
                                   [pb.chamfer2(tx + 0.0005, 0, 2 * D - 0.0115, 2 * W - 0.0115, 0.0028)], 0.0005,
                                   zc + 0.0030))
        lw, lh = min(2 * D - 0.008, 0.046), min(2 * D - 0.008, 0.046) / 4
        if i == len(cfg["towers"]) - 1:
            m.add(TEX, pb.g_quad(lw, lh, at.uv("top")), pb.label_frame((0, 0, 1), (0, 1, 0)), (tx + 0.0005, 0.0, zc + 0.00305))
            film_top = (tx + 0.0005, 0.0, zc + 0.0031)
        elif cfg.get("label2", True):
            m.add(TEX, pb.g_quad(lw, lh, at.uv("top2")), pb.label_frame((0, 0, 1), (0, 1, 0)), (tx + 0.0005, 0.0, zc + 0.00305))
    base_film(m, at, TEX)
    # fans on wire clips: each blows +x into the tower behind it
    for i, (tower, size, thick) in enumerate(cfg["fans"]):
        tx = cfg["towers"][tower]
        front = tx - D
        fc = (front - 0.0010 - thick / 2, 0.0, cfg.get("fan_z", (z0 + zt) / 2))
        fa = m.anchor(f"A_FAN_{i}", fc, (size, size, thick), forward=(-1, 0, 0), up=(0, 1, 0),
                      meta=pf.fan_meta("ccw", cfg.get("rpm", 1800), "rgb=1" if cfg.get("rgb_fan") else ""))
        fan(m, fa, size, thick, cfg["fan_scheme"], pid, at.uv("hub"), f"fan{i}", cfg.get("blades", 7),
            rgb=cfg.get("rgb_fan", False), col=col)
        xback = fc[0] + thick / 2
        q = size / 2 - 0.0075
        for sy in (-1, 1):
            pts = [(xback - 0.004, sy * q, fc[2] + q), (xback + 0.002, sy * q, fc[2] + q),
                   (front + 0.0065, sy * (W - 0.0013), fc[2] + min(q, 0.046)),
                   (front + 0.0065, sy * (W - 0.0013), fc[2] - min(q, 0.046)),
                   (xback + 0.002, sy * q, fc[2] - q), (xback - 0.004, sy * q, fc[2] - q)]
            m.add(cfg.get("clip_tag", "steel"), pb.g_sweep(pb.fillet_path(pts, 0.003, 6), 0.0006, 8))
        # the cable: motor -> lower +y strut -> frame corner -> down beside the base to its plug
        mc = (xback - 0.0015, 0.0, fc[2])
        px = -0.034 + 0.018 * i
        plug(m, i, (px, 0.090 + 0.004 * i, 0.006), (0, -1, 0), (0, 0, 1), mc,
             [(xback - 0.0015, q * 0.75, fc[2] - q * 0.75), (xback - 0.0015, q, fc[2] - q),
              (xback - 0.004, W - 0.0015, min(z0 - 0.010, fc[2] - q - 0.004)), (px - 0.002, 0.064 + 0.004 * i, 0.012)],
             target="CPU_FAN" if i == 0 else "SYS_FAN")
        if cfg.get("rgb_fan"):
            plug(m, i, (px + 0.010, 0.092, 0.005), (0, -1, 0), (0, 0, 1), (xback - 0.0025, -0.0, fc[2] - 0.004),
                 [(xback - 0.0025, q * 0.75 - 0.004, fc[2] - q * 0.75), (xback - 0.0035, q - 0.002, fc[2] - q),
                  (xback - 0.006, W - 0.003, min(z0 - 0.012, fc[2] - q - 0.006)), (px + 0.008, 0.066, 0.011)],
                 kind="argb3", target="ARGB", name="ARGB", tag="connector_white", cable_tag="black_plastic")
    if cfg.get("rgb_top"):  # the cap's own ARGB lead, daisy-chained into the fan's lead (looks only)
        m.add("black_plastic", pb.g_sweep(pb.fillet_path([(cfg["towers"][-1] + D - 0.004, W - 0.004, zc + 0.001),
                                                          (cfg["towers"][-1] + D - 0.002, W + 0.0008, zc - 0.006),
                                                          (cfg["towers"][-1] + D - 0.002, W + 0.0008, z0 - 0.004),
                                                          (-0.026, 0.068, 0.011)], 0.004, 6), 0.0009, 8))
    # hitboxes: each stack, each fan, the base
    for i, tx in enumerate(cfg["towers"]):
        m.anchor(f"A_HIT_{i}", (tx, 0, (z0 + zc + 0.003) / 2), (2 * D, 2 * W, zc + 0.003 - z0 + 0.002))
    nh = len(cfg["towers"])
    for i, (tower, size, thick) in enumerate(cfg["fans"]):
        fa = [a for a in m.anchors if a.name == f"A_FAN_{i}"][0]
        p, _, _ = pb.unity_pose(fa)
        m.anchor(f"A_HIT_{nh + i}", tuple(p), (thick, size, size))
    m.anchor(f"A_HIT_{nh + len(cfg['fans'])}", (0, 0, 0.012), (0.075, 0.075, 0.024))
    # the clear film over the label cover's insert (as cooler_tower: an anchor only)
    m.anchor("A_FILM_TOP_0", film_top, (min(2 * D - 0.010, 0.040), 2 * W - 0.010, 0.001), forward=(0, 0, 1),
             up=(0, 1, 0), meta="film=clear,on=top_cover,peel_from=+x")
    cx = sum(cfg["towers"]) / len(cfg["towers"])
    finish(m, pid, [
        dict(yaw=-50, pitch=20), dict(yaw=130, pitch=25), dict(yaw=90, pitch=10),
        dict(yaw=30, pitch=-40, target=(cx, 0, 0.02), dist=0.25), dict(yaw=0, pitch=80, dist=0.45),
        dict(yaw=20, pitch=15, target=(0.0, 0.0, 0.03), dist=0.18),
    ])
    return m


# ---------------------------------------------------------------- tower configs

def tower_cfg(**kw):
    cfg = dict(D=0.025, W=0.0625, fin_z0=0.040, pitch=0.0025, fin_n=45, pipes=4, towers=[0.0],
               fans=[(0, 0.12, 0.025)], fan_scheme=("fan_black", "fan_black"), tex=tex_tower,
               draw_top2=plain_top2, top_bg="#121315", top_fg="#eef1f5", accent="#7fb6e6", hub_bg="#141518",
               hub_fg="#e6ecf2")
    cfg.update(kw)
    return cfg


TOWERS = {
    # Arctic Freezer 34 eSports-style: 157 mm, 4 direct pipes, 120 mm fan, black top and fan
    "cooler_arctiq_34_black": tower_cfg(
        brand="Arctiq", model_line="CHILLER 34 ESPORT", draw_top=arctiq_top, draw_hub=arctiq_hub,
        fin_z0=0.0395, pitch=0.0023, fin_n=50, W=0.062, D=0.0245, teeth=12, amp=0.003,
        cover_tag="black_plastic", trim_tag="paint_black", top_bg="#0e0e10", accent="#9aa0a8", hub_bg="#111113",
        fan_scheme=("fan_black", "fan_black"), rpm=2100),
    "cooler_arctiq_34_white": tower_cfg(
        brand="Arctiq", model_line="CHILLER 34 ESPORT", draw_top=arctiq_top, draw_hub=arctiq_hub,
        fin_z0=0.0395, pitch=0.0023, fin_n=50, W=0.062, D=0.0245, teeth=12, amp=0.003,
        cover_tag="white_plastic", trim_tag="paint_white", top_bg="#ececea", top_fg="#1b1b1d", accent="#6d7178",
        hub_bg="#efefed", hub_fg="#1b1b1d", fan_scheme=("white_plastic", "white_plastic"), clip_tag="steel",
        film_col="#3d8ee6", rpm=2100),
    # DeepCool AK400 WH-style: 155 mm, 4 pipes, jagged fins painted white, white top and fan
    "cooler_glacier_ak400_white": tower_cfg(
        brand="Glacier", model_line="AK400 WH", draw_top=glacier_top, draw_hub=glacier_hub,
        fin_z0=0.0400, pitch=0.0024, fin_n=47, W=0.0625, D=0.0235, teeth=14, amp=0.0035, rear_teeth=14,
        fin_tag="paint_white", cover_tag="paint_white", trim_tag="alu", top_bg="#f0f0ee", top_fg="#202024",
        accent="#b9bcc2", hub_bg="#f2f2f0", hub_fg="#202024", fan_scheme=("white_plastic", "white_plastic"),
        rpm=1850),
    # DeepCool AK620-style: 160 mm, twin towers, 6 pipes, 2 x 120 mm, all black
    "cooler_glacier_ak620_black": tower_cfg(
        brand="Glacier", model_line="AK620", draw_top=glacier_top, draw_hub=glacier_hub,
        towers=[-0.0345, 0.0345], D=0.021, W=0.0645, fin_z0=0.0420, pitch=0.0024, fin_n=48, pipes=6, teeth=12,
        amp=0.003, rear_teeth=12, fans=[(0, 0.12, 0.025), (1, 0.12, 0.025)], fin_tag="alu_dark",
        pipe_tag="steel_dark", base_tag="nickel", cover_tag="paint_black", trim_tag="alu_dark", top_bg="#121214",
        accent="#3a3c42", hub_bg="#111113", rpm=1850, label2=False),
    # Noctua NH-D15-style: 165 mm, twin towers, 6 pipes, 2 x 140 mm beige/brown fans, nickel top fins
    "cooler_noctis_d15": tower_cfg(
        brand="Noctis", model_line="NH-D15", draw_top=noctis_top, draw_top2=noctis_top2, draw_hub=noctis_hub,
        towers=[-0.040, 0.040], D=0.026, W=0.075, fin_z0=0.0470, pitch=0.0025, fin_n=46, pipes=6, teeth=11,
        amp=0.0035, fans=[(0, 0.14, 0.025), (1, 0.14, 0.025)], fan_z=0.0935, cover_tag="nickel", trim_tag="alu",
        top_bg="#b8bbbf", top_fg="#3a2a22", accent="#6b3b2a", hub_bg="#6b3b2a", hub_fg="#e3d2b4",
        col={"frame": "#d6c3a0", "blade": "#6e3a2b"}, fan_scheme=("col:frame", "col:blade"), rpm=1500,
        film_col="#6e3a2b", film_stripe="#7b4636", clip_tag="steel"),
    # chromax.black-style: the same cooler, black coated, black fans
    "cooler_noctis_d15_black": tower_cfg(
        brand="Noctis", model_line="NH-D15", draw_top=noctis_top, draw_top2=noctis_top2, draw_hub=noctis_hub,
        towers=[-0.040, 0.040], D=0.026, W=0.075, fin_z0=0.0470, pitch=0.0025, fin_n=46, pipes=6, teeth=11,
        amp=0.0035, fans=[(0, 0.14, 0.025), (1, 0.14, 0.025)], fan_z=0.0935, fin_tag="paint_black",
        pipe_tag="steel_dark", base_tag="nickel", cap_tag="alu_dark", cover_tag="paint_black", trim_tag="alu_dark",
        top_bg="#121214", top_fg="#d8d8da", accent="#5a5a60", hub_bg="#101012", hub_fg="#d8d8da",
        fan_scheme=("fan_black", "fan_black"), rpm=1500, film_col="#2a2a2e", film_stripe="#34343a",
        clip_tag="paint_black"),
    # Frostpeak Tower 120 RGB: the house tower with an ARGB fan (clear blades) and an ARGB ring in the top cap
    "cooler_frostpeak_120_rgb": tower_cfg(
        brand="Frostpeak", model_line="TOWER 120 RGB", draw_top=frostpeak_top, draw_hub=frostpeak_hub,
        fin_z0=0.0400, pitch=0.0025, fin_n=46, fan_scheme=("fan_black", "white_plastic"), rgb_fan=True,
        rgb_top=True, cover_tag="paint_black", rpm=1800),
}


def build_low_profile():
    """Noctua NH-L9-style: 37 mm tall. A nickel base block, two flat U heat pipes through a stack of 9 horizontal
    fins (95 x 95 mm), a 92 x 14 mm fan on top blowing down. The cooler_tower screws keep their exact poses: they sit
    in wells cut through the fins, on a flat mounting plate (the X bracket's job) under the stack."""
    pid = "cooler_noctis_l9"
    cfg = tower_cfg(brand="Noctis", model_line="NH-L9", draw_top=noctis_top, draw_top2=noctis_top2,
                    draw_hub=noctis_hub, top_bg="#b8bbbf", top_fg="#3a2a22", accent="#6b3b2a", hub_bg="#6b3b2a",
                    hub_fg="#e3d2b4", film_col="#6e3a2b", film_stripe="#7b4636")
    at = tex_tower(pid, cfg)
    col = tex_col(pid, {"frame": "#d6c3a0", "blade": "#6e3a2b"})
    m = pb.Model(pid)
    TEX = "tex_" + pid
    # base block with the pipe grooves capped, and the flat mounting plate
    bc.box(m, "nickel", (-0.019, -0.020, 0.0), (0.019, 0.020, 0.0042), bevel=0.0004)
    bc.box(m, "copper", (-0.0165, -0.0175, 0.0042), (0.0165, 0.0175, 0.0075), bevel=0.0003)
    plate = pb.rrect2(0, 0, 0.082, 0.082, 0.008, 4)
    m.add("steel", pb.g_slab(plate, [pb.circle2(x, y, 0.0018, 16) for (x, y) in HOLES]
                             + [pb.rrect2(0, 0, 0.032, 0.032, 0.003, 3)], 0.0010, 0.0075, bevel=0.0002))
    # two flat U pipes: across the base along y, then out through the fins
    for xb in (-0.0085, 0.0085):
        pts = [(xb + 0.006 * (1 if xb > 0 else -1), -0.046, 0.0148), (xb, -0.024, 0.0148), (xb, -0.015, 0.0045),
               (xb, 0.015, 0.0045), (xb, 0.024, 0.0148), (xb + 0.006 * (1 if xb > 0 else -1), 0.046, 0.0148)]
        m.add("nickel", pb.g_sweep(pb.fillet_path(pts, 0.006, 8), 0.0026, 16))
        for sy in (-1, 1):
            m.add("nickel", pb.xf(pb.g_cyl(0.0022, 0.0014, 16, r2=0.0011), pb.rot("x", sy * math.pi / 2)), None,
                  (xb + 0.006 * (1 if xb > 0 else -1), sy * 0.0472, 0.0148))
    # nine horizontal fins with screw wells and a cut-out round the base
    S = 0.095
    fin = pb.rrect2(0, 0, S, S, 0.004, 3)
    wells = [pb.circle2(x, y, 0.0048, 20) for (x, y) in HOLES]
    z0, pitch, n = 0.0090, 0.0015, 9
    for k in range(n):
        hole = [pb.rrect2(0, 0, 0.034, 0.036, 0.003, 3)] if k < 3 else []
        m.add("alu", pb.g_slab(fin, wells + hole, 0.0004, z0 + k * pitch - 0.0002))
    zt = z0 + (n - 1) * pitch
    # seat collars in the wells (the springs rest on them) and the screws
    for i, (x, y) in enumerate(HOLES):
        m.add("steel", pb.g_ring(0.0019, 0.0040, 0.0066, 20), None, (x, y, 0.0085 + 0.0033))
        bc.spring_screw(m, i, x, y, 0.0141, 0.0196, head_r=0.0036, spring_r=0.0030)
    base_film(m, at, TEX)
    # 92 x 14 mm fan on top, blowing down (intake +z), held by two wire clips on the -+x sides
    fz = zt + 0.0004 + 0.0012 + 0.007
    fa = m.anchor("A_FAN_0", (0, 0, fz), (0.092, 0.092, 0.014), forward=(0, 0, 1), up=(0, 1, 0),
                  meta=pf.fan_meta("ccw", 2500))
    fan(m, fa, 0.092, 0.014, ("col:frame", "col:blade"), pid, at.uv("hub"), "fan0", col=col)
    for sx in (-1, 1):
        q = 0.0412
        pts = [(sx * q, -q, fz + 0.0062), (sx * q, -q, fz + 0.0072), (sx * 0.0476, -0.030, zt - 0.003),
               (sx * 0.0476, 0.030, zt - 0.003), (sx * q, q, fz + 0.0072), (sx * q, q, fz + 0.0062)]
        m.add("steel", pb.g_sweep(pb.fillet_path(pts, 0.002, 5), 0.0006, 8))
    plug(m, 0, (-0.034, 0.090, 0.006), (0, -1, 0), (0, 0, 1), (-0.040, 0.040, fz - 0.007),
         [(-0.044, 0.046, fz - 0.006), (-0.044, 0.050, z0), (-0.036, 0.064, 0.012)])
    m.anchor("A_HIT_0", (0, 0, (z0 + zt) / 2), (S, S, zt - z0 + 0.002))
    m.anchor("A_HIT_1", (0, 0, fz), (0.092, 0.092, 0.014))
    m.anchor("A_HIT_2", (0, 0, 0.004), (0.040, 0.040, 0.008))
    # no top cover: the clear film sits on the fan's hub sticker
    m.anchor("A_FILM_TOP_0", (0, 0, fz + 0.0075), (0.030, 0.030, 0.001), forward=(0, 0, 1), up=(0, 1, 0),
             meta="film=clear,on=fan_hub,peel_from=+x")
    finish(m, pid, [
        dict(yaw=25, pitch=35), dict(yaw=-40, pitch=-30), dict(yaw=75, pitch=12),
        dict(yaw=160, pitch=25, target=(0, 0, 0.0), dist=0.22), dict(yaw=0, pitch=0, dist=0.3),
        dict(yaw=60, pitch=40, target=(0.033, 0.033, 0.015), dist=0.09),
    ])
    return m


def tex_tiron_stock(pid):
    at = pb.Atlas(1024, 512)
    at.add("hub", 0, 0, 512, 512)
    at.add("ring", 512, 0, 512, 128)
    cv = pb.Canvas(1024, 512, bg="#0d0d0e")
    cx, cy = 256, 256
    cv.circle(cx, cy, 252, "#101114")
    cv.ring(cx, cy, 214, 226, "#0a6fc2")
    cv.text("TIRON", cx, cy - 18, 70, "#eef2f6", "arialb", "center", "center", spacing=1.15)
    cv.text("STOCK COOLER", cx, cy + 62, 24, "#7fb3e0", "arialb", "center", "center", spacing=1.8)
    cv.rect(512, 0, 512, 128, "#111214")
    cv.text("TIRON  RM1", 768, 64, 54, "#cfd3d8", "arialb", "center", "center", spacing=1.4)
    cv.render(pid)
    return at


def build_tiron_stock():
    """Intel Laminar RM1-style stock cooler (socket L17) on the cooler_stock contract: a round radial aluminium
    extrusion round a copper core, a black frameless fan in a round black shroud ring on four struts, a black
    mounting ring with four arms to the spring screws, pre-applied paste. Every anchor is cooler_stock's pose."""
    pid = "cooler_tiron_stock"
    at = tex_tiron_stock(pid)
    m = pb.Model(pid)
    TEX = "tex_" + pid
    # copper core and the aluminium hub
    m.add("copper", pb.g_lathe([(0.0, 0.0), (0.0160, 0.0), (0.0160, 0.0055), (0.0140, 0.0065), (0.0140, 0.0340),
                                (0.0, 0.0340)], 64))
    m.add("alu", pb.g_lathe([(0.0160, 0.0004), (0.0185, 0.0004), (0.0185, 0.0350), (0.0140, 0.0350),
                             (0.0140, 0.0065), (0.0160, 0.0055), (0.0160, 0.0004)], 64))
    # 56 swept radial fins, cut back at the bottom outside the mounting ring
    n = 56
    prof = [(0.0180, 0.0012), (0.0300, 0.0012), (0.0330, 0.0060), (0.0405, 0.0075), (0.0405, 0.0350),
            (0.0180, 0.0350)]
    for k in range(n):
        th0 = pb.TAU * k / n
        verts, faces, uvs, fl = pb.g_slab(prof, [], 0.0007, -0.00035)
        out = []
        for p in verts:
            rr, zz, w = p.x, p.y, p.z
            th = th0 + 9.0 * (rr - 0.0180)
            out.append(V((rr * math.cos(th) + w * math.sin(th), rr * math.sin(th) - w * math.cos(th), zz)))
        m.add("alu", (out, faces, None, fl))
    # the fan shroud: a round ring over the fins with four struts down to the mounting ring
    sh = m.mb("black_plastic")
    sh.add(pb.g_lathe([(0.0402, 0.0345), (0.0470, 0.0345), (0.0470, 0.0505), (0.0458, 0.0525), (0.0412, 0.0525),
                       (0.0402, 0.0510), (0.0402, 0.0345)], 96))
    sh.add(pb.g_lathe([(0.0402, 0.0355), (0.0418, 0.0355), (0.0418, 0.0365), (0.0402, 0.0365)], 96))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        d = V((math.cos(a), math.sin(a), 0))
        sh.add(pb.xf(pb.g_box((0.0050, 0.0040, 0.0160)), pb.rot("z", a), d * 0.0445 + V((0, 0, 0.0270))))
    # mounting ring with four arms ending in the screw wells
    ring = pb.circle2(0, 0, 0.0450, 96)
    sh.add(pb.g_slab(ring, [pb.circle2(0, 0, 0.0412, 96)], 0.0030, 0.0170, bevel=0.0004))
    for (x, y) in HOLES:
        sh.add(pb.g_ring(0.0042, 0.0058, 0.0090, 24), None, (x, y, 0.0200 - 0.0045))
        sh.add(pb.g_ring(0.0017, 0.0058, 0.0012, 24), None, (x, y, 0.0200 - 0.0006))  # spring seat
        d = V((x, y, 0)).normalized()
        sh.add(pb.xf(pb.g_box((0.0060, 0.0070, 0.0030)), pb.rot("z", math.atan2(y, x)), d * 0.0420 + V((0, 0, 0.0185))))
    # the brand band round the shroud (texture strip on the +x face)
    m.add(TEX, pb.g_quad(0.030, 0.0075, at.uv("ring")), pb.label_frame((1, 0, 0), (0, 0, 1)), (0.04705, 0.0, 0.0428))
    # fan: frameless, 9 blades, black
    fz = 0.0445
    fa = m.anchor("A_FAN_0", (0, 0, fz), (0.078, 0.078, 0.014), forward=(0, 0, 1), up=(0, 1, 0),
                  meta=pf.fan_meta("ccw", 2800))
    sf = pf.make_fan(fa, diameter=0.078, thickness=0.014, blades=9, frame=False, sticker=pid, sticker_uv=at.uv("hub"),
                     struts=4, name="stockfan", cov=(0.78, 1.0), sweep=0.5, return_all=True)
    hub_film(m, fa, sf["sticker"])
    for i, (x, y) in enumerate(HOLES):
        bc.spring_screw(m, i, x, y, 0.0200, 0.0262)
    pa = m.anchor("A_PASTE_PRE_0", (0, 0, 0), (0.030, 0.030, 0.004), forward=(0, 0, -1), up=(0, 1, 0),
                  meta="kind=preapplied,area=0.028x0.028")
    # Intel-style: three stripes of paste rather than a square
    pp = m.piece(pa, "paste", "paste")
    for k in (-1, 0, 1):
        pp.add(pb.g_slab(pb.rrect2(0, k * 0.0095, 0.026, 0.0065, 0.002, 3), [], 0.00018, -0.00018, bevel=0.00006))
    plug(m, 0, (0.010, 0.080, 0.004), (0, -1, 0), (0, 0, 1), (0.0, 0.006, fz - 0.0065),
         [(0.0, 0.040, fz - 0.0065), (0.0, 0.046, fz - 0.008), (0.002, 0.050, 0.030), (0.006, 0.056, 0.016),
          (0.008, 0.062, 0.006)])
    m.anchor("A_HIT_0", (0, 0, 0.027), (0.100, 0.100, 0.054))
    m.anchor("A_HIT_1", (0, 0, 0.003), (0.036, 0.036, 0.006))
    finish(m, pid, [
        dict(yaw=30, pitch=45), dict(yaw=200, pitch=20), dict(yaw=20, pitch=-60),
        dict(yaw=0, pitch=88, dist=0.25), dict(yaw=60, pitch=25, target=(0.033, 0.033, 0.03), dist=0.09),
        dict(yaw=160, pitch=-15, target=(0.0, 0.0, 0.01), dist=0.16),
    ])
    return m


# ====================================================================== AIO liquid coolers

def adopt(objs, anchor):
    """Turns static objects (a fan's frame, made under the root) into moving pieces of an anchor: pivot on the
    anchor, named '<name>@<anchor>#<tag>'."""
    mw = anchor.matrix_world.copy()
    for o in objs:
        base, tag = o.name.split("#", 1)
        o.data.transform(mw.inverted() @ o.matrix_world)
        o.matrix_world = mw
        c.attach(o, anchor, base, tag)


def resample(path, n):
    """Splits a polyline into n parts of equal length (lists of points, ends shared)."""
    P = [V(p) for p in path]
    L = [0.0]
    for a, b in zip(P, P[1:]):
        L.append(L[-1] + (b - a).length)
    total = L[-1]

    def at(s):
        for i in range(1, len(P)):
            if L[i] >= s:
                t = (s - L[i - 1]) / max(1e-12, L[i] - L[i - 1])
                return P[i - 1].lerp(P[i], t)
        return P[-1]

    parts = []
    for k in range(n):
        s0, s1 = total * k / n, total * (k + 1) / n
        pts = [at(s0)] + [P[i] for i in range(len(P)) if s0 < L[i] < s1] + [at(s1)]
        parts.append(pts)
    return parts, total


def tex_aio(pid, cfg):
    at = pb.Atlas(2048, 1024)
    at.add("cap", 0, 0, 512, 512)
    at.add("hub", 512, 0, 512, 512)
    at.add("film", 1024, 0, 512, 512)
    at.add("tab", 1536, 0, 256, 128)
    at.add("blue", 1792, 0, 64, 64)
    at.add("rad", 0, 512, 1024, 128)
    at.add("lcd", 1024, 512, 512, 512)
    cv = pb.Canvas(2048, 1024, bg="#0d0d0e")
    cfg["draw_cap"](cv, 256, 256, cfg)
    cfg["draw_hub"](cv, 768, 256, cfg)
    fx, fy = 1024, 0
    cv.rect(fx, fy, 512, 512, "#3d8ee6")
    for k in range(9):
        cv.line(fx, fy + 40 + k * 60, fx + 512, fy - 60 + k * 60, 14, "#4a98ec")
    cv.text("REMOVE", fx + 256, fy + 180, 64, "#ffffff", "arialb", "center", "center")
    cv.text("BEFORE USE", fx + 256, fy + 270, 52, "#ffffff", "arialb", "center", "center")
    cv.text(cfg["brand"].upper(), fx + 256, fy + 380, 30, "#e8f2ff", "arialb", "center", "center", spacing=1.3)
    cv.rect(1536, 0, 256, 128, "#3d8ee6")
    cv.text("PEEL >", 1536 + 128, 64, 40, "#ffffff", "arialb", "center", "center")
    cv.rect(1792, 0, 64, 64, "#3d8ee6")
    cv.rect(0, 512, 1024, 128, cfg["rad_bg"])
    cv.text(cfg["rad_text"], 512, 576, 58, cfg["rad_fg"], "arialb", "center", "center", spacing=1.4, maxw=900)
    # the LCD's idle screen (Corvex): coolant temperature on a dark round face
    lx, ly = 1280, 768
    cv.rect(1024, 512, 512, 512, "#05070a")
    cv.circle(lx, ly, 250, "#0b1220")
    cv.ring(lx, ly, 210, 236, "#1d2a44")
    for k in range(28):  # a temperature arc
        a = math.radians(140 + k * 9.3)
        cv.line(lx + 200 * math.cos(a), ly + 200 * math.sin(a), lx + 236 * math.cos(a), ly + 236 * math.sin(a), 9,
                "#3ec6ff" if k < 12 else "#26314a")
    cv.text("32", lx - 10, ly - 10, 150, "#f2f6fa", "arialb", "center", "center")
    cv.text("C", lx + 112, ly - 64, 40, "#9fb4cc", "arialb", "center", "center")
    cv.circle(lx + 84, ly - 84, 9, "#9fb4cc")
    cv.text("COOLANT", lx, ly + 110, 30, "#9fb4cc", "arialb", "center", "center", spacing=1.6)
    cv.text("CORVEX", lx, ly + 170, 26, "#5c6b80", "arialb", "center", "center", spacing=1.8)
    cv.render(pid)
    return at


def arctiq_cap(cv, x, y, cfg):
    cv.rect(x - 256, y - 256, 512, 512, "#111113")
    cx, cy = x, y - 60
    for k in range(3):
        a = k * math.pi / 3
        cv.line(cx - 70 * math.cos(a), cy - 70 * math.sin(a), cx + 70 * math.cos(a), cy + 70 * math.sin(a), 16, "#c9ccd2")
    cv.circle(cx, cy, 20, "#111113")
    cv.text("ARCTIQ", x, y + 70, 64, "#eef0f3", "arialb", "center", "center", spacing=1.25)
    cv.text("LIQUID CHILLER II", x, y + 140, 24, "#8c9098", "arialb", "center", "center", spacing=1.6, maxw=420)


def corvex_cap(cv, x, y, cfg):
    cv.rect(x - 256, y - 256, 512, 512, "#f1f1ef")
    cv.text("CORVEX", x, y, 64, "#202024", "arialb", "center", "center", spacing=1.5)


def glacier_cap(cv, x, y, cfg):
    cv.rect(x - 256, y - 256, 512, 512, "#07080a")
    for k in range(9):  # the 'infinity mirror' tunnel
        s = 230 - k * 22
        cv.frame_rect(x - s, y - s, 2 * s, 2 * s, 5, "#3a3f4a" if k % 2 else "#23262d", r=30)
    cv.text("GLACIER", x, y, 50, "#f0f2f5", "arialb", "center", "center", spacing=1.4)


def corvex_hub(cv, x, y, cfg):
    hub_ring(cv, x, y, "#f2f2f0", "#c9c9c6", "CORVEX", "#202024", "arialb", size=44)


def build_aio(pid, cfg):
    """An AIO: the pump block on the cooler_tower base contract, two segmented tubes (moving pieces of A_TUBE_0/1),
    the radiator as the moving piece A_RAD_0 with its fans, screw holes, ports and fan plug (see the report)."""
    at = tex_aio(pid, cfg)
    m = pb.Model(pid)
    TEX = "tex_" + pid
    body_t, cap_t, tube_t = cfg["body_tag"], cfg["cap_tag"], cfg["tube_tag"]
    # ------------------------------------------------------------ pump block
    m.add("copper", pb.g_slab(pb.rrect2(0, 0, 0.054, 0.054, 0.004, 3), [], 0.0030, 0.0, bevel=0.0003))
    B, H = cfg["pump_w"], cfg["pump_h"]
    m.add(body_t, pb.g_slab(pb.rrect2(0, 0, B, B, cfg.get("pump_r", 0.010), 6), [], H - 0.006, 0.0030, bevel=0.0012))
    # the X bracket and screws exactly as cooler_tower
    xb_poly = []
    for (hx, hy) in [(0.033, 0.033), (-0.033, 0.033), (-0.033, -0.033), (0.033, -0.033)]:
        d = V((hx, hy, 0)).normalized()
        p = V((-d.y, d.x, 0))
        tip = V((hx, hy, 0)) + d * 0.004
        xb_poly += [tuple(tip - p * 0.0045)[:2], tuple(tip + p * 0.0045)[:2]]
        nxt = math.atan2(hy, hx) + math.pi / 4
        xb_poly.append((math.cos(nxt) * 0.0120, math.sin(nxt) * 0.0120))
    m.add(cfg.get("bracket_tag", "steel_dark"), pb.g_slab(xb_poly, [pb.circle2(x, y, 0.0018, 16) for (x, y) in HOLES],
                                                          0.0015, 0.0126, bevel=0.0003))
    for i, (x, y) in enumerate(HOLES):
        bc.spring_screw(m, i, x, y, 0.0141, 0.0196, head_r=0.0036, spring_r=0.0030)
    base_film(m, at, TEX)
    zt = H - 0.003  # body top
    style = cfg["pump"]
    film_size = (0.040, 0.040)
    if style == "arctiq":  # flat square cap with the brand
        m.add(cap_t, pb.g_slab(pb.rrect2(0, 0, B - 0.004, B - 0.004, 0.008, 6), [], 0.003, zt, bevel=0.0008))
        m.add(TEX, pb.g_quad(0.042, 0.042, at.uv("cap")), pb.label_frame((0, 0, 1), (0, 1, 0)), (0, 0, zt + 0.00305))
        top = zt + 0.003
    elif style == "corvex":  # a round LCD in an RGB ring on a white body
        m.add(cap_t, pb.g_lathe([(0.0, zt), (0.029, zt), (0.029, zt + 0.006), (0.0275, zt + 0.0075), (0.0, zt + 0.0075)], 64))
        m.add("rgb", pb.g_ring(0.0262, 0.0278, 0.0012, 64), None, (0, 0, zt + 0.0078))
        m.add("glass", pb.g_cyl(0.0258, 0.0010, 64), None, (0, 0, zt + 0.0079))
        m.add(TEX, pb.g_disc(0.0240, 64, at.uv("lcd")), pb.label_frame((0, 0, 1), (0, 1, 0)), (0, 0, zt + 0.00845))
        m.anchor("A_SCREEN_0", (0, 0, zt + 0.0085), (0.048, 0.048, 0.002), forward=(0, 0, 1), up=(0, 1, 0),
                 meta="kind=lcd,shape=round,res=480x480,diameter=0.048")
        m.add(TEX, pb.g_quad(0.030, 0.0075, at.uv("rad")), pb.label_frame((1, 0, 0), (0, 0, 1)), (B / 2 + 0.00005, 0, zt * 0.5))
        film_size = (0.050, 0.050)
        top = zt + 0.0085
    else:  # glacier: square mirror cap with an ARGB frame
        m.add(cap_t, pb.g_slab(pb.rrect2(0, 0, B - 0.002, B - 0.002, 0.009, 6), [], 0.004, zt, bevel=0.0006))
        m.add("rgb", pb.g_slab(pb.rrect2(0, 0, B - 0.006, B - 0.006, 0.007, 6),
                               [pb.rrect2(0, 0, B - 0.011, B - 0.011, 0.006, 6)], 0.0010, zt + 0.0040))
        m.add("glass", pb.g_slab(pb.rrect2(0, 0, B - 0.011, B - 0.011, 0.006, 6), [], 0.0006, zt + 0.0040))
        m.add(TEX, pb.g_quad(B - 0.013, B - 0.013, at.uv("cap")), pb.label_frame((0, 0, 1), (0, 1, 0)), (0, 0, zt + 0.0047))
        top = zt + 0.0050
    m.anchor("A_FILM_TOP_0", (0, 0, top + 0.0001), (film_size[0], film_size[1], 0.001), forward=(0, 0, 1),
             up=(0, 1, 0), meta="film=clear,on=pump_cap,peel_from=+x")
    # the unboxing film on the pump cap / LCD (the catalogue's A_FILM_PUMP_0; the same film as A_FILM_TOP_0)
    m.anchor("A_FILM_PUMP_0", (0, 0, top + 0.0001), (film_size[0], film_size[1], 0.0001), forward=(0, 0, 1),
             up=(0, 1, 0), meta=f"film=clear,on={'lcd' if style == 'corvex' else 'pump_cap'},peel=+x,tab=+x+y,"
             "same_as=A_FILM_TOP_0")
    # swivel fittings on the -x side
    fz = 0.020 + 0.006
    fittings = []
    for sy in (1, -1):
        y = sy * 0.010
        m.add(cfg.get("fitting_tag", body_t), pb.xf(pb.g_cyl(0.0060, 0.010, 24), pb.rot("y", math.pi / 2)), None, (-B / 2 - 0.004, y, fz))
        m.add("steel_dark", pb.xf(pb.g_cyl(0.0064, 0.0025, 24), pb.rot("y", math.pi / 2)), None, (-B / 2 - 0.0095, y, fz))
        fittings.append(V((-B / 2 - 0.011, y, fz)))
    # pump cable (and ARGB lead) to the plugs, from the +y side of the body
    plug(m, 0, (-0.034, 0.090, 0.006), (0, -1, 0), (0, 0, 1), (0.010, B / 2 - 0.002, 0.012),
         [(0.010, B / 2 + 0.008, 0.010), (-0.020, 0.064, 0.010)], target="AIO_PUMP")
    if cfg.get("rgb"):
        plug(m, 0, (-0.016, 0.094, 0.005), (0, -1, 0), (0, 0, 1), (0.018, B / 2 - 0.002, 0.012),
             [(0.018, B / 2 + 0.010, 0.010), (-0.004, 0.068, 0.010)], kind="argb3", target="ARGB", name="ARGB",
             tag="connector_white")
    m.anchor("A_HIT_0", (0, 0, top / 2), (B, B, top))
    # ------------------------------------------------------------ radiator (moving piece A_RAD_0)
    n, T = cfg["fans"], cfg["rad_t"]
    L = 0.120 * n + 0.004  # core length
    TW = 0.022  # end tank length
    W = 0.121
    ry = -0.20
    rc = V((0.0, ry, T / 2))
    ra = m.anchor("A_RAD_0", tuple(rc), (L + 2 * TW, W, T), forward=(0, 0, 1), up=(0, 1, 0),
                  meta=f"fans={n},size=120,length={L + 2 * TW:.3f},thickness={T:.3f},fan_side=+z,ports=-x")
    rp = lambda tag: m.piece(ra, tag, "rad")  # noqa: E731
    rad_t, tank_t = cfg["rad_tag"], cfg["tank_tag"]
    # core: dark fin block with the flat water tubes showing as strips on both faces
    rp("mesh_black").add(pb.g_box((L, 0.101, T - 0.001)), None, rc)
    for k in range(13):
        y = ry + (k - 6) * 0.0078
        rp(rad_t).add(pb.g_box((L, 0.0016, T - 0.0004)), None, (0, y, T / 2))
    for sy in (1, -1):  # side rails (C channels) with the screw-hole rows
        rp(rad_t).add(pb.g_box((L + 0.002, 0.010, T), 0.0005), None, (0, ry + sy * 0.0555, T / 2))
    holes = []
    for k in range(n):
        xc = (k - (n - 1) / 2) * 0.120
        for sx in (-1, 1):
            for sy in (-1, 1):
                for z, s in ((T + 0.00005, 1), (-0.00005, -1)):
                    rp("steel_dark").add(pb.g_cyl(0.0019, 0.0002, 12), None, (xc + sx * 0.0525, ry + sy * 0.0525, z))
                holes.append((xc + sx * 0.0525, ry + sy * 0.0525))
    for sx in (-1, 1):  # end tanks
        rp(tank_t).add(pb.g_box((TW, W, T + 0.002), 0.0015), None, (sx * (L / 2 + TW / 2), ry, T / 2))
    m.piece(ra, TEX, "radlabel").add(pb.g_quad(0.090, 0.0113, at.uv("rad")), pb.label_frame((0, 1, 0), (0, 0, 1)),
                                    (0.0, ry + W / 2 - 0.0004 + 0.0005, T / 2))
    # ports on the -x tank, pointing -x
    ports = []
    for k, y in enumerate((ry + W / 2 - 0.016, ry + W / 2 - 0.036)):
        x0 = -(L / 2 + TW)
        rp(tank_t).add(pb.xf(pb.g_cyl(0.0060, 0.008, 24), pb.rot("y", math.pi / 2)), None, (x0 - 0.004, y, T / 2))
        rp("steel_dark").add(pb.xf(pb.g_cyl(0.0064, 0.0025, 24), pb.rot("y", math.pi / 2)), None, (x0 - 0.0085, y, T / 2))
        pa = m.anchor(f"A_PORT_RAD_{k}", (x0 - 0.010, y, T / 2), (0.014, 0.014, 0.012), forward=(-1, 0, 0),
                      up=(0, 0, 1), meta=f"tube=A_TUBE_{k}", parent=ra)
        ports.append(V((x0 - 0.010, y, T / 2)))
    for i, (x, y) in enumerate(holes):
        m.anchor(f"A_HOLE_RAD_{i}", (x, y, 0.0), (0.006, 0.006, 0.004), forward=(0, 0, -1), up=(0, 1, 0),
                 meta=f"thread=6-32,face=case,fan={i // 4}", parent=ra)
    # fans on the +z face, their corner screws, a daisy-chained cable to one plug
    for k in range(n):
        xc = (k - (n - 1) / 2) * 0.120
        fa = m.anchor(f"A_RAD_FAN_{k}", (xc, ry, T + 0.0125), (0.12, 0.12, 0.025), forward=(0, 0, 1), up=(0, 1, 0),
                      meta=pf.fan_meta("ccw", cfg["rpm"], "rgb=1" if cfg.get("rgb") else ""), parent=ra)
        r = fan(m, fa, 0.12, 0.025, cfg["fan_scheme"], pid, at.uv("hub"), f"radfan{k}", rgb=cfg.get("rgb", False))
        adopt(r["static"], ra)
        for sx in (-1, 1):
            for sy in (-1, 1):
                rp("steel_dark").add(pb.g_screw_head(0.0028, 0.0016, "ph", 16), None,
                                     (xc + sx * 0.0525, ry + sy * 0.0525, T + 0.025))
    cab = [V(((k - (n - 1) / 2) * 0.120 - 0.052, ry - 0.0585, T + 0.004)) for k in range(n)]
    pts = list(reversed(cab)) + [V((-(L / 2) - 0.004, ry - 0.0615, T * 0.5)), V((-(L / 2) - 0.026, ry - 0.075, 0.004))]
    rp("black_plastic").add(pb.g_sweep(pb.fillet_path(pts, 0.006, 6), 0.0013, 10))
    pl_face = V((-(L / 2) - 0.034, ry - 0.085, 0.004))
    pla = m.anchor("A_PLUG_RADFAN_0", tuple(pl_face), (0.012, 0.008, 0.016), forward=(-1, 0, 0), up=(0, 0, 1),
                   meta=f"kind=fan4,frame=plug,target=CPU_OPT,chain={n}", parent=ra)
    M = pb.frame((-1, 0, 0), (0, 0, 1))
    pl = m.piece(pla, "connector_black", "plug")
    pl.add(pb.g_slab(pb.rrect2(0, 0, 0.0101, 0.0058, 0.0005, 2),
                     [pb.rect2((k - 1.5) * 0.00254, -0.0004, 0.0012, 0.0012) for k in range(4)], 0.0025, 0.0), M, pl_face)
    pl.add(pb.g_box((0.0101, 0.0058, 0.0110), 0.0003), M, pl_face + M @ V((0, 0, 0.0080)))
    rp("black_plastic").add(pb.g_sweep(pb.fillet_path([pts[-1], pl_face + M @ V((0, 0, 0.020)),
                                                       pl_face + M @ V((0, 0, 0.012))], 0.004, 4), 0.0013, 10))
    m.anchor("A_HIT_1", tuple(rc + V((0, 0, 0.0125))), (L + 2 * TW, W, T + 0.025), parent=ra)
    # ------------------------------------------------------------ tubes: segmented, moving pieces at the pump
    seg_n = 8
    lengths = []
    for k, (f, p) in enumerate(zip(fittings, ports)):
        path = [f, f + V((-0.035, 0, 0)), V((f.x - 0.075, f.y - 0.045, 0.024)),
                V((p.x - 0.060, p.y + 0.050, T / 2)), V((p.x - 0.030, p.y, T / 2)), p]
        path = pb.fillet_path(path, 0.030, 8)
        ta = m.anchor(f"A_TUBE_{k}", tuple(f), (0.014, 0.014, 0.014), forward=(-1, 0, 0), up=(0, 0, 1),
                      meta=f"to=A_PORT_RAD_{k}@A_RAD_0,radius=0.0055,segments={seg_n},min_bend=0.035,max_length={cfg['tube_len']}")
        parts, total = resample(path, seg_n)
        lengths.append(total)
        tb = m.piece(ta, tube_t, "tube")
        for i, part in enumerate(parts):
            tb.add(pb.g_sweep(part, 0.0055, 14))
            if i:
                d = (part[1] - part[0]).normalized()
                tb.add(pb.g_ring(0.0054, 0.0060, 0.0025, 18), pb.frame(d, (0, 0, 1) if abs(d.z) < 0.9 else (0, 1, 0)), part[0])
        ta["meta"] = ta["meta"] + f",length={total:.3f}"
    extra = "   TUBES " + ", ".join(f"A_TUBE_{k} length {l:.3f} m" for k, l in enumerate(lengths))
    finish(m, pid, [
        dict(yaw=-30, pitch=-50, dist=0.75), dict(yaw=30, pitch=30, target=(0, 0, 0.03), dist=0.25),
        dict(yaw=200, pitch=-60, dist=0.75), dict(yaw=-60, pitch=-25, target=(-0.1, -0.1, 0.02), dist=0.4),
        dict(yaw=0, pitch=0, target=(0, 0, 0.03), dist=0.22),
        dict(yaw=180, pitch=-10, target=(0, ry, 0.0), dist=0.6),
    ], extra)
    return m


AIOS = {
    # Arctic Liquid Freezer II 240-style: 38 mm thick radiator, black, sleeved tubes, no RGB
    "cooler_arctiq_lc240": dict(
        tube_len=0.45,
        brand="Arctiq", pump="arctiq", draw_cap=arctiq_cap, draw_hub=arctiq_hub, fans=2, rad_t=0.038,
        pump_w=0.070, pump_h=0.053, pump_r=0.012, body_tag="black_plastic", cap_tag="paint_black",
        tube_tag="rubber", rad_tag="paint_black", tank_tag="black_plastic", fan_scheme=("fan_black", "fan_black"),
        rpm=1800, rad_bg="#111113", rad_fg="#e8eaee", rad_text="ARCTIQ  LIQUID CHILLER II 240",
        hub_bg="#111113", hub_fg="#e6ecf2", accent="#9aa0a8"),
    # Corsair H150i Elite LCD-style, white: 360 mm, RGB fans, round LCD pump cap
    "cooler_corvex_h150i_white": dict(
        tube_len=0.40,
        brand="Corvex", pump="corvex", draw_cap=corvex_cap, draw_hub=corvex_hub, fans=3, rad_t=0.027,
        pump_w=0.064, pump_h=0.048, pump_r=0.016, body_tag="white_plastic", cap_tag="white_plastic",
        tube_tag="white_plastic", rad_tag="paint_white", tank_tag="white_plastic", fitting_tag="white_plastic",
        bracket_tag="steel", fan_scheme=("white_plastic", "white_plastic"), rgb=True, rpm=2100,
        rad_bg="#f0f0ee", rad_fg="#1f1f22", rad_text="CORVEX  H150i  VISTA LCD"),
    # DeepCool LS720-style: 360 mm, black, ARGB fans and an ARGB mirror cap
    "cooler_glacier_ls720": dict(
        tube_len=0.41,
        brand="Glacier", pump="glacier", draw_cap=glacier_cap, draw_hub=glacier_hub, fans=3, rad_t=0.027,
        pump_w=0.068, pump_h=0.050, pump_r=0.012, body_tag="black_plastic", cap_tag="paint_black",
        tube_tag="rubber", rad_tag="paint_black", tank_tag="black_plastic", fan_scheme=("fan_black", "white_plastic"),
        rgb=True, rpm=2250, rad_bg="#111113", rad_fg="#e8eaee", rad_text="GLACIER  LS720",
        hub_bg="#111113", hub_fg="#e6ecf2", accent="#7fb6e6"),
}

# ====================================================================== server heatsinks

SPV_SCREWS = [(sx * 0.0385, y) for sx in (1, -1) for y in (0.051, 0.0, -0.051)]  # 6 x Torx T20 (socket SP-V)
L46_SCREWS = [(sx * 0.0345, sy * 0.047) for sx in (1, -1) for sy in (1, -1)]  # 4 x Torx T30 (socket L46)


def tex_server(pid, title, sub):
    at = pb.Atlas(1024, 512)
    at.add("label", 0, 0, 1024, 256)
    at.add("film", 0, 256, 512, 256)
    at.add("blue", 512, 256, 64, 64)
    cv = pb.Canvas(1024, 512, bg="#e9e9e6")
    cv.rect(0, 0, 1024, 256, "#ececea")
    cv.text(title, 40, 70, 54, "#16171a", "arialb", "left", "center", maxw=940)
    cv.text(sub, 40, 140, 30, "#3c3f45", "arialb", "left", "center", maxw=940)
    cv.text("TORQUE IN SEQUENCE  1 > 2 > 3 ...  12 KGF-CM", 40, 200, 24, "#a01818", "arialb", "left", "center", maxw=940)
    cv.barcode(760, 168, 230, 64, seed=len(title))
    cv.rect(0, 256, 512, 256, "#d9dde2")
    cv.text("REMOVE COVER", 256, 340, 40, "#1d2a44", "arialb", "center", "center")
    cv.text("PRE-APPLIED TIM", 256, 410, 30, "#1d2a44", "arialb", "center", "center")
    cv.rect(512, 256, 64, 64, "#d9dde2")
    cv.render(pid)
    return at


def torx_screw(m, i, kind, x, y, z_seat, z_head, n, meta):
    """A captive spring screw with a Torx-looking head (a hexalobe recess approximated by the 'ph' head with a
    6-point socket ring), the anchor on the head."""
    a = m.anchor(f"A_SCREW_{kind}_{i}", (x, y, z_head + 0.0024), (0.011, 0.011, 0.014), forward=(0, 0, 1),
                 up=(0, 1, 0), meta=meta + f",order={n}")
    m.add("steel", pb.g_helix(0.0034, 0.0004, z_seat + 0.0002, z_head - 0.0002, max(3.0, (z_head - z_seat) / 0.0011),
                              8, 14), None, (x, y, 0))
    sc = m.piece(a, "steel_dark", "screw")
    sc.add(pb.g_cyl(0.0042, 0.0024, 6, bevel=0.0003), None, (x, y, z_head + 0.0012))  # hex-ish captive head
    sc.add(pb.g_ring(0.0012, 0.0020, 0.0008, 6), None, (x, y, z_head + 0.0026))
    L = z_head - (bc.Z_BOARD - 0.004)
    sc.add(pb.g_cyl(0.0019, L, 14), None, (x, y, z_head - L / 2))
    return a


def server_film(m, at, w, h):
    fa_ = m.anchor("A_FILM_0", (0, 0, 0), (w + 0.004, h + 0.004, 0.003), forward=(0, 0, -1), up=(0, 1, 0),
                   meta="peel_from=+x,text=REMOVE COVER,covers=preapplied_tim")
    fp = m.piece(fa_, "tex_" + m.id, "film")
    fp.add(pb.solid(pb.g_slab(pb.rect2(0, 0, w, h), [], 0.00025, -0.00026, back=False), at.uv("blue")))
    fp.add(pb.g_quad(min(w, h * 2), min(w, h * 2) / 2, at.uv("film")), pb.label_frame((0, 0, -1), (0, 1, 0)),
           (0, 0, -0.000265))


def build_srv_epoch_1u():
    """A 1U passive heatsink for Arc Epoch (socket SP-V): 92.4 (x, along the airflow) x 118 (y) x 27 mm, a thick
    copper base with dense copper-coloured skived fins along x, cut back round six Torx T20 captive screws."""
    pid = "cooler_srv_epoch_1u"
    at = tex_server(pid, "STRATA 1U HEATSINK  SP-V", "ARC EPOCH  /  PASSIVE  /  AIRFLOW >")
    m = pb.Model(pid)
    X, Y, H = 0.0924, 0.118, 0.027
    zb = 0.0060
    m.add("copper", pb.g_slab(pb.rect2(0, 0, X, Y), [pb.circle2(x, y, 0.0024, 16) for (x, y) in SPV_SCREWS], zb, 0.0,
                              bevel=0.0004))
    pitch, n = 0.00125, int((Y - 0.002) / 0.00125)
    for k in range(n):
        y = -Y / 2 + 0.001 + k * pitch
        cuts = [sx * 0.0385 for (sx, sy) in [(s[0] / 0.0385, s[1]) for s in SPV_SCREWS] if abs(sy - y) < 0.0062]
        xs = [-X / 2] + sorted(set(c for cut in cuts for c in (cut - 0.0060, cut + 0.0060))) + [X / 2]
        for a0, a1 in zip(xs[0::2], xs[1::2]):
            if a1 - a0 > 0.001:
                m.add("copper", pb.g_box((a1 - a0, 0.00035, H - zb)), None, ((a0 + a1) / 2, y, (zb + H) / 2))
    # a steel top strap holding the fin tips, the label on it
    for sx in (-1, 1):
        bc.box(m, "steel", (sx * 0.0175 - 0.0045, -Y / 2, H), (sx * 0.0175 + 0.0045, Y / 2, H + 0.0006))
    bc.box(m, "steel", (-0.0175, -0.030, H), (0.0175, 0.030, H + 0.0006))
    m.add("tex_" + pid, pb.g_quad(0.040, 0.010, at.uv("label")), pb.label_frame((0, 0, 1), (1, 0, 0)), (0, 0, H + 0.00065))
    for i, (x, y) in enumerate(SPV_SCREWS):
        torx_screw(m, i, "T20", x, y, zb, zb + 0.0045, [1, 3, 5, 2, 4, 6][i],
                   "spring=1,thread=M4,drive=T20,torque=1.2")
    server_film(m, at, 0.060, 0.060)
    m.anchor("A_HIT_0", (0, 0, (H + 0.0006) / 2), (X, Y, H + 0.0006))
    m.anchor("A_AIRFLOW_0", (0, 0, H / 2), (X, Y, H), forward=(1, 0, 0), up=(0, 0, 1),
             meta="passive=1,needs_cfm=12,height_class=1U")
    finish(m, pid, [
        dict(yaw=-40, pitch=30), dict(yaw=130, pitch=25), dict(yaw=90, pitch=10),
        dict(yaw=200, pitch=-40, target=(0, 0, 0.0), dist=0.25), dict(yaw=0, pitch=0, dist=0.3),
        dict(yaw=20, pitch=35, target=(0.0385, 0.051, 0.01), dist=0.08),
    ])
    return m


def build_srv_platinum_2u():
    """A 2U heatsink for Tiron Platinum (socket L46, narrow ILM): a copper base with screw ears, five 6 mm heat pipes
    U-bent up into a stack of horizontal aluminium fins (air flows along x between them), four Torx T30 captive
    screws in wells through the stack."""
    pid = "cooler_srv_platinum_2u"
    at = tex_server(pid, "STRATA 2U HEATSINK  L46", "TIRON PLATINUM  /  PASSIVE  /  AIRFLOW >")
    m = pb.Model(pid)
    X, Y = 0.078, 0.108
    zb = 0.0065
    base = pb.rrect2(0, 0, 0.064, 0.108, 0.003, 3)
    m.add("copper", pb.g_slab(base, [], zb, 0.0, bevel=0.0004))
    for (x, y) in L46_SCREWS:  # ears
        m.add("copper", pb.g_slab(pb.rrect2(x * 0.97, y, 0.016, 0.014, 0.004, 3), [pb.circle2(x, y, 0.0025, 16)],
                                  0.0040, 0.0, bevel=0.0003))
    z0, pitch, n = 0.020, 0.0019, 24
    zt = z0 + (n - 1) * pitch
    pipes = [-0.026, -0.013, 0.0, 0.013, 0.026]
    for k, x in enumerate(pipes):
        w = 0.040 if k % 2 else 0.046
        half = [(x, w, zt + 0.002), (x, w, z0 - 0.004), (x, w * 0.55, zb + 0.004), (x, 0.012, zb - 0.003)]
        pts = [(p[0], -p[1], p[2]) for p in half] + list(reversed(half))
        m.add("nickel", pb.g_sweep(pb.fillet_path(pts, 0.008, 8), 0.0030, 16))
        for sy in (-1, 1):
            m.add("nickel", pb.g_cyl(0.0024, 0.0016, 16, r2=0.0012), None, (x, sy * w, zt + 0.0028))
    fin = pb.rect2(0, 0, X, Y)
    wells = [pb.circle2(x, y, 0.0062, 20) for (x, y) in L46_SCREWS]
    for k in range(n):
        m.add("alu", pb.g_slab(fin, wells, 0.0004, z0 + k * pitch - 0.0002))
    for k in range(4):  # the side tie bars that hold the stack
        sx, sy = (1, -1)[k % 2], (1, -1)[k // 2]
        bc.box(m, "steel", (sx * X / 2 - 0.004, sy * Y / 2 - 0.0008 * (sy > 0) - 0.0002, z0 - 0.001),
               (sx * X / 2 + 0.000, sy * Y / 2 + 0.0008 * (sy < 0) + 0.0002, zt + 0.001))
    for (x, y) in L46_SCREWS:  # sleeves in the wells down to the ears
        m.add("steel", pb.g_ring(0.0050, 0.0058, zt - 0.0040, 24), None, (x, y, 0.0040 + (zt - 0.0040) / 2))
    m.add("tex_" + pid, pb.g_quad(0.044, 0.011, at.uv("label")), pb.label_frame((0, 0, 1), (1, 0, 0)), (0, 0, zt + 0.00025))
    for i, (x, y) in enumerate(L46_SCREWS):
        torx_screw(m, i, "T30", x, y, 0.0040, 0.0105, [1, 3, 4, 2][i], "spring=1,thread=M4,drive=T30,torque=1.1")
    server_film(m, at, 0.056, 0.094)
    m.anchor("A_HIT_0", (0, 0, zt / 2), (X, Y, zt + 0.003))
    m.anchor("A_AIRFLOW_0", (0, 0, (z0 + zt) / 2), (X, Y, zt - z0), forward=(1, 0, 0), up=(0, 0, 1),
             meta="passive=1,needs_cfm=20,height_class=2U")
    finish(m, pid, [
        dict(yaw=-40, pitch=30), dict(yaw=130, pitch=25), dict(yaw=90, pitch=10),
        dict(yaw=200, pitch=-40, target=(0, 0, 0.0), dist=0.3), dict(yaw=0, pitch=0, dist=0.35),
        dict(yaw=20, pitch=35, target=(0.0345, 0.047, 0.03), dist=0.1),
    ])
    return m


BUILDERS = {k: (lambda k=k: build_tower_model(k, TOWERS[k])) for k in TOWERS}
BUILDERS["cooler_noctis_l9"] = build_low_profile
BUILDERS["cooler_tiron_stock"] = build_tiron_stock
BUILDERS.update({k: (lambda k=k: build_aio(k, AIOS[k])) for k in AIOS})
BUILDERS["cooler_srv_epoch_1u"] = build_srv_epoch_1u
BUILDERS["cooler_srv_platinum_2u"] = build_srv_platinum_2u


def write_report():
    path = os.path.join(c.PREVIEWS, "cat_coolers_report.txt")
    old = {}
    if os.path.exists(path):  # keep the other ids' sections when only some are rebuilt
        cur = None
        for ln in open(path, encoding="utf-8").read().split("\n"):
            if ln.startswith("== "):
                cur = ln[3:].strip()
                old[cur] = []
            if cur:
                old[cur].append(ln)
    for txt in REPORT:
        lines = txt.split("\n")
        old[lines[0][3:].strip()] = lines
    with open(path, "w", encoding="utf-8") as f:
        for k in BUILDERS:
            if k in old:
                f.write("\n".join(old[k]).rstrip() + "\n\n")


if __name__ == "__main__":
    a = c.args()
    if "--nopreview" in a:
        PREVIEW[0] = False
    ids = [x for x in a if x in BUILDERS] or list(BUILDERS)
    for pid in ids:
        BUILDERS[pid]()
    write_report()
