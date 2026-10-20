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
| 5 | `mb_aegis_z790_keystone` | `io_aegis_z790_keystone` | mb_ridge_z4 + DDR5 notch (L17, DDR5) | done |
| 6 | `mb_mako_z790_riptide` | `io_mako_z790_riptide` | mb_ridge_z4 + DDR5 notch (L17, DDR5) | done |
| 7 | `mb_kestrel_z790_talon` | `io_kestrel_z790_talon` | mb_ridge_z4 + DDR5 notch (L17, DDR5) | done |
| 8 | `mb_ridge_b760_d4` | `io_ridge_b760_d4` | mb_ridge_z4 (L17, DDR4) | done |
| 9 | `mb_strata_spv` | `io_strata_spv` | new: server board SP-V | done |
| 10 | `mb_strata_l46` | `io_strata_l46` | new: server board L46 dual | done |

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

### The new combination: Socket L17 + DDR5

Boards 5–7 use `mb_ridge_z4`'s layout (its L17 socket, lever, load plate, cooler holes, VRM, rear I/O, every other
anchor) with `mem="DDR5"` in the config. `build_board.dimms` takes the notch from `NOTCH[cfg["mem"]]`, and the DIMM
x positions, length and latches are the same on both siblings, so the DIMM slots come out exactly as
`mb_ridge_b5`'s: the key is moulded at −3.9 mm (DDR5) instead of +4.3 mm (DDR4), and `A_SOCKET_RAM_0..3` carry
`notch=-0.0039,...,mem=DDR5`. The silkscreen reads `DDR5_DIMM` and "DDR5 READY". Check:
- vs `mb_ridge_z4`: 76 SAME; DIFF only `A_SOCKET_RAM_0..3` (meta `notch=0.0043,mem=DDR4` → `notch=-0.0039,mem=DDR5`,
  same position, axes and size); ONLY_B the two film anchors.
- vs `mb_ridge_b5`: `A_SOCKET_RAM_0..3` and `A_LATCH_RAM_*` all SAME (the rest differs, as the socket is L17).

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

## 5. `mb_aegis_z790_keystone` + `io_aegis_z790_keystone`: Aegis Keystone Z790-A WiFi

- **Analog:** ASUS Prime Z790-A WIFI. Socket L17, **DDR5**, ATX; `mb_ridge_z4` layout with `mb_ridge_b5`'s DDR5 slots.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; tallest part the I/O cover (z 0.0371).
- **Triangles:** 45,060 in 41 meshes. Shield: 1,244 in 1.
- **Look:** black PCB with white circuit-line graphics; brushed silver `slab` VRM heatsinks with white bands and
  covers; a white `slab` I/O cover; a silver-and-white chipset plate with an RGB strip along its front edge; white
  and grey DIMM slots, white latches; silver x16 armour; two silver M.2 heatsinks with white trim. Shield: bare steel.
- **Anchors:** see "The new combination" above (vs `mb_ridge_z4`: 76 SAME, 4 DIFF = the DDR5 notch, 2 ONLY_B films).
- **I/O shield:** pre-attached on the analog (shipped here as the separate `io_aegis_z790_keystone` all the same).

## 6. `mb_mako_z790_riptide` + `io_mako_z790_riptide`: Mako Riptide Z790 WiFi

- **Analog:** MSI MPG Z790 EDGE WIFI (white). Socket L17, DDR5, ATX; `mb_ridge_z4` layout with the DDR5 slots.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; tallest part the I/O cover (z 0.0371).
- **Triangles:** 45,308 in 40 meshes. Shield: 1,244 in 1.
- **Look:** silver-white PCB with grey line graphics; white `slab` VRM heatsinks with silver bands and inlays; a
  white **RGB I/O cover** (the lit emblem panel on the top and the light bar); white DIMM and PCIe slots, silver
  armour on both full-length slots; a white `slab` chipset heatsink; two white M.2 heatsinks. Shield: bare steel.
- **Anchors:** vs `mb_ridge_z4`: 76 SAME, 4 DIFF (the DDR5 notch), 2 ONLY_B (films). vs `mb_aegis_z790_keystone`:
  82 SAME.
- **I/O shield:** pre-attached on the analog (shipped here as the separate `io_mako_z790_riptide` all the same).

## 7. `mb_kestrel_z790_talon` + `io_kestrel_z790_talon`: Kestrel Z790 Talon Elite AX

- **Analog:** Gigabyte Z790 AORUS ELITE AX. Socket L17, DDR5, ATX; `mb_ridge_z4` layout with the DDR5 slots.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; tallest part the I/O cover (z 0.0371).
- **Triangles:** 45,922 in 39 meshes. Shield: 1,244 in 1.
- **Look:** black PCB with angular dark-orange graphics and orange print; `fins` VRM heatsinks (dark covers over
  fin stacks, an orange lip line and slashes); an `armour` I/O cover with stepped plates, an orange line and the RGB
  light bar; an `armour` chipset heatsink with an orange slash; steel x16 armour; black DIMM slots; two M.2
  heatsinks with orange marks. Shield: painted black.
- **Anchors:** vs `mb_ridge_z4`: 76 SAME, 4 DIFF (the DDR5 notch), 2 ONLY_B (films). vs `mb_aegis_z790_keystone`:
  82 SAME.
- **I/O shield:** pre-attached on the analog (shipped here as the separate `io_kestrel_z790_talon` all the same).

## 8. `mb_ridge_b760_d4` + `io_ridge_b760_d4`: Ridge B760 Pro D4

- **Analog:** ASRock B760 Pro RS/D4. Socket L17, DDR4, ATX; `mb_ridge_z4` layout.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; tallest part the I/O cover (z 0.0371); VRM heatsinks only 20–24 mm.
- **Triangles:** 43,932 in 39 meshes. Shield: 1,244 in 1.
- **Look:** the budget board: black PCB with the Ridge stripe graphics; small `budget` extruded VRM heatsinks
  (open fins, a silver stripe) over a shorter span; a low plastic I/O cover over the rear of the port stack only; a
  low open-fin chipset heatsink; no PCIe armour, no RGB, no second M.2 heatsink; black and grey DIMM slots.
  Shield: bare steel.
- **Anchors:** vs `mb_ridge_z4`: 80 SAME, 0 DIFF, ONLY_B `A_FILM_CHIPSET_0`, `A_FILM_IO_0` (the committed z4 predates
  the films; the low cover keeps its logo plate where `A_FILM_IO_0` sits).
- **I/O shield:** not pre-attached on the analog.

## 9. `mb_strata_spv` + `io_strata_spv`: Strata SP-V 1S Server Board

- **Analog:** a single-socket SP5 server board of the Supermicro H13SSL / ASRock Rack GENOAD8X class.
- **Size:** SSI-EEB 0.3302 × 0.3048, PCB z 0..0.0016.
- **Triangles:** 37,372 in 53 meshes. Shield: 756 in 1.
- **Contents:** socket SP-V (rail frame, force frame with 3 Torx screws, PnP cap, 4 heatsink standoffs), 12 DDR5
  RDIMM slots (6 each side), 3 × PCIe x16 (slot 1 armoured), OCP 3.0 SFF slot with its bay, 2 × M.2, BMC with DRAM,
  flash and PHY, PCH heatsink, 24-pin + 2 × EPS 8-pin, 6 fan headers, 4 SATA, 2 MCIO, USB 3 / TPM / COM headers,
  POST display, rear I/O (UID, 2 USB, BMC LAN, VGA, 2 × 10 GbE).
- **Contract:** new, see below.

## 10. `mb_strata_l46` + `io_strata_l46`: Strata L46 2S Server Board

- **Analog:** a dual-socket LGA4677 server board of the Supermicro X13DEI class.
- **Size:** SSI-EEB 0.3302 × 0.3048, PCB z 0..0.0016.
- **Triangles:** 43,184 in 57 meshes. Shield: 756 in 1.
- **Contents:** two L46 sockets (bolster, 4 studs each, dust cover), 16 DDR5 RDIMM slots (4 each side of each
  socket), 4 × PCIe x16 (slots 1–2 on CPU0, 3–4 on CPU1), 2 × M.2, BMC, PCH heatsink, 24-pin + 4 × EPS 8-pin, the same
  headers, front connectors and rear I/O as the SP-V board. No OCP slot.
- **Contract:** new, see below.

## New contract: server board (SSI-EEB), `mb_strata_spv` and `mb_strata_l46`

Written like `docs/MODEL_PIPELINE.md` §2. Values in metres, Unity axes, board frame. Built by
`Tools/Blender/server_boards.py`, which reuses `build_board.Board`'s helpers (connectors, chips, headers, PCB art)
with the server geometry swapped in for the duration of the build.

**Frame:**
- Origin at the PCB centre. The PCB spans z 0..0.0016. +z is the component side, +x the rear I/O edge, +y the edge
  that would be the top in a tower (same axes as the ATX boards).
- SSI-EEB size: 0.3302 (x, 13") by 0.3048 (y, 12"). The rear edge is at x +0.1651.
- Airflow runs front (−x) to rear (+x), so the DIMM slots run **along x** (on the desktop boards they run along y).
- Layout: socket(s) in the front half, DIMM banks above and below each socket, VRMs in front of and behind each
  socket under low heatsinks; PCIe slots in the rear half below the I/O window; M.2, BMC, EPS headers in the rear
  half above them; 24-pin, fans, SATA, MCIO and the front-panel header along the front edge.
- The rear I/O aperture is the ATX one (same y and z as the desktop boards), so the shields are the same 158.75 ×
  44.45 mm plate; the port faces sit 4 mm past the rear edge (x 0.1691), the shield plate at x 0.1710.
- These boards go in servers, not desktop cases (the chassis task maps `A_HOLE_*` to its standoffs).

**Anchors:**
- `A_HOLE_0..7`: eight mounting holes, meta `eeb=<id>`, `d=0.00396`, each with `A_SCREW_PH2_<n>` (forward +z).
  The three rear holes keep the ATX A, C, F positions measured from the rear edge (x 0.155 / y −0.1359,
  x 0.155 / y −0.0114, x 0.1321 / y 0.14605); the others are R1 (0.06, 0.14605), R2 (0.06, −0.0114),
  R3 (−0.155, −0.1359), R4 (−0.155, −0.0114), R5 (−0.155, 0.14605).
- `A_SOCKET_CPU_<n>`: the seating plane at the socket centre, forward +z, z 0.0046 (as the desktop boards); meta
  `socket=SP-V` or `socket=L46`, `pin1=+x-y`. `A_MARK_SOCKET_<n>` is the socket's pin-1 triangle corner.
- `A_SOCKET_COOLER_<n>`: the cooler base contact pose, forward +z, at z 0.0046 + 0.0065 (assumes the server CPUs'
  IHS top is 6.5 mm above their contact face; change this one number if the CPU contract says otherwise). Size =
  the cooler keep-out.
- `A_COVER_CPU_<n>`: the protective socket cap (moving piece, `remove=+z`).
- **SP-V** (SP5-style mechanism):
  - `A_RAIL_CPU_0` at the −x end of the socket (x −0.099, y 0.010, z 0.0042): the rail frame, a moving piece,
    `hinge=y,open=-75`. The CPU's orange carrier slides into it along +x until `carrier_stop`, then the rail frame
    closes.
  - `A_PLATE_CPU_0` at the same hinge: the force frame, a moving piece, `hinge=y,open=-110`, closed after the rail
    frame. Its three captive screws are `A_SCREW_TORX_0..2@A_PLATE_CPU_0` (meta `seq=1..3,t20=1,torque=1.6Nm`):
    screw 1 at the +x end, 2 and 3 at the −x corners, tightened 1-2-3 (printed on the frame).
  - Four heatsink standoffs at (±0.056, ±0.040) from the socket centre (`A_SOCKET_COOLER_0` meta
    `standoffs=0.112x0.080,screws=4,t20=1,order=1-2-3-4`), numbered on the silkscreen.
  - Package seat: 72 × 75 mm (x × y).
- **L46** (LGA4677-style, processor-heatsink module): no lever or load plate. The CPU is clipped to its cooler with
  its carrier clip and the module lands on four threaded studs at (±0.058, ±0.036). The nuts are
  `A_SCREW_TORX_<4n+k>` at the stud tops (meta `stud=1,seq=1..4,t30=1,torque=0.9Nm,cooler=A_SOCKET_COOLER_<n>`),
  tightened in the order printed on the board. Package seat: 105 × 61 mm (x × y), the long axis along the airflow.
- `A_SOCKET_RAM_<i>`: RDIMM slots, the stick's bottom-edge centre, forward +z, **up +x** (so the stick's own +y,
  its length, runs along the board's x); meta `notch=-0.0039` (DDR5, along the stick's y as on the desktop boards),
  `slot=P<cpu>_DIMM<A..>1`, `mem=DDR5,rdimm=1,cpu=<n>,latch=both`. `A_LATCH_RAM_<i>_0/_1`: the latches at the −x and
  +x ends (moving pieces, `hinge=y`). Pitch 0.0076 (SP-V, 6 slots per side) and 0.0072 (L46, 4 per side per CPU).
- `A_SOCKET_PCIE16_<i>` (card origin, as the GPU frame; `lanes=16,slot=SLOT<n>,cpu=<n>`) with `A_LATCH_PCIE_<i>`.
  The card origin is 0.092 in front of the rear edge as on the ATX boards (x 0.0731), so a card's bracket lands on
  the rear edge.
- `A_SOCKET_OCP_0` (SP-V only): the OCP 3.0 SFF (4C+) connector mouth, forward +x (the NIC slides in from the rear
  along −x), meta `ocp=3.0,form=sff,lanes=16,card_origin=1,insert=-x`. The bay (x 0.052..0.165, y −0.146..−0.078)
  is marked keep-out on the PCB.
- `A_SOCKET_M2_0..1` + `A_STANDOFF_M2_0..1`: two M.2 2280 slots (the 22110 standoff spot is printed too), lying along
  +x, no heatsink.
- Power: `A_PORT_ATX24_0` (front edge), `A_PORT_EPS8_0..1` (SP-V) or `_0..3` (L46: two per CPU, meta `cpu=<n>`;
  `split=none`, the server 8-pin is not split 4+4).
- Headers: `A_PORT_FANSYS_0..5` (front edge, 4-pin), `A_PORT_FPANEL_0` (the desktop 2×5 pinout, so the game can
  reuse its front-panel logic), `A_PORT_USB3HDR_0`, `A_PORT_SATA_0..3` (front edge, facing −x), `A_PORT_MCIO_0..1`
  (MCIO x8 for NVMe backplanes, facing −x).
- Rear I/O (forward +x, as the desktop ports): `A_BUTTON_UID_0` (with its blue LED), `A_PORT_USBA_0..1`,
  `A_PORT_ETH_0` (BMC management LAN), `A_PORT_VGA_0`, `A_PORT_ETH_1..2` (10 GbE).
- `A_LED_BMC_0` (BMC heartbeat, led_green mesh) and `A_DISPLAY_POST_0` (a 2-digit POST code display, led_red mesh,
  looks only).
- `A_HIT_0..n`: the PCB, each socket, each DIMM bank, the PCIe block and the rear I/O.

**Looks:** green server PCB with white silkscreen; LGA sockets with gold pin fields, steel bolsters, the SP-V's rail
frame / force frame with its torque label, the L46's studs; RDIMM slots in black/grey pairs; VRM chokes and power
stages under low finned aluminium heatsinks; the BMC with its DRAM and flash; a finned PCH heatsink; MCIO, SATA,
TPM, COM, USB 3 headers; a CMOS battery and a POST display. No RGB. Shields: painted black.

**What the game needs to support them:** a server socket (`SP-V`, `L46`) with the mechanisms above, RDIMM slots
along x, an OCP slot, and server chassis standoffs at `A_HOLE_*`. `game.socket` in `boards.json` carries `SP-V` /
`L46`; `new_contract: true`.

## Deviations

- **`build_board.py` is unchanged.** No hooks were needed: everything is done by overriding look methods in a
  subclass. `CatBoard.build` and `build_cat_boards.build_shield` are copies of the originals that differ only in the
  texture file names (`<id without mb_>_pcb/_mk`), the joined-mesh prefix (`mb_`, `io_`) and the shield paint, because
  the longer catalogue ids would push `<id>_<tag>#<tag>` past Blender's 63-character name limit.
- **Siblings without film anchors.** The committed `mb_ridge_b5.fbx` and `mb_ridge_z4.fbx` were exported before
  `build_board.films()` existed, so every new board shows `A_FILM_IO_0` and `A_FILM_CHIPSET_0` as ONLY_B against
  them. `mb_ridge_x5` (today's `build_board.py`) has them, and the V5 boards are SAME with it anchor for anchor.
- **L17 + DDR5** is a new combination (documented above): the z4 layout with the b5 DIMM notch. Only the four
  `A_SOCKET_RAM_*` metas differ from `mb_ridge_z4`.
- **Rear I/O** keeps each sibling's ports (they carry anchors), so the Z790 boards still show the Z4's PS/2 port
  and the X870E the B5's port set.
- **Pre-attached shields.** The analogs of Vanguard, Harpoon, Glide, Keystone, Riptide and Talon come with the shield
  pre-mounted. As the brief asks, each still ships a separate `io_*` model; the game can fit it automatically for these.
- **Server sockets without the CPU contract.** The CPU task (catalogue 10) was not available on any branch, so the
  SP-V and L46 socket sides were designed from its brief (package 72 × 75 mm with an orange carrier on a rail; 61 ×
  105 mm with a carrier clip). The cooler pose assumes an IHS top 6.5 mm above the contact face (`IHS_H` in
  `server_boards.py`). Torque values and the screw order are plausible, not taken from a spec.
- **Server holes** are this contract's own pattern (the rear three at the ATX A, C, F positions), not the full SSI-EEB
  list. The server front-panel header uses the desktop 2×5 pinout, so the game's front-panel logic applies as is.
- **Fonts and textures.** Built on Linux, the Windows fonts are replaced by Liberation/DejaVu stand-ins
  (`dct_common.font_file`), so a Windows rebuild gives slightly different texture text.
