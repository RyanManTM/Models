"""
rig_common: helpers for the retail packaging rigs (box_<partid>, built by build_boxes.py). Owner: Blender agent B.

The contract is Logs/UNBOXING.md section 2.2. Everything here takes UNITY coordinates (via parts_c / dct_common).

  * Rig: one packaging model. Its anchors carry the opening steps (A_SEAL, A_TAPE, A_FLAP, A_LID, A_SLEEVE,
    A_INSERT_<KIND>, A_CLAMLID) and the content poses (A_ITEM_PART, A_ITEM_ACC, A_ITEM_DOC, A_ITEM_CORD, A_ITEM_HW,
    A_ITEM_POUCH), with their meta. Removable pieces are meshes named '<piece>@<A_ANCHOR>#<tag>' modelled in the
    closed pose; finalize() joins them per (anchor, tag) and puts each piece's pivot ON its anchor.
  * Nested pieces (a clamshell lid on the clamshell on the tray) are anchors named 'A_CHILD@A_PARENT', the same
    link ModelLibrary already re-parents ('A_SCREW_THUMB_0@A_PANEL_SIDE_0'); the meta repeats it as parent=.
  * Meta: 'key=value' pairs joined by ','. 'under=' is always the LAST key and its value is a comma list of anchor
    base names running to the end of the string. Directions and hinge axes are in the anchor's LOCAL axes (almost
    every anchor here is rotation-free, so local = the box axes). Angles in degrees, Unity rotation sense
    (Quaternion.AngleAxis(open, localAxis)).
  * Geometry helpers for packaging: board panels with a printed skin, thermoformed shells (clamshells, blisters,
    moulded pulp) with real wall thickness, foam blocks with boolean die-cuts.
  * Preview helpers: physically based stand-ins for the new tags (UNBOXING.md 2.1), the part model imported at its
    A_ITEM_PART anchors, placeholders for papers and bags, the opened and the exploded pose.
"""
import bmesh
import bpy
import math
import os
import sys
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ
DEG = math.pi / 180.0
F = P.Frame

# ---------------------------------------------------------------- preview stand-ins for the new material tags

NEW_PBR = {
    # tag: (base colour, metallic, roughness, transmission, alpha)
    "clear_plastic": ((0.90, 0.94, 0.97), 0.0, 0.04, 1.0, 1.0),
    "smoke_plastic": ((0.20, 0.21, 0.23), 0.0, 0.06, 0.85, 1.0),
    "antistatic_pink": ((0.95, 0.52, 0.64), 0.0, 0.22, 0.55, 1.0),
    "antistatic_silver": ((0.32, 0.33, 0.35), 0.55, 0.30, 0.0, 0.45),
    "bag_clear": ((0.95, 0.96, 0.97), 0.0, 0.08, 1.0, 1.0),
    "bubble_wrap": ((0.92, 0.95, 0.97), 0.0, 0.10, 1.0, 1.0),
    "eps_foam": ((0.93, 0.93, 0.91), 0.0, 0.92, 0.0, 1.0),
    "pe_foam": ((0.035, 0.035, 0.04), 0.0, 0.88, 0.0, 1.0),
    "pulp": ((0.60, 0.56, 0.48), 0.0, 0.98, 0.0, 1.0),
    "kraft_paper": ((0.55, 0.40, 0.25), 0.0, 0.9, 0.0, 1.0),
    "paper_white": ((0.88, 0.88, 0.86), 0.0, 0.85, 0.0, 1.0),
    "tape_brown": ((0.55, 0.36, 0.14), 0.0, 0.25, 0.3, 1.0),
    "tape_clear": ((0.93, 0.92, 0.88), 0.0, 0.12, 0.9, 1.0),
    "film_clear": ((0.94, 0.95, 0.96), 0.0, 0.10, 0.95, 1.0),
    "seal_clear": ((0.93, 0.94, 0.95), 0.0, 0.10, 0.85, 1.0),
    "fabric_black": ((0.03, 0.03, 0.032), 0.0, 0.95, 0.0, 1.0),
    "velcro_black": ((0.02, 0.02, 0.022), 0.0, 0.9, 0.0, 1.0),
    "doc_cover": ((0.92, 0.92, 0.90), 0.0, 0.7, 0.0, 1.0),
    "doc_back": ((0.92, 0.92, 0.90), 0.0, 0.7, 0.0, 1.0),
}
PREVIEW_COLOURS = {k: v[0] for k, v in NEW_PBR.items()}
_orig_pbr = P.pbr_material


def pbr_material(tag, lit_leds=False):
    """parts_c.pbr_material plus the packaging tags (renders only)."""
    if tag not in NEW_PBR:
        return _orig_pbr(tag, lit_leds)
    name = "pbr_" + tag
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    col, met, rough, trans, alpha = NEW_PBR[tag]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Metallic"].default_value = met
    b.inputs["Roughness"].default_value = rough
    if trans > 0:
        # thin clear sheets: alpha-blended (as the game will draw them), glossy highlights stay
        b.inputs["Alpha"].default_value = {"smoke_plastic": 0.55, "antistatic_pink": 0.55, "tape_clear": 0.35,
                                           "tape_brown": 0.8}.get(tag, 0.18)
        b.inputs["Roughness"].default_value = min(rough, 0.08)
        try:
            b.inputs["Coat Weight"].default_value = 0.6
        except KeyError:
            pass
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    if tag in ("eps_foam", "pulp", "pe_foam", "kraft_paper", "fabric_black"):
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = {"eps_foam": 900.0, "pulp": 450.0, "pe_foam": 1500.0}.get(tag, 700.0)
        nz.inputs["Detail"].default_value = 6.0
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = {"eps_foam": 0.35, "pulp": 0.5}.get(tag, 0.2)
        bp.inputs["Distance"].default_value = 0.0004
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
        if tag in ("eps_foam", "pulp"):
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            lo = tuple(x * 0.9 for x in col)
            ramp.color_ramp.elements[0].color = (*lo, 1)
            ramp.color_ramp.elements[1].color = (*col, 1)
            nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


P.pbr_material = pbr_material   # parts_c.beauty() looks the function up at call time
for _k, _v in PREVIEW_COLOURS.items():
    c.TAGS.setdefault(_k, _v)


# ---------------------------------------------------------------- small maths

def resample(outline, n):
    """A closed 2D outline resampled to n points evenly by arc length, starting at the point nearest the +x
    direction from its centroid (so rings of different shapes line up for lofting)."""
    raw = [Vector((p[0], p[1])) for p in outline]
    per = sum((raw[(i + 1) % len(raw)] - raw[i]).length for i in range(len(raw)))
    step = per / 512.0
    pts = []                                   # densified, so the start point lands mid-edge on every ring
    for i in range(len(raw)):
        a, b = raw[i], raw[(i + 1) % len(raw)]
        k = max(1, int((b - a).length / step))
        for j in range(k):
            pts.append(a + (b - a) * (j / k))
    cx = sum(p.x for p in raw) / len(raw)
    cy = sum(p.y for p in raw) / len(raw)
    start = max(range(len(pts)), key=lambda i: (pts[i].x - cx) / max(1e-9, (pts[i] - Vector((cx, cy))).length)
                - 0.001 * abs(pts[i].y - cy))
    pts = pts[start:] + pts[:start]
    segs = [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    lens = [(b - a).length for a, b in segs]
    total = sum(lens)
    out = []
    k = 0
    acc = 0.0
    for i in range(n):
        target = total * i / n
        while k < len(segs) - 1 and acc + lens[k] < target:
            acc += lens[k]
            k += 1
        a, b = segs[k]
        t = (target - acc) / max(1e-12, lens[k])
        p = a + (b - a) * t
        out.append((p.x, p.y))
    return out


def rr(w, h, r, cx=0.0, cy=0.0, n=48):
    """A rounded rectangle resampled to n points (for lofted rings)."""
    return resample(P.rrect(w, h, r, cx, cy, 6), n)


def unity_to_blender_matrix():
    return Matrix(((-1, 0, 0), (0, 0, -1), (0, 1, 0)))


# ---------------------------------------------------------------- the rig

ORDER_KEYS = ("shape", "strip", "seg", "peel", "hinge", "open", "lift", "slide", "dist", "tuck", "id", "doc", "form",
              "kind", "tie", "bag", "guard", "coil", "frame", "print", "wrap", "label", "order", "parent", "with")


def meta_str(meta):
    meta = dict(meta)
    under = meta.pop("under", None)
    keys = [k for k in ORDER_KEYS if k in meta] + [k for k in meta if k not in ORDER_KEYS]
    parts = []
    for k in keys:
        v = meta[k]
        if v is None:
            continue
        if isinstance(v, float):
            v = f"{v:.4f}".rstrip("0").rstrip(".")
        parts.append(f"{k}={v}")
    if under:
        if isinstance(under, str):
            under = [under]
        parts.append("under=" + ",".join(under))
    return ",".join(parts)


class Rig:
    """One packaging model under construction."""

    def __init__(self, bid):
        self.bid = bid
        self.root = c.root(bid)
        self.anchors = {}      # base name -> empty
        self.meta = {}         # base name -> dict
        self.parent_of = {}    # base name -> parent anchor base name (hierarchy, from parent= or with=)
        self.frames = {}       # base name -> P.Frame (closed pose)
        self.sizes = {}
        self.extras = {}       # preview-only stand-ins per anchor

    # anchors ---------------------------------------------------------------
    def anchor(self, name, fr_, size, parent=None, **meta):
        if "with_" in meta:
            meta["with"] = meta.pop("with_")
        if parent is not None:
            meta.setdefault("parent", parent)
        frame = fr_ if isinstance(fr_, P.Frame) else P.Frame(fr_)
        e = c.anchor(name, tuple(frame.o), size, None, frame.fwd, frame.up, meta_str(meta) if meta else None)
        if parent is not None:
            e.name = f"{name}@{parent}"
        c.set_parent(e, self.root)
        self.anchors[name] = e
        self.meta[name] = meta
        self.frames[name] = frame
        self.sizes[name] = size
        link = parent or meta.get("with")
        if link:
            self.parent_of[name] = link
        return name

    # pieces ----------------------------------------------------------------
    def own(self, obj, anc, base=None):
        """Makes obj a piece of anchor anc (or a static part of the body when anc is None)."""
        tag = P._tag_of(obj.name)
        b = base or obj.get("base") or obj.name.split("#", 1)[0].split("@", 1)[0]
        obj["base"] = b
        if anc:
            obj.name = f"{b}@{anc}#{tag}"
        else:
            obj.name = f"{b}#{tag}"
        if obj.data is not None:
            obj.data.name = obj.name
        if obj.parent is not self.root:
            c.set_parent(obj, self.root)
        return obj

    def cube(self, name, center, size, tag, frame=P.WORLD, anc=None, bevel=0.0, **kw):
        o = P.cube(name, center, size, tag, frame, parent=self.root, bevel=bevel, **kw)
        return self.own(o, anc, name)

    def slab(self, name, outline, depth, tag, frame=P.WORLD, holes=(), anc=None, **kw):
        o = P.slab(name, outline, depth, tag, frame, holes=holes, parent=self.root, **kw)
        return self.own(o, anc, name)

    def quad(self, name, frame, w, h, tag, uv=(0, 0, 1, 1), anc=None, flip_u=True):
        o = P.quad(name, frame, w, h, tag, self.root, uv=uv, flip_u=flip_u)
        return self.own(o, anc, name)

    def loft(self, name, sections, tag, frame=P.WORLD, anc=None, smooth=50, caps=(True, True), **kw):
        o = P.loft(name, sections, tag, frame, parent=self.root, smooth=smooth, caps=caps, **kw)
        return self.own(o, anc, name)

    def cylinder(self, name, frame, r, h, tag, segs=24, anc=None, z0=None, r2=None, smooth=40, **kw):
        o = P.cylinder(name, frame, r, h, tag, segs, parent=self.root, z0=z0, r2=r2, smooth=smooth, **kw)
        return self.own(o, anc, name)

    def lathe(self, name, profile, tag, frame=P.WORLD, segs=24, anc=None, smooth=40, **kw):
        o = P.lathe(name, profile, tag, frame, segs, parent=self.root, smooth=smooth, **kw)
        return self.own(o, anc, name)

    def tube(self, name, points, radius, tag, anc=None, verts=8):
        o = P.tube(name, points, radius, tag, parent=self.root, verts=verts)
        return self.own(o, anc, name)

    def text(self, name, text, size, depth, tag, frame, font="arialbd.ttf", anc=None, width=None):
        o = P.text3d(name, text, size, depth, tag, frame, font, parent=self.root, width=width)
        return self.own(o, anc, name)

    def emit(self, name, bm, frame, tag, anc=None, smooth=None, **kw):
        o = P.emit(name, bm, frame, tag, self.root, smooth, **kw)
        return self.own(o, anc, name)

    # packaging geometry ----------------------------------------------------
    def board(self, name, frame, w, h, t, inner, anc=None, tex=None, uv=None, e=0.00015, flip_u=True, back_tex=None,
              back_uv=None):
        """A board panel in the frame's XY plane: its OUTER face at local z=0 facing +Z, the board body from
        z=-t to 0 (tag 'inner': cardboard, paper_white or a tex_), and an optional printed skin (tex, uv rect)
        just outside the outer face. back_tex/back_uv print the inner face too (a printed inside)."""
        out = [self.cube(name, (0, 0, -t / 2), (w, h, t), inner, frame, anc)]
        if tex:
            out.append(self.quad(name + "_print", frame.sub(0, 0, e), w, h, tex, uv or (0, 0, 1, 1), anc, flip_u))
        if back_tex:
            bf = F(frame.p(0, 0, -t - e), tuple(-frame.w), tuple(frame.v))
            out.append(self.quad(name + "_printin", bf, w, h, back_tex, back_uv or (0, 0, 1, 1), anc, flip_u))
        return out

    def shell(self, name, rings, t, tag, frame, anc=None, cap=True, smooth=40, up=1.0, ref=0):
        """A thermoformed or moulded sheet with real thickness: rings = [(outline, z), ...] (same point count,
        CCW in the frame's local XY, at local z) skinned in order; the last ring is capped (the floor). The surface
        is the FACE side of the sheet: the band rings[ref] -> rings[ref + 1] (a flat band, e.g. a flange) gets its
        normals toward local +z * up, and the material goes t behind the surface."""
        bm = bmesh.new()
        vr = [[bm.verts.new((p[0], p[1], z)) for p in pts] for pts, z in rings]
        n = len(vr[0])
        for a, b in zip(vr, vr[1:]):
            for k in range(n):
                k2 = (k + 1) % n
                bm.faces.new((a[k], a[k2], b[k2], b[k]))
        if cap:
            f = bm.faces.new(vr[-1])
            bmesh.ops.triangulate(bm, faces=[f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        # the reference band's normals must point to +z*up (the face side)
        band = set(vr[ref]) | set(vr[ref + 1]) if ref + 1 < len(vr) else set(vr[ref])
        nz = sum(f.normal.z * f.calc_area() for f in bm.faces if all(v in band for v in f.verts))
        if nz * up < 0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
            bm.normal_update()
        bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=t)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
        return self.emit(name, bm, frame, tag, anc, smooth=smooth)

    def cut(self, obj, cutters, solver="EXACT"):
        """Boolean difference of cutter objects (created with tmp_*), then removes the cutters."""
        tag = P._tag_of(obj.name)
        for i, ct in enumerate(cutters):
            m = obj.modifiers.new(f"cut{i}", "BOOLEAN")
            m.operation = "DIFFERENCE"
            m.object = ct
            m.solver = solver
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        old = obj.data
        obj.modifiers.clear()
        obj.data = me
        me.name = obj.name
        bpy.data.meshes.remove(old)
        for ct in cutters:
            d = ct.data
            bpy.data.objects.remove(ct)
            if d is not None and d.users == 0:
                bpy.data.meshes.remove(d)
        me.materials.clear()
        me.materials.append(c.mat(tag))
        me.shade_flat()
        return obj

    def union(self, obj, others):
        tag = P._tag_of(obj.name)
        for i, ct in enumerate(others):
            m = obj.modifiers.new(f"un{i}", "BOOLEAN")
            m.operation = "UNION"
            m.object = ct
            m.solver = "EXACT"
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        old = obj.data
        obj.modifiers.clear()
        obj.data = me
        me.name = obj.name
        bpy.data.meshes.remove(old)
        for ct in others:
            d = ct.data
            bpy.data.objects.remove(ct)
            if d is not None and d.users == 0:
                bpy.data.meshes.remove(d)
        me.materials.clear()
        me.materials.append(c.mat(tag))
        return obj

    # finishing ---------------------------------------------------------------
    def finalize(self):
        """Joins the body per tag and each anchor's pieces per tag; pivots pieces on their anchor; box UVs on
        plain tags (tex_ meshes keep their own UVs)."""
        root = self.root
        for ob in c.descendants(root):
            if ob.type != "MESH":
                continue
            # one UV layer named UVMap on every mesh (bmesh quads call theirs 'Float2', curve meshes 'UVMap':
            # joining meshes with different layer names loses the UVs)
            me = ob.data
            if me.uv_layers:
                keep = me.uv_layers.active or me.uv_layers[0]
                for l in list(me.uv_layers):
                    if l != keep:
                        me.uv_layers.remove(l)
                me.uv_layers[0].name = "UVMap"
            if not P._tag_of(ob.name).startswith("tex_"):
                P.box_uv(ob)
        statics, pieces = {}, {}
        for ob in list(root.children):
            if ob.type != "MESH":
                continue
            tag = P._tag_of(ob.name)
            head = ob.name.split("#", 1)[0]
            if "@" in head:
                anc = head.split("@")[1]
                pieces.setdefault((anc, tag), []).append(ob)
            else:
                statics.setdefault(tag, []).append(ob)
        for tag, obs in statics.items():
            base = obs[0].get("base", "body")
            j = P._join(obs)
            nm = f"{self.bid}_{tag}#{tag}"
            if len(nm) > 63:
                nm = f"s_{tag}#{tag}"
            j.name = nm
            j.data.name = j.name
        for (anc, tag), obs in pieces.items():
            base = obs[0].get("base", anc[2:].lower())
            j = P._join(obs)
            nm = f"{base}@{anc}#{tag}"
            if len(nm) > 63:
                nm = f"p@{anc}#{tag}"
            j.name = nm
            j.data.name = j.name
            a = self.anchors.get(anc)
            if a is not None:
                mw = j.matrix_world.copy()
                am = a.matrix_world.copy()
                j.data.transform(am.inverted() @ mw)
                j.matrix_world = am
            else:
                print("WARNING piece without an anchor:", j.name)
        for ob in c.descendants(root):
            if ob.type == "MESH" and len(ob.data.materials) != 1:
                print("WARNING material count", ob.name, len(ob.data.materials))
            if len(ob.name) > 63:
                print("WARNING long name", ob.name)

    def check(self):
        """Contract checks: every piece's anchor exists, every parent/with/under names a real anchor."""
        bad = []
        names = set(self.anchors)
        for ob in c.descendants(self.root):
            if ob.type == "MESH" and "@" in ob.name:
                anc = ob.name.split("#", 1)[0].split("@")[1]
                if anc not in names:
                    bad.append(f"piece {ob.name}: no anchor {anc}")
        for a, m in self.meta.items():
            for k in ("parent", "with"):
                if m.get(k) and m[k] not in names:
                    bad.append(f"{a}: {k}={m[k]} is not an anchor")
            u = m.get("under")
            if u:
                for x in ([u] if isinstance(u, str) else u):
                    if x not in names:
                        bad.append(f"{a}: under {x} is not an anchor")
                    elif self.meta[x].get("order", 0) >= m.get("order", 0):
                        bad.append(f"{a}: under {x} has order {self.meta[x].get('order')} >= {m.get('order')}")
        for b in bad:
            print("RIG CHECK:", self.bid, b)
        return bad


# ---------------------------------------------------------------- temporary cutters (never part of a model)

def tmp_cube(center, size, frame=P.WORLD, bevel=0.0):
    return P.cube("tmpcut", center, size, "cardboard", frame, parent=None, bevel=bevel)


def tmp_slab(outline, depth, frame=P.WORLD, holes=()):
    return P.slab("tmpcut", outline, depth, "cardboard", frame, holes=holes)


def tmp_cyl(frame, r, h, segs=24, z0=None):
    return P.cylinder("tmpcut", frame, r, h, "cardboard", segs, parent=None, z0=z0)


def tmp_loft(sections, frame=P.WORLD):
    return P.loft("tmpcut", sections, "cardboard", frame, parent=None)


# ---------------------------------------------------------------- previews: open / exploded poses and stand-ins

def _unity_rot(axis, deg):
    return Matrix.Rotation(deg * DEG, 3, Vector(axis))


def anchor_motion(rig, name, k=1.0, extra=None):
    """The world-space (Blender) matrix that moves anchor 'name' (and everything on it) from its closed pose to
    its open pose (k=1), from its meta. extra: an added Unity-space translation."""
    m = rig.meta.get(name, {})
    fr = rig.frames[name]
    C = unity_to_blender_matrix()
    p = c.conv(fr.o)
    M = Matrix.Identity(4)
    axes = {"x": fr.u, "y": fr.v, "z": fr.w}
    if "hinge" in m and "open" in m:
        ax = axes[m["hinge"][-1]]
        R = C @ _unity_rot(ax, float(m["open"]) * k) @ C.inverted()
        M = Matrix.Translation(p) @ R.to_4x4() @ Matrix.Translation(-p)
    for key in ("lift", "slide"):
        if key in m:
            d = m[key]
            s = -1.0 if d.startswith("-") else 1.0
            ax = axes[d[-1]] * s
            dist = float(m.get("dist", 0.05)) * k
            M = Matrix.Translation(c.conv(ax * dist)) @ M
    if extra is not None:
        M = Matrix.Translation(c.conv(extra)) @ M
    return M


def chain(rig, name):
    out = []
    while name:
        out.append(name)
        name = rig.parent_of.get(name)
    return list(reversed(out))


def pose_matrices(rig, moves):
    """moves: {anchor: matrix (own motion)}. Returns {anchor: total matrix} through the parent/with chain."""
    tot = {}
    for a in rig.anchors:
        # compose: the parent's motion is applied after the child's own (root-most first)
        Mt = Matrix.Identity(4)
        for b in chain(rig, a):          # root-most first
            if b in moves:
                Mt = Mt @ moves[b]
        tot[a] = Mt
    return tot


def objects_of(rig, anc):
    out = []
    for ob in c.descendants(rig.root):
        if ob.type == "MESH":
            head = ob.name.split("#", 1)[0]
            if "@" in head and head.split("@")[1] == anc:
                out.append(ob)
    for ob in rig.extras.get(anc, []) if hasattr(rig, "extras") else []:
        out.append(ob)
    return out


def apply_pose(rig, moves):
    """Moves every piece and stand-in by its anchor's total matrix; returns an undo list."""
    tot = pose_matrices(rig, moves)
    undo = []
    for a, M in tot.items():
        if M == Matrix.Identity(4):
            continue
        for ob in objects_of(rig, a):
            undo.append((ob, ob.matrix_world.copy()))
            ob.matrix_world = M @ ob.matrix_world
    return undo


def undo_pose(undo):
    for ob, mw in reversed(undo):
        ob.matrix_world = mw


def import_model(model_id):
    path = os.path.join(c.MODELS, model_id + ".fbx")
    if not os.path.exists(path):
        return None
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def place_model(rig, model_id, anc, keep_anchors=False):
    """Imports a part model for the previews and puts its own frame on anchor anc (preview scene only)."""
    objs = import_model(model_id)
    if not objs:
        return []
    for o in list(objs):
        if o.type == "EMPTY" and o.name.startswith("A_") and not keep_anchors:
            pass
    meshes = [o for o in objs if o.type == "MESH"]
    for o in meshes:
        tag = o.data.materials[0].name if o.data.materials else P._tag_of(o.name)
        if "." in tag and tag.rsplit(".", 1)[1].isdigit():
            tag = tag.rsplit(".", 1)[0]
        o.name = "prev_" + model_id + "#" + tag
        o.data.materials.clear()
        o.data.materials.append(c.mat(tag))
    pivot = bpy.data.objects.new("prev_pivot_" + anc, None)
    bpy.context.scene.collection.objects.link(pivot)
    for o in objs:
        if o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = pivot
            o.matrix_world = mw
    pivot.matrix_world = rig.anchors[anc].matrix_world.copy()
    bpy.context.view_layer.update()
    out = []
    for o in meshes:
        mw = o.matrix_world.copy()
        o.parent = rig.root
        o.matrix_world = mw
        out.append(o)
    for o in objs:
        if o.type == "EMPTY":
            bpy.data.objects.remove(o)
    bpy.data.objects.remove(pivot)
    rig.extras.setdefault(anc, []).extend(out)
    return out


def stand_in(rig, anc, tag, center=None, size=None, bevel=0.0005):
    """A preview block for something the game spawns (a paper, a bag, a cord) on anchor anc: size from the anchor
    (flat items: x, y in the anchor's plane, z = thickness above it)."""
    fr = rig.frames[anc]
    s = size or rig.sizes[anc]
    cen = center or (0, 0, s[2] / 2)
    o = P.cube("prev_" + anc, cen, s, tag, fr, parent=rig.root, bevel=min(bevel, min(s) * 0.4))
    rig.extras.setdefault(anc, []).append(o)
    return o


def clear_extras(rig):
    for anc, obs in getattr(rig, "extras", {}).items():
        for o in obs:
            try:
                d = o.data
                bpy.data.objects.remove(o)
                if d is not None and d.users == 0:
                    bpy.data.meshes.remove(d)
            except ReferenceError:
                pass
    rig.extras = {}


def hide(objs, flag=True):
    for o in objs:
        o.hide_render = flag
