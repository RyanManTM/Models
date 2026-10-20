r"""
cat_shape_compare.py - an order-independent model comparison, for meshes whose triangulation order changes from
run to run (build_cpu.py's heat-spreader prism: extras_compare.py reports its .polys/.uvs as CHANGED even between
two runs of the same script).

    blender -b --factory-startup -P Tools/Blender/cat_shape_compare.py -- <old_dir> <new_dir> <id> [...] [--png a.png b.png ...]

For every id it imports both FBXs and compares, object by object: type, parent, world matrix, custom properties,
and for meshes the set of polygons, each polygon as its corner positions with their UVs (rounded to 1e-7 m / 1e-6),
independent of the polygon and vertex order. It prints "IDENTICAL" or "DIFFERENT: ..." per id.
--png compares textures pixel by pixel: the largest channel difference (0..255) and the share of pixels that differ.
Exits 1 if any id differs.
"""
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
            uvl = me.uv_layers[0].data if me.uv_layers else None
            polys = []
            for p in me.polygons:
                corners = []
                for li in p.loop_indices:
                    v = me.vertices[me.loops[li].vertex_index].co
                    uv = tuple(_r(x, 6) for x in uvl[li].uv) if uvl else ()
                    corners.append((tuple(_r(x) for x in v), uv))
                polys.append(tuple(sorted(corners)))
            info["polys"] = sorted(polys)
            info["mats"] = tuple(m.name if m else None for m in me.materials)
        out[o.name] = info
    return out


def png_diff(a, b):
    import numpy as np
    ia, ib = bpy.data.images.load(a), bpy.data.images.load(b)
    if tuple(ia.size) != tuple(ib.size):
        return f"size {tuple(ia.size)} vs {tuple(ib.size)}"
    pa = np.array(ia.pixels[:]).reshape(-1, ia.channels)[:, :3]
    pb = np.array(ib.pixels[:]).reshape(-1, ib.channels)[:, :3]
    d = np.abs(pa - pb).max(axis=1) * 255.0
    return f"max diff {d.max():.1f}/255, {100.0 * (d > 2.0).mean():.3f}% of pixels differ by more than 2"


def main(argv):
    pngs = []
    if "--png" in argv:
        k = argv.index("--png")
        pngs, argv = argv[k + 1:], argv[:k]
    old_dir, new_dir, ids = argv[0], argv[1], argv[2:]
    bad = False
    for pid in ids:
        a = snapshot(os.path.join(old_dir, pid + ".fbx"))
        b = snapshot(os.path.join(new_dir, pid + ".fbx"))
        diff = sorted(set(a) ^ set(b))
        for name in sorted(set(a) & set(b)):
            for k in a[name]:
                if a[name][k] != b[name].get(k):
                    diff.append(f"{name}.{k}")
        if diff:
            bad = True
            print(f"SHAPE {pid}: DIFFERENT: {diff[:20]}")
        else:
            print(f"SHAPE {pid}: IDENTICAL ({len(a)} objects, "
                  f"{sum(len(v.get('polys', [])) for v in a.values())} polygons)")
    for i in range(0, len(pngs) - 1, 2):
        print(f"PNG {os.path.basename(pngs[i])}: {png_diff(pngs[i], pngs[i + 1])}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])
