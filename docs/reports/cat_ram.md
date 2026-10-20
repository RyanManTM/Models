# Catalogue 13 report: memory (20 models)

Script: `Tools/Blender/build_cat_ram.py` (new). It reuses `build_ram.py`'s constants (`LEN`, `PCB_H`, `PCB_T`,
`NOTCH`), its gold-finger layout and its SMD / chip helpers, and builds its own spreaders, PCB art and labels.
**`build_ram.py` is not changed** (no hooks), so `ram_ddr5_16` and `ram_ddr4_8` are untouched and need no
re-export proof. Catalogue data: `docs/catalog/ram.json` (written by the script from its `CAT` table).

**Status: all 20 ids done.**

| # | id | kind | status |
|---|---|---|---|
| 1 | `ram_corvex_ddr5_32_black` | DDR5 kit | done |
| 2 | `ram_corvex_ddr5_32_white_rgb` | DDR5 kit | done |
| 3 | `ram_gstride_ddr5_48_rgb` | DDR5 kit | done |
| 4 | `ram_gstride_ddr5_32_lp` | DDR5 kit | done |
| 5 | `ram_kingsland_ddr5_64` | DDR5 kit | done |
| 6 | `ram_kingsland_ddr5_32_white_rgb` | DDR5 kit | done |
| 7 | `ram_crux_ddr5_96` | DDR5 kit | done |
| 8 | `ram_crux_ddr5_16` | DDR5 kit | done |
| 9 | `ram_teamforge_ddr5_32_white_rgb` | DDR5 kit | done |
| 10 | `ram_volt_ddr5_64_rgb` | DDR5 kit | done |
| 11 | `ram_corvex_ddr4_16_lp` | DDR4 kit | done |
| 12 | `ram_corvex_ddr4_32_rgb` | DDR4 kit | done |
| 13 | `ram_gstride_ddr4_16_red` | DDR4 kit | done |
| 14 | `ram_kingsland_ddr4_32` | DDR4 kit | done |
| 15 | `ram_crux_ddr4_64` | DDR4 kit | done |
| 16 | `ram_teamforge_ddr4_32_red` | DDR4 kit | done |
| 17 | `ram_kingsland_rdimm5_32` | DDR5 RDIMM | done |
| 18 | `ram_sorin_rdimm5_64` | DDR5 RDIMM | done |
| 19 | `ram_crux_rdimm5_128` | DDR5 RDIMM (3DS) | done |
| 20 | `ram_kingsland_rdimm4_32` | DDR4 RDIMM | done |

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_ram.py -- [ids...] [--nopreview]
```

Ids may also be `guard_rdimm_ddr5` / `guard_rdimm_ddr4` (the RDIMM finger guards). No ids = all 20 sticks and both guards (about 25 minutes with previews on 4 cores). Each id writes `Assets/Resources/Models/<id>.fbx`, one
texture atlas `Assets/Resources/Models/Textures/cr_<short id>.png` (the texture name is shortened, e.g.
`cr_kl_ddr5_32_wrgb`, so `ram_tex_<file>#tex_<file>` stays under Blender's 63-character name limit) and the previews
`Logs/ModelPreviews/<id>_0..3.png` (EEVEE: three views and a close-up of the label). Every run merges the rebuilt ids
into `Logs/ModelPreviews/cat_ram_report.txt` (every mesh with its triangles, every anchor with position, size and
meta) and rewrites `docs/catalog/ram.json`.

Ids follow the catalogue README's example (`ram_corvex_ddr5_32_white_rgb`): the number in a desktop id is the **kit**
capacity; `game.ram_gb` is one stick and `game.per_box` is 2. RDIMMs are sold singly (`per_box` 1) and their id
carries the module capacity.

These models were built on Linux with Blender 5.0.1 as the `bpy` module (download.blender.org is blocked in the
cloud session), with `bpy.app.binary_path` set so the EEVEE previews find the studio light.

**README line** (scripts table):

| `build_cat_ram.py` | Memory catalogue: 16 desktop DDR5/DDR4 kits (Corvex, G.Stride, Kingsland, Crux, TeamForge, Volt) and 4 server RDIMMs (new `rdimm` contract); reuses `build_ram.py`'s PCB and finger layout; writes `docs/catalog/ram.json` |

## Desktop sticks: the `ram` contract (same as `ram_ddr5_16` / `ram_ddr4_8`)

Frame exactly as `docs/MODEL_PIPELINE.md` §2 RAM: origin at the bottom-edge centre, thickness along x, the
133.35 mm length along y, the height along z; the gold fingers, latch notches and key notch are `build_ram`'s
(`pcb_outline` / `finger_positions`). The spec sticker is on the +x face (on the bare Crux stick: the −x face, the
side without chips, as on the real module).

Anchors:
- `A_NOTCH_0` at (0, notch, 0), size 0.004 × 0.0025 × 0.004, meta `y=-0.0039,mem=DDR5` or `y=0.0043,mem=DDR4`.
- `A_HIT_0` at (0, 0, height/2), size (spreader width) × 0.13335 × height.

What varies (looks only): spreader height (32.0 to 51.0 mm; 31.25 mm for the bare PCB), spreader outline and art,
colour, RGB light bars / diffusers (`rgb` tag), the label text.

`anchor_compare.py` against the sibling (`ram_ddr5_16` for DDR5, `ram_ddr4_8` for DDR4): **`A_NOTCH_0` SAME for all
16**; `A_HIT_0` differs only by the stick's height (z position and size) and the spreader thickness (0.0075 vs
0.0077 / 0.0072 m; 0.00407 m for the bare PCB), the free axes.

| id | name (game) | height mm | tris | meshes | `A_NOTCH_0` | `A_HIT_0` (pos z; size) |
|---|---|---|---|---|---|---|
| `ram_corvex_ddr5_32_black` | Corvex Vector DDR5 2×16 GB 6000 CL30 | 34.9 | 4894 | 6 | SAME | 0.01745; 0.0075 × 0.13335 × 0.0349 |
| `ram_corvex_ddr5_32_white_rgb` | Corvex Vector RGB DDR5 2×16 GB 6000 white | 44.0 | 4970 | 8 | SAME | 0.0220; 0.0075 × 0.13335 × 0.0440 |
| `ram_gstride_ddr5_48_rgb` | G.Stride Trine Z5 RGB DDR5 2×24 GB 7200 | 44.0 | 4914 | 7 | SAME | 0.0220; 0.0075 × 0.13335 × 0.0440 |
| `ram_gstride_ddr5_32_lp` | G.Stride Flare X5 DDR5 2×16 GB 6000 LP | 33.0 | 4862 | 6 | SAME | 0.0165; 0.0075 × 0.13335 × 0.0330 |
| `ram_kingsland_ddr5_64` | Kingsland Ferox DDR5 2×32 GB 5600 | 34.9 | 4870 | 6 | SAME | 0.01745; 0.0075 × 0.13335 × 0.0349 |
| `ram_kingsland_ddr5_32_white_rgb` | Kingsland Ferox RGB DDR5 2×16 GB 6000 white | 42.2 | 4902 | 7 | SAME | 0.0211; 0.0075 × 0.13335 × 0.0422 |
| `ram_crux_ddr5_96` | Crux Pro DDR5 2×48 GB 5600 | 35.0 | 4862 | 6 | SAME | 0.0175; 0.0075 × 0.13335 × 0.0350 |
| `ram_crux_ddr5_16` | Crux DDR5 2×8 GB 5600 (bare PCB) | 31.25 | 5054 | 5 | SAME | 0.01562; 0.00407 × 0.13335 × 0.03125 |
| `ram_teamforge_ddr5_32_white_rgb` | TeamForge T-Forge Delta RGB DDR5 2×16 GB 6400 white | 46.1 | 4922 | 7 | SAME | 0.02305; 0.0075 × 0.13335 × 0.0461 |
| `ram_volt_ddr5_64_rgb` | Volt Flux RGB DDR5 2×32 GB 6400 | 42.6 | 5010 | 8 | SAME | 0.0213; 0.0075 × 0.13335 × 0.0426 |
| `ram_corvex_ddr4_16_lp` | Corvex Vector LPX DDR4 2×8 GB 3200 | 34.0 | 5130 | 6 | SAME | 0.0170; 0.0075 × 0.13335 × 0.0340 |
| `ram_corvex_ddr4_32_rgb` | Corvex Vector RGB Pro DDR4 2×16 GB 3600 | 51.0 | 4986 | 8 | SAME | 0.0255; 0.0075 × 0.13335 × 0.0510 |
| `ram_gstride_ddr4_16_red` | G.Stride Riptide V DDR4 2×8 GB 3200 red | 42.0 | 4938 | 6 | SAME | 0.0210; 0.0075 × 0.13335 × 0.0420 |
| `ram_kingsland_ddr4_32` | Kingsland Ferox DDR4 2×16 GB 3200 | 34.1 | 4826 | 6 | SAME | 0.01705; 0.0075 × 0.13335 × 0.0341 |
| `ram_crux_ddr4_64` | Crux Tracer DDR4 2×32 GB 3200 | 39.0 | 4858 | 6 | SAME | 0.0195; 0.0075 × 0.13335 × 0.0390 |
| `ram_teamforge_ddr4_32_red` | TeamForge T-Forge Vulcan Z DDR4 2×16 GB 3600 red | 32.0 | 4834 | 6 | SAME | 0.0160; 0.0075 × 0.13335 × 0.0320 |

Meshes per stick: the textured body (`tex_cr_<…>`: PCB, spreader plates, sticker, chip tops), `gold`, `chip_black`,
`ceramic`, `solder`, `thermal_pad`, plus `rgb` and `alu_dark` / `white_plastic` (light-bar end caps) on the RGB sticks.

Spreader styles (`STYLES` in the script), each modelled on its real analog:
- `vector` (Corsair Vengeance DDR5): stepped top shoulder, ribbed right-hand panel.
- `vector_rgb` (Vengeance RGB DDR5): white plate, full-length light bar with end caps.
- `trine` (Trident Z5 RGB): brushed silver over a black lower body with a raked split, winged light bar.
- `flare` (Flare X5): low profile, raked stripes.
- `ferox` / `ferox_rgb` (Fury Beast / Fury Beast RGB): asymmetric stepped top, angular shards; the RGB one has a
  wave light bar.
- `crux_pro` (Crucial Pro): plain black plate with engraved lines.
- `bare` (Crucial UDIMM): no spreader, green PCB, four DRAM packages, PMIC with inductors, SPD hub.
- `delta` (T-Force Delta RGB): white frame with a wide triangular RGB diffuser on both faces and a thin top bar.
- `flux` (the Volt house look of `ram_ddr5_16`): raked relief panel, diffuser bar on a bridge.
- `lpx` (Vengeance LPX): the stepped fin top.
- `rgbpro` (Vengeance RGB Pro): tall light bar with a dark rim.
- `riptide` (Ripjaws V): red with claw teeth along the top.
- `tracer` (Ballistix): black with a raised badge and a red rake.
- `vulcan` (T-Force Vulcan Z): low-profile red with grey angular blades.

Every stick carries a printed spec label: brand, series and generation, capacity, speed (MT/s), CL timings, voltage,
part number, barcode and serial. The part numbers follow each brand's real numbering scheme with the brand prefix
changed (no real part number is printed).

## New contract: `rdimm` (server registered ECC DIMMs)

Ids: `ram_kingsland_rdimm5_32`, `ram_sorin_rdimm5_64`, `ram_crux_rdimm5_128`, `ram_kingsland_rdimm4_32`.
`new_contract: true` in `ram.json`; the game can't install them until server boards carry RDIMM slots.

**Frame:** the same as the desktop stick: origin at the bottom-edge centre, thickness along x, the 0.13335 m length
along y, the height along z. The PCB is 31.25 mm tall (JEDEC), except the 128 GB 3DS module, which is 38.0 mm (see
deviations). No heat spreader.

**Anchors:**
- `A_NOTCH_0` at (0, notch, 0), size 0.004 × 0.0025 × 0.004 (forward +z, like the desktop stick). Meta
  `y=<offset>,mem=<DDR4|DDR5>,type=RDIMM,ecc=1`.
  - **DDR5 RDIMM: y = −0.0019 m.** DDR5 RDIMMs have their own key position (2.0 mm nearer the centre than the DDR5
    UDIMM key at −0.0039), so a DDR5 RDIMM fits only a DDR5 RDIMM slot and a desktop DDR5 stick doesn't fit a server
    slot. A server board's `A_SOCKET_RAM_<n>` should carry `notch=-0.0019` and `type=RDIMM`.
  - DDR4 RDIMM: y = +0.0043 m, the same key as DDR4 UDIMMs (as in reality). The slot must still check `type=RDIMM`,
    since registered and unbuffered DDR4 are electrically incompatible.
- `A_HIT_0` at (0, 0, height/2), size (PCB + packages) × 0.13335 × height.

**Looks:** green PCB with traces, vias and silkscreen (part number, chip outlines); gold fingers with the notch gap;
10 DRAM packages per side (9 on the DDR4 module) in a row with the brand's marking, split 5 + 5 around the middle;
the RCD (register clock driver) in the middle of the +x face with its marking; decoupling caps under every package;
DDR5: the PMIC at the +y end with four inductors, the SPD hub in the middle and two thermal sensors; DDR4: an SPD
EEPROM with a thermal sensor. The spec sticker (with `ECC REGISTERED`, the rank organisation and the part number)
sits across the packages on the −x face.

| id | name (game) | PCB mm | packages | tris | meshes | `A_NOTCH_0` meta | `A_HIT_0` (pos z; size) |
|---|---|---|---|---|---|---|---|
| `ram_kingsland_rdimm5_32` | Kingsland Server Premier DDR5-4800 RDIMM 32 GB (2Rx8) | 31.25 | 2 × 10 | 6494 | 5 | `y=-0.0019,mem=DDR5,type=RDIMM,ecc=1` | 0.01562; 0.00407 × 0.13335 × 0.03125 |
| `ram_sorin_rdimm5_64` | Sorin DDR5-4800 RDIMM 64 GB (2Rx4) | 31.25 | 2 × 10 | 6494 | 5 | `y=-0.0019,mem=DDR5,type=RDIMM,ecc=1` | 0.01562; 0.00407 × 0.13335 × 0.03125 |
| `ram_crux_rdimm5_128` | Crux DDR5-5600 RDIMM 128 GB (2S2Rx4 3DS) | 38.0 | 2 × 10 (1.45 mm stacked) | 6494 | 5 | `y=-0.0019,mem=DDR5,type=RDIMM,ecc=1` | 0.0190; 0.00497 × 0.13335 × 0.0380 |
| `ram_kingsland_rdimm4_32` | Kingsland Server Premier DDR4-3200 RDIMM 32 GB (2Rx4) | 31.25 | 2 × 9 | 5990 | 5 | `y=0.0043,mem=DDR4,type=RDIMM,ecc=1` | 0.01562; 0.00407 × 0.13335 × 0.03125 |

## Unboxing: films and guards

Retrofitted after the catalogue README gained "The unboxing on every part (required)". Only anchors were added:
the 14 spreader sticks were re-exported and `extras_compare.py` (old FBX vs new, both built on Linux) prints
**ONLY ADDED: A_FILM_SPREADER_0, A_FILM_SPREADER_1** for every one of them; the bare Crux stick and the four
RDIMMs have no films and were not re-exported (SAME).

**Films** (anchors only; the game builds the peel meshes), on every stick with a heat spreader:
- `A_FILM_SPREADER_0` on the +x face, `A_FILM_SPREADER_1` on the −x face, at the plate centre
  (0.1 mm above the highest raised panel, face diffuser or sticker), forward ±x (out), up +z.
- `size` = 0.1282 × (plate height − 0.6 mm) × 0.0005: the whole plate face including the sticker. RGB light bars
  on top are not covered.
- Meta `film=clear,on=spreader_+x|spreader_-x,peel=-y,tab=+y+z`: the tab is the top corner at the +y end and the
  film peels towards −y.

| id | film size (m) |
|---|---|
| `ram_corvex_ddr5_32_black`, `ram_kingsland_ddr5_64` | 0.1282 × 0.0273 |
| `ram_corvex_ddr5_32_white_rgb` | 0.1282 × 0.0299 |
| `ram_gstride_ddr5_48_rgb` | 0.1282 × 0.0294 |
| `ram_gstride_ddr5_32_lp` | 0.1282 × 0.0254 |
| `ram_kingsland_ddr5_32_white_rgb` | 0.1282 × 0.0292 |
| `ram_crux_ddr5_96` | 0.1282 × 0.0274 |
| `ram_teamforge_ddr5_32_white_rgb` | 0.1282 × 0.0369 |
| `ram_volt_ddr5_64_rgb` | 0.1282 × 0.0304 |
| `ram_corvex_ddr4_16_lp` | 0.1282 × 0.0264 |
| `ram_corvex_ddr4_32_rgb`, `ram_crux_ddr4_64` | 0.1282 × 0.0314 |
| `ram_gstride_ddr4_16_red` | 0.1282 × 0.0344 |
| `ram_kingsland_ddr4_32` | 0.1282 × 0.0265 |
| `ram_teamforge_ddr4_32_red` | 0.1282 × 0.0244 |

**Guards** (`caps` in `ram.json`, `blocks=install`), all placed at the stick's root: position (0, 0, 0),
forward (0, 0, −1), up (0, 1, 0) in the stick frame (`localRotation = LookRotation(forward, up)`), like the existing
guards in `extras_caps.PLACEMENTS`:
- Desktop DDR5 sticks: the existing `guard_ram_ddr5`. Desktop DDR4 sticks: the existing `guard_ram_ddr4`.
- DDR5 RDIMMs: **new `guard_rdimm_ddr5`**. DDR4 RDIMM: **new `guard_rdimm_ddr4`**.

The new guards are built by `build_cat_ram.py` (ids `guard_rdimm_ddr5`, `guard_rdimm_ddr4`) with
`extras_caps.build_guard_ram` (not changed): the same clear clip over the gold fingers as the desktop guards, with
the 2 mm gap at the RDIMM notch. They have 728 triangles in one `clear_plastic` mesh (the tag the existing guards
use), and local +Z is the pull-off direction.
- `A_HIT_0` pos (0, 0.0020, −0.0014), size 0.00237 × 0.1386 × 0.0040, meta
  `remove=+z,travel=0.0015,part=ram,blocks=install,notch=-0.0019` (DDR5) / `notch=0.0043` (DDR4).
- `A_GRIP_0` pos (0, 0.0692, −0.0010), the pull tab at the +y end, meta `pull=+z`.

`guard_rdimm_ddr4` has the same shape as `guard_ram_ddr4`, because the DDR4 RDIMM shares the UDIMM key. It is a
separate id so the game can keep server and desktop packaging apart. Previews: `Logs/ModelPreviews/guard_rdimm_*_0..2.png`.

**Papers.** Every entry in `ram.json` now has:
- `unbox` (films, caps, stickers: none);
- `docs`: `guide` (the installation card) and `warranty`, plus `safety` (ESD) for the RDIMMs;
- `doc_notes`, 6–9 facts. Desktop: slots A2/B2 first; enable EXPO/XMP (DDR5) or XMP/DOCP (DDR4), otherwise
  JEDEC 4800 / 2133 MT/s; the rated speed, timings and voltage; DDR4/DDR5 keying; the latches; ESD; DDR5
  first-boot training; the RGB software; peel the films. RDIMMs: server boards only and the keying; slot 1 of every
  channel first; don't mix ranks or 3DS; speed and voltage; ESD; training time.

## Catalogue data

`docs/catalog/ram.json`: 20 entries, `category` RAM, `contract` `ram` (desktop) or `rdimm` (server,
`new_contract: true`). `game` holds `mem`, `ram_gb` (one stick), `per_box` and `perf: 0`. `specs` holds the kit,
speed, CAS and full timings, voltage, height and whether it has a spreader (RDIMMs: `ecc`, `registered`, `ranks`).
`power_w` is per stick (DDR5 5 W, DDR4 3 W, DDR5 RDIMM 10 W, 128 GB 3DS 13 W, DDR4 RDIMM 6 W). Prices are
approximate street prices of the real analogs in USD; DRAM prices move fast, so check them before release.

## Deviations

- **No hooks in `build_ram.py`.** Its texture and spreader code are written around the Volt look, so the catalogue
  script has its own (`textures`, `build_spreader`, `pcb_outline` with a height parameter); the PCB outline,
  finger layout, SMD helpers and notch values come from `build_ram`.
- **Spreader thickness** is 2.15–3.35 mm per side for every style (sibling: 2.25–3.45 DDR5 RGB, 2.05–3.2 DDR4), so
  `A_HIT_0` is 0.0075 m thick. A stick still fits the 7.5 mm slot pitch.
- **The 128 GB 3DS RDIMM is 38.0 mm tall** (the brief asks for a taller module); real 3DS RDIMMs are mostly
  31.25 mm with taller stacked packages, which this model also has (1.45 mm instead of 1.0 mm).
- **DDR5 RDIMM notch offset** (−1.9 mm) is a game value chosen to differ from the UDIMM key, like the existing DDR4/DDR5
  offsets; it is not a measured JEDEC value.
- **DDR4 RDIMM has 9 packages per side** (x4 2R with ECC on this layout), not 10.
- The bare Crux stick and the RDIMMs carry the sticker on the −x face (the real modules' sticker side); the spreader
  sticks have it on +x as before.
- The silkscreen chip outlines are on both faces of the bare PCBs (the PCB art is shared by both faces); on the
  single-sided Crux stick the back shows empty footprints, as on real single-rank boards.
