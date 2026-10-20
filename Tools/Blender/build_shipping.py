"""
Shipping and unboxing models (Logs/UNBOXING.md section 2.3, Blender agent A): shipping cartons and their flats,
packing filler, crumpled trash looks, small bits, the box cutter, the unboxing table, the wheelie bin, bin bags and
the paperwork tray.

Run:  "D:\\New folder\\blender.exe" -b --factory-startup -P Tools/Blender/build_shipping.py -- [ids...] [--nopreview]
      ids are model ids (ship_carton_s, wheelie_bin, ...) or group names (cartons, filler, crumples, bits,
      furniture); none = everything.

Outputs: Assets/Resources/Models/<id>.fbx, textures in Assets/Resources/Models/Textures/ (tex_ship_*),
previews Logs/ModelPreviews/<id>_<n>.png, and one anchor report Logs/ModelPreviews/shipping_report.txt.

Every model has its origin at the bottom centre (unless its notes in the report say otherwise), front at +z, and an
A_HIT_0 (hitboxes are centred on their anchor). Modules: shipping_lib (helpers), shipping_cartons,
shipping_filler, shipping_bits, shipping_furniture.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import shipping_lib as S  # noqa: E402
import shipping_cartons as SC  # noqa: E402

MODELS = {}
GROUPS = {}


def register(group, mid, build):
    MODELS[mid] = build
    GROUPS.setdefault(group, []).append(mid)


# ====================================================================== cartons

_atlas_done = set()


def carton_atlas(key):
    L, H, W = SC.SIZES[key]
    at = SC.Atlas(key, L, H, W)
    if key not in _atlas_done:
        P.reset()
        SC.carton_texture(at, seed=11 + "sml".index(key))
        _atlas_done.add(key)
    return at


def make_carton(key):
    def build(mid, prev):
        at = carton_atlas(key)
        kit = S.Kit(mid)
        SC.build_carton(key, kit, at)
        kit.finish(smooth=30.0)
        L, H, W = SC.SIZES[key]
        notes = [f"  note: outer {L} x {H} x {W} m (x, y, z), board {SC.T * 1000:.0f} mm; origin bottom centre, front +z.",
                 "  note: flap anchors sit on the crease axis; A_TAPE_* are segment centres on the cardboard, local +Y "
                 "along the peel path (seg i -> i+1), local X = tape width; strip 0 = top (end tab, seam, end tab), "
                 "strip 1 = bottom.",
                 "  note: under= lists run to the end of the meta (comma separated anchor names).",
                 "  note: tapelook#tape_brown is look-only (both strips); hide it when the code builds the peel strips."]
        out = finish_model(kit, mid, notes)
        if prev:
            S.render(kit.root, mid, [(32, 26), (-145, 24)], samples=48)
            S.render(kit.root, mid, [(30, -40)], samples=48, start=2, floor=False, below=True)
            S.pose_pieces(kit.root, {"A_FLAP_0": ("x", -150), "A_FLAP_1": ("x", 200), "A_FLAP_2": ("z", 110),
                                     "A_FLAP_3": ("z", -110)})
            S.render(kit.root, mid, [(18, 48)], samples=48, start=3, hide=("tapelook",))
        return out
    return build


def make_flat(key):
    def build(mid, prev):
        at = carton_atlas(key)
        kit = S.Kit(mid)
        SC.build_flat(key, kit, at)
        kit.finish(smooth=30.0)
        L, H, W = SC.SIZES[key]
        notes = [f"  note: lies flat; origin at the bottom centre of the flat; {L + W:.2f} (x) x {2 * SC.T:.3f} (y) x "
                 f"{H + W:.2f} (z) m including the flaps; the original top edge is at -z; bottom layer = back + right "
                 "panels (y 0..T), top layer = left + front panels (y T..2T)."]
        out = finish_model(kit, mid, notes)
        if prev:
            S.render(kit.root, mid, [(25, 55), (80, 12)], samples=48)
            S.render(kit.root, mid, [(200, -45)], samples=48, start=2, floor=False, below=True)
        return out
    return build


for k in ("s", "m", "l"):
    register("cartons", f"ship_carton_{k}", make_carton(k))
for k in ("s", "m", "l"):
    register("cartons", f"ship_carton_{k}_flat", make_flat(k))


# ====================================================================== driver

def finish_model(kit, mid, notes=None):
    return S.finish_model(kit, mid, notes)


def _load_more():
    """The other groups live in their own modules (imported lazily so a broken one doesn't stop the rest)."""
    for modname in ("shipping_filler", "shipping_bits", "shipping_furniture"):
        try:
            mod = __import__(modname)
        except ImportError as e:
            print("module not available:", modname, e)
            continue
        for group, mid, build in mod.MODELS:
            register(group, mid, build)


def main(argv):
    _load_more()
    do_prev = "--nopreview" not in argv
    P.PREVIEW[0] = do_prev
    want = [a for a in argv if not a.startswith("--")]
    ids = []
    for a in want:
        if a in GROUPS:
            ids += GROUPS[a]
        elif a in MODELS:
            ids.append(a)
        else:
            print("UNKNOWN id", a)
    if not want:
        ids = list(MODELS)
    blocks = {}
    t0 = time.time()
    for mid in ids:
        t = time.time()
        blocks[mid] = MODELS[mid](mid, do_prev)
        print(f"TIME {mid} {time.time() - t:.1f}s")
    S.merge_report(blocks, list(MODELS))
    print(f"DONE {len(ids)} models in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(c.args())
