# Catalogue 12: Motherboards

Branch `claude/cat-12-motherboards`. Script `Tools/Blender/build_cat_boards.py` (desktop boards, I/O shields) and
`Tools/Blender/server_boards.py` (the two server boards). Catalogue data: `docs/catalog/boards.json`.

## Status

| # | Id | I/O shield | Contract (layout sibling) | Status |
|---|---|---|---|---|
| 1 | `mb_aegis_b650_bulwark` | `io_aegis_b650_bulwark` | mb_ridge_b5 (V5, DDR5) | done |
| 2 | `mb_aegis_x870e_vanguard` | `io_aegis_x870e_vanguard` | mb_ridge_b5 (V5, DDR5) | done |
| 3 | `mb_mako_b650_harpoon` | `io_mako_b650_harpoon` | mb_ridge_b5 (V5, DDR5) | done |
| 4 | `mb_kestrel_b650_glide` | `io_kestrel_b650_glide` | mb_ridge_b5 (V5, DDR5) | done |
| 5 | `mb_aegis_z790_keystone` | `io_aegis_z790_keystone` | mb_ridge_z4 + DDR5 notch (L17, DDR5) | not yet |
| 6 | `mb_mako_z790_riptide` | `io_mako_z790_riptide` | mb_ridge_z4 + DDR5 notch (L17, DDR5) | not yet |
| 7 | `mb_kestrel_z790_talon` | `io_kestrel_z790_talon` | mb_ridge_z4 + DDR5 notch (L17, DDR5) | not yet |
| 8 | `mb_ridge_b760_d4` | `io_ridge_b760_d4` | mb_ridge_z4 (L17, DDR4) | not yet |
| 9 | `mb_strata_spv` | `io_strata_spv` | new: server board SP-V | not yet |
| 10 | `mb_strata_l46` | `io_strata_l46` | new: server board L46 dual | not yet |

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_boards.py -- [ids...] [--nopreview]
```

With no ids it builds every board and its shield. Each writes `Assets/Resources/Models/<id>.fbx` (+ the shield's),
the textures `Assets/Resources/Models/Textures/<id without mb_>_pcb.png`, `<id without mb_>_mk.png` and
`io_<...>.png`, previews `Logs/ModelPreviews/<id>_<n>.png` and `<id>_report.txt` (every mesh with its triangles,
every anchor); the run also writes `Logs/ModelPreviews/cat_boards_report.txt` (all reports in one file).

Anchor comparison against the sibling:

```bash
blender -b --factory-startup -P Tools/Blender/anchor_compare.py -- Assets/Resources/Models/mb_ridge_x5.fbx Assets/Resources/Models/<id>.fbx
```

These models were built on Linux with Blender 5.0.1 as the `bpy` Python module (download.blender.org is blocked in
the cloud session), with `bpy.app.binary_path` set to the package folder so the EEVEE previews find the studio HDRI.

**README line to add** (the scripts table):

| `build_cat_boards.py` | Catalogue motherboards: 8 ATX boards (Aegis, Mako, Kestrel, Ridge; V5/DDR5, L17/DDR5, L17/DDR4) on the `build_board.py` layouts, 2 SSI-EEB server boards (`server_boards.py`), each with its I/O shield `io_*` |

## How the desktop boards are made

`CatBoard` subclasses `build_board.Board` the way `build_parts_d.py`'s `PremiumBoard` made `mb_ridge_x5`. It
overrides only methods that create no anchor: `vrm`, `chipset`, `io_shroud`, `silkscreen`, `dimm_slot`,
`pcie_slot`, and extends `m2` (calls the sibling's first, then adds trim and an optional second heatsink). Every
anchor therefore comes from the sibling's own code. `build_board.py` is **unchanged** (no hooks were needed), so
the existing boards need no re-export proof.

`build` and the shield builder are copied with two changes only: the texture files are named after the id without
its `mb_` prefix (`<key>_pcb`, `<key>_mk`) and the joined meshes get the prefix `mb_` / `io_`, because
`<id>_<tag>#<tag>` with these longer ids would pass Blender's 63-character name limit (which silently truncates
the tag). The I/O shield builder also takes the paint (black or bare steel) from the style.

Colours that are not a plain material tag (military tan, the orange accents, painted greys) are painted through
the board's marks atlas (`tex_<key>_mk` swatches), so no new material tag was needed.

Looks are per style: VRM heatsink kind (`armour`: a solid block with a long chamfer, cut lines, trim inlay and
fin slots; `slab`: layered blocks with a contrasting band; `fins`: an exposed fin stack under a cover; `budget`:
a small extruded heatsink), chipset heatsink kind, I/O cover kind (`armour`, `slab`, `rgb` with a lit emblem
panel, `budget`), PCIe armour (none, x16, both), slot and DIMM colours, M.2 trim and a second M.2 heatsink, and
the silkscreen pattern (`tactical`, `angular`, `lines`, `dots`, `circuit`, `stripes`). Heatsinks stay in the
sibling's zones (rear heatsink from x 0.0774 on V5 and 0.0826 on L17, as the siblings), so the cooler keep-out of
`A_SOCKET_COOLER_0` is respected.

### Anchor check

The committed `mb_ridge_b5.fbx` and `mb_ridge_z4.fbx` predate `build_board.films()`, so they lack
`A_FILM_IO_0` and `A_FILM_CHIPSET_0`; `mb_ridge_x5` (built with today's `build_board.py`) has them. Each V5 board
is compared with both: against `mb_ridge_x5` every anchor is SAME; against `mb_ridge_b5` every shared anchor is
SAME and the two film anchors are ONLY_B.

---

## 1. `mb_aegis_b650_bulwark` + `io_aegis_b650_bulwark`: Aegis Bulwark Gaming B650-Plus WiFi

- **Analog:** ASUS TUF Gaming B650-PLUS WIFI. Socket V5, DDR5, ATX; `mb_ridge_b5` layout.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; tallest part the I/O cover (z 0.0371).
- **Triangles:** 44,786 in 38 meshes. Shield: 1,244 in 1.
- **Look:** black PCB with tan hazard stripes and a stencil "BULWARK" print; dark gunmetal `armour` VRM
  heatsinks with a tan chamfer and inlay, cut lines and fin slots; armour-style I/O cover with stepped plates and a
  tan line; armoured (steel) x16 slot; black DIMM slots; black M.2 heatsink with tan marks; chipset heatsink with a
  tan corner slash. No RGB. Shield: painted black.
- **Anchors:** vs `mb_ridge_x5`: 82 SAME, 0 DIFF. vs `mb_ridge_b5`: 80 SAME, ONLY_B `A_FILM_CHIPSET_0`, `A_FILM_IO_0`.
- **I/O shield:** not pre-attached on the analog.

## 2. `mb_aegis_x870e_vanguard` + `io_aegis_x870e_vanguard`: Aegis Vanguard X870E-E Gaming WiFi

- **Analog:** ASUS ROG Strix X870E-E Gaming WiFi. Socket V5, DDR5, ATX; `mb_ridge_b5` layout.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; tallest part the I/O cover (z 0.0371; the rear VRM heatsink reaches
  the same height, the top one 0.034).
- **Triangles:** 45,512 in 41 meshes. Shield: 1,244 in 1.
- **Look:** black PCB with dark angular graphics and red accents; tall `armour` VRM heatsinks in near-black with
  mirror-silver (`alu`) chamfers and inlays; an **RGB I/O cover**: a lit emblem panel on the cover top (an `rgb` plate
  under a dark grille with a silver shield emblem) plus the RGB light bar; steel armour on **both** full-length PCIe
  slots; a black `slab` chipset heatsink with diagonal grooves; two dark M.2 heatsinks with silver ridges; black
  DIMM slots. Shield: painted black.
- **Anchors:** vs `mb_ridge_x5`: 82 SAME, 0 DIFF.
- **I/O shield:** pre-attached on the analog (shipped here as the separate `io_aegis_x870e_vanguard` all the same).

## 3. `mb_mako_b650_harpoon` + `io_mako_b650_harpoon`: Mako Harpoon B650 WiFi

- **Analog:** MSI MAG B650 TOMAHAWK WIFI. Socket V5, DDR5, ATX; `mb_ridge_b5` layout.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; tallest part the I/O cover (z 0.0371).
- **Triangles:** 44,886 in 38 meshes. Shield: 1,244 in 1.
- **Look:** black PCB with grey line graphics; layered `slab` VRM heatsinks in mid grey with a dark band, groove
  lines and a brushed inlay; a `slab` I/O cover with a band and grooves; a gunmetal chipset heatsink with diagonal
  grooves; steel-armoured x16 slot; two dark M.2 heatsinks (the second over M2_2 is fixed, looks only); black DIMM
  slots. No RGB. Shield: painted black.
- **Anchors:** vs `mb_ridge_x5`: 82 SAME, 0 DIFF. vs `mb_ridge_b5`: 80 SAME, ONLY_B `A_FILM_CHIPSET_0`, `A_FILM_IO_0`.
- **I/O shield:** pre-attached on the analog (shipped here as the separate `io_mako_b650_harpoon` all the same).

## 4. `mb_kestrel_b650_glide` + `io_kestrel_b650_glide`: Kestrel B650 Glide G

- **Analog:** Gigabyte B650 AERO G (the white/silver creator board). Socket V5, DDR5, ATX; `mb_ridge_b5` layout.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; tallest part the I/O cover (z 0.0371).
- **Triangles:** 45,616 in 41 meshes. Shield: 1,244 in 1.
- **Look:** white PCB with a grey dot-matrix graphic and dark silkscreen; `fins` VRM heatsinks (white covers over
  exposed silver fin stacks, a silver lip line); a white `slab` I/O cover with a soft RGB line; a white chipset
  plate; white DIMM and PCIe slots, the x16 one with silver armour; two white M.2 heatsinks. Shield: bare steel.
- **Anchors:** vs `mb_ridge_x5`: 82 SAME, 0 DIFF.
- **I/O shield:** pre-attached on the analog (shipped here as the separate `io_kestrel_b650_glide` all the same).

## Deviations

- None so far.
