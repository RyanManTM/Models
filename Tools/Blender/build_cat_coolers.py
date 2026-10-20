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
    return r


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


BUILDERS = {k: (lambda k=k: build_tower_model(k, TOWERS[k])) for k in TOWERS}


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
