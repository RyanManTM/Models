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
| HDD 1 | `hdd_seacrest_2tb` | hdd35 (new) | done |
| HDD 2 | `hdd_westline_4tb` | hdd35 (new) | done |
| HDD 3 | `hdd_seacrest_8tb` | hdd35 (new) | done |
| HDD 4 | `hdd_seacrest_exos_20tb` | hdd35 (new) | done |
| U.2 1 | `ssd_sorin_pm9a3_3840` | u2 (new) | done |
| U.2 2 | `ssd_sorin_pm9a3_7680` | u2 (new) | done |

`docs/catalog/storage.json` already lists all 17 parts (it is written from `CATALOG` in the runner).

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_storage.py -- [ids...] [--nopreview] [--json]
```

No ids = all 17 plus `cap_u2`. Each id writes `Assets/Resources/Models/<id>.fbx`, its texture
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

Built by `cat_storage_hdd.build_hdd`. `new_contract: true` in the JSON.

**Frame:**
- Origin at the body centre. x = length 0.147 (the SATA connectors at −x), y = height 0.0261 (+y = the top cover and
  label), z = width 0.1016 (SFF-8301 sizes).
- The PCB is on the bottom (−y) at the connector end, components facing out. The casting overhangs the connectors.

**Anchors** (Unity metres):

| anchor | pos | fwd | up | size | meta |
|---|---|---|---|---|---|
| `A_PORT_SATA_0` | (−0.0735, −0.00915, 0.0300) | −x | +y | 0.012 × 0.007 × 0.008 | `depth=0.006,pins=7` |
| `A_PORT_SATAPWR_0` | (−0.0735, −0.00915, 0.0116) | −x | +y | 0.024 × 0.007 × 0.008 | `depth=0.006,pins=15` |
| `A_HOLE_0..3` | x 0.0450 / −0.0566, y −0.0067, z ±0.0508 | ±z (outward) | +y | 0.006³ | `6-32,side` |
| `A_HOLE_4..9` | x 0.0319 / −0.01255 / −0.0443, y −0.01305, z ±0.04763 | −y | +x | 0.006³ | `6-32,bottom` |
| `A_HIT_0` | (0, 0, 0) | +z | +y | 0.147 × 0.0261 × 0.1016 | |

- The side holes sit 28.5 and 130.1 mm from the front (+x) end, 6.35 mm above the bottom. The bottom holes sit 41.6,
  86.05 and 117.8 mm from the front, 95.25 mm apart across the width (SFF-8301 positions).
- The plugs are the existing `plug_sata_data` and `plug_sata_power`, the same sockets as on the 2.5" drives.
  `A_PORT_SATA_0` is the data socket; the brief names it that, where the 2.5" contract says `A_PORT_SATADATA_0`.

**What the game needs for a 3.5" bay** (cases only have `A_SOCKET_SSD25_*` today):
- A new case socket `A_SOCKET_HDD35_<n>`: the drive's origin pose in the bay or cage. Local +Z = the slide-in direction
  reversed (the side the drive comes from), local +Y = the label side. The bay must leave the −x end open for cables
  (about 0.03 m behind it for the SATA plugs' bend).
- Screws: four 6-32 UNC screws into `A_HOLE_0..3` (side rails), or `A_HOLE_4..9` for a bottom mount. A `screw_hdd`
  (6-32, coarse thread, a larger head than the M3 `screw_ph2`) would be new, or `screw_ph2` can stand in. Tool-less
  trays only need the side-hole positions as pin locations.
- Cable: the PSU's SATA power plug and the board's SATA data cable, the same as the 2.5" SSD.
- Rough clearance: 0.147 × 0.0261 × 0.1016 m plus the plug length at −x.

**Models:**

| id | tris | meshes | look |
|---|---|---|---|
| `hdd_seacrest_2tb` | 3372 | 9 | stamped steel cover with 8 Torx screws, a light label with the dark brand band and a teal wave logo, a breather hole |
| `hdd_westline_4tb` | 3336 | 9 | the same mechanics, a white label with the blue Azure band |
| `hdd_seacrest_8tb` | 3324 | 9 | a charcoal NAS label with an orange stripe, the wolf-head emblem and the NAS badge |
| `hdd_seacrest_exos_20tb` | 2068 | 9 | helium: a flush welded top cover with the weld seam, no screws, no breather hole, a white and navy label with the He badge |

All four have the cast aluminium base with the side groove and rails, the green PCB underneath (traces, test pads,
SoC, DRAM, motor controller, passives), the spindle motor with its label, casting ribs, and SATA sockets with
real shrouds, keys and contacts. The labels read in portrait, with the connector end at the bottom.

## Enterprise U.2 (new contract `u2`)

Built by `cat_storage_hdd.build_u2`. `new_contract: true` in the JSON.

**Frame:** the `ssd_sata_500` frame, 15 mm thick. Origin at the body centre, x = length 0.10045 (connector at −x),
y = thickness 0.015 (+y = the finned top), z = width 0.06985.

**Anchors:**

| anchor | pos | fwd | up | size | meta |
|---|---|---|---|---|---|
| `A_PORT_U2_0` | (−0.05023, −0.0050, 0.0052) | −x | +y | 0.040 × 0.007 × 0.008 | `sff8639,pcie=4x4,depth=0.0045` |
| `A_SCREW_PH2_0..3` | x −0.0360 / 0.0406, y −0.0045, z ±0.03492 | ±z | +y | 0.006³ | `m3,side` |
| `A_HOLE_0..3` | x −0.0360 / 0.0406, y −0.0075, z ±0.03086 | −y | +x | 0.006³ | `m3,bottom` |
| `A_HIT_0` | (0, 0, 0) | +z | +y | 0.10045 × 0.015 × 0.06985 | |

- The side and bottom holes have the same x and z as `ssd_sata_500` and sit 3 mm above the bottom, like SFF-8201.
  So a 2.5" 15 mm bay or sled fits both, only taller.
- The SFF-8639 connector is one wide tongue over the span of the SATA data and power segments (z −0.0151..0.0255),
  with the SATA-style key and contacts on both faces. `A_PORT_U2_0` is at its centre.
- **What the game needs:** a U.2 cable or backplane plug (`plug_u2`: SFF-8639 to SlimSAS/OCuLink, or a server
  backplane slot). Desktop boards have no U.2 port, so it's a server part: a 2.5" hot-swap bay in `srv_*` chassis
  (task 18) with a `A_SOCKET_U2_<n>` pose. Power comes through the same connector.

| id | tris | meshes |
|---|---|---|
| `ssd_sorin_pm9a3_3840` | 2026 | 7 |
| `ssd_sorin_pm9a3_7680` | 2026 | 7 |

Looks: an aluminium shell with 15 longitudinal fins over the top, a flat band with the engraved-style SORIN logo at
the connector end, a seam to the bottom cover, four cover screws and a large spec label underneath. The two
capacities differ only in their labels, like the real drives.

## Unboxing: films, caps, papers

Following "The unboxing on every part" in `docs/tasks/catalog/README.md`. The films are anchors only (the game builds
the peel mesh), and the U.2 cap is a separate model. `meta` gives `peel` and `tab` in the film anchor's own axes.

| part | bit | anchor / model | pose (Unity, the part's frame) | size | meta |
|---|---|---|---|---|---|
| `ssd_sorin_870_1tb`, `ssd_crux_mx500_2tb`, `ssd_kingsland_a400_480` | clear film on the top label | `A_FILM_LABEL_0` | (0, 0.00352, 0), fwd +y, up +z (local x = drive −x) | 0.098 × 0.06785 × 0.0001 | `film=clear,on=top_label,peel=-x,tab=+x+y` (tab at the connector end, peels towards the far end) |
| `ssd_sorin_990pro_2tb_hs` | clear film on the heatsink top | `A_FILM_HEATSINK_0` | (0.0008, 0, 0.00702), fwd +z, up +y | 0.0692 × 0.0216 × 0.0001 | `film=clear,on=heatsink_top,peel=-x,tab=+x+y` |
| `ssd_westline_sn850x_1tb_hs` | film on the flat, printed part of the top (the fins are bare) | `A_FILM_HEATSINK_0` | (−0.01385, 0, 0.00662), fwd +z, up +y | 0.0399 × 0.0216 × 0.0001 | same |
| `ssd_crux_t705_2tb_hs` | film on the printed brand bar over the fins | `A_FILM_HEATSINK_0` | (0.0008, 0, 0.02062), fwd +z, up +y | 0.0700 × 0.0058 × 0.0001 | same |
| `ssd_sorin_pm9a3_3840`, `ssd_sorin_pm9a3_7680` | black plastic connector cover | model `cap_u2` | at `A_PORT_U2_0`, identity (local +Z = pull = drive −x) | | `A_HIT_0` `remove=+z,travel=0.004,port=u2,blocks=plug`; `A_GRIP_0` `pull=+z` |
| the other 5 M.2 drives | none: the printed label is the cover | | | | |
| the 4 HDDs | none: they ship in an anti-static bag (the box's job) | | | | |

**`cap_u2`** (192 triangles, 1 mesh, `dark_plastic`; built by `cat_storage_hdd.build_cap_u2`, id `cap_u2`, previews
`cap_u2_0..1.png`). Its frame is the drive's `A_PORT_U2_0`: origin at the pocket mouth, +z out of the drive.
- An insert fills the connector pocket round the tongue and key (z −0.0036..0; the pocket's back wall is at −0.0038).
- A 45 × 6.8 mm flange sits on the end face, with a ribbed 12 mm pull tab standing out to z 0.0072.
- `A_HIT_0` (0, 0.001, 0.0018), size 0.045 × 0.0068 × 0.0108. `A_GRIP_0` (0, 0.001, 0.0042).

**Re-export proof.** The six changed FBX files were re-exported with the new script (`--nopreview`, same Linux
machine as their committed export) and compared with `extras_compare.py` against the committed ones:

```
COMPARE ssd_sorin_990pro_2tb_hs: ONLY ADDED: A_FILM_HEATSINK_0 (12 objects unchanged)
COMPARE ssd_westline_sn850x_1tb_hs: ONLY ADDED: A_FILM_HEATSINK_0 (12 objects unchanged)
COMPARE ssd_crux_t705_2tb_hs: ONLY ADDED: A_FILM_HEATSINK_0 (11 objects unchanged)
COMPARE ssd_sorin_870_1tb: ONLY ADDED: A_FILM_LABEL_0 (14 objects unchanged)
COMPARE ssd_crux_mx500_2tb: ONLY ADDED: A_FILM_LABEL_0 (14 objects unchanged)
COMPARE ssd_kingsland_a400_480: ONLY ADDED: A_FILM_LABEL_0 (14 objects unchanged)
```

Their textures re-rendered byte-different but unchanged in content, so they were not committed. The other 11 FBX
files are untouched.

**Papers.** Every JSON entry has `"unbox"` (films, caps, stickers as above), `"docs": ["guide", "warranty"]` (an
installation card and the warranty leaflet) and 8–9 `"doc_notes"`: the interface and capacity, the slot and screw
(M.2 PH0 at the notch, 2.5" M3, 3.5" 6-32 UNC, U.2 sled), the cables, speeds and endurance, film and label warnings
(heatsink drives: remove the board's M.2 heatsink first; HDDs: breather hole or helium seal), GPT and formatting,
and the warranty term.

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
- The 3.5" data port is `A_PORT_SATA_0` (as the brief says), not `A_PORT_SATADATA_0` as on the 2.5" drives.
- The HDD labels and the U.2 band are plain decals (quads) on flat faces; the HDD screw heads sit on top of the label.
- Prices are approximate.
