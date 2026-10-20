"""Smoke test for dct_common: a small board with a socket anchor, exported and previewed."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c

c.reset()
r = c.root("_smoke")
c.box("pcb", (0, 0, 0.0008), (0.1, 0.06, 0.0016), "pcb_green", r)
c.box("chip", (0.02, 0.01, 0.0026), (0.02, 0.02, 0.002), "chip_black", r, bevel=0.0005)
c.cyl("cap", (-0.03, 0.0, 0.006), 0.004, 0.009, "alu", axis="z", parent=r, bevel=0.0006)
c.from_profile("bracket", [(0, 0), (0.02, 0), (0.02, 0.01), (0.01, 0.02), (0, 0.02)], 0.002, "steel", (0.04, -0.02, 0.003), r)
c.tube("pipe", [(-0.04, -0.02, 0.004), (-0.02, -0.02, 0.012), (0.0, -0.02, 0.004)], 0.002, "copper", r)
lever = c.anchor("A_LEVER_CPU_0", (0.03, 0.02, 0.003), (0.016, 0.03, 0.06), r, forward=(0, 0, 1), up=(0, 1, 0))
c.box("lever_arm", (0.03, 0.02, 0.003), (0.003, 0.003, 0.05), "steel", lever)
c.anchor("A_SOCKET_RAM_0", (-0.01, 0.0, 0.0016), (0.006, 0.05, 0.03), r)
c.join_by_tag(r, "smoke")
c.export(r, "_smoke")
print(c.preview(r, "_smoke"))
