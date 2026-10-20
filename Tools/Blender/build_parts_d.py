r"""
build_parts_d.py - parts batch D: four new catalog parts that drop into the game exactly like their siblings.

    "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_parts_d.py -- [ids...] [--nopreview]

  cpu_arc9      ARC 9 9900X, Socket V5. build_cpu.py with a new spec: cpu_arc5/arc7's package, frame and anchors,
                its own heat-spreader markings (cpu_arc9_ihs.png; the substrate art cpu_v5_pcb.png is shared).
  gpu_rx77      VOLTRA RX 7700, 270 mm, 2.5 slots, 3 fans, 2 x PCIe 8-pin. build_gpu.py with a new spec and style
                hooks (the shroud overlay, skirts, logo plate, backplate); the frame and anchor kinds of gpu_rx66/rx88.

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
import build_gpu  # noqa: E402

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


# ---------------------------------------------------------------- gpu_rx77
# build_gpu.py's card with a new spec: 270 mm, 2.5 slots (50 mm), three 78 mm fans, two PCIe 8-pin ports, a dark
# grey shroud with silver rings, edge rails and chevrons, a brushed silver backplate with a hex flow-through window.
# The style hooks get (m, ns): ns holds build_gpu.build()'s local variables (xa, xb, H, yF, fxs, fz, r_hole, ...).

def _rx77_backplate(m, n):
    """Flow-through: a hex-perforated window past the end of the PCB (over the third fan)."""
    return build_gpu.hex_grid(n.xa + 0.010, 0.016, n.pcb_end - 0.006, n.H - 0.016, 0.0034, 0.0012)


def _rx77_overlay(m, n):
    G, pb = build_gpu, build_gpu.pb
    xa, xb, H, yF, fz = n.xa, n.xb, n.H, n.yF, n.fz
    fxs = n.fxs

    def mirror(pts):
        return [(x, 2 * fz - z) for (x, z) in reversed(pts)]

    # silver rails along both long edges, with slanted ends
    rail = [(xa + 0.014, 0.0058), (xb - 0.017, 0.0058), (xb - 0.0130, 0.0090), (xa + 0.0180, 0.0090)]
    for pts in (rail, mirror(rail)):
        G.slab_xz(m, "alu", pts, [], yF - 0.0012, 0.0012, bevel=0.0002)
    # black wedges between the fan rings (top and bottom) with a silver chevron and a screw
    for i in range(len(fxs) - 1):
        xm = (fxs[i] + fxs[i + 1]) / 2
        wedge = [(xm - 0.019, fz + 0.0445), (xm + 0.019, fz + 0.0445), (xm + 0.0035, fz + 0.0205), (xm - 0.0035, fz + 0.0205)]
        for pts, sgn in ((wedge, 1), (mirror(wedge), -1)):
            G.slab_xz(m, n.s["over_tag"], pts, [], yF - 0.0016, 0.0016, bevel=0.0003)
            for side in (-1, 1):
                strip = [(xm + side * 0.0125, fz + sgn * 0.0415), (xm + side * 0.0100, fz + sgn * 0.0415),
                         (xm + side * 0.0010, fz + sgn * 0.0262), (xm + side * 0.0035, fz + sgn * 0.0262)]
                if side < 0:
                    strip = list(reversed(strip))
                if sgn < 0:
                    strip = list(reversed(strip))
                G.slab_xz(m, "alu", strip, [], yF - 0.0019, 0.0004)
            pb.screw_ph(m.mb("steel_dark"), (xm, yF - 0.0016, fz + sgn * 0.0355), (0, -1, 0), (1, 0, 0), r=0.0016, h=0.0007)
    # silver corner blades at both ends
    for (x0, d) in ((xa + 0.0045, 1), (xb - 0.0045, -1)):
        for sgn in (1, -1):
            zz = fz + sgn * (H / 2 - 0.0035)
            blade = [(x0, zz), (x0 + d * 0.0035, zz), (x0 + d * 0.0035, zz - sgn * 0.030), (x0, zz - sgn * 0.024)]
            if (d > 0) != (sgn > 0):
                blade = list(reversed(blade))
            G.slab_xz(m, "alu", blade, [], yF - 0.0016, 0.0016, bevel=0.0002)


def _rx77_skirts(m, n):
    xa, xb, yF = n.xa, n.xb, n.yF
    top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.022), (xb - 0.018, yF + 0.022), (xb - 0.026, yF + 0.0145),
           (xa + 0.092, yF + 0.0145), (xa + 0.080, yF + 0.0265), (xa + 0.002, yF + 0.0265)]
    bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.0145), (xa + 0.032, yF + 0.0145), (xa + 0.020, yF + 0.0225),
           (xa + 0.004, yF + 0.0225)]
    return top, bot, 0.0265


def _rx77_logo(m, n):
    xa, xb, yF = n.xa, n.xb, n.yF
    lw, lh = 0.092, 0.0105
    lx = (xa + 0.092 + xb - 0.026) / 2
    return lw, lh, lx, yF + 0.0074, (xa + 0.016, xb - 0.030), yF + 0.0017


def _rx77_trim(m, n):
    G, pb = build_gpu, build_gpu.pb
    xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
    # a silver line along the step of the top skirt, and the model print on the bottom edge
    G.box(m, "alu", (xa + 0.094, yF + 0.0136, H - 0.0001), (xb - 0.028, yF + 0.0146, H + 0.0004))
    G.box(m, "alu", (xa + 0.006, yF + 0.0250, H - 0.0001), (xa + 0.078, yF + 0.0260, H + 0.0004))
    m.add(n.TEX, pb.g_quad(0.08, 0.010, n.at.uv("plate")), pb.label_frame((0, 0, -1), (0, 1, 0)),
          ((xa + xb) / 2 + 0.02, yF + 0.0075, 0.0020 - 0.00005))


build_gpu.SPECS["gpu_rx77"] = dict(
    L=0.270, H=0.118, T=0.050, Hp=0.108, fans=3, fan_d=0.078, blades=11, tip_ring=False, power="pcie8",
    px=[-0.1005, -0.0790], model="RX 7700", mem="12GB GDDR6", pcb_end=-0.128, pipes=5, pipe_tag="nickel", xd=0.022,
    zd=0.058, bracket_tag="steel", back_tag="alu", face_tag="steel_dark", over_tag="black_plastic", ring_tag="alu",
    logo_tag="paint_black", accent="#c4c8ce", emblem="#c4c8ce", vent="slots", sn="S/N 241077A0071942", qr_seed=8,
    swatch="#c4c8ce", logo_maxw=262, bp_logo_x=-0.045, core="screws", backplate=_rx77_backplate, overlay=_rx77_overlay,
    skirts=_rx77_skirts, logo=_rx77_logo, trim=_rx77_trim)


def build_gpu_rx77():
    if not PREVIEW[0]:
        build_gpu.pb.shots = lambda *a, **k: None
    mdl = build_gpu.build("gpu_rx77")
    with open(os.path.join(c.PREVIEWS, "gpu_rx77_report.txt"), "w", encoding="utf-8") as fh:
        fh.write(mdl.report() + "\n")
    return mdl


JOBS = {
    "cpu_arc9": build_cpu_arc9,
    "gpu_rx77": build_gpu_rx77,
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
