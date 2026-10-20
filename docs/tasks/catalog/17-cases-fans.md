# Catalogue 17: Cases and fans (14)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_cases.py` (new) and optional hooks in `build_case.py`. If you add hooks, prove that `case_brickhouse`, `case_breeze` and `case_aero` re-export SAME.

**Fans:** don't edit `parts_fan.py`; wrap or extend `make_fan` in your own module.

**Delivers:** `docs/catalog/cases.json` and `docs/reports/cat_cases.md`.

## Cases: the case_breeze contract (7)
- **The same frame and anchor names and positions as case_breeze** (case_breeze_report.txt): 0.42 × 0.45 × 0.21, origin at the bottom centre, −x front, window +z. Check with `anchor_compare.py`, as case_aero did.
- **Different looks:** front panel (mesh, glass, solid, wood), colours, RGB fans, top panel, feet, PSU shroud details.
- **Fan positions may differ** in count and placement only on the front, top and bottom. Keep the rear fan, and list the differences.
- **Game data:** `case_airflow` (mesh fronts about 0.85, glass or solid fronts about 1.1).

1. Lumin Lancool 216-style: mesh front with two 160 mm fans, black.
2. Facet North-style: walnut wood slats on the front, charcoal, no RGB.
3. Facet Pop Air-style: budget, white, a coloured front accent.
4. Nexa H5 Flow-style: white, perforated front.
5. Phanta G360A-style: mesh front with 3 ARGB fans, black.
6. Hush Pure Base 500DX-style: black, with a front ARGB strip.
7. "Brickhouse Beige 98": a retro beige throwback case with a fake 5.25" bay and a turbo button. Just for fun.

## Retrofit: glass films on case_aero
`case_aero` (built by `build_parts_d.py`) has glass on its front corner and its side, but no film anchors.
- **Add the anchors:** `A_FILM_GLASS_<n>` on both sides of every glass pane, each in its panel's frame (`@A_PANEL_SIDE_0` for the side glass), per the catalogue README's unboxing rules.
- **Add only anchors** through a small optional hook, then re-export. `extras_compare.py` must report **ONLY ADDED** against the committed FBX.
- `build_parts_d.py` is task 03's script; touch only the case_aero part of it.

## Fans (7, new contract)
A case fan model:
- **Frame:** origin at the frame centre, +Z = airflow direction.
- **Anchors:**
  - the rotor as a moving piece `A_FAN_0` (meta `axis=z,spin=..,rpm=..`, plus `rgb=1` on RGB fans);
  - `A_PLUG_FAN_0` (4-pin PWM) and, for RGB fans, an ARGB plug anchor;
  - the 4 screw holes `A_HOLE_0..3` at 105 mm / 125 mm spacing.

Fan packs are one fan model; `per_box` is the count.
1. Noctis NF-A12x25-style 120 mm: beige frame, brown blades.
2. Noctis NF-A12x25 chromax-style 120 mm: black.
3. Arctiq P12 PWM-style 120 mm: black, a 5-pack.
4. Arctiq P14 PWM-style 140 mm: black.
5. Lumin Uni Fan-style 120 mm: daisy-chain RGB, white, a 3-pack. Model the interlocking side connectors.
6. Corvex AF120 RGB-style 120 mm: black, a 3-pack.
7. Hush Silent Wings-style 140 mm: black, with orange corner details.
