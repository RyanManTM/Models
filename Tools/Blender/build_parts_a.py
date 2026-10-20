"""
Builds parts batch A in one Blender run: motherboards mb_ridge_b5 / mb_ridge_z4 and their I/O shields
io_ridge_b5 / io_ridge_z4, CPUs cpu_arc5 / cpu_arc7 / cpu_tiron5, RAM ram_ddr5_16 / ram_ddr4_8 and SSDs
ssd_1tb / ssd_sata_500.

Outputs: Assets/Resources/Models/<id>.fbx, textures in Assets/Resources/Models/Textures/, previews in
Logs/ModelPreviews/.

Run:  "D:\\New folder\\blender.exe" -b --factory-startup -P Tools/Blender/build_parts_a.py -- [--no-previews] [ids...]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_pcb as pp  # noqa: E402
import build_board  # noqa: E402
import build_cpu  # noqa: E402
import build_ram  # noqa: E402
import build_ssd  # noqa: E402

ALL = ["mb_ridge_b5", "mb_ridge_z4", "cpu_arc5", "cpu_arc7", "cpu_tiron5", "ram_ddr5_16", "ram_ddr4_8", "ssd_1tb", "ssd_sata_500"]


def main():
    argv = c.args()
    previews = "--no-previews" not in argv
    ids = [a for a in argv if not a.startswith("--")] or ALL
    if not previews:
        pp.preview = lambda *a, **k: []  # skip the (slow) EEVEE renders
    t0 = time.time()
    done = []
    for pid in ids:
        t = time.time()
        if pid in build_board.BOARDS:
            build_board.build(pid, previews=previews)          # also builds the matching I/O shield
            done += [pid, build_board.BOARDS[pid]["shield"]]
        elif pid in build_cpu.SPECS:
            root = build_cpu.build(pid)
            if previews:
                build_cpu.previews(pid, root)
            done.append(pid)
        elif pid in build_ram.SPECS:
            root = build_ram.build(pid)
            if previews:
                build_ram.previews(pid, root)
            done.append(pid)
        elif pid == "ssd_1tb":
            root = build_ssd.build_m2()
            if previews:
                build_ssd.previews(pid, root)
            done.append(pid)
        elif pid == "ssd_sata_500":
            root = build_ssd.build_sata()
            if previews:
                build_ssd.previews(pid, root)
            done.append(pid)
        else:
            print("UNKNOWN PART", pid)
            continue
        print(f"BUILT {pid} in {time.time() - t:.1f}s")
    missing = [p for p in done if not os.path.exists(os.path.join(c.MODELS, p + ".fbx"))]
    print(f"BUILD_PARTS_A done: {len(done)} models in {time.time() - t0:.1f}s; missing: {missing or 'none'}")
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
