# Catalogue 10 report: CPUs

14 CPUs: 10 desktop parts on the existing V5 and L17 contracts, and 4 server parts on two new socket contracts
(SP-V and L46). Catalogue data: `docs/catalog/cpus.json`.

## Status

| Id | Name | Socket | Contract | Status |
|---|---|---|---|---|
| `cpu_arc7_9800x3d` | Arc 7 9800X3D | V5 | `cpu_arc5` | done |
| `cpu_arc5_9600x` | Arc 5 9600X | V5 | `cpu_arc5` | done |
| `cpu_arc7_9700x` | Arc 7 9700X | V5 | `cpu_arc5` | done |
| `cpu_tiron_i5_14600k` | Tiron i5-14600K | L17 | `cpu_tiron5` | done |
| `cpu_tiron_i7_14700k` | Tiron i7-14700K | L17 | `cpu_tiron5` | done |
| `cpu_tiron_i9_14900k` | Tiron i9-14900K | L17 | `cpu_tiron5` | building |
| `cpu_arc9_9950x3d` | Arc 9 9950X3D | V5 | `cpu_arc5` | building |
| `cpu_arc3_8300g` | Arc 3 8300G | V5 | `cpu_arc5` | building |
| `cpu_tiron_i3_14100` | Tiron i3-14100 | L17 | `cpu_tiron5` | building |
| `cpu_tiron_i7_14700` | Tiron i7-14700 | L17 | `cpu_tiron5` | building |
| `cpu_epoch_9654` | Arc Epoch 9654 | SP-V | new `cpu_spv` | not done |
| `cpu_epoch_9354` | Arc Epoch 9354 | SP-V | new `cpu_spv` | not done |
| `cpu_epoch_9124` | Arc Epoch 9124 | SP-V | new `cpu_spv` | not done |
| `cpu_tiron_plat_8480` | Tiron Platinum 8480 | L46 | new `cpu_l46` | not done |

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_cpus.py -- [ids...] [--nopreview]
```

With no ids it builds all 14. It writes `Assets/Resources/Models/<id>.fbx`, the textures, the previews
`Logs/ModelPreviews/<id>_<n>.png`, the per-model report `Logs/ModelPreviews/<id>_report.txt`, and the family anchor
report `Logs/ModelPreviews/cat_cpus_report.txt`. The desktop builds also re-render the shared `cpu_v5_pcb.png` and
`cpu_l17_pcb.png` with unchanged art; they are not committed.

Built with Blender 5.0.1 as the `bpy` Python module (download.blender.org is blocked in the cloud session), with
`bpy.app.binary_path` set to the package folder so the EEVEE previews find the studio HDRI.
