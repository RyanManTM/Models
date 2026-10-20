# Catalogue 15: Power supplies (13)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_psus.py` (new) and optional hooks in `build_psu.py`. If you add hooks, prove that `psu_450` and `psu_750` re-export SAME.

**Delivers:** `docs/catalog/psus.json` and `docs/reports/cat_psus.md`.

## The ATX contract (psu_450 / psu_750)
- **Frame:** origin at the box centre of the 140 mm-deep unit; x = depth, with the rear face at +x; y = height, with the fan grille at −y; z = width.
- **Longer units** (160–200 mm) must keep the rear face at x = +0.07 and grow towards −x, so they still fit the case's PSU socket.
- **Rear-face anchors stay at the same positions:** `A_SWITCH_PSU_0`, the C14 inlet and the screw holes.
- **Modular port anchors** (`A_PORT_MOD_*`) for modular units. Semi-modular units have fixed ATX/EPS cables (non-modular style) plus modular PCIe/SATA ports.
- **Game data:** `psu_watts`, `psu_efficiency`, `psu_eps8`, `psu_pcie8`, `psu_16`, `psu_sata`, `psu_modular`. These must match the real unit's connector count.
- **Each unit gets its own look:** paint, fan grille style, spec label, and the 80 PLUS badge in the right colour (Bronze, Gold, Platinum, Titanium).

## Desktop ATX (10)
1. Ampere 550 W Bronze: non-modular, black.
2. Corvex CX-style 650 W Bronze: semi-modular.
3. Seastar Focus-style 850 W Gold: fully modular, black.
4. Seastar Vertex-style 1000 W Platinum: white, ATX 3.1, 12V-2x6.
5. Corvex RM-style 850 W Gold: white, fully modular, 12V-2x6.
6. Hush Pure Power-style 750 W Gold: black with silver stripes.
7. Hush Dark Power-style 1200 W Titanium: black with a silver fan ring.
8. Mako 850 W Gold: ATX 3.1, black.
9. Aegis Thor-style 1200 W Platinum: RGB side and a small OLED wattage display. Put an `A_SCREEN_0` on the display.
10. Corvex AX-style 1600 W Titanium: 200 mm deep.

## SFX (1, new contract)
1. **Corvex SF-style 750 W Platinum:** 125 × 63.5 × 100 mm. Same anchor kinds; document the new frame and the SFX-to-ATX bracket.

## Server CRPS (2, new contract)
Hot-swap modules, about 73.5 × 40 × 185 mm, with a card-edge connector at the front (into the server), and a handle, latch, status LED and C14 inlet at the rear. Anchors: `A_LATCH_0`, `A_HANDLE_0`, `A_LED_STATUS_0`, `A_PORT_C14_0`.
1. Strata 800 W Platinum
2. Strata 1600 W Titanium
