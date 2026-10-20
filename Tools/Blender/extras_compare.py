r"""
extras_compare.py - proves a part re-export changed nothing but the anchors that were added (agent C).

    "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/extras_compare.py -- <old_dir> <new_dir> <id> [...]

For every id it imports <old_dir>/<id>.fbx and <new_dir>/<id>.fbx and compares, object by object (by name):
type, parent, world matrix, custom properties (size, meta), and for meshes the vertex positions, the polygons, the
UVs, the materials and the smooth flags (as hashes, rounded to 1e-7 m / 1e-6). It prints one line per id:
"SAME" or "ONLY ADDED: <names>" (only new objects, all of them anchors) or "CHANGED: ..." with the details.
Exits 1 if any id has a change other than added anchors.
"""
import hashlib
import os
import sys

import bpy


def _r(x, k=7):
    return round(float(x), k) + 0.0


def snapshot(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path, use_custom_props=True)
    out = {}
    for o in bpy.context.scene.objects:
        info = {"type": o.type, "parent": o.parent.name if o.parent else None,
                "mw": tuple(_r(v, 6) for row in o.matrix_world for v in row),
                "props": tuple(sorted((k, str(o[k])) for k in o.keys() if not k.startswith("_")))}
        if o.type == "MESH":
            me = o.data
            h = hashlib.md5()
            for v in me.vertices:
                h.update(("%.7f %.7f %.7f;" % tuple(v.co)).encode())
            info["verts"] = (len(me.vertices), h.hexdigest())
            h = hashlib.md5()
            for p in me.polygons:
                h.update((",".join(str(i) for i in p.vertices) + ("s" if p.use_smooth else "f") + ";").encode())
            info["polys"] = (len(me.polygons), h.hexdigest())
            h = hashlib.md5()
            for uvl in me.uv_layers:
                h.update(uvl.name.encode())
                for d in uvl.data:
                    h.update(("%.6f %.6f;" % tuple(d.uv)).encode())
            info["uvs"] = h.hexdigest()
            info["mats"] = tuple(m.name if m else None for m in me.materials)
        out[o.name] = info
    return out


def main(argv):
    old_dir, new_dir, ids = argv[0], argv[1], argv[2:]
    bad = False
    for pid in ids:
        a = snapshot(os.path.join(old_dir, pid + ".fbx"))
        b = snapshot(os.path.join(new_dir, pid + ".fbx"))
        removed = sorted(set(a) - set(b))
        added = sorted(set(b) - set(a))
        changed = []
        for name in sorted(set(a) & set(b)):
            for k in a[name]:
                if a[name][k] != b[name].get(k):
                    changed.append(f"{name}.{k}")
        non_anchor = [n for n in added if not (b[n]["type"] == "EMPTY" and n.startswith("A_"))]
        if not removed and not changed and not added:
            print(f"COMPARE {pid}: SAME ({len(a)} objects)")
        elif not removed and not changed and not non_anchor:
            print(f"COMPARE {pid}: ONLY ADDED: {', '.join(added)} ({len(a)} objects unchanged)")
            for n in added:
                print(f"COMPARE {pid}:   + {n} {dict(b[n]['props'])}")
        else:
            bad = True
            print(f"COMPARE {pid}: CHANGED: removed={removed} changed={changed[:40]} added={added}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])
