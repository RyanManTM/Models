r"""
build_parts_d.py - parts batch D: four new catalog parts that drop into the game exactly like their siblings.

    "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_parts_d.py -- [ids...] [--nopreview]

  cpu_arc9      ARC 9 9900X, Socket V5. build_cpu.py with a new spec: cpu_arc5/arc7's package, frame and anchors,
                its own heat-spreader markings (cpu_arc9_ihs.png; the substrate art cpu_v5_pcb.png is shared).

With no ids it builds all of them. Each model writes Assets/Resources/Models/<id>.fbx, its textures, previews
Logs/ModelPreviews/<id>_<n>.png and Logs/ModelPreviews/<id>_report.txt (meshes, triangles, every anchor).
Nothing here edits an existing model: the existing builders are reused with new specs.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import parts_pcb as pp  # noqa: E402
import build_cpu  # noqa: E402

PREVIEW = [True]

# ---------------------------------------------------------------- cpu_arc9

build_cpu.SPECS["cpu_arc9"] = dict(sock="V5", line1="ARC 9 9900X", cores="12-CORE", opn="100-000001277",
                                   lot="9MK4813R50093", fab="DIFFUSED IN TAIWAN", made="MADE IN MALAYSIA", seed=9)


def build_cpu_arc9():
    root = build_cpu.build("cpu_arc9")
    P.write_report(root, "cpu_arc9", "frame: as cpu_arc5/arc7 (V5 40 x 40 mm package, origin at the contact face centre, +z up)")
    if PREVIEW[0]:
        build_cpu.previews("cpu_arc9", root)
    return root


JOBS = {
    "cpu_arc9": build_cpu_arc9,
}


def main(argv):
    if "--nopreview" in argv:
        PREVIEW[0] = False
        P.PREVIEW[0] = False
    ids = [a for a in argv if not a.startswith("--")] or list(JOBS)
    t0 = time.time()
    for pid in ids:
        t = time.time()
        JOBS[pid]()
        print(f"BUILT {pid} in {time.time() - t:.1f}s")
    print(f"BUILD_PARTS_D done: {len(ids)} jobs in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main(c.args())
