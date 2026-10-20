# Task 03 report: new parts to buy, with retail boxes

Four new catalog parts, each built by reusing an existing builder with a new spec or style, so they drop into the
game exactly like their siblings. Status: **in progress** (this report is updated with every model).

| Part | Sibling(s) | Status |
|---|---|---|
| `cpu_arc9` | `cpu_arc5`, `cpu_arc7` | done |
| `gpu_rx77` | `gpu_rx66`, `gpu_rx88` | to do |
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

## Deviations

None so far.
