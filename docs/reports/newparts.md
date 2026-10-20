# Task 03 report: new parts to buy, with retail boxes

Four new catalog parts, each built by reusing an existing builder with a new spec or style, so they drop into the
game exactly like their siblings. Status: **in progress** (this report is updated with every model).

| Part | Sibling(s) | Status |
|---|---|---|
| `cpu_arc9` | `cpu_arc5`, `cpu_arc7` | done |
| `gpu_rx77` | `gpu_rx66`, `gpu_rx88` | done |
| `case_aero` | `case_breeze` | to do |
| `mb_ridge_x5` + `io_ridge_x5` | `mb_ridge_b5` + `io_ridge_b5` | to do |
| `box_cpu_arc9`, `box_gpu_rx77`, `box_case_aero`, `box_mb_ridge_x5` | the sibling boxes | to do |

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_parts_d.py -- [cpu_arc9 ...] [--nopreview]
```

With no ids, `build_parts_d.py` builds every part of this batch. It writes `Assets/Resources/Models/<id>.fbx`, the
textures, `Logs/ModelPreviews/<id>_<n>.png` and `Logs/ModelPreviews/<id>_report.txt` (every mesh with its
triangles, every anchor with position, axes, size and meta).

Anchor comparison against a sibling (used for the tables below):

```bash
blender -b --factory-startup -P Tools/Blender/anchor_compare.py -- Assets/Resources/Models/cpu_arc5.fbx Assets/Resources/Models/cpu_arc9.fbx
```

These models were built with Blender 5.0.1 as the `bpy` Python module (download.blender.org was blocked in the
cloud session); rebuilding a committed model this way gives an FBX that `extras_compare.py` reports SAME (for
example `plug_atx24`), so the module build matches the desktop Blender build.

---

## 1. `cpu_arc9`: ARC 9 9900X (Socket V5)

- **Script:** `build_parts_d.py` adds a spec to `build_cpu.SPECS` and calls `build_cpu.build`; `build_cpu.py` itself
  is unchanged.
- **Size:** 40 × 40 mm V5 LGA package, IHS top at z 0.006 (same package, outline and octopus IHS as arc5 and arc7).
- **Triangles:** 13,696 in 5 meshes (the same as arc5 and arc7).
- **Frame:** origin at the centre of the contact face, +z up, pin 1 at the (+x, −y) corner.
- **Textures:** `cpu_arc9_ihs.png` (new laser-etched markings: ARC logo, "ARC 9 9900X", "12-CORE",
  OPN 100-000001277, lot 9MK4813R50093, "DIFFUSED IN TAIWAN", "MADE IN MALAYSIA"); the substrate art is the shared
  `cpu_v5_pcb.png` (unchanged).

**Anchors**

| Anchor | Position | Size | Meta |
|---|---|---|---|
| `A_HIT_0` | (0, 0, 0.0030) | 0.040 × 0.040 × 0.0064 | |
| `A_MARK_PIN1_0` | (0.0193, −0.0193, 0.0012) | 0.006 × 0.006 × 0.002 | `corner=+x-y` |
| `A_PASTE_0` | (0, 0, 0.0060) | 0.030 × 0.030 × 0.002 | `ihs=0.0350x0.0380` |

**Anchor comparison** (`anchor_compare.py`): position, axes, size and meta of every anchor.

| Anchor | vs `cpu_arc5` | vs `cpu_arc7` |
|---|---|---|
| `A_HIT_0` | SAME | SAME |
| `A_MARK_PIN1_0` | SAME | SAME |
| `A_PASTE_0` | SAME | SAME |
| **Summary** | 3 / 3 SAME | 3 / 3 SAME |

**Suggested catalog data**

| Field | Value |
|---|---|
| Brand | ARC |
| Name | ARC 9 9900X |
| Socket | V5 (fits `mb_ridge_b5` and `mb_ridge_x5`) |
| Cores / threads | 12 / 24 |
| Clocks | 4.4 GHz base, 5.6 GHz boost |
| Cache | 64 MB L3 |
| Memory | DDR5 |
| TDP / power draw | 120 W TDP (about 160 W peak package power) |
| Price | $449 |
| Retail box | `box_cpu_arc9`, 0.11 × 0.07 × 0.11 (as the other CPUs) |

---

## 2. `gpu_rx77`: VOLTRA RX 7700 12GB (2.5-slot, triple fan)

- **Script:** `build_parts_d.py` adds a spec to `build_gpu.SPECS`; its look comes from style hooks in the spec
  (`backplate`, `overlay`, `skirts`, `logo`, `trim`). `build_gpu.py` was made configurable for this (see "Existing
  models unchanged" below): optional spec keys, absent on rx66/rx88, so those two cards build exactly as before.
- **Size:** 0.270 (x) × 0.0527 (y, fan face to backplate) × 0.118 (z) m; the PCB is 0.223 long (to x −0.128), the cooler
  runs past it to x −0.175 with a flow-through window in the backplate. 2.5 slots thick, on a 2-slot bracket.
- **Triangles:** 53,966 in 21 meshes (rx66 39,636; rx88 61,518).
- **Frame:** as rx66/rx88: origin at the PCIe contact edge, the bracket at x +0.095, the card runs towards −x, the cooler
  faces −y, the height runs along +z; gold fingers at y −0.001, z −0.002.
- **Look:** a gunmetal dark-grey shroud (`steel_dark`) with silver (`alu`) fan rings, silver edge rails, black wedges
  with silver chevrons between the fans and silver corner blades; three 78 mm 11-blade fans with VOLTRA hub stickers;
  five nickel heat pipes through an aluminium fin stack; a brushed silver backplate (`alu`) with a black VOLTRA print,
  four GPU-bracket screws and a hex-perforated flow-through window; a steel bracket with 3 × DP + HDMI and vent slots;
  the logo plate and RGB strip on the top edge; two PCIe 8-pin sockets on the top edge.
- **Texture:** `gpu_rx77.png` (logo plates, hub sticker, serial label, PCB back), from `build_gpu.make_texture`.

**Anchors** (Unity metres, card frame)

| Anchor | Position | Forward / up | Size | Meta |
|---|---|---|---|---|
| `A_PORT_PCIE8_0` | (−0.1005, −0.0066, 0.1120) | +z / +y | 0.0226 × 0.0126 × 0.012 | `pins=8,latch=+y` |
| `A_PORT_PCIE8_1` | (−0.0790, −0.0066, 0.1120) | +z / +y | 0.0226 × 0.0126 × 0.012 | `pins=8,latch=+y` |
| `A_PORT_DP_0..2` | (0.0965, −0.0046, 0.018 / 0.037 / 0.056) | +x / +y | 0.019 × 0.008 × 0.012 | `kind=displayport,chamfer=-y` |
| `A_PORT_HDMI_0` | (0.0965, −0.0046, 0.075) | +x / +y | 0.017 × 0.008 × 0.012 | `kind=hdmi,narrow=-y` |
| `A_SCREW_PH2_0` / `_1` | (0.1015, −0.0069 / −0.0272, 0.1065) | +z / +x | 0.008 cube | `slot=0` / `slot=1` |
| `A_FAN_0..2` | x −0.1248 / −0.0402 / 0.0443, y −0.0423, z 0.0600 | −y / +z | 0.078 × 0.078 × 0.013 | `axis=z,spin=-1,rpm=1900` |
| `A_FILM_BACKPLATE_0` | (−0.0408, 0.0029, 0.0605) | +y / +z | 0.2615 × 0.110 × 0.001 | `film=clear,peel_from=+x,chamfer=0.004@+x,screws=proud` |
| `A_FILM_SHROUD_0` | (−0.0070, −0.0426, 0.1184) | +z / +y | 0.0936 × 0.0121 × 0.001 | `film=clear,on=logo_plate,peel_from=-x` |
| `A_HIT_0` | (−0.0400, −0.0236, 0.0590) | | 0.270 × 0.0527 × 0.118 | (the card body) |
| `A_HIT_1` | (0.1010, −0.0166, 0.0465) | | 0.011 × 0.0392 × 0.120 | (the bracket) |
| `A_HIT_2` | (0, −0.0010, −0.0028) | | 0.090 × 0.003 × 0.006 | (the PCIe edge; `cap_pcie16` sits here) |

The fan rotors (`gpufan<n>_rotor@A_FAN_<n>#fan_black`) and hub stickers (`gpufan<n>_sticker@A_FAN_<n>#tex_gpu_rx77`)
are moving pieces of their fan anchors, as on the siblings.

**Anchor comparison** (`anchor_compare.py`; "same" = position, axes, size and meta identical)

| Anchor | vs `gpu_rx66` | vs `gpu_rx88` | Why it differs |
|---|---|---|---|
| `A_PORT_DP_0..2`, `A_PORT_HDMI_0` | SAME | SAME | |
| `A_SCREW_PH2_0..1` | SAME | SAME | |
| `A_HIT_1` (bracket), `A_HIT_2` (PCIe edge) | SAME | SAME | |
| `A_PORT_PCIE8_0` | position only (size and meta SAME) | rx88 has `A_PORT_12V2X6_0` instead | on this card's top edge, near the end of its PCB |
| `A_PORT_PCIE8_1` | new | new | the second 8-pin, 21.5 mm beside the first |
| `A_FAN_0..2` | position, size, rpm (rx66 has 2 fans) | position and size | three 78 mm fans on a 270 mm card |
| `A_FILM_BACKPLATE_0`, `A_FILM_SHROUD_0`, `A_HIT_0` | position and size | position and size | they follow the card's size |
| **Summary** | 8 SAME, 6 DIFF, 2 only in rx77 | 8 SAME, 6 DIFF, 1 only in rx88, 2 only in rx77 | |

**Suggested catalog data**

| Field | Value |
|---|---|
| Brand | VOLTRA |
| Name | VOLTRA RX 7700 12GB |
| Memory | 12 GB GDDR6, 192-bit |
| Clocks | 2.17 GHz game, 2.54 GHz boost |
| Outputs | 3 × DisplayPort 1.4, 1 × HDMI 2.1 |
| Power connectors | 2 × PCIe 8-pin |
| Board power / power draw | 245 W (recommended PSU 700 W) |
| Size | 270 mm, 2.5 slots |
| Price | $419 |
| Retail box | `box_gpu_rx77`, 0.36 × 0.09 × 0.17 (as the other GPUs) |

---

## Existing models unchanged

`build_gpu.py` (made configurable for `gpu_rx77`): `gpu_rx66` and `gpu_rx88` were re-exported into a scratch project
(`DCT_PROJECT`) with the unchanged script and with the edited script, and compared:

```
COMPARE gpu_rx66: SAME (37 objects)
COMPARE gpu_rx88: SAME (38 objects)
```

Their textures `gpu_rx66.png` and `gpu_rx88.png` are pixel-identical too (max difference 0). The comparison is against a
re-export from the unchanged script in the same environment because Linux re-exports never match the committed
Windows exports exactly: the unchanged script already differs in the text meshes (Liberation fonts stand in for
Agency FB and Eras) and in the heat-pipe sweep vertices. None of the re-exports are committed.

## Deviations

None so far.
