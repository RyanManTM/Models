r"""
build_datacenter.py - the data-centre gear (docs/tasks/01-datacentre-gear.md):

  ac_12k                 FrostLine 12,000 BTU through-the-wall AC (datacenter_ac.py)
  server_1u, server_2u   19" rack servers (datacenter_server.py)
  rack_42u, rack_12u_open  the enclosed 42U rack and the 12U open frame (datacenter_rack.py)
  switch_24, patch_panel_24  1U 24-port gigabit switch and Cat6 patch panel (datacenter_net.py)
  ups_2u, ups_tower, pdu_0u, pdu_1u  power: rack and tower UPS, zero-U and 1U PDUs (datacenter_power.py)

Run:  blender -b --factory-startup -P Tools/Blender/build_datacenter.py -- [ids...] [--nopreview]
With no ids it builds all of them. Outputs Assets/Resources/Models/<id>.fbx, its textures, the previews
Logs/ModelPreviews/<id>_<n>.png and the anchor report Logs/ModelPreviews/<id>_report.txt.

Rack devices share one frame: origin at the centre of the front mounting plane, at the bottom of the device's U
space, +Z out of the front, +Y up, the chassis towards -Z (see datacenter_common.py).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402

BUILDERS = {
    "ac_12k": ("datacenter_ac", "build", ()),
    "server_1u": ("datacenter_server", "build", ("server_1u",)),
    "server_2u": ("datacenter_server", "build", ("server_2u",)),
    "rack_42u": ("datacenter_rack", "build", ("rack_42u",)),
    "rack_12u_open": ("datacenter_rack", "build", ("rack_12u_open",)),
    "switch_24": ("datacenter_net", "build_switch", ()),
    "patch_panel_24": ("datacenter_net", "build_patch", ()),
    "ups_2u": ("datacenter_power", "build_ups_2u", ()),
    "ups_tower": ("datacenter_power", "build_ups_tower", ()),
    "pdu_0u": ("datacenter_power", "build_pdu_0u", ()),
    "pdu_1u": ("datacenter_power", "build_pdu_1u", ()),
}
ALL = list(BUILDERS)


def main(argv):
    t0 = time.time()
    if "--nopreview" in argv:
        P.PREVIEW[0] = False
    ids = [a for a in argv if not a.startswith("--")] or ALL
    done = {}
    for mid in ids:
        if mid not in BUILDERS:
            print("unknown id", mid, "- known:", ", ".join(ALL))
            continue
        mod, fn, a = BUILDERS[mid]
        m = __import__(mod)
        t1 = time.time()
        done[mid] = getattr(m, fn)(*a)
        print("BUILT %s %s in %.0f s" % (mid, done[mid], time.time() - t1))
    print("\n==== data-centre gear: %d models in %.0f s" % (len(done), time.time() - t0))
    for k, v in done.items():
        print("  ", k, v)


if __name__ == "__main__":
    main(c.args())
