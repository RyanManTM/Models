r"""
build_parts_b.py - builds every "B" part in one Blender run: graphics cards, power supplies, CPU coolers.

    "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_parts_b.py -- [ids...]

With no ids it builds all of: gpu_rx66 gpu_rx88 psu_450 psu_750 cooler_stock cooler_tower.
Outputs: Assets/Resources/Models/<id>.fbx, Assets/Resources/Models/Textures/<id>.png,
Logs/ModelPreviews/<id>_<n>.png, and a summary (triangles, anchors) in Logs/ModelPreviews/parts_b_report.txt.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import build_cooler  # noqa: E402
import build_gpu  # noqa: E402
import build_psu  # noqa: E402

JOBS = {
    "gpu_rx66": lambda: build_gpu.build("gpu_rx66"),
    "gpu_rx88": lambda: build_gpu.build("gpu_rx88"),
    "psu_450": lambda: build_psu.build("psu_450"),
    "psu_750": lambda: build_psu.build("psu_750"),
    "cooler_stock": build_cooler.build_stock,
    "cooler_tower": build_cooler.build_tower,
}

if __name__ == "__main__":
    ids = [a for a in c.args() if a in JOBS] or list(JOBS)
    reports = []
    failed = []
    for pid in ids:
        t0 = time.time()
        try:
            m = JOBS[pid]()
            reports.append(m.report() + f"\n   built in {time.time() - t0:.1f} s")
        except Exception as e:  # keep going, report at the end
            import traceback
            traceback.print_exc()
            failed.append(f"{pid}: {e}")
    path = os.path.join(c.PREVIEWS, "parts_b_report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(reports))
        if failed:
            f.write("\n\nFAILED:\n" + "\n".join(failed))
    print("REPORT", path)
    if failed:
        print("FAILED:", failed)
        sys.exit(1)
