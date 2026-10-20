r"""
anchor_compare.py - compares the anchors of two models anchor by anchor (a new part against its sibling).

    "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/anchor_compare.py -- <a.fbx> <b.fbx> [--md] [--tol 1e-5]

Imports both FBX files and matches the empties named A_* by name. For each anchor it compares the position (Unity
metres), the forward (+Z) and up (+Y) axes, the hitbox size and the meta. One line per anchor:
  SAME            identical within --tol (default 1e-5 m / 1e-4 on the axes)
  DIFF <what>     present in both, something differs (the values are printed)
  ONLY_A / ONLY_B present in one model only
--md prints a Markdown table instead. The summary line counts each kind. Exits 0 always (it is a report).
"""
import sys

import bpy
from mathutils import Vector


def to_unity(v):
    """Blender -> Unity (the inverse of dct_common.conv)."""
    return Vector((-v[0], v[2], -v[1]))


def anchors(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path, use_custom_props=True)
    out = {}
    for o in bpy.context.scene.objects:
        if o.type != "EMPTY" or not o.name.startswith("A_"):
            continue
        m = o.matrix_world
        out[o.name] = dict(pos=to_unity(m.translation), fwd=-to_unity(m.col[1].xyz).normalized(),
                           up=to_unity(m.col[2].xyz).normalized(), size=str(o.get("size", "")), meta=str(o.get("meta", "")))
    return out


def fmt(v):
    return "(%.4f, %.4f, %.4f)" % (v.x + 0.0, v.y + 0.0, v.z + 0.0)


def main(argv):
    md = "--md" in argv
    tol = 1e-5
    if "--tol" in argv:
        tol = float(argv[argv.index("--tol") + 1])
    files = [a for a in argv if a.endswith(".fbx")]
    a, b = anchors(files[0]), anchors(files[1])
    counts = {"SAME": 0, "DIFF": 0, "ONLY_A": 0, "ONLY_B": 0}
    rows = []
    for name in sorted(set(a) | set(b)):
        if name not in b:
            counts["ONLY_A"] += 1
            rows.append((name, "ONLY_A", fmt(a[name]["pos"]), "", a[name]["meta"]))
            continue
        if name not in a:
            counts["ONLY_B"] += 1
            rows.append((name, "ONLY_B", "", fmt(b[name]["pos"]), b[name]["meta"]))
            continue
        x, y = a[name], b[name]
        what = []
        if (x["pos"] - y["pos"]).length > tol:
            what.append("pos d=%.4f" % (x["pos"] - y["pos"]).length)
        if (x["fwd"] - y["fwd"]).length > 1e-4 or (x["up"] - y["up"]).length > 1e-4:
            what.append("axes")
        if x["size"] != y["size"]:
            what.append(f"size {x['size']} -> {y['size']}")
        if x["meta"] != y["meta"]:
            what.append(f"meta {x['meta']} -> {y['meta']}")
        kind = "SAME" if not what else "DIFF"
        counts[kind] += 1
        rows.append((name, kind if not what else "DIFF " + "; ".join(what), fmt(x["pos"]), fmt(y["pos"]), y["meta"]))
    if md:
        print("| anchor | result | A pos | B pos |")
        print("|---|---|---|---|")
        for r in rows:
            print(f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} |")
    else:
        for r in rows:
            print(f"ANCHOR {r[0]:34s} {r[1]:10s} A={r[2]} B={r[3]}")
    print("SUMMARY %s vs %s: %d anchors in A, %d in B; SAME %d, DIFF %d, ONLY_A %d, ONLY_B %d" % (
        files[0].split("/")[-1], files[1].split("/")[-1], len(a), len(b), counts["SAME"], counts["DIFF"], counts["ONLY_A"],
        counts["ONLY_B"]))


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
