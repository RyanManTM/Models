"""
cat_psus_art.py - the artwork for build_cat_psus.py: one texture atlas per PSU (spec label with the 80 PLUS badge in
the tier colour, fan hub sticker, grille badge, QC sticker, the printed modular panel, the OLED screen face and, for
CRPS modules, the top label). Brand logos are drawn from simple shapes (fictional brands only).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_b as pb  # noqa: E402

# 80 PLUS badge colours per tier: (face, rim, text on the face)
TIERS = {
    "BRONZE": ("#b0703a", "#5a3418", "#f6f2e6"),
    "GOLD": ("#c9a23a", "#6b5313", "#f6f2e6"),
    "PLATINUM": ("#c9ced6", "#6d737d", "#1b1d22"),
    "TITANIUM": ("#7d838c", "#2f3236", "#f2f3f5"),
}

# label colour schemes per brand: bg, band (top strip), band_ink, ink, sub (small band text), accent
STYLES = {
    "Ampere": dict(bg="#e9e9e6", band="#151517", band_ink="#f4f4f4", ink="#141414", sub="#b9b9bd", accent="#c9a23a",
                   font="eras"),
    "Corvex": dict(bg="#1e1e20", band="#0c0c0d", band_ink="#f2f2f2", ink="#e6e6e6", sub="#f0c419", accent="#f0c419",
                   font="franklin"),
    "Corvex_white": dict(bg="#f4f4f2", band="#e2e2df", band_ink="#151515", ink="#151515", sub="#8a8a8a",
                         accent="#d9a91a", font="franklin"),
    "Seastar": dict(bg="#f2f3f5", band="#0f2a4a", band_ink="#f4f6f8", ink="#14202e", sub="#7fb6e6", accent="#2a8fd6",
                    font="segoe_black"),
    "Seastar_white": dict(bg="#fbfbfb", band="#e9edf2", band_ink="#0f2a4a", ink="#14202e", sub="#2a8fd6",
                          accent="#2a8fd6", font="segoe_black"),
    "Hush": dict(bg="#1b1b1c", band="#0b0b0b", band_ink="#f0f0f0", ink="#dcdcdc", sub="#f39200", accent="#f39200",
                 font="segoe"),
    "Mako": dict(bg="#161617", band="#0a0a0a", band_ink="#f0f0f0", ink="#dedede", sub="#d4141c", accent="#d4141c",
                 font="franklin"),
    "Aegis": dict(bg="#121214", band="#0a0a0b", band_ink="#f0f0f0", ink="#dedede", sub="#e0102a", accent="#e0102a",
                  font="agency"),
    "Strata": dict(bg="#f4f4f2", band="#1d3d6b", band_ink="#f4f4f4", ink="#141414", sub="#a9c4e6", accent="#2a6db5",
                   font="arialb"),
}


def logo(cv, brand, x, y, h, col, accent, font, align="left"):
    """Draws the brand mark (a shape plus the word) with its left edge (or centre) at x, caps centred on y.
    h = cap height in px. Returns the width drawn."""
    word = brand.upper()
    if brand == "Hush":
        word = "hush"
    tw = pb.text_width(word, font, h, 1.15)
    icon = h * 1.25 if brand in ("Corvex", "Seastar", "Mako", "Aegis", "Strata") else 0.0
    total = icon + (h * 0.35 if icon else 0) + tw + (h * 0.45 if brand == "Hush" else 0)
    x0 = x - total / 2 if align == "center" else x
    ix = x0 + icon / 2
    if brand == "Corvex":  # three sails
        for k, s in enumerate((1.0, 0.8, 0.6)):
            bx = x0 + k * icon * 0.30
            cv.poly([(bx, y + h * 0.62), (bx + icon * 0.28, y - h * 0.62 * s - h * 0.1), (bx + icon * 0.34, y + h * 0.62)], col)
    elif brand == "Seastar":  # a five-point star over a wave
        pts = []
        for k in range(10):
            r = h * 0.62 if k % 2 == 0 else h * 0.26
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((ix + r * math.cos(a), y - h * 0.08 + r * math.sin(a)))
        cv.poly(pts, accent)
        cv.rect(x0, y + h * 0.52, icon, h * 0.12, col)
    elif brand == "Mako":  # a shark fin
        cv.poly([(x0, y + h * 0.6), (x0 + icon * 0.55, y - h * 0.7), (x0 + icon * 0.48, y - h * 0.1),
                 (x0 + icon, y + h * 0.6)], accent)
    elif brand == "Aegis":  # a shield with an eye slit
        cv.poly([(ix - icon * 0.45, y - h * 0.62), (ix + icon * 0.45, y - h * 0.62), (ix + icon * 0.42, y + h * 0.1),
                 (ix, y + h * 0.66), (ix - icon * 0.42, y + h * 0.1)], accent)
        cv.poly([(ix - icon * 0.30, y - h * 0.12), (ix + icon * 0.30, y - h * 0.20), (ix + icon * 0.10, y + h * 0.02),
                 (ix - icon * 0.30, y + h * 0.02)], "#0a0a0b")
    elif brand == "Strata":  # stacked layers
        for k in range(3):
            cv.rect(x0 + k * icon * 0.08, y - h * 0.6 + k * h * 0.42, icon * (1 - k * 0.16), h * 0.3, accent if k == 1 else col)
    tx = x0 + icon + (h * 0.35 if icon else 0)
    cv.text(word, tx, y, h, col, font, "left", "center", spacing=1.15)
    if brand == "Hush":
        cv.text("!", tx + tw + h * 0.08, y, h, accent, font, "left", "center")
    return total


def badge80(cv, bx, by, w, tier):
    face, rim, txt = TIERS[tier]
    ink = "#141414"
    hgt = w * 300 / 230
    cv.rect(bx, by, w, hgt, rim, r=w * 0.08)
    cv.rect(bx + w * 0.045, by + w * 0.045, w * 0.91, hgt - w * 0.09, face, r=w * 0.05)
    cx = bx + w / 2
    cv.circle(cx, by + w * 0.5, w * 0.374, "#f6f2e6")
    cv.text("80", cx, by + w * 0.452, w * 0.278, ink, "black", "center", "center")
    cv.text("PLUS", cx, by + w * 0.696, w * 0.113, ink, "arialb", "center", "center", spacing=1.3)
    cv.text(tier, cx, by + w * 1.078, w * 0.148, txt, "arialb", "center", "center", maxw=w * 0.83)


def make_texture(pid, s, panel=None, panel_rect=None):
    """The atlas for one ATX/SFX unit. panel: the socket layout [(name, kind, u, v, text)], panel_rect (u0, v0, u1, v1)."""
    st = STYLES[s["style"]]
    at = pb.Atlas(2048, 2048)
    at.add("label", 0, 0, 1600, 922)
    at.add("hub", 1600, 0, 448, 448)
    at.add("badge", 1600, 448, 448, 448)
    at.add("qc", 1600, 1024, 256, 128)
    at.add("oled", 1600, 1200, 448, 160)
    at.add("swatch", 1880, 1024, 64, 64)
    cv = pb.Canvas(2048, 2048, bg="#101011")
    W, Hh = 1600, 922
    ink = st["ink"]
    tier = s["tier"]
    face = TIERS[tier][0]
    # ---------------------------------------------------------------- spec label
    cv.rect(0, 0, W, Hh, st["bg"])
    cv.rect(0, 0, W, 190, st["band"])
    cv.poly([(0, 190), (520, 190), (470, 230), (0, 230)], st["band"])
    logo(cv, s["brand"], 60, 92, 70, st["band_ink"], st["accent"], st["font"])
    cv.text(s["series"].upper(), 64, 160, 22, st["sub"], "arialb", "left", "center", spacing=1.6)
    cv.text(f"{s['watts']}W", W - 60, 96, 96, st["band_ink"], "franklin", "right", "center")
    sub = {"none": "ATX12V  v3.0", "semi": "SEMI MODULAR", "full": "FULLY MODULAR"}[s["modular"]]
    if s.get("atx3"):
        sub = f"{sub}  |  ATX {s['atx3']}"
    cv.text(sub, W - 64, 162, 22, face if tier != "PLATINUM" else st["sub"], "arialb", "right", "center", spacing=1.4)
    badge80(cv, 1300, 250, 230, tier)
    cv.text("MODEL: " + s["code"], 60, 272, 30, ink, "arialb", "left", "center")
    cv.text("AC INPUT: 100-240V~  " + s.get("amps", "15-8A") + "  50/60Hz", 60, 322, 24, ink, "arial", "left", "center")
    cv.text(f"EFFICIENCY: {s['eff']} @ 50% LOAD", 60, 362, 24, ink, "arial", "left", "center")
    tx, ty, tw = 60, 410, 1180
    a12 = f"{s['watts'] / 12.0:.1f}A".replace(".0A", "A")
    rails = [("+3.3V", s.get("a33", "20A")), ("+5V", s.get("a5", "20A")), ("+12V", a12), ("-12V", "0.3A"),
             ("+5Vsb", s.get("asb", "3A"))]
    combined = [s.get("c335", "100W"), f"{s['watts']}W", "3.6W", "15W"]
    cols = ["DC OUTPUT"] + [r[0] for r in rails]
    colw = [260] + [184] * 5
    rows = ["MAX LOAD"] + [r[1] for r in rails]
    comb = ["MAX COMBINED"] + [combined[0], "", combined[1], combined[2], combined[3]]
    rh = 62
    cv.frame_rect(tx, ty, tw, rh * 3 + 50, 3, ink)
    x = tx
    for k, cw in enumerate(colw):
        if k > 0:
            cv.rect(x, ty, 3, rh * (2 if k == 2 else 3), ink)
        cv.text(cols[k], x + cw / 2, ty + rh / 2, 22, ink, "arialb", "center", "center", maxw=cw - 16)
        cv.text(rows[k], x + cw / 2, ty + rh * 1.5, 22, ink, "arial" if k else "arialb", "center", "center", maxw=cw - 16)
        if k != 2:
            cv.text(comb[k], x + (cw * (2 if k == 1 else 1)) / 2, ty + rh * 2.5, 22, ink, "arial" if k else "arialb",
                    "center", "center", maxw=cw * (2 if k == 1 else 1) - 16)
        x += cw
    for k in (1, 2, 3):
        cv.rect(tx, ty + rh * k, tw, 3, ink)
    cv.text(f"TOTAL POWER: {s['watts']}W", tx + tw / 2, ty + rh * 3 + 25, 24, ink, "arialb", "center", "center")
    cv.rect(60, 690, 1180, 2, "#888888")
    warn = ["CAUTION: HAZARDOUS VOLTAGE INSIDE. DO NOT REMOVE THE COVER.",
            "NO USER SERVICEABLE PARTS INSIDE. REFER SERVICING TO QUALIFIED PERSONNEL.",
            "FOR INDOOR USE ONLY. SWITCH OFF AND UNPLUG BEFORE CONNECTING CABLES."]
    cv.poly([(80, 760), (118, 704), (156, 760)], "#f0c419")
    cv.text("!", 118, 738, 30, "#141414", "black", "center", "center")
    for k, w in enumerate(warn):
        cv.text(w, 180, 712 + k * 26, 16, ink, "arialb", "left", "center", maxw=1060)
    for k, mk in enumerate(["CE", "FC", "UKCA", "RoHS", "TUV"]):
        mx = 60 + k * 120
        cv.frame_rect(mx, 800, 100, 64, 3, ink, r=8)
        cv.text(mk, mx + 50, 832, 24, ink, "arialb", "center", "center", maxw=84)
    cv.rect(770, 790, 460, 110, "#f4f4f2")
    cv.barcode(780, 800, 440, 76, seed=s["watts"] + len(pid))
    sn = f"S/N: {s['code'].replace('-', '')[:6]}{2409 + len(pid)}A0{(s['watts'] * 7 + len(pid) * 131) % 9973:05d}"
    cv.text(sn, 1000, 888, 18, "#141414", "mono", "center", "center")
    cv.text("MADE IN CHINA", 60, 892, 18, ink, "arialb", "left", "center")
    cv.text(s.get("www", f"www.{s['brand'].lower()}-power.example"), 1300, 620, 16, "#777777", "arial", "left", "center",
            maxw=280)
    # ---------------------------------------------------------------- fan hub sticker and grille badge
    for name in ("hub", "badge"):
        x0, y0, w, h = at.px(name)
        cxp, cyp = x0 + w / 2, y0 + h / 2
        cv.rect(x0, y0, w, h, "#0d0d0e")
        cv.circle(cxp, cyp, w * 0.49, s.get("hub_bg", "#141416"))
        cv.ring(cxp, cyp, w * 0.42, w * 0.44, st["accent"] if name == "hub" else face)
        logo(cv, s["brand"], cxp, cyp, 46, s.get("hub_ink", "#ededee"), st["accent"], st["font"], "center")
    x0, y0, w, h = at.px("qc")
    cv.rect(x0, y0, w, h, "#f2f2f0")
    cv.text("QC PASS", x0 + w / 2, y0 + 44, 30, "#1a7a2a", "arialb", "center", "center")
    cv.text("2409", x0 + w / 2, y0 + 92, 22, "#1a1a1a", "mono", "center", "center")
    x0, y0, w, h = at.px("swatch")
    cv.rect(x0, y0, w, h, st["accent"])
    # ---------------------------------------------------------------- OLED screen face (wattage read-out)
    x0, y0, w, h = at.px("oled")
    cv.rect(x0, y0, w, h, "#040405")
    cv.text(f"{int(s['watts'] * 0.38)}", x0 + 300, y0 + 80, 84, "#f2f6ff", "franklin", "right", "center")
    cv.text("W", x0 + 316, y0 + 98, 44, "#9fb4d8", "arialb", "left", "center")
    cv.text("OUT", x0 + 316, y0 + 46, 22, "#9fb4d8", "arialb", "left", "center")
    for k in range(6):
        cv.rect(x0 + 380, y0 + 128 - k * 20, 40, 12, "#e0102a" if k > 3 else "#f2f6ff")
    # ---------------------------------------------------------------- modular panel print
    if panel:
        u0, v0, u1, v1 = panel_rect
        pw = int(min(1536, 1000 * (u1 - u0) / (v1 - v0)))
        ph = int(round(pw * (v1 - v0) / (u1 - u0)))
        at.add("panel", 0, 1024, pw, ph)
        x0, y0, w, h = at.px("panel")
        k = w / (u1 - u0)

        def P(u, v):
            return x0 + (u - u0) * k, y0 + (v1 - v) * k

        cv.rect(x0, y0, w, h, "#121213")
        wht = "#e6e6e6"
        for (name, kind, u, v, text, sw, sh) in panel:
            px, py = P(u - sw / 2 - 0.0012, v + sh / 2 + 0.0012)
            cv.frame_rect(px, py, (sw + 0.0024) * k, (sh + 0.0024) * k, 3, "#4a4a4e", r=6)
            if text:
                tx_, ty_ = P(u, v - sh / 2 - 0.0030)
                cv.text(text, tx_, ty_, 17, wht, "arialb", "center", "center", maxw=(sw + 0.006) * k)
        hint = s.get("panel_hint", f"USE ONLY {s['brand'].upper()} MODULAR CABLES")
        tx_, ty_ = P((u0 + u1) / 2, v0 + 0.0022)
        cv.text(hint, tx_, ty_, 14, "#bdbdc0", "arialb", "center", "center", maxw=w - 40)
    cv.render(pid)
    return at


def make_crps_texture(pid, s):
    """The atlas for a CRPS module: the top label, the handle grip print and the status legend."""
    st = STYLES["Strata"]
    at = pb.Atlas(2048, 1024)
    at.add("label", 0, 0, 1600, 640)
    at.add("legend", 1600, 0, 448, 256)
    at.add("swatch", 1600, 300, 64, 64)
    at.add("hub", 1700, 300, 256, 256)
    cv = pb.Canvas(2048, 1024, bg="#101011")
    ink = st["ink"]
    W, H = 1600, 640
    cv.rect(0, 0, W, H, st["bg"])
    cv.rect(0, 0, W, 120, st["band"])
    logo(cv, "Strata", 50, 60, 52, st["band_ink"], "#7fb0e8", st["font"])
    cv.text(f"{s['watts']}W  CRPS HOT-PLUG POWER SUPPLY", W - 50, 60, 34, st["band_ink"], "arialb", "right", "center",
            maxw=880)
    badge80(cv, 1340, 150, 200, s["tier"])
    cv.text("MODEL: " + s["code"], 50, 170, 30, ink, "arialb", "left", "center")
    cv.text("AC INPUT: " + s["ac"], 50, 216, 24, ink, "arial", "left", "center", maxw=1240)
    cv.text("DC OUTPUT: " + s["dc"], 50, 256, 24, ink, "arial", "left", "center", maxw=1240)
    cv.text(f"EFFICIENCY: {s['eff']} @ 50% LOAD (230 V)", 50, 296, 24, ink, "arial", "left", "center")
    cv.rect(50, 330, 1240, 2, "#888888")
    cv.text("HOT SWAP: PULL THE LATCH, THEN THE HANDLE. LED: GREEN = OK, AMBER = FAULT, BLINK = STANDBY.", 50, 360, 18,
            ink, "arialb", "left", "center", maxw=1240)
    cv.text("CAUTION: DISCONNECT THE AC CORD BEFORE SERVICING. MULTIPLE POWER SOURCES.", 50, 390, 18, ink, "arialb",
            "left", "center", maxw=1240)
    for k, mk in enumerate(["CE", "FC", "UL", "RoHS", "TUV", "CCC"]):
        mx = 50 + k * 115
        cv.frame_rect(mx, 430, 100, 60, 3, ink, r=8)
        cv.text(mk, mx + 50, 460, 22, ink, "arialb", "center", "center", maxw=84)
    cv.barcode(800, 430, 480, 120, seed=s["watts"])
    cv.text(f"S/N: CN0{s['watts']}{s['code'][-3:]}7A{s['watts'] * 13 % 99991:05d}", 1040, 580, 20, ink, "mono",
            "center", "center")
    cv.text("PPID / DP/N " + s["code"], 50, 540, 22, ink, "mono", "left", "center")
    cv.text("REV A01", 50, 580, 20, ink, "mono", "left", "center")
    x0, y0, w, h = at.px("legend")
    cv.rect(x0, y0, w, h, "#1a1a1c")
    cv.text(f"{s['watts']}W", x0 + w / 2, y0 + 70, 64, "#f0f0f0", "franklin", "center", "center")
    cv.text(s["tier"], x0 + w / 2, y0 + 150, 34, TIERS[s["tier"]][0], "arialb", "center", "center")
    cv.text("HOT PLUG", x0 + w / 2, y0 + 210, 26, "#bdbdc0", "arialb", "center", "center")
    x0, y0, w, h = at.px("swatch")
    cv.rect(x0, y0, w, h, s["latch_col"])
    x0, y0, w, h = at.px("hub")
    cv.rect(x0, y0, w, h, "#0d0d0e")
    cv.circle(x0 + w / 2, y0 + h / 2, w * 0.48, "#141416")
    logo(cv, "Strata", x0 + w / 2, y0 + h / 2, 30, "#ededee", "#7fb0e8", "arialb", "center")
    cv.render(pid)
    return at
