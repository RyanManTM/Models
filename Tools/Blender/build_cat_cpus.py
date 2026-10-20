r"""
build_cat_cpus.py - catalogue 10: CPUs (10 desktop on the existing V5 / L17 contracts, 4 server on new contracts).

    blender -b --factory-startup -P Tools/Blender/build_cat_cpus.py -- [ids...] [--nopreview]

Desktop (build_cpu.py with new specs: the sibling's package, frame and anchors; each part its own IHS markings):
  Socket V5 (cpu_arc5's 40 x 40 mm package)    cpu_arc3_8300g, cpu_arc5_9600x, cpu_arc7_9700x, cpu_arc7_9800x3d,
                                               cpu_arc9_9950x3d
  Socket L17 (cpu_tiron5's 37.5 x 45 mm)       cpu_tiron_i3_14100, cpu_tiron_i5_14600k, cpu_tiron_i7_14700,
                                               cpu_tiron_i7_14700k, cpu_tiron_i9_14900k
  The V5 parts add a Data Matrix code (and the X3D parts a 3D cache mark) through build_cpu's optional ihs_extra hook.
Server (cat_cpus_server.py, new contracts):
  Socket SP-V (72 x 75.4 mm, orange carrier)   cpu_epoch_9124, cpu_epoch_9354, cpu_epoch_9654
  Socket L46 (61 x 105 mm, black carrier clip) cpu_tiron_plat_8480
  Their clear contact covers (unboxing caps on A_CAP_PADS_0): cap_cpu_spv, cap_cpu_l46

With no ids it builds all of them. Each model writes Assets/Resources/Models/<id>.fbx, its textures, previews
Logs/ModelPreviews/<id>_<n>.png and Logs/ModelPreviews/<id>_report.txt; every run also writes the anchor report
Logs/ModelPreviews/cat_cpus_report.txt (every catalogue CPU that has a report). The shared substrate art (cpu_v5_pcb.png,
cpu_l17_pcb.png) is re-rendered unchanged by the desktop builds: don't commit it.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import parts_pcb as pp  # noqa: E402
import build_cpu  # noqa: E402
import cat_cpus_server as srv  # noqa: E402

PREVIEW = [True]
ETCH = build_cpu.ETCH


# ---------------------------------------------------------------- V5 markings hook

def v5_marks(cache3d=False):
    """ihs_extra hook for the V5 heat spreader (35 x 38 mm panel, image left = +x): a Data Matrix code left of the
    serial lines, and for the X3D parts a cube mark and "3D V-CACHE" to the right of the ARC logo."""
    def draw(a, S, w, h):
        cym = h / 2
        build_cpu.datamatrix(a, 2.6, cym - 8.6, 4.4, 14, S["seed"] * 7 + 1, ETCH)
        if cache3d:
            ly = cym + 9.4 - 0.6
            x0 = w / 2 + 2.6
            s = 1.5  # an isometric cube outline
            top = [(x0, ly + s), (x0 + s * 0.87, ly + s * 0.5), (x0, ly), (x0 - s * 0.87, ly + s * 0.5)]
            a.line(top + [top[0]], 0.28, ETCH, z=0.5)
            for (px, py) in (top[1], top[2], top[3]):
                a.line([(px, py), (px, py - s)], 0.28, ETCH, z=0.5)
            a.line([(top[3][0], top[3][1] - s), (x0, ly - s), (top[1][0], top[1][1] - s)], 0.28, ETCH, z=0.5)
            a.text("3D V-CACHE", x0 + 2.2, ly, 1.55, ETCH, font="narrowbd", ax="LEFT", fit=w - 1.6 - (x0 + 2.2))
    return draw


# ---------------------------------------------------------------- desktop specs

# The IHS texture is named cpu_ihs_<model> (build_cpu's ihs_tex hook): "<id>_ihs" would push the joined mesh name
# "<id>_tex_<tex>#tex_<tex>" past Blender's 63-character limit for ids this long.

def v5(line1, cores, opn, lot, made, seed, cache3d=False):
    tex = "cpu_ihs_" + line1.split()[-1].lower()
    return dict(sock="V5", line1=line1, cores=cores, opn=opn, lot=lot, fab="DIFFUSED IN TAIWAN", made=made, seed=seed,
                copy="© 2024", ihs_extra=v5_marks(cache3d), ihs_tex=tex)


def l17(line1, spec, fpo, seed):
    tex = "cpu_ihs_" + line1.split("-")[-1].lower()
    return dict(sock="L17", line1=line1, spec=spec, fpo=fpo, year="©'23", seed=seed, ihs_tex=tex)


DESKTOP = {
    "cpu_arc3_8300g": v5("ARC 3 8300G", "4-CORE", "100-000001184", "9AS7215P40021", "MADE IN CHINA", 31),
    "cpu_arc5_9600x": v5("ARC 5 9600X", "6-CORE", "100-000001405", "9GT2481M10058", "MADE IN MALAYSIA", 51),
    "cpu_arc7_9700x": v5("ARC 7 9700X", "8-CORE", "100-000001404", "9KM3366S30174", "MADE IN MALAYSIA", 71),
    "cpu_arc7_9800x3d": v5("ARC 7 9800X3D", "8-CORE", "100-000001084", "9PE5072V20033", "MADE IN CHINA", 73, True),
    "cpu_arc9_9950x3d": v5("ARC 9 9950X3D", "16-CORE", "100-000000719", "9RZ1640K50112", "MADE IN MALAYSIA", 93, True),
    "cpu_tiron_i3_14100": l17("TIRON® CORE™ i3-14100", "SRN3P 3.50GHZ", "X351C204", 141),
    "cpu_tiron_i5_14600k": l17("TIRON® CORE™ i5-14600K", "SRN43 3.50GHZ", "X347B615", 146),
    "cpu_tiron_i7_14700": l17("TIRON® CORE™ i7-14700", "SRN3Y 2.10GHZ", "X402A883", 147),
    "cpu_tiron_i7_14700k": l17("TIRON® CORE™ i7-14700K", "SRN3X 3.40GHZ", "X338F051", 148),
    "cpu_tiron_i9_14900k": l17("TIRON® CORE™ i9-14900K", "SRN48 3.20GHZ", "X342D769", 149),
}
SIBLING = {"V5": "cpu_arc5", "L17": "cpu_tiron5"}


def build_desktop(cid):
    S = DESKTOP[cid]
    build_cpu.SPECS[cid] = S
    root = build_cpu.build(cid)
    P.write_report(root, cid, f"frame: as {SIBLING[S['sock']]} (Socket {S['sock']} package, origin at the contact face "
                              "centre, +z up)")
    if PREVIEW[0]:
        build_cpu.previews(cid, root)
    return root


# ---------------------------------------------------------------- runner

JOBS = {cid: (lambda cid=cid: build_desktop(cid)) for cid in DESKTOP}
for _cid in srv.SPECS:
    JOBS[_cid] = (lambda cid=_cid: srv.build_and_preview(cid, PREVIEW[0]))
for _cid in srv.CAPS.values():
    JOBS[_cid] = (lambda cid=_cid: srv.build_cap_and_preview(cid, PREVIEW[0]))


def anchor_report():
    """Logs/ModelPreviews/cat_cpus_report.txt: the per-model reports of every catalogue CPU, in one file."""
    path = os.path.join(c.PREVIEWS, "cat_cpus_report.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("catalogue 10 (CPUs): models, triangles and anchors (Unity metres)\n\n")
        for cid in JOBS:
            rp = os.path.join(c.PREVIEWS, f"{cid}_report.txt")
            if os.path.exists(rp):
                with open(rp, encoding="utf-8") as f:
                    fh.write(f.read() + "\n")
    print("REPORT ->", path)


def main(argv):
    if "--nopreview" in argv:
        PREVIEW[0] = False
        P.PREVIEW[0] = False
    ids = [a for a in argv if not a.startswith("--")] or list(JOBS)
    t0 = time.time()
    for cid in ids:
        t = time.time()
        JOBS[cid]()
        print(f"BUILT {cid} in {time.time() - t:.1f}s")
    anchor_report()
    print(f"BUILD_CAT_CPUS done: {len(ids)} jobs in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main(c.args())
