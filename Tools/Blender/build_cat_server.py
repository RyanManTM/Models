r"""
build_cat_server.py - catalogue 18, server add-ins and gear (docs/tasks/catalog/18-server.md).

PCIe add-in cards (cat_server_cards.py), each with its loose low-profile bracket <id>_lpbracket:
  nic_linkwave_350t2        dual-port 1GbE RJ45, x4
  nic_linkwave_710da2       dual-port 10GbE SFP+, x8
  nic_melnet_strand6_25g    dual-port 25GbE SFP28, x8
  nic_melnet_strand6_100g   dual-port 100GbE QSFP28, x16
  hba_broadline_9500_16i    16-port SAS/SATA/NVMe HBA, x8, two SFF-8654 x8
  hba_broadline_9560_16i    RAID controller, x8, cache module and a supercap pack on a cable
Rack gear (cat_server_rack.py), in the rack device frame of datacenter_common.py:
  srv_strata_sg840_4u       4U GPU server, 8 double-width GPU sleds, 4 CRPS PSUs, a fan wall
  srv_strata_sr224_2u       2U storage server, 24 x 2.5" bays
  srv_linkwave_ls4804x      1U 48 x 1GbE + 4 x SFP+ switch
  srv_linkwave_ls1600x      1U 16 x 10GbE SFP+ aggregation switch
  srv_strata_shelf_1u       1U cantilever shelf
  srv_strata_blank_1u, srv_strata_blank_2u   blanking panels
  srv_strata_cma            cable management arm for the servers' slide rails
  srv_strata_kvm_1u         1U KVM console drawer (LCD and keyboard)

Run:  blender -b --factory-startup -P Tools/Blender/build_cat_server.py -- [ids...] [--nopreview]
With no ids it builds all of them. Then the fit check: Tools/Blender/cat_server_fit.py.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402

CARDS = ["nic_linkwave_350t2", "nic_linkwave_710da2", "nic_melnet_strand6_25g", "nic_melnet_strand6_100g",
         "hba_broadline_9500_16i", "hba_broadline_9560_16i"]
BUILDERS = {}
for _cid in CARDS:
    BUILDERS[_cid] = ("cat_server_cards", "build_card", (_cid,))
    BUILDERS[_cid + "_lpbracket"] = ("cat_server_cards", "build_lpbracket", (_cid,))
RACK = {
    "srv_strata_sg840_4u": "build_gpu_server",
    "srv_strata_sr224_2u": "build_storage_server",
    "srv_linkwave_ls4804x": "build_switch48",
    "srv_linkwave_ls1600x": "build_switch_agg",
    "srv_strata_shelf_1u": "build_shelf",
    "srv_strata_blank_1u": "build_blank_1u",
    "srv_strata_blank_2u": "build_blank_2u",
    "srv_strata_cma": "build_cma",
    "srv_strata_kvm_1u": "build_kvm",
}
for _rid, _fn in RACK.items():
    BUILDERS[_rid] = ("cat_server_rack", _fn, ())
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
    print("\n==== catalogue 18 server gear: %d models in %.0f s" % (len(done), time.time() - t0))
    for k, v in done.items():
        print("  ", k, v)


if __name__ == "__main__":
    main(c.args())
