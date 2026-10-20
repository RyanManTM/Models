"""
parts_fan.py - a reusable, realistic PC fan: case fans, CPU cooler fans, GPU fans, PSU fans.

    import parts_fan as pf
    a = c.anchor("A_FAN_0", (0.188, 0.355, 0.03), (0.12, 0.12, 0.03), root, forward=(-1, 0, 0), up=(0, 1, 0),
                 meta=pf.fan_meta(spin="ccw", rpm=1200))
    rotor = pf.make_fan(a, diameter=0.12, thickness=0.025, blades=7, frame=True, rgb=False)

make_fan(parent_or_anchor, centre=None, diameter=0.12, thickness=0.025, blades=7, frame=True, rgb=False, **opts)
  parent_or_anchor  an anchor empty (A_FAN_<n>): the fan is built on the anchor's pose (centre/axis/up default
                    to it), the ROTOR becomes moving pieces '<name>_rotor@A_FAN_<n>#<tag>' (+ '_sticker@...'),
                    the static parts (frame, stator struts, motor, label, rgb ring) are plain objects under the
                    model root (dct_common.join_by_tag merges them with the rest).
                    Or any other parent (the model root): everything, rotor included, is static geometry
                    under it (it will be joined - pass an anchor if the rotor must spin).
  centre            Unity point at the middle of the fan's thickness.
  diameter          frame=True: nominal size = outer frame square (0.08, 0.092, 0.12, 0.14);
                    frame=False: blade tip diameter.
  thickness         frame=True: frame depth (0.025 typical, 0.015 slim); frame=False: rotor + stator depth.
  blades            blade count (7 for case fans, 9-11 for GPU fans).
  frame             square frame with flanges, venturi bore, corner holes (4.3 mm at the standard spacing),
                    corner pillars and webs, and stator struts at the back. False = frameless (GPU / stock
                    cooler fans): just the stator struts, the motor and an optional thin stator ring.
  rgb               adds 'rgb' diffuser rings (front and back of the bore, or the stator ring when frameless).
Options:
  axis, up          the fan's front direction (intake side, where the hub sticker is) and the frame's up.
  spin              'ccw' or 'cw' as seen from the front (intake). Most PC fans: 'ccw'. The blades are curved
                    and pitched for that direction. fan_meta(spin) gives the anchor meta for the game.
  name              object name prefix (default fan<serial>; keep it unique per model).
  blade_tag, frame_tag, rgb_tag     material tags (default fan_black, fan_black, rgb); the hub is moulded with
                    the blades (blade_tag); hub_tag is accepted for compatibility and ignored.
  sticker           texture file for the hub sticker (tag 'tex_<sticker>'; the disc maps to the circle
                    inscribed in sticker_uv=(u0, v0, u1, v1), default the whole image, see
                    hub_sticker_texture); None = a plain disc tagged sticker_tag.
  label, label_uv   texture file (and UV rect) for the round label on the back of the motor (None = a
                    plain label_tag disc).
  struts            stator strut count (default 4 framed, 3 frameless; 0 = none).
  tip_ring          a ring joining the blade tips (some GPU fans).
  stator_ring       frameless only: the thin ring the struts hang from (default True).
  hub_ratio, cov, sweep, camber, res        blade shape overrides (hub radius / diameter, (root, tip)
                    coverage of the blade pitch, forward sweep in radians, camber, (radial, chord) segments).
  return_all        return a dict {rotor, sticker, static: [objects], exit: Unity point} instead of the rotor.
Returns the rotor object (the blades and hub mesh); it spins about the anchor's local +Z.

cable_exit(centre, diameter, thickness, axis, up, frame=True, corner=(-1, -1)) gives the Unity point at the back
of the frame corner (or the stator ring) where a fan's cable leaves, to start a cable towards its A_PLUG_FAN_<n>.

fan_meta(spin='ccw', rpm=1500) -> 'axis=z,spin=-1,rpm=1500': spin is the sign of the Unity rotation angle about
the anchor's local +Z while running (+1 = clockwise seen from the front).
hub_sticker_texture(file, brand, sub=None, bg, fg, accent, font, size) and motor_label_texture(file, brand, model)
render round sticker PNGs into Assets/Resources/Models/Textures (use them as sticker= / label=).
"""
import math

import dct_common as c
import parts_b as pb
from mathutils import Matrix, Vector as V

TAU = pb.TAU
_serial = [0]

HOLE_SPACING = {0.08: 0.0715, 0.092: 0.0825, 0.12: 0.105, 0.14: 0.1245}


def fan_meta(spin="ccw", rpm=1500, extra=""):
    """Anchor meta for a fan: axis=z, spin sign of the Unity rotation about local +Z (+1 = clockwise seen from
    the front), and a nominal full-speed rpm."""
    s = -1 if spin == "ccw" else 1
    m = f"axis=z,spin={s:+d},rpm={rpm}"
    return m + ("," + extra if extra else "")


def blade_geo(r0, r1, z0, z1, n_blades, cov=(0.62, 0.92), sweep=0.32, camber=0.3, t_root=0.0018, t_tip=0.0010,
              nr=9, nc=7, depth_tip=0.82):
    """One blade in fan space (axis +Z = front), turning towards +theta (x -> y): the leading edge is at the
    front (+Z) and ahead in the turning direction; it is cambered, twisted (the pitch falls towards the tip
    because the blade's axial depth is fixed while its arc grows) and swept forward."""
    D = z1 - z0
    zc = (z0 + z1) / 2
    pitch = TAU / n_blades
    top, bot = [], []
    for i in range(nr + 1):
        u = i / nr
        r = r0 + (r1 - r0) * u
        cv = pb.lerp(cov[0], cov[1], u ** 0.8)
        ext = cv * pitch
        d = D * pb.lerp(1.0, depth_tip, u)
        thc = sweep * (u ** 1.6)
        th_half = 0.5 * pb.lerp(t_root, t_tip, u)
        for j in range(nc + 1):
            s = -0.5 + j / nc
            th = thc + s * ext
            z = zc + s * d + camber * d * (0.25 - s * s)
            tp = th_half * (0.35 + 0.65 * math.sqrt(max(0.0, 1.0 - (2 * s) ** 2)))
            x, y = r * math.cos(th), r * math.sin(th)
            top.append(V((x, y, z + tp)))
            bot.append(V((x, y, z - tp)))
    verts = top + bot
    off = len(top)
    W = nc + 1

    def T(i, j):
        return i * W + j

    def B(i, j):
        return off + i * W + j

    faces = []
    for i in range(nr):
        for j in range(nc):
            faces.append([T(i, j), T(i + 1, j), T(i + 1, j + 1), T(i, j + 1)])
            faces.append([B(i, j), B(i, j + 1), B(i + 1, j + 1), B(i + 1, j)])
    for i in range(nr):
        faces.append([T(i, nc), T(i + 1, nc), B(i + 1, nc), B(i, nc)])  # leading edge
        faces.append([T(i, 0), B(i, 0), B(i + 1, 0), T(i + 1, 0)])  # trailing edge
    for j in range(nc):
        faces.append([T(nr, j), B(nr, j), B(nr, j + 1), T(nr, j + 1)])  # tip
        faces.append([T(0, j), T(0, j + 1), B(0, j + 1), B(0, j)])  # root
    return verts, faces, None


def rotor_geo(n_blades, r_hub, r_tip, z_back, z_front, spin="ccw", cov=(0.62, 0.92), sweep=0.32, camber=0.3,
              res=(9, 7), tip_ring=False, hub_front=None, t_root=0.0018, t_tip=0.001):
    """(blades+hub geometry, sticker centre z, sticker radius) in fan space."""
    zb = z_back
    zf = hub_front if hub_front is not None else z_front + 0.0004
    parts = []
    one = blade_geo(r_hub - 0.0008, r_tip, z_back + 0.0006, z_front, n_blades, cov, sweep, camber,
                    t_root, t_tip, res[0], res[1])
    for k in range(n_blades):
        parts.append(pb.xf(one, pb.rot("z", TAU * k / n_blades)))
    # hub: a cup with a rounded front rim and a shallow recess for the sticker
    f = min(0.0018, r_hub * 0.15)
    rs = r_hub * 0.82
    prof = [(0.0, zb), (r_hub - 0.0006, zb), (r_hub, zb + 0.0006), (r_hub, zf - f)]
    for k in range(1, 4):
        a = 90 * k / 4 * pb.DEG
        prof.append((r_hub - f + f * math.cos(a), zf - f + f * math.sin(a)))
    prof += [(r_hub - f, zf), (rs + 0.0004, zf), (rs + 0.0002, zf - 0.0003), (0.0, zf - 0.0003)]
    parts.append(pb.g_lathe(prof, 48))
    if tip_ring:
        d_tip = (z_front - z_back) * 0.82
        zc = (z_front + z_back) / 2 + 0.0
        parts.append(pb.xf(pb.g_ring(r_tip - 0.0004, r_tip + 0.0004, d_tip * 0.85, 96), None, (0, 0, zc)))
    geo = pb.merge(*parts)
    if spin == "ccw":
        geo = pb.xf(geo, Matrix(((-1, 0, 0), (0, 1, 0), (0, 0, 1))))
    return geo, zf - 0.0003, rs


def make_fan(parent_or_anchor, centre=None, diameter=0.12, thickness=0.025, blades=7, frame=True, rgb=False,
             axis=None, up=None, spin="ccw", name=None, blade_tag="fan_black", hub_tag=None, frame_tag="fan_black",
             sticker=None, sticker_tag="grey_plastic", label=None, label_tag="white_plastic", struts=None,
             tip_ring=False, stator_ring=True, hub_ratio=None, cov=None, sweep=None, camber=0.3, rgb_tag="rgb",
             res=(9, 7), sticker_uv=(0, 0, 1, 1), label_uv=(0, 0, 1, 1), return_all=False):
    _serial[0] += 1
    name = name or f"fan{_serial[0]}"
    hub_tag = hub_tag or blade_tag
    anchor = parent_or_anchor if pb.is_anchor(parent_or_anchor) else None
    root = c.top_of(parent_or_anchor) if anchor is not None else parent_or_anchor
    if anchor is not None:
        apos, afwd, aup = pb.unity_pose(anchor)
        centre = apos if centre is None else centre
        axis = afwd if axis is None else axis
        up = aup if up is None else up
    axis = V(axis if axis is not None else (0, 0, 1))
    up = V(up if up is not None else ((0, 1, 0) if abs(axis.normalized().y) < 0.9 else (0, 0, 1)))
    M = pb.frame(axis, up)
    t = V(centre)
    h = thickness / 2

    stat = {}  # tag -> MB (static)
    rot_mb = {}  # tag -> MB (rotor)

    def S(tag):
        return stat.setdefault(tag, pb.MB())

    def R(tag):
        return rot_mb.setdefault(tag, pb.MB())

    if frame:
        Sz = diameter
        wall = max(0.0012, Sz * 0.0105)
        Rb = Sz / 2 - wall  # throat of the venturi
        Rf = min(Rb + 0.0016, Sz / 2 - 0.0007)  # flared intake
        r_tip = Rb - 0.0011
        ft = 0.0032 if thickness >= 0.02 else 0.0025
        rc = 0.0045 if Sz >= 0.1 else 0.0035
        hs = HOLE_SPACING.get(round(Sz, 3), Sz * 0.875)
        r_hole = 0.00215
        corners = [(sx * hs / 2, sy * hs / 2) for sx in (-1, 1) for sy in (-1, 1)]
        holes_f = [pb.circle2(0, 0, Rf, 112)] + [pb.circle2(x, y, r_hole, 16) for (x, y) in corners]
        holes_b = [pb.circle2(0, 0, Rb, 112)] + [pb.circle2(x, y, r_hole, 16) for (x, y) in corners]
        outer = pb.rrect2(0, 0, Sz, Sz, rc, 4)
        fr = S(frame_tag)
        fr.add(pb.g_slab(outer, holes_f, ft, h - ft), M, t)
        fr.add(pb.g_slab(outer, holes_b, ft, -h), M, t)
        # venturi wall between the flanges, flared at the intake
        z0, z1 = -h + ft - 0.0002, h - ft + 0.0002
        ro = Sz / 2 - 0.0004
        prof = [(Rb, z0), (ro, z0), (ro, z1), (Rf, z1), (Rf - 0.0006, z1 - 0.0012), (Rb + 0.0002, z1 - 0.0035),
                (Rb, z1 - 0.005), (Rb, z0)]
        fr.add(pb.g_lathe(prof, 112), M, t)
        # corner pillars round the screw holes, and webs to the venturi
        L = thickness - 2 * ft + 0.0004
        for (x, y) in corners:
            fr.add(pb.g_ring(r_hole, 0.0046, L, 20), M, t + M @ V((x, y, 0)))
            d = V((x, y, 0)).normalized()
            r_a, r_b = ro - 0.0005, V((x, y, 0)).length - 0.004
            mid = d * (r_a + r_b) / 2
            web = pb.xf(pb.g_box((r_b - r_a, 0.0014, L)), pb.rot("z", math.atan2(y, x)), mid)
            fr.add(web, M, t)
        # little side ribs at the middle of each side (most frames are open at the corners only)
        z_back, z_front = -h + 0.0068, h - 0.0016
        r_hub = Sz * (hub_ratio or 0.172)
        n_struts = 4 if struts is None else struts
        strut_to = Rb + 0.0006
        motor_r = r_hub * 0.93
        motor_z0, motor_z1 = -h, -h + 0.006
        if rgb:
            for zz, rr in ((h + 0.00015, Rf), (-h - 0.00015, Rb)):
                S(rgb_tag).add(pb.g_ring(rr - 0.0003, rr + 0.0011, 0.0008, 112), M, t + M @ V((0, 0, zz)))
    else:
        r_tip = diameter / 2
        r_hub = diameter * (hub_ratio or 0.2)
        n_struts = 3 if struts is None else struts
        z_back, z_front = -h + 0.0048, h - 0.0004
        strut_to = r_tip + 0.0022
        motor_r = r_hub * 0.9
        motor_z0, motor_z1 = -h, -h + 0.0042
        if stator_ring and n_struts > 0:
            S(frame_tag).add(pb.g_ring(r_tip + 0.0014, r_tip + 0.0030, 0.0035, 96), M, t + M @ V((0, 0, -h + 0.00175)))
            if rgb:
                S(rgb_tag).add(pb.g_ring(r_tip + 0.0016, r_tip + 0.0028, 0.0006, 96), M, t + M @ V((0, 0, -h + 0.0038)))
        elif rgb:
            S(rgb_tag).add(pb.g_ring(r_hub * 0.86, r_hub * 0.96, 0.0006, 64), M, t + M @ V((0, 0, z_front + 0.0007)))

    # stator: motor housing and struts at the back
    st = S(frame_tag)
    st.add(pb.g_cyl(motor_r, motor_z1 - motor_z0, 40, bevel=0.0006), M, t + M @ V((0, 0, (motor_z0 + motor_z1) / 2)))
    for k in range(n_struts):
        a = TAU * k / n_struts + (math.pi / 4 if n_struts == 4 else math.pi / 2)
        r_a, r_b = motor_r - 0.001, strut_to
        mid = V((math.cos(a), math.sin(a), 0)) * (r_a + r_b) / 2
        bar = pb.g_box((r_b - r_a, 0.0032 if frame else 0.0026, 0.0034 if frame else 0.0028), bevel=0.0004)
        bar = pb.xf(bar, pb.rot("x", 28 * pb.DEG))
        st.add(pb.xf(bar, pb.rot("z", a), mid + V((0, 0, -h + 0.0019))), M, t)
    # round label on the back of the motor
    lab = pb.g_disc(motor_r * 0.86, 40, uv_rect=label_uv, depth=0.00008)
    lab_fr = Matrix(((1, 0, 0), (0, 1, 0), (0, 0, -1)))  # faces -Z (the back), reads correctly from behind
    if label:
        S("tex_" + label).add(pb.xf(lab, lab_fr), M, t + M @ V((0, 0, motor_z0 - 0.00005)))
    else:
        S(label_tag).add(pb.xf(lab, lab_fr), M, t + M @ V((0, 0, motor_z0 - 0.00005)))

    # rotor
    if cov is None:
        cov = (0.62, 0.92) if frame else (0.82, 1.06) if blades >= 9 else (0.7, 0.98)
    if sweep is None:
        sweep = 0.32 if frame else 0.42
    t_root, t_tip = (0.0018, 0.0010) if diameter >= 0.1 else (0.0014, 0.0008)
    geo, z_st, r_st = rotor_geo(blades, r_hub, r_tip, z_back, z_front, spin, cov, sweep, camber, res, tip_ring,
                                t_root=t_root, t_tip=t_tip)
    R(blade_tag).add(geo, M, t)  # hub and blades share a builder when the tags match
    if hub_tag != blade_tag:
        pass  # (hub drawn in blade_tag; a separate hub colour would need a split - keep one plastic)
    disc = pb.xf(pb.g_disc(r_st, 48, uv_rect=sticker_uv, depth=0.0001), Matrix(((-1, 0, 0), (0, 1, 0), (0, 0, 1))))  # reads from the front
    if sticker:
        R("tex_" + sticker).add(disc, M, t + M @ V((0, 0, z_st + 0.00011)))
    else:
        R(sticker_tag).add(disc, M, t + M @ V((0, 0, z_st + 0.00011)))

    # build objects
    static_objs = []
    for tag, mb in stat.items():
        if mb.f:
            static_objs.append(pb.build_mesh(mb, f"{name}_{tag.replace('tex_', 't_')}", tag, root))
    rotor_obj, sticker_obj = None, None
    holder = anchor if anchor is not None else root
    for tag, mb in rot_mb.items():
        if not mb.f:
            continue
        nm = f"{name}_rotor" if tag == blade_tag else f"{name}_sticker"
        if anchor is None:
            nm = f"{name}_{'rotor' if tag == blade_tag else 'sticker'}_static"
        o = pb.build_mesh(mb, nm, tag, holder)
        if tag == blade_tag:
            rotor_obj = o
        else:
            sticker_obj = o
    if return_all:
        return {"rotor": rotor_obj, "sticker": sticker_obj, "static": static_objs,
                "exit": cable_exit(t, diameter, thickness, axis, up, frame)}
    return rotor_obj


def cable_exit(centre, diameter, thickness, axis=(0, 0, 1), up=(0, 1, 0), frame=True, corner=(-1, -1)):
    """Unity point where the fan cable leaves: the back of a frame corner (framed) or of the stator ring."""
    M = pb.frame(axis, up)
    h = thickness / 2
    if frame:
        q = diameter / 2 - 0.0065
        local = V((corner[0] * q, corner[1] * q, -h + 0.002))
    else:
        r = diameter / 2 + 0.003
        local = V((corner[0] * r * 0.7071, corner[1] * r * 0.7071, -h + 0.0018))
    return V(centre) + M @ local


def hub_sticker_texture(file, brand, sub=None, bg="#121214", fg="#e8e8ea", accent="#b8bcc4", font="eras", size=512):
    """A round hub sticker: dark disc, a thin accent ring, the brand (and a small sub line). The image is square;
    make_fan maps the hub disc onto it."""
    cv = pb.Canvas(size, size, bg=bg)
    s = size
    cv.ring(s / 2, s / 2, s * 0.43, s * 0.455, accent)
    cv.ring(s / 2, s / 2, s * 0.47, s * 0.5, "#0a0a0b")
    cv.text(brand, s / 2, s / 2 - (s * 0.03 if sub else 0), s * 0.11, fg, font, "center", "center", maxw=s * 0.7)
    if sub:
        cv.text(sub, s / 2, s / 2 + s * 0.13, s * 0.045, accent, "arialb", "center", "center", maxw=s * 0.6)
    return cv.render(file)


def motor_label_texture(file, brand, model="DC 12V 0.20A", bg="#d9d9d6", fg="#1a1a1a", size=512):
    """The round label on the back of a fan motor: brand, model and rating, like the real ones."""
    cv = pb.Canvas(size, size, bg=bg)
    s = size
    cv.text(brand, s / 2, s * 0.36, s * 0.085, fg, "arialb", "center", "center", maxw=s * 0.62)
    cv.text(model, s / 2, s * 0.52, s * 0.05, fg, "arial", "center", "center", maxw=s * 0.7)
    cv.text("DC BRUSHLESS", s / 2, s * 0.64, s * 0.04, fg, "arial", "center", "center", maxw=s * 0.6)
    cv.barcode(s * 0.33, s * 0.72, s * 0.34, s * 0.06, seed=len(brand))
    return cv.render(file)
