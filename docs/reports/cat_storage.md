# Catalogue 14 report: storage

Scripts: `Tools/Blender/build_cat_storage.py` (runner, configs, label art, catalogue data, report file), with the
helpers `cat_storage_ssd.py` (M.2 and 2.5" SATA builders) and `cat_storage_hdd.py` (3.5" HDD and U.2 builders).
`build_ssd.py` is **not** edited: its outline, finger, connector and hole constants are imported, so no SAME proof is
needed for `ssd_1tb` and `ssd_sata_500`.

## Status

| # | id | contract | state |
|---|---|---|---|
| M.2 1 | `ssd_sorin_990pro_1tb` | ssd_1tb | done |
| M.2 2 | `ssd_sorin_990pro_2tb_hs` | ssd_1tb | done |
| M.2 3 | `ssd_sorin_980_500` | ssd_1tb | done |
| M.2 4 | `ssd_westline_sn850x_2tb` | ssd_1tb | done |
| M.2 5 | `ssd_westline_sn850x_1tb_hs` | ssd_1tb | done |
| M.2 6 | `ssd_westline_sn580_1tb` | ssd_1tb | done |
| M.2 7 | `ssd_crux_p3plus_2tb` | ssd_1tb | done |
| M.2 8 | `ssd_crux_t705_2tb_hs` | ssd_1tb | done |
| SATA 1 | `ssd_sorin_870_1tb` | ssd_sata_500 | done |
| SATA 2 | `ssd_crux_mx500_2tb` | ssd_sata_500 | done |
| SATA 3 | `ssd_kingsland_a400_480` | ssd_sata_500 | done |
| HDD 1 | `hdd_seacrest_2tb` | hdd35 (new) | not yet |
| HDD 2 | `hdd_westline_4tb` | hdd35 (new) | not yet |
| HDD 3 | `hdd_seacrest_8tb` | hdd35 (new) | not yet |
| HDD 4 | `hdd_seacrest_exos_20tb` | hdd35 (new) | not yet |
| U.2 1 | `ssd_sorin_pm9a3_3840` | u2 (new) | not yet |
| U.2 2 | `ssd_sorin_pm9a3_7680` | u2 (new) | not yet |

`docs/catalog/storage.json` already lists all 17 parts (it is written from `CATALOG` in the runner).

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_storage.py -- [ids...] [--nopreview] [--json]
```

No ids = all 17. Each id writes `Assets/Resources/Models/<id>.fbx`, its texture
`Assets/Resources/Models/Textures/<file>.png`, the EEVEE previews `Logs/ModelPreviews/<id>_0..3.png`, and its block
in `Logs/ModelPreviews/cat_storage_report.txt` (the other blocks are kept). `--json` only rewrites
`docs/catalog/storage.json`. About 1 minute per model with previews (Linux, bpy 5.0.1, 4 cores).

**Texture names.** The texture file is the id without its kind prefix (`ssd_westline_sn850x_1tb_hs` →
`Textures/westline_sn850x_1tb_hs.png`, tag `tex_westline_sn850x_1tb_hs`), and the joined meshes are named
`m_<tag>#<tag>`. With the id as both, the longest names went over Blender's 63-character limit and the tag was cut.

README line for the script table:

| `build_cat_storage.py` | Catalogue storage: 8 M.2 NVMe `ssd_sorin_*/ssd_westline_*/ssd_crux_*`, 3 2.5" SATA, 4 3.5" HDDs `hdd_*`, 2 U.2 `ssd_sorin_pm9a3_*` (helpers `cat_storage_ssd.py`, `cat_storage_hdd.py`) |

## M.2 2280 NVMe (the ssd_1tb contract)

Frame and anchors exactly as `ssd_1tb`: origin at the PCB centre on its bottom face, PCB z 0..0.0008, M-key fingers at
−x, the screw notch at +x.

- `A_SCREW_PH0_0` (0.04, 0, 0.0008), meta `notch=+x`
- `A_KEY_M2_0` (−0.04, 0.006, 0.0004), meta `key=M,y=0.0060`
- `A_HIT_0` the body (grown to cover a heatsink, see below)

`anchor_compare.py` against `ssd_1tb.fbx`:

| id | tris | meshes | SAME | DIFF | sides | heatsink |
|---|---|---|---|---|---|---|
| `ssd_sorin_990pro_1tb` | 1534 | 6 | 3 | 0 | 1 | – |
| `ssd_sorin_990pro_2tb_hs` | 1462 | 8 | 2 | 1 (`A_HIT_0`) | 1 | 8.4 mm, RGB |
| `ssd_sorin_980_500` | 1518 | 6 | 3 | 0 | 1 | – |
| `ssd_westline_sn850x_2tb` | 1298 | 6 | 3 | 0 | **2** | – |
| `ssd_westline_sn850x_1tb_hs` | 1630 | 8 | 2 | 1 (`A_HIT_0`) | 1 | 9.1 mm, RGB |
| `ssd_westline_sn580_1tb` | 1266 | 6 | 3 | 0 | 1 | – |
| `ssd_crux_p3plus_2tb` | 1310 | 6 | 3 | 0 | 1 | – |
| `ssd_crux_t705_2tb_hs` | 1722 | 7 | 2 | 1 (`A_HIT_0`) | **2** | 22.6 mm, fins |

The only DIFF is the hitbox of the three heatsink drives, which grows to the heatsink (990 Pro: centre z 0.0030, size
0.080 × 0.0242 × 0.0084; SN850X: z 0.0033, 0.080 × 0.0242 × 0.0091; T705: z 0.0093, 0.080 × 0.0246 × 0.0226). The
anchors that install the drive (`A_KEY_M2_0`, `A_SCREW_PH0_0`) are SAME on all eight.

**Looks.** Each drive has its own controller, DRAM (990 Pro, SN850X, T705) or DRAM-less layout (980, SN580, P3 Plus),
one or two NAND packages, the PMIC and inductor, passives, a full-length printed label (`tex_`) in the real brand's
style, and a regulatory sticker underneath. The 990 Pro has the nickel-lidded controller. The SN850X 2 TB and the
T705 carry NAND on both sides (the sticker sits on the bottom chips). The P3 Plus has a green PCB, the others black.

**Heatsink drives** (`"has_heatsink": true` in specs) can't take the motherboard's M.2 heatsink: the game should hide or
refuse `A_COVER_M2_0` on the board when one of these is installed.
- The shells leave the M.2 fingers (x < −0.035) and the screw notch (x > 0.0366) free, so the drive still goes into the
  slot and takes the board's PH0 screw.
- Under the PCB they reach z −0.0012 (990 Pro, SN850X) or −0.0020 (T705, chips on both sides). The board leaves
  0.0025 under the SSD (`M2_Z` 4.1 mm over a 1.6 mm PCB), so they fit.
- Heights: 990 Pro 8.4 mm, SN850X 9.1 mm (the real drives are 8.2 and 8.8 mm), T705 22.6 mm (≤ 25 mm for Gen5). The
  T705 is too tall for most boards' M.2 area under a GPU; the game may want a clearance check against the x16 card.
- RGB light bars (`rgb` tag) on the 990 Pro and SN850X heatsinks: a strip on the top at the +x end and the end face.

## 2.5" SATA SSD (the ssd_sata_500 contract)

Built by `cat_storage_ssd.build_sata`: the `build_ssd.build_sata` tray, pocket, connectors, holes and anchors, with
the look from the config (top art, cover colour, tray tag, lid bevel, optional top screws).

Frame: origin at the body centre, x = length (connectors at −x), y = thickness (+y = top), z = width. Anchors
`A_PORT_SATADATA_0`, `A_PORT_SATAPWR_0`, `A_SCREW_PH2_0..3` (meta `m3,side`), `A_HIT_0`.

| id | tris | meshes | anchor_compare vs `ssd_sata_500` |
|---|---|---|---|
| `ssd_sorin_870_1tb` | 1470 | 6 | SAME 7 / 7 |
| `ssd_crux_mx500_2tb` | 1598 | 6 | SAME 7 / 7 |
| `ssd_kingsland_a400_480` | 1470 | 6 | SAME 7 / 7 |

Looks: the 870 is a black metal shell with a rounded lid and a dark printed top; the MX500 a grey brushed-metal top
with four lid screws and a black label; the A400 a black plastic shell (`black_plastic` tray) with the red-accented
label. Each has its own bottom sticker.

## 3.5" hard drives (new contract `hdd35`)

Not built yet.

## Enterprise U.2 (new contract `u2`)

Not built yet.

## Catalogue data

`docs/catalog/storage.json`: 17 entries, category `Storage`, `game.storage_gb` and `game.sata25` (true only for the
three 2.5" SATA SSDs; the HDDs and U.2 drives use new contracts and say so with `new_contract: true`), `perf: 0`.
Prices are rough US street prices of the real analog in late 2026. Names avoid the real series trademarks:
"870 Edge" (EVO), "Westline Onyx" (WD_BLACK), "Westline Azure" (WD Blue), "Seacrest Shoreline" (BarraCuda),
"Seacrest Tidewolf" (IronWolf), "Seacrest Abyss" (Exos). Model numbers keep the real scheme.

## Deviations

- No hooks were added to `build_ssd.py`; the catalogue builders live in `cat_storage_ssd.py` and import its constants.
- Texture files and mesh-name prefixes are shortened (see Rebuild) to stay inside Blender's name limit.
- The heatsink drives' `A_HIT_0` differs from `ssd_1tb` (it covers the heatsink).
