# Catalogue 16: CPU coolers (13)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_coolers.py` (new) and optional hooks in `build_cooler.py`. If you add hooks, prove that `cooler_stock` and `cooler_tower` re-export SAME.

**Fans:** don't edit `parts_fan.py`. Wrap or extend `make_fan` from your own module (brown/beige Noctis fans, ARGB fans, white fans).

**Delivers:** `docs/catalog/coolers.json` and `docs/reports/cat_coolers.md`.

## Air coolers: the cooler_tower contract (8)
The cooler_tower contract (docs/MODEL_PIPELINE.md §2 and parts_b_report.txt):
- **Base frame:** origin at the centre of the base contact face, +z away from the board.
- **Anchors:** mounting screws `A_SCREW_PH2_*`, `A_FILM_0` (the base film), `A_FAN_n`, `A_PLUG_FAN_n` and `A_FILM_TOP_0`.
- **What may vary:** height, fin stack, heat pipes, single or dual tower, 1–2 fans, colour, ARGB.
- **Game data:** `cooler_max_w` (the real rated TDP). Keep the total height ≤ 165 mm and say each one's height in specs.

1. Arctiq Freezer 34-style: single tower, black.
2. Arctiq Freezer 34-style: white.
3. Glacier AK400-style: single tower, white.
4. Glacier AK620-style: dual tower, black.
5. Noctis NH-D15-style: dual tower, nickel fins, beige/brown fans.
6. Noctis NH-D15-style chromax: all black.
7. Noctis NH-L9-style: low profile, 37 mm, with a 92 mm fan.
8. Frostpeak Tower 120 RGB: an ARGB fan and an RGB top cap.

**Also:**
9. Tiron Laminar-style stock cooler (L17): round aluminium, black fan, pre-applied paste. Use the cooler_stock contract.

## AIO liquid coolers (3, new contract)
- **The pump block** sits on the CPU, with the same base contract as cooler_tower (screws, base film, `A_FILM_TOP_0`) plus `A_PLUG_FAN_0` for the pump.
- **Two tubes** run to a **radiator**, a separate moving piece with its own anchors:
  - `A_RAD_0` (radiator origin);
  - `A_RAD_FAN_n` (fans on the radiator);
  - radiator screw holes `A_HOLE_RAD_n`;
  - fan plugs.
- **Model the tubes** as a bendable look: a few segments along a curve from the pump to the radiator. Note in the report how the game should route them.
- **The game** mounts the radiator on the case's top or front fan positions. Note which `A_FAN_n` positions of case_breeze it would use.

1. Arctiq Liquid Freezer-style 240: black, with a thick radiator.
2. Corvex H150i-style 360: white, RGB, an LCD pump cap with `A_SCREEN_0`.
3. Glacier LS720-style 360: black, ARGB.

## Server heatsinks (2, new contracts)
1. A 1U passive heatsink for Arc Epoch (socket SP-V), copper base and dense fins.
2. A 2U heatsink for Tiron Platinum (L46).

Both have spring screws `A_SCREW_*` in the socket's pattern (match the CPU task's sockets). Document them.
