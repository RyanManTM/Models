# Catalogue 10 report: CPUs

14 CPUs: 10 desktop parts on the existing V5 and L17 contracts, and 4 server parts on two new socket contracts
(SP-V and L46). Catalogue data: `docs/catalog/cpus.json`.

## Status

All 14 are done, each committed with its model, textures, previews and report.

| Id | Name | Socket | Contract | Status |
|---|---|---|---|---|
| `cpu_arc7_9800x3d` | Arc 7 9800X3D | V5 | `cpu_arc5` | done |
| `cpu_arc5_9600x` | Arc 5 9600X | V5 | `cpu_arc5` | done |
| `cpu_arc7_9700x` | Arc 7 9700X | V5 | `cpu_arc5` | done |
| `cpu_tiron_i5_14600k` | Tiron i5-14600K | L17 | `cpu_tiron5` | done |
| `cpu_tiron_i7_14700k` | Tiron i7-14700K | L17 | `cpu_tiron5` | done |
| `cpu_tiron_i9_14900k` | Tiron i9-14900K | L17 | `cpu_tiron5` | done |
| `cpu_arc9_9950x3d` | Arc 9 9950X3D | V5 | `cpu_arc5` | done |
| `cpu_arc3_8300g` | Arc 3 8300G | V5 | `cpu_arc5` | done |
| `cpu_tiron_i3_14100` | Tiron i3-14100 | L17 | `cpu_tiron5` | done |
| `cpu_tiron_i7_14700` | Tiron i7-14700 | L17 | `cpu_tiron5` | done |
| `cpu_epoch_9654` | Arc Epoch 9654 | SP-V | new `cpu_spv` | done |
| `cpu_epoch_9354` | Arc Epoch 9354 | SP-V | new `cpu_spv` | done |
| `cpu_epoch_9124` | Arc Epoch 9124 | SP-V | new `cpu_spv` | done |
| `cpu_tiron_plat_8480` | Tiron Platinum 8480 | L46 | new `cpu_l46` | done |
| `cap_cpu_spv` | contact cover for SP-V (unboxing cap) | SP-V | new cap | done |
| `cap_cpu_l46` | contact cover for L46 (unboxing cap) | L46 | new cap | done |

Unboxing retrofit (the catalogue README's "The unboxing on every part"): done for all 14. The JSON has `unbox`,
`docs` and `doc_notes` on every entry; the 4 server CPUs have `A_CAP_PADS_0` and their caps.

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_cpus.py -- [ids...] [--nopreview]
```

With no ids it builds all 14 CPUs and the 2 cap models. It writes `Assets/Resources/Models/<id>.fbx`, the textures, the previews
`Logs/ModelPreviews/<id>_<n>.png`, the per-model report `Logs/ModelPreviews/<id>_report.txt`, and the family anchor
report `Logs/ModelPreviews/cat_cpus_report.txt`. The desktop builds also re-render the shared `cpu_v5_pcb.png` and
`cpu_l17_pcb.png` with unchanged art; they are not committed.

Built with Blender 5.0.1 as the `bpy` Python module (download.blender.org is blocked in the cloud session), with
`bpy.app.binary_path` set to the package folder so the EEVEE previews find the studio HDRI.

**Files**

| File | What |
|---|---|
| `Tools/Blender/build_cat_cpus.py` | new: the family runner, the 10 desktop specs and the V5 marking hook (Data Matrix, 3D cache mark) |
| `Tools/Blender/cat_cpus_server.py` | new: the SP-V and L46 packages, IHS, substrate and carrier art, the carrier moving piece |
| `Tools/Blender/cat_cpus_unbox.py` | new: adds `A_CAP_PADS_0` to the committed server CPU FBXs without rebuilding them (see "Unboxing") |
| `Tools/Blender/cat_shape_compare.py` | new: an order-independent model and texture comparison (see "Existing models unchanged") |
| `Tools/Blender/build_cpu.py` | three optional spec keys: `ihs_extra`, `copy`, `ihs_tex` (existing CPUs unchanged) |
| `Assets/Resources/Models/` | the 14 `cpu_*.fbx`, `cap_cpu_spv.fbx`, `cap_cpu_l46.fbx`, `Textures/cpu_ihs_<model>.png` each, `cpu_spv_pcb.png`, `cpu_l46_pcb.png`, `cpu_spv_carrier.png`, `cpu_l46_carrier.png` |
| `Logs/ModelPreviews/` | 4 previews and `<id>_report.txt` per model, `cat_cpus_report.txt` |
| `docs/catalog/cpus.json` | the shop data |

**README line to add** (the scripts table):

| `build_cat_cpus.py` | Catalogue 10, CPUs: 5 Arc (V5) and 5 Tiron (L17) desktop CPUs on `build_cpu.py`, plus the server CPUs Arc Epoch 9124 / 9354 / 9654 (Socket SP-V, orange carrier) and Tiron Platinum 8480 (Socket L46) from `cat_cpus_server.py` |

## Desktop CPUs (existing contracts)

All ten are `build_cpu.build` with a new spec, so the package geometry, frame and anchors are the sibling's by
construction; only the IHS texture differs. Frame: origin at the centre of the contact face, +z up, IHS top at
z 0.006, pin 1 at (+x, −y).

| Id | Triangles | Meshes | IHS texture | Markings |
|---|---|---|---|---|
| `cpu_arc3_8300g` | 13,696 | 5 | `cpu_ihs_8300g.png` | ARC 3 8300G / 4-CORE / 100-000001184 / 9AS7215P40021 / MADE IN CHINA |
| `cpu_arc5_9600x` | 13,696 | 5 | `cpu_ihs_9600x.png` | ARC 5 9600X / 6-CORE / 100-000001405 / 9GT2481M10058 / MADE IN MALAYSIA |
| `cpu_arc7_9700x` | 13,696 | 5 | `cpu_ihs_9700x.png` | ARC 7 9700X / 8-CORE / 100-000001404 / 9KM3366S30174 / MADE IN MALAYSIA |
| `cpu_arc7_9800x3d` | 13,696 | 5 | `cpu_ihs_9800x3d.png` | ARC 7 9800X3D / 8-CORE / 3D V-CACHE mark / 100-000001084 / 9PE5072V20033 |
| `cpu_arc9_9950x3d` | 13,696 | 5 | `cpu_ihs_9950x3d.png` | ARC 9 9950X3D / 16-CORE / 3D V-CACHE mark / 100-000000719 / 9RZ1640K50112 |
| `cpu_tiron_i3_14100` | 14,410 | 5 | `cpu_ihs_14100.png` | TIRON® CORE™ i3-14100 / SRN3P 3.50GHZ / X351C204 |
| `cpu_tiron_i5_14600k` | 14,410 | 5 | `cpu_ihs_14600k.png` | TIRON® CORE™ i5-14600K / SRN43 3.50GHZ / X347B615 |
| `cpu_tiron_i7_14700` | 14,410 | 5 | `cpu_ihs_14700.png` | TIRON® CORE™ i7-14700 / SRN3Y 2.10GHZ / X402A883 |
| `cpu_tiron_i7_14700k` | 14,410 | 5 | `cpu_ihs_14700k.png` | TIRON® CORE™ i7-14700K / SRN3X 3.40GHZ / X338F051 |
| `cpu_tiron_i9_14900k` | 14,410 | 5 | `cpu_ihs_14900k.png` | TIRON® CORE™ i9-14900K / SRN48 3.20GHZ / X342D769 |

Every IHS also has its own Data Matrix code (seeded per part), the etched pin-1 triangle and the year. The V5 parts
get "DIFFUSED IN TAIWAN", the year "© 2024" and a Data Matrix code left of the serial lines through the
`ihs_extra` hook. The L17 parts already had a Data Matrix code in `build_cpu.py`. The K and non-K i7s differ only
in their markings.

**Anchor comparison** (`anchor_compare.py <sibling>.fbx <id>.fbx`): position, axes, size and meta.

| Id | vs | `A_HIT_0` | `A_MARK_PIN1_0` | `A_PASTE_0` | Summary |
|---|---|---|---|---|---|
| `cpu_arc3_8300g` | `cpu_arc5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_arc5_9600x` | `cpu_arc5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_arc7_9700x` | `cpu_arc5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_arc7_9800x3d` | `cpu_arc5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_arc9_9950x3d` | `cpu_arc5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_tiron_i3_14100` | `cpu_tiron5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_tiron_i5_14600k` | `cpu_tiron5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_tiron_i7_14700` | `cpu_tiron5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_tiron_i7_14700k` | `cpu_tiron5` | SAME | SAME | SAME | 3 / 3 SAME |
| `cpu_tiron_i9_14900k` | `cpu_tiron5` | SAME | SAME | SAME | 3 / 3 SAME |

Values (as the siblings): V5 `A_MARK_PIN1_0` (0.0193, −0.0193, 0.0012), `A_PASTE_0` (0, 0, 0.006) `ihs=0.0350x0.0380`,
`A_HIT_0` (0, 0, 0.003) 0.040 × 0.040 × 0.0064; L17 `A_MARK_PIN1_0` (0.0181, −0.0218, 0.0011), `A_PASTE_0`
(0, 0, 0.006), `A_HIT_0` (0, 0, 0.003).

### Existing models unchanged (the `build_cpu.py` hooks)

The three keys are optional and absent from the old specs: `ihs_extra(art, S, w, h)` draws more markings into the
IHS panel, `copy` replaces the "© 2023" line (V5), and `ihs_tex` names the IHS texture. The `ihs_tex` key is needed
because `<id>_ihs` pushes the joined mesh name `<id>_tex_<tex>#tex_<tex>` past Blender's 63-character limit for
ids like `cpu_tiron_i9_14900k`, which breaks the tag.

Proof: on Linux, I exported `cpu_arc5`, `cpu_arc7`, `cpu_tiron5` and `cpu_arc9` with the old `build_cpu.py`
twice (old, old2) and once with the new one, each into its own scratch project.
- `extras_compare.py` old vs new: only the IHS mesh's `.polys`/`.uvs` change. Old vs old2 gives exactly the same
  result: `prism_bevel`'s n-gon triangulation order changes from run to run (the task 03 report notes this too).
- `cat_shape_compare.py` old vs new (the polygon set with positions and UVs, independent of order): IDENTICAL for
  all four.
- Their IHS textures and the shared `cpu_v5_pcb.png` / `cpu_l17_pcb.png`: max pixel difference 0/255.
- None of these re-exports is committed.

```bash
blender -b --factory-startup -P Tools/Blender/cat_shape_compare.py -- <old>/Assets/Resources/Models <new>/Assets/Resources/Models cpu_arc5 cpu_arc7 cpu_tiron5 cpu_arc9 --png <old.png> <new.png> ...
```

## Server models

| Id | Triangles | Meshes | IHS texture | Markings |
|---|---|---|---|---|
| `cpu_epoch_9124` | 33,390 | 6 | `cpu_ihs_9124.png` | ARC EPOCH / 9124 / 16-CORE / 100-000000802 / 2CK8149D10023 / MADE IN MALAYSIA |
| `cpu_epoch_9354` | 33,390 | 6 | `cpu_ihs_9354.png` | ARC EPOCH / 9354 / 32-CORE / 100-000000798 / 2CN4417F20061 / MADE IN MALAYSIA |
| `cpu_epoch_9654` | 33,390 | 6 | `cpu_ihs_9654.png` | ARC EPOCH / 9654 / 96-CORE / 100-000000789 / 2CQ7350G40188 / MADE IN CHINA |
| `cpu_tiron_plat_8480` | 43,510 | 6 | `cpu_ihs_8480.png` | tiron / TIRON® PLATINUM 8480 / SRM7H 2.00GHZ / X2360A51 / ©'22 56C (e4) / MALAY |

- **Meshes:** the substrate (`tex_cpu_spv_pcb` / `tex_cpu_l46_pcb`, shared per socket), the IHS (its own texture),
  gold (the lands and the pin-1 triangle), ceramic and solder (the capacitors), and the carrier moving piece.
- **IHS markings:** each IHS has its own Data Matrix code and an etched pin-1 triangle.
- **Triangles:** most of them are the LGA lands, which are real hexagons so they show when the part is held (V5 has
  octagons for about 1,700 lands). The land side also carries the pads in its texture, so a LOD could drop the land
  geometry.
- **Anchors:** `anchor_compare.py` of `cpu_epoch_9124` and `cpu_epoch_9354` against `cpu_epoch_9654` gives 5 / 5
  SAME for both.

## Unboxing: films, caps, stickers and papers

| Id | Films | Caps | Stickers | Docs |
|---|---|---|---|---|
| 10 desktop CPUs | none | none | none | guide, warranty, sticker (case badge) |
| `cpu_epoch_9124` / `9354` / `9654` | none | `cap_cpu_spv` on `A_CAP_PADS_0`, blocks install | none | guide, warranty |
| `cpu_tiron_plat_8480` | none | `cap_cpu_l46` on `A_CAP_PADS_0`, blocks install | none | guide, warranty |

- **Desktop CPUs:** nothing on the part, as on the real product. The clamshell is part of the box (task 19), and
  the models are unchanged.
- **Server CPUs:** they get one new anchor, plus the carrier they already had (`A_CARRIER_0`). The carrier stays on,
  because the CPU is installed in it; the JSON says so under `unbox.carrier`.
  - `A_CAP_PADS_0`, at (0, 0, −0.00004) on the contact face, just under the lands, which stand 0.03 mm proud.
    - Forward −z, up +y, so the cap's local +Z is the pull-off direction and its local +x is the package's −x.
    - Size: SP-V 0.0740 × 0.0774 × 0.0016; L46 0.0630 × 0.1070 × 0.0016.
    - Meta: `model=cap_cpu_spv|cap_cpu_l46,remove=-z,blocks=install`.
- **Cap models**, `cap_cpu_spv` and `cap_cpu_l46` (532 triangles, 1 mesh, tag `glass`):
  - Frame: origin at the contact face centre, +z = pull-off direction (away from the pads).
  - The plate (0.7 mm) overhangs the substrate by 1 mm on each side. That stays below the carrier wall, which starts
    0.25 mm above the contact face.
  - A 1.2 mm rim and two stiffening ribs on the outer side.
  - A pull tab with a grip ridge at −y. The −y end is the same in both frames; it is below the carrier's grip tab.
  - A moulded pin-1 triangle at the package's (+x, −y) corner.
  - `A_HIT_0` at (0, 0, 0.0008), the plate size × 0.0016, meta `remove=+z,travel=0.030,blocks=install`.
  - Where it sits: parent anchor `A_CAP_PADS_0` of the CPU, at the anchor's position with the anchor's rotation
    (identity in the anchor frame).
- **Papers:** `doc_notes` holds 8–10 lines per CPU: the socket, the install steps (lever / rail and carrier / heatsink
  module), the pin-1 triangle, the paste amount, TDP and peak power with the cooler to match, cores and clocks,
  memory rules and handling warnings.

**ONLY ADDED proof.** A rebuild can't show this with `extras_compare.py`, because the heat-spreader prisms
triangulate in a different order on every run: even an unchanged rebuild shows the IHS `.polys`/`.uvs` as CHANGED.
So `cat_cpus_unbox.py` adds the anchor to the committed FBXs instead.
- It imports each FBX with the axis settings that undo `dct_common.export`; a plain round trip compares SAME.
- It adds the anchor with the same `cap_anchor()` the build uses, then re-exports.
- `extras_compare.py <previous FBXs> Assets/Resources/Models` then prints, for all four server CPUs,
  `ONLY ADDED: A_CAP_PADS_0 (12 objects unchanged)`.
- A full rebuild with `build_cat_cpus.py` into a scratch project gives the same six anchors: `anchor_compare.py`
  reports 6 / 6 SAME against the retrofitted FBXs.

```bash
blender -b --factory-startup -P Tools/Blender/cat_cpus_unbox.py -- [cpu_epoch_9124 ...]
blender -b --factory-startup -P Tools/Blender/extras_compare.py -- <previous_fbx_dir> Assets/Resources/Models cpu_epoch_9124 cpu_epoch_9354 cpu_epoch_9654 cpu_tiron_plat_8480
```

## Deviations

- **Real numbers:**
  - `power_w` is the TDP: AMD's TDP, Intel's base power. `specs.peak_w` holds AMD's PPT or Intel's maximum turbo power,
    for PSU sizing.
  - Prices are rounded street prices (October 2026).
  - The S-spec, OPN and lot codes look real but are invented.
- **Fonts:** the art asks for Windows fonts (OCR-A, Agency). On Linux they fall back to Liberation/DejaVu, so the
  serial lines aren't in OCR-A. A Windows rebuild gives the intended fonts with the same layout.
- **L46 package size:** it follows the brief (about 61 × 105 mm), not the real LGA4677 (77.5 × 56.5 mm).
- **Tags:** no new material tags. The carriers use their own `tex_` atlas (flat orange or black swatches plus the
  moulded legend), because no plain orange tag exists.
- **Texture names:** the IHS textures are named `cpu_ihs_<model>`, not `<id>_ihs`, to keep mesh names under 63
  characters (see the hooks section).

## New contracts: server CPU sockets

Both sockets use the desktop CPU frame and anchor kinds, plus a carrier. The model is in `cat_cpus_server.py`.

### `cpu_spv`: Socket SP-V (Arc Epoch, the EPYC 9004 / SP5 analog)

**Frame:**
- Origin at the centre of the bottom (contact) face, +z up, pin 1 at the (+x, −y) corner.
- The package is 0.072 (x) by 0.0754 (y), an LGA with about 6,600 lands (0.94 mm hex pitch; the real SP5 has 6,096).
- The substrate spans z 0..0.0016.
- The IHS is two-tiered:
  - a foot flange, 0.063 × 0.0664, z 0.0016..0.0026, with two notches on each x side at y ±0.021 (the carrier's clip fingers sit in them);
  - a raised top, 0.058 × 0.0636, up to z 0.0064, which carries the markings.
- 0402 capacitors in two rows across both exposed y ends.

**Anchors:**

| Anchor | Position | Forward / up | Size | Meta |
|---|---|---|---|---|
| `A_MARK_PIN1_0` | (0.0340, −0.0357, 0.0016) | +z / +y | 0.006 × 0.006 × 0.002 | `corner=+x-y` (the gold substrate triangle, inset 2 mm, clear of the carrier lip) |
| `A_PASTE_0` | (0, 0, 0.0064) | +z / +y | 0.0464 × 0.0509 × 0.002 | `ihs=0.0580x0.0636` (the raised top) |
| `A_HIT_0` | (0, 0, 0.0032) | +z / +y | 0.072 × 0.0754 × 0.0068 | the package |
| `A_CARRIER_0` | (0, 0, 0.0016) | +z / +y | 0.0816 × 0.0966 × 0.0031 | `socket=SP-V,pose=installed,clip=+z,rail=+y,color=#f26b1d` |
| `A_CAP_PADS_0` | (0, 0, −0.00004) | −z / +y | 0.0740 × 0.0774 × 0.0016 | `model=cap_cpu_spv,remove=-z,blocks=install` (the contact cover, see Unboxing) |
| `A_MARK_CARRIER_0@A_CARRIER_0` | (0.0358, −0.0375, 0.0026) | +z / +y | 0.005 × 0.005 × 0.002 | `corner=+x-y` (the carrier's own triangle) |

**The carrier** (`carrier@A_CARRIER_0#tex_cpu_spv_carrier`, a moving piece):
- Bright orange plastic, modelled in the installed pose. Its pivot is the anchor, on the substrate top at the package centre.
- A wall around the substrate edge (from z 0.00025, so it never touches the socket lands), and a 1.3 mm lip over the substrate top.
- Four clip fingers in the IHS flange notches.
- Rails along both x sides (y ±0.0307, z 0.0017..0.0026) that slide into the socket's rail frame.
- Two stop hooks at the +y end.
- A grip tab at −y with a finger slot and the moulded legend "SP-V", an arrow pointing +y, "PUSH" and "CARRIER A1".
- A pin-1 triangle at the (+x, −y) corner.
- Meta: `clip=+z` means the carrier lifts off the package along its +z (forward). `rail=+y` means the package in
  its carrier slides into the socket's rail frame towards +y, grip first in the hand.

**What the socket needs** (for a future SP-V board, `mb_*` with `socket=SP-V`):
- `A_SOCKET_CPU_0`: the seating plane at the socket centre (forward +z), with the package frame on it. The pin-1 corner `A_MARK_SOCKET_0` is at (+x, −y).
- A **rail frame** (moving piece, `A_RAIL_CPU_0`): hinged at the socket's +y end, `hinge=x,open=~60`. In the open pose its two channels line up with the carrier rails (inner width 0.0860, at the carrier rail height), so the carrier slides in along +y until the hooks stop. Then it closes onto the socket.
- A **force frame** (moving piece, `A_LEVER_CPU_0` style, `hinge=x,open=~110`) over the rail frame, held by three captive Torx T20 screws tightened in sequence (`A_SCREW_T20_0..2`, meta `order=1..3`).
- A protective socket cap (`A_COVER_CPU_0`).
- `A_SOCKET_COOLER_0` at the IHS top (z 0.0064 above the seating plane), with a footprint keep-out of about 0.105 × 0.080 for SP5-style heatsinks.
- The game must not seat the package without its carrier: the carrier holds the package in the rail.

### `cpu_l46`: Socket L46 (Tiron Platinum, the Xeon Scalable / LGA4677 analog)

**Frame:**
- As SP-V: origin at the contact face centre, +z up, pin 1 at (+x, −y), the long side along y.
- The package is 0.061 (x) by 0.105 (y), with about 7,300 lands (0.95 mm hex pitch) and a capacitor island in the middle of the land side (0.010 × 0.034).
- The substrate spans z 0..0.0016.
- The IHS:
  - a foot flange, 0.051 × 0.082, z 0.0016..0.0027, with four ears on the x sides at y ±0.031 (0.057 across the ears), where the clip fingers press;
  - a raised top, 0.048 × 0.079, up to z 0.0066.
- Four rows of capacitors across each y end, and small clusters beside the ears.

**Anchors:**

| Anchor | Position | Forward / up | Size | Meta |
|---|---|---|---|---|
| `A_MARK_PIN1_0` | (0.0285, −0.0505, 0.0016) | +z / +y | 0.006 × 0.006 × 0.002 | `corner=+x-y` |
| `A_PASTE_0` | (0, 0, 0.0066) | +z / +y | 0.0384 × 0.0632 × 0.002 | `ihs=0.0480x0.0790` |
| `A_HIT_0` | (0, 0, 0.0033) | +z / +y | 0.061 × 0.105 × 0.0070 | the package |
| `A_CARRIER_0` | (0, 0, 0.0016) | +z / +y | 0.0706 × 0.1242 × 0.0031 | `socket=L46,pose=installed,clip=+z,mount=heatsink,color=#26282b` |
| `A_CAP_PADS_0` | (0, 0, −0.00004) | −z / +y | 0.0630 × 0.1070 × 0.0016 | `model=cap_cpu_l46,remove=-z,blocks=install` (the contact cover, see Unboxing) |
| `A_MARK_CARRIER_0@A_CARRIER_0` | (0.0303, −0.0523, 0.0026) | +z / +y | 0.005 × 0.005 × 0.002 | `corner=+x-y` |

**The carrier clip** (`carrier@A_CARRIER_0#tex_cpu_l46_carrier`, a moving piece):
- Black plastic, the same build as the SP-V carrier: wall, lip, four fingers over the IHS ears, side latches, a grip tab with "L46", "HEATSINK SIDE UP" and "CLIP E1A", and a pin-1 triangle.
- `mount=heatsink`: as on the real platform, the clip snaps the package to the heatsink. The heatsink, clip and CPU then go onto the socket together as one module.

**What the socket needs** (a future L46 board):
- `A_SOCKET_CPU_0` (seating plane, forward +z) and `A_MARK_SOCKET_0` at (+x, −y).
- A **bolster plate** with four studs for the heatsink module, with Torx T30 nuts (`A_SCREW_T30_0..3`, meta `order=1..4`, tightened in a cross pattern).
- Two alignment posts that match the carrier's grip end (−y) and hook end (+y), so the module only fits one way round.
- A protective socket cap (`A_COVER_CPU_0`).
- `A_SOCKET_COOLER_0` at the IHS top (z 0.0066), with a footprint of about 0.078 × 0.110.
- No lever: the heatsink nuts load the socket. The CPU is installed into the heatsink first (the carrier clip), not into the socket.
