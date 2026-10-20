"""
shipping_cartons: the brown shipping cartons ship_carton_<s|m|l> (a regular slotted container in 4 mm C-flute
corrugated board) and their broken-down flats ship_carton_<s|m|l>_flat. Used by build_shipping.py.

Closed carton frame: origin at the bottom centre, outer size L (x) x H (y) x W (z), the front at +z.
  * Static body: the four walls (rounded vertical folds), the bottom major flaps (taped) with the minor flaps inside,
    and the rounded creases. Outer faces and cut edges use tex_ship_carton_<k> (kraft print + corrugated edges),
    inner faces the 'cardboard' tag.
  * A_FLAP_0 back long flap, A_FLAP_1 front long flap (hinge=x), A_FLAP_2 left / A_FLAP_3 right short flaps
    (hinge=z, underneath); as build_boxes.py, but each anchor sits ON the crease axis (the flap's rounded hinge
    end turns about it, so the fold looks right at any angle).
  * A_TAPE_0..2: the top strip (strip=0): seg 0 the -x end tab (free end at the bottom), seg 1 the seam, seg 2 the
    +x end tab. A_TAPE_3..5: the bottom strip (strip=1), the same path under the box. Each anchor is the segment's
    centre ON the cardboard (the tape lies on its XY plane, +Z out), local +Y points along the peel path from
    seg i to seg i + 1 (peel=+y), local X is the tape's width.
  * A_LABEL_0@A_FLAP_1: the shipping label area on the front flap (+Z out of the lid, +Y towards the back so it
    reads from the front). A_SPACE_0: the inner volume (centred). A_HIT_0: the whole carton (centred).
  * tapelook#tape_brown: a look-only tape mesh (both strips) for the closed carton; the game hides it.

Flat frame: lying flat, origin at the bottom centre of the flat; x = along the collapsed tube (L + W), z = the
panel height direction with the original top at -z (flaps sticking out at both z ends), +y up: the bottom layer
(back + right panels) is y 0..T, the top layer (left + front panels) T..2T, its flaps curl up a little.
"""
import math
import os

import shipping_lib as S
from shipping_lib import V, B, P, c

T = 0.004          # board thickness (C flute)
FLUTE = 0.0079     # C-flute pitch
SIZES = {"s": (0.36, 0.26, 0.22), "m": (0.46, 0.36, 0.32), "l": (0.60, 0.46, 0.40)}
TAPE_W = 0.048
TAPE_T = 0.00006
TAPE_DOWN = 0.065
LABEL = {"s": (0.140, 0.072), "m": (0.152, 0.102), "l": (0.178, 0.127)}
N_PX = 2048
KRAFT = (0.69, 0.535, 0.37)       # sRGB


# ====================================================================== the printed atlas

class Atlas:
    """tex_ship_carton_<k>: face regions in metres (origin bottom-left, v up), k px per metre."""

    def __init__(self, key, L, H, W):
        self.key, self.L, self.H, self.W = key, L, H, W
        pad = 0.012
        self.pad = pad
        self.reg = {
            "front": (pad, pad, L, H), "right": (2 * pad + L, pad, W, H),
            "back": (pad, 2 * pad + H, L, H), "left": (2 * pad + L, 2 * pad + H, W, H),
            "top": (pad, 3 * pad + 2 * H, L, W), "bottom": (2 * pad + L, 3 * pad + 2 * H, L, W),
        }
        aw, ah = 3 * pad + 2 * L, 4 * pad + 2 * H + W
        self.k = N_PX / max(aw, ah)
        k = self.k
        # the spare column right of 'right'/'left': flute strips (anisotropic) and a plain kraft patch
        x0 = (3 * pad + L + W) * k
        x1 = (2 * pad + 2 * L) * k
        self.fw = 40                                           # px across a 4 mm edge
        self.strips = {"wave": (x0, pad * k), "side": (x0 + self.fw + 8, pad * k)}
        self.strip_len = (2 * H + pad) * k                     # px along v
        px0 = x0 + 2 * self.fw + 20
        self.plain = (px0, pad * k, max(40.0, x1 - px0), (2 * H + pad) * k)   # px rect
        self.tag = f"tex_ship_carton_{key}"

    # -- UV helpers
    def uv_px(self, x, y):
        return (x / N_PX, y / N_PX)

    def face_uv(self, face, p):
        """UV of a closed-box point p (Unity) on a face (as seen from outside)."""
        L, H, W = self.L, self.H, self.W
        x, y, z = p[0], p[1], p[2]
        if face == "front":
            u, v = L / 2 - x, y
        elif face == "back":
            u, v = x + L / 2, y
        elif face == "right":
            u, v = z + W / 2, y
        elif face == "left":
            u, v = W / 2 - z, y
        elif face == "top":
            u, v = L / 2 - x, W / 2 - z
        elif face == "bottom":
            u, v = x + L / 2, W / 2 - z
        else:
            raise KeyError(face)
        x0, y0, w, h = self.reg[face]
        u = min(max(u, 0.0), w)
        v = min(max(v, 0.0), h)
        return self.uv_px((x0 + u) * self.k, (y0 + v) * self.k)

    def plain_uv(self, a, b):
        """Plain kraft (unprinted outer liner): physical (a, b) metres, wrapped into the patch."""
        px, py, pw, ph = self.plain
        k = self.k
        sa = (a * k) % (pw - 4) + 2
        sb = (b * k) % (ph - 4) + 2
        return self.uv_px(px + sa, py + sb)

    def flute_fn(self, kind, length, rng):
        """(s metres along the edge, t 0..1 across the thickness) -> UV on a flute strip."""
        x0, y0 = self.strips[kind]
        span = self.strip_len - 4
        need = length * self.k
        off = rng.uniform(0, max(0.0, span - need)) if need < span else 0.0
        sc = 1.0 if need <= span else span / need

        def f(s, t):
            return self.uv_px(x0 + 2 + t * (self.fw - 4), y0 + 2 + off + s * self.k * sc)
        return f


def carton_texture(at, seed=1):
    """Paints tex_ship_carton_<k>.png: kraft with fibres and flute washboarding, flexo prints (this side up,
    handle with care, recycling, the box maker's certificate, size marks), a red FRAGILE stamp, handling grime,
    and the two corrugated-edge strips."""
    import numpy as np
    k, L, H, W = at.k, at.L, at.H, at.W
    n = N_PX
    rng = np.random.default_rng(seed)
    # -- kraft base: mottling + fibres smeared along x + fine grain
    mott = S.noise_field(n, n, 40.0, seed + 1)
    mott2 = S.noise_field(n, n, 9.0, seed + 2)
    fib = S.noise_field(n, n, 7.0, seed + 3, sy=0.7)
    grain = rng.normal(0, 1, (n, n)).astype(np.float32)
    lum = 1.0 + 0.020 * mott + 0.008 * mott2 + 0.010 * fib + 0.010 * grain
    base = np.zeros((n, n, 3), dtype=np.float32)
    for i in range(3):
        base[..., i] = KRAFT[i]
    hue = S.noise_field(n, n, 60.0, seed + 4)
    base[..., 0] *= 1 + 0.012 * hue
    base[..., 2] *= 1 - 0.03 * hue
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    # -- per-face tint, washboard (flutes run along each region's v), edge grime
    for name, (rx, ry, rw, rh) in at.reg.items():
        x0, y0, x1, y1 = int(rx * k), int(ry * k), int((rx + rw) * k), int((ry + rh) * k)
        sl = (slice(y0, y1), slice(x0, x1))
        u = (xx[sl] - rx * k) / k
        v = (yy[sl] - ry * k) / k
        tint = 1.0 + rng.uniform(-0.025, 0.02)
        wash = 1.0 + 0.006 * np.sin(2 * math.pi * u / FLUTE + rng.uniform(0, 6.28))
        d = np.minimum(np.minimum(u, rw - u), np.minimum(v, rh - v))
        gn = S.noise_field(y1 - y0, x1 - x0, 25.0, seed + 10 + len(name)) if (y1 > y0 and x1 > x0) else 0
        grime = 1.0 - 0.07 * np.clip(1 - d / 0.02, 0, 1) ** 2 * np.clip(0.6 + 0.5 * gn, 0, 1.4)
        lum[sl] *= tint * wash * grime
    # the plain patch gets the same washboard
    px, py, pw, ph = at.plain
    sl = (slice(int(py), int(py + ph)), slice(int(px), int(px + pw)))
    lum[sl] *= 1.0 + 0.006 * np.sin(2 * math.pi * (xx[sl] / k) / FLUTE)
    img = base * lum[..., None]

    # -- scuffs: the top liner scraped (lighter streaks) and a few darker rub marks
    for _ in range(int(14 + 10 * (k / 1500))):
        name = list(at.reg)[rng.integers(0, 6)]
        rx, ry, rw, rh = at.reg[name]
        cx, cy = (rx + rng.uniform(0.02, rw - 0.02)) * k, (ry + rng.uniform(0.02, rh - 0.02)) * k
        ang = rng.uniform(0, math.pi)
        ln = rng.uniform(0.01, 0.05) * k
        wd = rng.uniform(0.6, 1.8)
        dx, dy = xx - cx, yy - cy
        along = dx * math.cos(ang) + dy * math.sin(ang)
        across = -dx * math.sin(ang) + dy * math.cos(ang)
        m = np.clip(1 - np.abs(across) / wd, 0, 1) * np.clip(1 - np.abs(along) / (ln / 2), 0, 1) ** 0.3
        img *= (1.0 + (0.10 if rng.random() < 0.7 else -0.08) * m)[..., None]

    # -- prints: flexo ink layer and the red stamp layer
    ink = S.art_layer(n, n, f"ship_ink_{at.key}", lambda a: _draw_ink(a, at))
    red = S.art_layer(n, n, f"ship_red_{at.key}", lambda a: _draw_red(a, at))
    flexo = np.clip(0.88 + 0.12 * S.noise_field(n, n, 1.2, seed + 20), 0, 1)
    ia = ink[..., 3] * flexo * 0.92
    ink_col = np.array([0.17, 0.14, 0.12], dtype=np.float32)
    img = img * (1 - ia[..., None]) + img * ink_col * ia[..., None]
    g1 = S.noise_field(n, n, 1.4, seed + 21)
    g2 = S.noise_field(n, n, 7.0, seed + 22)
    stamp = np.clip((g1 * 0.5 + g2 * 0.6 + 1.5) * 0.9, 0, 1)
    ra = red[..., 3] * stamp * 0.88
    red_col = np.array([0.93, 0.16, 0.10], dtype=np.float32)
    img = img * (1 - ra[..., None]) + img * red_col * ra[..., None]

    # -- corrugated edge strips (anisotropic: fw px across 4 mm, k px per metre along)
    fw = at.fw
    for kind, (sx, sy) in at.strips.items():
        x0, y0 = int(sx), int(sy)
        y1 = int(sy + at.strip_len)
        t = (xx[y0:y1, x0:x0 + fw] - x0 + 0.5) / fw          # 0..1 across the board
        s = (yy[y0:y1, x0:x0 + fw] - y0) / k                  # metres along the edge
        liner_col = np.array([0.74, 0.57, 0.39], dtype=np.float32)
        med_col = np.array([0.60, 0.44, 0.27], dtype=np.float32)
        void_col = np.array([0.16, 0.11, 0.07], dtype=np.float32)
        lin = 0.13
        aa = 1.5 / fw
        out = np.zeros(t.shape + (3,), dtype=np.float32)
        liner = np.clip((lin - np.minimum(t, 1 - t)) / aa + 0.5, 0, 1)
        if kind == "wave":
            mid = 0.5 + (0.5 - lin - 0.05) * np.sin(2 * math.pi * s / FLUTE)
            med = np.clip((0.075 - np.abs(t - mid)) / aa + 0.5, 0, 1)
            # the voids get darker away from the medium (shadow depth)
            depth = np.clip(np.abs(t - mid) / 0.35, 0, 1)
            void = void_col[None, None, :] * (1.25 - 0.5 * depth[..., None])
            body = void * (1 - med[..., None]) + med_col * med[..., None]
        else:
            # seen along the flutes: the medium's crests and a dark band between them
            band = 0.5 + 0.5 * np.cos(2 * math.pi * (t - 0.5) / (1 - 2 * lin))
            body = void_col * 1.4 * (1 - band[..., None] * 0.45) + med_col * band[..., None] * 0.45
        out = body * (1 - liner[..., None]) + liner_col * liner[..., None]
        out *= (1 + 0.05 * rng.normal(0, 1, out.shape[:2]).astype(np.float32))[..., None]
        img[y0:y1, x0:x0 + fw] = out
    arr = np.ones((n, n, 4), dtype=np.float32)
    arr[..., :3] = np.clip(img, 0, 1)
    return P.save_png(arr, f"ship_carton_{at.key}")


class FaceArt:
    """Draws on one face region in metres: (u, v) from the face's bottom-left as seen from outside."""

    def __init__(self, art, at, face):
        self.a, self.at = art, at
        self.x0, self.y0, self.w, self.h = at.reg[face]
        self.k = at.k

    def p(self, u, v):
        return ((self.x0 + u) * self.k, (self.y0 + v) * self.k)

    def text(self, s, u, v, size, font="arialbd.ttf", align="LEFT", maxw=None, rot=0.0, col=(0, 0, 0), valign="BASE",
             spacing=1.0):
        x, y = self.p(u, v)
        return self.a.text(s, x, y, size * self.k, col, font, align=align, maxw=None if maxw is None else maxw * self.k,
                           rot=rot, valign=valign, spacing=spacing)

    def rect(self, u, v, w, h, col=(0, 0, 0)):
        x, y = self.p(u, v)
        self.a.rect(x, y, w * self.k, h * self.k, col)

    def poly(self, pts, col=(0, 0, 0)):
        self.a.poly([self.p(u, v) for u, v in pts], col)

    def ring(self, u, v, r0, r1, col=(0, 0, 0)):
        x, y = self.p(u, v)
        self.a.ring(x, y, r0 * self.k, r1 * self.k, col, n=96)

    def circle(self, u, v, r, col=(0, 0, 0)):
        x, y = self.p(u, v)
        self.a.circle(x, y, r * self.k, col, n=64)


def iso_up(F, u, v, s, col=(0, 0, 0)):
    """ISO 780 'this way up': two arrows over a bar (u, v = bottom-left, s = size)."""
    for cx in (0.30, 0.70):
        F.rect(u + s * cx - s * 0.055, v + s * 0.16, s * 0.11, s * 0.48, col)
        F.poly([(u + s * (cx - 0.17), v + s * 0.60), (u + s * (cx + 0.17), v + s * 0.60), (u + s * cx, v + s * 0.98)], col)
    F.rect(u + s * 0.08, v, s * 0.84, s * 0.09, col)


def iso_glass(F, u, v, s, col=(0, 0, 0)):
    """ISO 780 'fragile': a wine glass."""
    bowl = [(u + s * (0.5 + 0.30 * math.cos(a)), v + s * (0.62 + 0.28 * math.sin(a))) for a in
            [math.pi + i * math.pi / 10 for i in range(11)]]
    F.poly([(u + s * 0.18, v + s * 0.98), (u + s * 0.82, v + s * 0.98)] + [(x, y) for (x, y) in reversed(bowl)][0:0] +
           [(u + s * 0.80, v + s * 0.62)] + [(x, y) for (x, y) in reversed(bowl)][1:-1] + [(u + s * 0.20, v + s * 0.62)], col)
    F.rect(u + s * 0.46, v + s * 0.10, s * 0.08, s * 0.28, col)
    F.rect(u + s * 0.28, v + s * 0.04, s * 0.44, s * 0.07, col)


def iso_umbrella(F, u, v, s, col=(0, 0, 0)):
    """ISO 780 'keep dry'."""
    pts = [(u + s * (0.5 + 0.42 * math.cos(a)), v + s * (0.50 + 0.36 * math.sin(a))) for a in
           [i * math.pi / 14 for i in range(15)]]
    F.poly(pts, col)
    F.rect(u + s * 0.475, v + s * 0.12, s * 0.05, s * 0.40, col)
    F.rect(u + s * 0.40, v + s * 0.08, s * 0.125, s * 0.05, col)
    for kx in (0.2, 0.35, 0.65, 0.8):
        F.rect(u + s * kx, v + s * 0.90, s * 0.03, s * 0.08, col)


def recycle_mark(F, u, v, s, col=(0, 0, 0)):
    """The recycling loop and a two-line note under it (u, v = centre of the loop)."""
    F.text("♻", u, v, s, "seguisym.ttf", align="CENTER", valign="CENTER", col=col)
    F.text("PLEASE RECYCLE", u, v - s * 0.78, s * 0.15, align="CENTER", col=col)
    F.text("100% RECYCLABLE CORRUGATED", u, v - s * 0.98, s * 0.10, "arial.ttf", align="CENTER", col=col)


def bmc(F, u, v, r, key, col=(0, 0, 0)):
    """A box maker's certificate seal (centred at u, v, radius r)."""
    F.ring(u, v, r * 0.93, r, col)
    F.ring(u, v, r * 0.66, r * 0.69, col)
    sz = r * 0.15
    x, y = F.p(u, v)
    S.text_on_arc(F.a, "BOX MAKER'S CERTIFICATE", x, y, (r * 0.72) * F.k, sz * F.k, col, "arialbd.ttf", 90,
                  clockwise=True)
    S.text_on_arc(F.a, "NORTHGATE PACKAGING CO.", x, y, (r * 0.885) * F.k, sz * 0.95 * F.k, col, "arialbd.ttf", 270,
                  clockwise=False, inward=True)
    lines = [("THIS SINGLE WALL BOX MEETS", 0.055), ("ALL CONSTRUCTION REQUIREMENTS", 0.055),
             ("OF APPLICABLE FREIGHT CLASS.", 0.055), ("32 ECT", 0.17), ("EDGE CRUSH TEST", 0.065),
             ("32 LBS PER INCH WIDTH", 0.055), ("SIZE LIMIT 75 IN", 0.05), ("GROSS WT LT 40 LBS", 0.05)]
    yy = v + r * 0.42
    for s_, h in lines:
        hh = r * h * 1.55
        F.text(s_, u, yy - hh, hh, align="CENTER", maxw=r * 1.18, col=col)
        yy -= hh * 1.32


def size_marks(F, u, v, at, align="LEFT", col=(0, 0, 0)):
    L, H, W = at.L, at.H, at.W
    s = 0.0065
    F.text(f"{int(round((L - 2 * T) * 1000))} x {int(round((W - 2 * T) * 1000))} x {int(round((H - 4 * T) * 1000))} mm  I.D.",
           u, v + s * 1.5, s, align=align, col=col)
    F.text(f"RSC  •  SINGLE WALL  •  C FLUTE  •  CODE NG-{at.key.upper()}{int(L * 100)}{int(W * 100)}",
           u, v, s * 0.85, "arial.ttf", align=align, col=col)


def _draw_ink(a, at):
    L, H, W = at.L, at.H, at.W
    ink = (0.0, 0.0, 0.0)
    s = min(0.075, max(0.042, H * 0.17))         # handling symbol size
    ts = s * 0.20                                 # caption cap height
    # FRONT: this side up (top left), keep dry, the size marks (bottom right)
    F = FaceArt(a, at, "front")
    iso_up(F, 0.035, H - 0.03 - s, s, ink)
    F.text("THIS SIDE UP", 0.035 + s * 0.5, H - 0.03 - s - ts * 1.6, ts, align="CENTER", col=ink)
    iso_umbrella(F, 0.035 + s * 1.25, H - 0.03 - s, s * 0.9, ink)
    F.text("KEEP DRY", 0.035 + s * 1.7, H - 0.03 - s - ts * 1.6, ts, align="CENTER", col=ink)
    size_marks(F, L - 0.03, 0.022, at, align="RIGHT", col=ink)
    # BACK: handle with care (top left), this side up (top right), size marks (bottom left)
    F = FaceArt(a, at, "back")
    iso_glass(F, 0.035, H - 0.03 - s, s, ink)
    F.text("HANDLE WITH CARE", 0.035 + s * 0.5, H - 0.03 - s - ts * 1.6, ts, align="CENTER", col=ink)
    iso_up(F, L - 0.035 - s, H - 0.03 - s, s, ink)
    F.text("THIS SIDE UP", L - 0.035 - s * 0.5, H - 0.03 - s - ts * 1.6, ts, align="CENTER", col=ink)
    size_marks(F, 0.03, 0.022, at, col=ink)
    # LEFT end: arrows under the tape tab, the recycling mark lower left (clear of the bottom tape)
    F = FaceArt(a, at, "left")
    top = H - TAPE_DOWN - 0.015
    iso_up(F, W / 2 - s / 2, top - s, s, ink)
    F.text("THIS SIDE UP", W / 2, top - s - ts * 1.6, ts, align="CENTER", col=ink)
    rs = min(0.045, W * 0.16)
    if top - s - ts * 2.6 - TAPE_DOWN > rs * 1.45:    # room between the arrows and the bottom tape
        recycle_mark(F, W * 0.5, TAPE_DOWN + rs * 0.95, rs, ink)
    else:                                              # beside the bottom tape tab
        rs = min(rs, (W / 2 - TAPE_W / 2) * 0.62)
        recycle_mark(F, (W / 2 - TAPE_W / 2) / 2, rs * 1.15, rs, ink)
    # RIGHT end: arrows, the box maker's certificate
    F = FaceArt(a, at, "right")
    r = min(0.052, W * 0.21, (top - s - ts * 2.5 - TAPE_DOWN) * 0.5 - 0.004)
    iso_up(F, W / 2 - s / 2, top - s, s, ink)
    F.text("THIS SIDE UP", W / 2, top - s - ts * 1.6, ts, align="CENTER", col=ink)
    bmc(F, W / 2, TAPE_DOWN + 0.006 + r, r, at.key, ink)
    # BOTTOM: the certificate again on a flap, a lot code
    F = FaceArt(a, at, "bottom")
    rb = min(0.06, W * 0.2)
    bmc(F, L * 0.24, W * 0.27, rb, at.key, ink)
    F.text("LOT 2611-B  •  09/26  •  MADE IN U.S.A.", L * 0.72, W * 0.12, 0.006, align="CENTER", col=ink)
    # TOP: nothing but a small printer's mark near a flap corner
    F = FaceArt(a, at, "top")
    F.text("NG", 0.03, W - 0.03, 0.008, col=ink)


def _draw_red(a, at):
    L, H, W = at.L, at.H, at.W
    red = (0.0, 0.0, 0.0)

    def stamp(F, u, v, w, rot):
        h = w * 0.36
        ca, sa = math.cos(rot), math.sin(rot)

        def R(du, dv):
            return (u + du * ca - dv * sa, v + du * sa + dv * ca)
        t = w * 0.035
        for (a0, b0, a1, b1) in ((-w / 2, -h / 2, w / 2, -h / 2 + t), (-w / 2, h / 2 - t, w / 2, h / 2),
                                 (-w / 2, -h / 2, -w / 2 + t, h / 2), (w / 2 - t, -h / 2, w / 2, h / 2)):
            F.poly([R(a0, b0), R(a1, b0), R(a1, b1), R(a0, b1)], red)
        cu, cv = R(0, h * 0.06)
        F.text("FRAGILE", cu, cv, h * 0.48, "STENCIL.TTF", align="CENTER", valign="CENTER", maxw=w * 0.86, rot=rot,
               col=red)
        cu, cv = R(0, -h * 0.33)
        F.text("HANDLE WITH CARE", cu, cv, h * 0.12, align="CENTER", valign="CENTER", maxw=w * 0.8, rot=rot, col=red)
    F = FaceArt(a, at, "front")
    stamp(F, L * 0.64, H * 0.47, min(0.22, L * 0.44), -7 * S.DEG)
    F = FaceArt(a, at, "back")
    stamp(F, L * 0.36, H * 0.42, min(0.18, L * 0.38), 5 * S.DEG)


# ====================================================================== geometry

class Builder:
    """Board pieces with printed outsides, cardboard insides and corrugated cut edges."""

    def __init__(self, kit, at, seed):
        self.kit, self.at = kit, at
        self.rng = S.seeded(seed)

    def mbs(self, anchor=None, name="piece"):
        if anchor is None:
            return self.kit.mb(self.at.tag), self.kit.mb("cardboard")
        return self.kit.piece(anchor, self.at.tag, name), self.kit.piece(anchor, "cardboard", name)

    def _uv(self, spec, p_closed):
        if spec[0] == "face":
            return self.at.face_uv(spec[1], p_closed)
        if spec[0] == "plain":
            a, b = spec[1](p_closed) if len(spec) > 1 else (p_closed[0] + p_closed[2], p_closed[1])
            return self.at.plain_uv(a, b)
        raise KeyError(spec)

    def slab(self, mbs, O, U, Vv, N, u0, u1, v0, v1, t0, t1, faces, xf=None, closed=None):
        """A board block: points O + U*u + V*v + N*t. faces: '+t','-t','+u','-u','+v','-v' ->
        ('face', name) | ('plain',) | ('card',) | ('wave',) | ('side',) | None.
        closed(p) maps a construction point to its closed-box position (for the printed UVs);
        xf(p) maps it to its final position."""
        O, U, Vv, N = V(O), V(U), V(Vv), V(N)
        xf = xf or (lambda p: p)
        closed = closed or (lambda p: p)
        mt, mc = mbs

        def pt(u, v, t):
            return O + U * u + Vv * v + N * t
        quads = {
            "+t": ([(u0, v0, t1), (u1, v0, t1), (u1, v1, t1), (u0, v1, t1)], N, "uv"),
            "-t": ([(u0, v0, t0), (u1, v0, t0), (u1, v1, t0), (u0, v1, t0)], -N, "uv"),
            "+u": ([(u1, v0, t0), (u1, v1, t0), (u1, v1, t1), (u1, v0, t1)], U, "v"),
            "-u": ([(u0, v0, t0), (u0, v1, t0), (u0, v1, t1), (u0, v0, t1)], -U, "v"),
            "+v": ([(u0, v1, t0), (u1, v1, t0), (u1, v1, t1), (u0, v1, t1)], Vv, "u"),
            "-v": ([(u0, v0, t0), (u1, v0, t0), (u1, v0, t1), (u0, v0, t1)], -Vv, "u"),
        }
        for key, spec in faces.items():
            if spec is None:
                continue
            corners, nrm, along = quads[key]
            pts = [pt(*q) for q in corners]
            if spec[0] == "card":
                add = [xf(p) for p in pts]
                S.add_quad(mc, add, None, xf(O + nrm) - xf(O))
                continue
            if spec[0] in ("face", "plain"):
                uvs = [self._uv(spec, closed(p)) for p in pts]
            else:   # flute strips: s along the edge, t across the thickness
                if along == "v":
                    length = abs(v1 - v0)
                    st = [((q[1] - v0) if v1 > v0 else (v0 - q[1]), (q[2] - t0) / (t1 - t0)) for q in corners]
                else:
                    length = abs(u1 - u0)
                    st = [((q[0] - u0) if u1 > u0 else (u0 - q[0]), (q[2] - t0) / (t1 - t0)) for q in corners]
                f = self.at.flute_fn(spec[0], length, self.rng)
                uvs = [f(s_, t_) for s_, t_ in st]
            S.add_quad(mt, [xf(p) for p in pts], uvs, xf(O + nrm) - xf(O))

    def roll(self, mbs, C, axis, length, r, d0, d1, sweep, segs=6, caps=True, xf=None, closed=None, plain_ab=None):
        """A cylinder surface (the rounded fold): centre line C +- axis*length/2, radius r, from direction d0
        turning towards d1 by 'sweep' degrees. Outside: plain kraft; end caps (pie slices): flute 'wave'."""
        C, A, D0, D1 = V(C), V(axis).normalized(), V(d0).normalized(), V(d1).normalized()
        xf = xf or (lambda p: p)
        closed = closed or (lambda p: p)
        mt, _ = mbs
        dirs = []
        for i in range(segs + 1):
            a = sweep * S.DEG * i / segs
            dirs.append(D0 * math.cos(a) + D1 * math.sin(a))
        h = length / 2
        for i in range(segs):
            da, db = dirs[i], dirs[i + 1]
            pts = [C - A * h + da * r, C + A * h + da * r, C + A * h + db * r, C - A * h + db * r]
            mid = (da + db).normalized()
            uvs = []
            for p in pts:
                q = closed(p)
                ab = plain_ab(q) if plain_ab else (q[0] + q[2], q[1])
                uvs.append(self.at.plain_uv(*ab))
            S.add_quad(mt, [xf(p) for p in pts], uvs, xf(C + mid) - xf(C))
        if caps:
            for sgn in (-1, 1):
                c0 = C + A * h * sgn
                f = self.at.flute_fn("wave", 2 * r, self.rng)
                for i in range(segs):
                    pts = [c0, c0 + dirs[i] * r, c0 + dirs[i + 1] * r]
                    uvs = [f(r, 0.5), f(r + r * dirs[i].dot(D0), 0.5 + 0.5 * dirs[i].dot(D1)),
                           f(r + r * dirs[i + 1].dot(D0), 0.5 + 0.5 * dirs[i + 1].dot(D1))]
                    S.add_quad(mt, [xf(p) for p in pts], uvs, xf(c0 + A * sgn) - xf(c0))


def build_carton(key, kit, at):
    """The closed carton ship_carton_<key> (see the module docstring)."""
    L, H, W = SIZES[key]
    bd = Builder(kit, at, "carton_" + key)
    body = bd.mbs()
    e = 0.0015       # major flaps are cut a little short of the ends
    e2 = 0.0012      # minor flaps clear the long walls
    g = 0.002        # gap between the two long flaps
    yb = H - 1.5 * T  # top of the tube (the short flaps' crease axis)
    ya = T            # bottom of the tube (on the bottom long flaps)
    X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
    xi, zi = L / 2 - T, W / 2 - T   # inner corner (fold axis) positions

    # -- the tube: four walls with rounded vertical folds (outer radius T about the inner corner)
    for sz in (1, -1):   # front (+z) and back (-z) walls, between the folds
        face = "front" if sz > 0 else "back"
        bd.slab(body, (0, 0, sz * W / 2), X, Y, Z * sz, -xi, xi, ya, yb, -T, 0,
                {"+t": ("face", face), "-t": ("card",)})
        # extension up to the long flap's crease axis, and down to the bottom crease
        bd.slab(body, (0, 0, sz * W / 2), X, Y, Z * sz, -xi, xi, yb, H - T / 2, -T, 0,
                {"+t": ("face", face), "-t": ("card",), "+u": ("side",), "-u": ("side",)})
        bd.slab(body, (0, 0, sz * W / 2), X, Y, Z * sz, -xi, xi, T / 2, ya, -T, 0,
                {"+t": ("face", face), "-t": ("card",), "+u": ("side",), "-u": ("side",)})
    for sx in (1, -1):   # the ends
        face = "right" if sx > 0 else "left"
        bd.slab(body, (sx * L / 2, 0, 0), Z * -sx, Y, X * sx, -zi, zi, ya, yb, -T, 0,
                {"+t": ("face", face), "-t": ("card",)})
    for sx in (1, -1):   # the four folds
        for sz in (1, -1):
            C = V((sx * xi, (ya + yb) / 2, sz * zi))
            face_a = "right" if sx > 0 else "left"
            bd.roll(body, C, Y, yb - ya, T, X * sx, Z * sz, 90, segs=3,
                    plain_ab=lambda q: (q[0] + q[2], q[1]))

    # -- bottom: two long flaps (static, taped) and the short flaps inside
    for sz in (1, -1):
        bd.slab(body, (0, 0, 0), X, Z * sz, Y, -L / 2 + e, L / 2 - e, g / 2, W / 2 - T / 2, 0, T,
                {"-t": ("face", "bottom"), "+t": ("card",), "-v": ("wave",), "+u": ("side",), "-u": ("side",)})
        bd.roll(body, (0, T / 2, sz * (W / 2 - T / 2)), X, L - 2 * e, T / 2, Z * sz, -Y, 90, segs=3,
                plain_ab=lambda q: (q[0], q[1] + q[2]))
    for sx in (1, -1):
        bd.slab(body, (sx * (L / 2 - T), 0, 0), X * -sx, Z, Y, 0, W / 2 - T, -zi + e2, zi - e2, T, 2 * T,
                {"+t": ("card",), "+u": ("wave",), "+v": ("side",), "-v": ("side",)})

    # -- top flaps (moving pieces), each turning about its crease axis
    flaps = []
    for i, sz in enumerate((-1, 1)):    # A_FLAP_0 back, A_FLAP_1 front
        piv = V((0, H - T / 2, sz * (W / 2 - T / 2)))
        meta = f"hinge=x,open={-215 if sz < 0 else 215},order=1,side={'back' if sz < 0 else 'front'},under=A_TAPE_1"
        a = kit.anchor(f"A_FLAP_{i}", tuple(piv), (L - 2 * e, T, W / 2), meta=meta)
        flaps.append(a)
        mbs = bd.mbs(a, "flap")
        bd.slab(mbs, (0, 0, 0), X, Z * -sz, Y, -L / 2 + e, L / 2 - e, -(W / 2 - T / 2), -g / 2, H - T, H,
                {"+t": ("face", "top"), "-t": ("card",), "+v": ("wave",), "+u": ("side",), "-u": ("side",)})
        bd.roll(mbs, piv, X, L - 2 * e, T / 2, Y, Z * sz, 180, segs=6, plain_ab=lambda q: (q[0], q[1] + q[2]))
    for i, sx in enumerate((-1, 1)):    # A_FLAP_2 left, A_FLAP_3 right
        piv = V((sx * (L / 2 - T / 2), H - 1.5 * T, 0))
        meta = (f"hinge=z,open={200 if sx < 0 else -200},order=2,side={'left' if sx < 0 else 'right'},"
                f"under=A_FLAP_0,A_FLAP_1")
        a = kit.anchor(f"A_FLAP_{2 + i}", tuple(piv), (W / 2, T, W - 2 * T - 2 * e2), meta=meta)
        flaps.append(a)
        mbs = bd.mbs(a, "flap")
        bd.slab(mbs, (sx * (L / 2 - T / 2), 0, 0), X * -sx, Z, Y, 0, W / 2 - T / 2, -zi + e2, zi - e2, H - 2 * T, H - T,
                {"+t": ("plain",), "-t": ("card",), "+u": ("wave",), "+v": ("side",), "-v": ("side",)})
        bd.roll(mbs, piv, Z, W - 2 * T - 2 * e2, T / 2, Y, X * sx, 180, segs=6,
                plain_ab=lambda q: (q[0] + q[2], q[1]))

    # -- anchors: tape (top strip 0, bottom strip 1), label, space, hit
    tw = TAPE_W
    segs = [
        ("A_TAPE_0", (-L / 2, H - TAPE_DOWN / 2, 0), (-1, 0, 0), (0, 1, 0), TAPE_DOWN, "strip=0,seg=0,peel=+y,order=0,face=top"),
        ("A_TAPE_1", (0, H, 0), (0, 1, 0), (1, 0, 0), L, "strip=0,seg=1,peel=+y,order=0,face=top"),
        ("A_TAPE_2", (L / 2, H - TAPE_DOWN / 2, 0), (1, 0, 0), (0, -1, 0), TAPE_DOWN, "strip=0,seg=2,peel=+y,order=0,face=top"),
        ("A_TAPE_3", (-L / 2, TAPE_DOWN / 2, 0), (-1, 0, 0), (0, -1, 0), TAPE_DOWN, "strip=1,seg=0,peel=+y,order=0,face=bottom"),
        ("A_TAPE_4", (0, 0, 0), (0, -1, 0), (1, 0, 0), L, "strip=1,seg=1,peel=+y,order=0,face=bottom"),
        ("A_TAPE_5", (L / 2, TAPE_DOWN / 2, 0), (1, 0, 0), (0, 1, 0), TAPE_DOWN, "strip=1,seg=2,peel=+y,order=0,face=bottom"),
    ]
    for nm, pos, fw, up, ln, meta in segs:
        kit.anchor(nm, pos, (tw, ln, TAPE_T), forward=fw, up=up, meta=meta)
    lw, lh = LABEL[key]
    lz = (tw / 2 + W / 2 - T) / 2 + 0.002
    kit.anchor("A_LABEL_0", (L * 0.10, H, lz), (lw, lh, 0.0002), forward=(0, 1, 0), up=(0, 0, -1),
               meta="print=shipping_label", parent=flaps[1])
    kit.anchor("A_SPACE_0", (0, H / 2, 0), (L - 2 * T, H - 4 * T, W - 2 * T))
    kit.anchor("A_HIT_0", (0, H / 2, 0), (L, H, W))

    # -- the look-only tape (both strips), hidden by the game when it builds its own peel strips
    tape_look(kit, L, H)
    return flaps


def tape_look(kit, L, H):
    mb = kit.named_mb("tapelook", "tape_brown")
    tw, o = TAPE_W, 0.00025
    rc = 0.0015

    def strip(top):
        ys = 1 if top else -1
        y_edge = H if top else 0.0
        # the path in the x-y plane: up the -x end, across, down the +x end (with small rounded corners)
        pts = []
        y_end = (H - TAPE_DOWN) if top else TAPE_DOWN
        # a lifted tab at the start (the free end of strip 0 curls out a little)
        lift = 0.0025 if top else 0.0
        pts.append((-L / 2 - o - lift, y_end))
        pts.append((-L / 2 - o - lift * 0.3, y_end + ys * 0.006))
        pts.append((-L / 2 - o, y_end + ys * 0.012))
        for i in range(4):
            a = (math.pi / 2) * i / 3
            cx, cy = -L / 2 + rc, y_edge - ys * rc
            pts.append((cx - (rc + o) * math.cos(a), cy + ys * (rc + o) * math.sin(a)))
        for i in range(4):
            a = (math.pi / 2) * i / 3
            cx, cy = L / 2 - rc, y_edge - ys * rc
            pts.append((cx + (rc + o) * math.sin(a), cy + ys * (rc + o) * math.cos(a)))
        pts.append((L / 2 + o, y_end))
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            quad = [V((x0, y0, -tw / 2)), V((x1, y1, -tw / 2)), V((x1, y1, tw / 2)), V((x0, y0, tw / 2))]
            # outward: away from the box centre line
            mid = (quad[0] + quad[2]) / 2
            out = mid - V((0, H / 2, 0))
            out.z = 0
            S.add_quad(mb, quad, None, out)
    strip(True)
    strip(False)


def build_flat(key, kit, at):
    """ship_carton_<key>_flat: the tube collapsed flat (two layers), the flaps sticking out at both ends."""
    L, H, W = SIZES[key]
    bd = Builder(kit, at, "flat_" + key)
    body = bd.mbs()
    X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
    e, e2 = 0.0015, 0.0012
    rng = S.seeded("flat" + key)

    # Construction happens in "unfolded box space": layer 1 (front + left panel) lies in the plane z = W/2 (outer
    # side +z), layer 2 (back + right) in z = -W/2 (outer side -z); box y is the panel height. xf() then lays it down.
    def lay(layer):
        dx = W / 2 if layer == 1 else -W / 2

        def f(p):
            p = V(p)
            if layer == 1:
                return V((p.x + dx, p.z - W / 2 + 2 * T, -(p.y - H / 2)))
            return V((p.x + dx, p.z + W / 2, -(p.y - H / 2)))
        return f

    def tilt(f, axis_pt, axis, deg):
        """Wraps an xf: rotates (in final space) about a line before the final mapping."""
        R = S.Matrix.Rotation(deg * S.DEG, 3, V(axis))

        def g(p):
            q = f(p)
            return R @ (q - axis_pt) + axis_pt
        return g

    # closed-box positions of the unfolded points (for the printed UVs)
    def closed_front(p):
        return V((p.x, p.y, W / 2))

    def closed_left(p):           # unfolded about the front-left fold: x' < -L/2
        return V((-L / 2, p.y, W / 2 + (p.x + L / 2)))

    def closed_back(p):
        return V((p.x, p.y, -W / 2))

    def closed_right(p):          # unfolded about the back-right fold: x' > L/2
        return V((L / 2, p.y, -W / 2 + (p.x - L / 2)))

    def closed_major_top(p, sz):  # flap above a long panel, unfolded upwards
        return V((p.x, H, sz * (W / 2 - (p.y - H))))

    def closed_major_bot(p, sz):
        return V((p.x, 0.0, sz * (W / 2 + p.y)))

    l1, l2 = lay(1), lay(2)
    # layer 1: front panel x in [-L/2, L/2], left panel x in [-L/2 - W, -L/2]; outer at z = W/2
    fr = (0, 0, W / 2)
    bd.slab(body, fr, X, Y, Z, -L / 2, L / 2, 0, H, -T, 0, {"+t": ("face", "front"), "-t": ("card",)}, xf=l1,
            closed=closed_front)
    bd.slab(body, fr, X, Y, Z, -L / 2 - W + T, -L / 2, 0, H, -T, 0, {"+t": ("face", "left"), "-t": ("card",)}, xf=l1,
            closed=closed_left)
    # layer 2: back panel x in [-L/2, L/2], right panel x in [L/2, L/2 + W]; outer at z = -W/2
    bk = (0, 0, -W / 2)
    bd.slab(body, bk, X, Y, -Z, -L / 2, L / 2, 0, H, -T, 0, {"+t": ("face", "back"), "-t": ("card",)}, xf=l2,
            closed=closed_back)
    bd.slab(body, bk, X, Y, -Z, L / 2, L / 2 + W - T, 0, H, -T, 0, {"+t": ("face", "right"), "-t": ("card",)}, xf=l2,
            closed=closed_right)
    # the two end folds (180 degrees): a half round of radius T joining the layers, along the panel height
    xa = L / 2 + W / 2            # final x of the folds
    for sx in (1, -1):
        Cf = V((sx * (xa - T), T, 0))
        bd.roll(body, Cf, Z, H, T, Y, X * sx, 180, segs=6, plain_ab=lambda q: (q[2], q[1]))
    # crease grooves across the layers where the tube's other two folds were (a printed-looking dark line is enough:
    # a narrow strip a hair above the surface using the crease of the side flute strip)
    for (xc, yv, sgn) in ((-L / 2 + W / 2, 2 * T, 1), (L / 2 - W / 2, 0.0, -1)):
        f = bd.at.flute_fn("side", H, bd.rng)
        w = 0.0012
        pts = [V((xc - w, yv + sgn * 0.00012, -H / 2)), V((xc + w, yv + sgn * 0.00012, -H / 2)),
               V((xc + w, yv + sgn * 0.00012, H / 2)), V((xc - w, yv + sgn * 0.00012, H / 2))]
        S.add_quad(body[0], pts, [f(0, 0.48), f(0, 0.52), f(H, 0.52), f(H, 0.48)], Y * sgn)

    # flaps: (layer, x range, closed mapping kind, closed side)
    flap_specs = [
        (1, -L / 2 + e, L / 2 - e, "major", 1),           # front's flaps
        (1, -L / 2 - W + T + e2, -L / 2 - T - e2, "minor_left", 1),
        (2, -L / 2 + e, L / 2 - e, "major", -1),          # back's flaps
        (2, L / 2 + T + e2, L / 2 + W - T - e2, "minor_right", -1),
    ]
    for layer, x0, x1, kind, sz in flap_specs:
        f_lay = l1 if layer == 1 else l2
        O = fr if layer == 1 else bk
        Nn = Z if layer == 1 else -Z
        depth = W / 2 - T / 2
        for top in (True, False):
            # each flap curls a little: the top layer's flaps lift off the bottom layer's
            deg = rng.uniform(4, 13) if layer == 1 else rng.uniform(0.0, 1.5)
            yv0, yv1 = (H, H + depth) if top else (-depth, 0.0)
            hinge_y = H if top else 0.0
            # final-space hinge line: the flap's outer edge at the crease; positive turns lift a top flap
            hp = f_lay(V((0, hinge_y, O[2])))
            xf = tilt(f_lay, hp, (1, 0, 0), deg if top else -deg)

            if kind == "major":
                def cl(p, top=top, sz=sz):
                    return closed_major_top(p, sz) if top else closed_major_bot(p, sz)
                face = "top" if top else "bottom"
                spec_out = ("face", face)
            else:
                cl = None
                spec_out = ("plain",)
            faces = {"+t": spec_out, "-t": ("card",), "+u": ("side",), "-u": ("side",)}
            faces["+v" if top else "-v"] = ("wave",)
            bd.slab(body, O, X, Y, Nn, x0, x1, yv0, yv1, -T, 0, faces, xf=xf, closed=cl)
    kit.anchor("A_HIT_0", (0, T * 1.5, 0), (L + W, 3 * T, H + W))
