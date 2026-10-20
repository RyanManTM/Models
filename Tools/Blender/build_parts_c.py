r"""
Builds everything of parts batch C in one Blender run:
  plugs and small items (build_plugs.py): plug_<kind> for every kind, screw_ph2, screw_ph0, screw_thumb,
      standoff_brass, usb_stick;
  cases (build_case.py): case_brickhouse, case_breeze;
  the bench monitor (build_monitor.py): monitor_24;
  retail boxes (build_boxes.py), last, because their product shots are rendered from the finished part models:
      box_<partid> for every catalog item plus box_ssd_sata_500 and box_usb_installer.
Outputs: Assets/Resources/Models/<id>.fbx, Assets/Resources/Models/Textures/*.png, previews and <id>_report.txt
(triangles, meshes, anchors) in Logs/ModelPreviews.

Run:  "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_parts_c.py -- [options]
Options: --nopreview   skip the preview renders (much faster)
         --noboxes     skip the boxes;  --boxesonly  only the boxes (re-run once all part models exist)
         --noshots     boxes: reuse the cached product shots in Logs/ModelPreviews/boxshots
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import build_plugs  # noqa: E402
import build_case  # noqa: E402
import build_monitor  # noqa: E402
import build_boxes  # noqa: E402


def main(argv):
    t0 = time.time()
    if "--nopreview" in argv:
        P.PREVIEW[0] = False
    done = {}
    if "--boxesonly" not in argv:
        done.update(build_plugs.main())
        done.update(build_case.main())
        done["monitor_24"] = build_monitor.main()
    if "--noboxes" not in argv:
        box_args = [a for a in argv if a in ("--noshots", "--nopreview")]
        done.update({"box_" + k: v for k, v in build_boxes.main(box_args).items()})
    print("\n==== parts C: %d models in %.0f s" % (len(done), time.time() - t0))
    for k, v in done.items():
        print("  ", k, v)


if __name__ == "__main__":
    main(c.args())
