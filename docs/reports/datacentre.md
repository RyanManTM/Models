# Task 01 report: data-centre gear

Script: `Tools/Blender/build_datacenter.py` with the helpers `datacenter_common.py` (ports, ears, LEDs, buttons,
low-poly fans, print atlases), `datacenter_ac.py`, `datacenter_server.py`, `datacenter_rack.py`, `datacenter_net.py`
and `datacenter_power.py`.

## Models

| Model | Size (x × y × z, m) | Triangles | Meshes | Anchors |
|---|---|---|---|---|
| `ac_12k` | 0.696 × 0.480 × 0.638 | 9,340 | 23 | 9 |
| `server_1u` | 0.483 × 0.044 × 0.779 | 22,984 | 140 | 72 |
| `server_2u` | 0.483 × 0.087 × 0.796 | 25,164 | 189 | 86 |
| `rack_42u` | 0.610 × 2.002 × 1.099 | 20,442 | 29 | 51 |
| `rack_12u_open` | 0.593 × 0.691 × 0.795 | 5,274 | 8 | 15 |
| `switch_24` | 0.483 × 0.044 × 0.254 | 11,794 | 65 | 93 |
| `patch_panel_24` | 0.483 × 0.043 × 0.114 | 6,232 | 7 | 55 |
| `ups_2u` | 0.483 × 0.088 × 0.518 | 8,596 | 30 | 29 |
| `ups_tower` | 0.170 × 0.219 × 0.485 | 7,782 | 27 | 23 |
| `pdu_0u` | 0.045 × 1.870 × 0.078 | 7,554 | 9 | 35 |
| `pdu_1u` | 0.483 × 0.044 × 0.235 | 2,972 | 8 | 17 |

Budgets: servers and the switch under 25k triangles, racks under 40k. Sizes are the full bounds of each model,
moving pieces included (rails, handles, cord boots).

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_datacenter.py -- [ids...] [--nopreview]
```

With no ids it builds every model below. Then the fit check installs the devices in both racks at their
anchors, checks every ear hole against the rack holes and every device against its neighbours, and renders
`Logs/ModelPreviews/datacentre_fit*.png`:

```bash
blender -b --factory-startup -P Tools/Blender/datacenter_fit.py -- [--nopreview]
```

Each model writes `Assets/Resources/Models/<id>.fbx`, its textures in `Assets/Resources/Models/Textures/`, previews `Logs/ModelPreviews/<id>_<n>.png` (0–1 Workbench, the rest Cycles) and
the full anchor report `Logs/ModelPreviews/<id>_report.txt` (every mesh and every anchor, plus the bounds).

Built in the cloud session with the `bpy` 5.0.1 module (download.blender.org was blocked; `pip install bpy==5.0.1`
under Python 3.11). Rebuilding an existing model (plug_atx24) that way gives an FBX that `extras_compare.py`
reports SAME.

## Conventions used by all the gear

- **Rack device frame:** origin at the centre of the front mounting plane (the front face of the rack's front
  rails), at the bottom of the device's U space; +Z out of the front, +Y up, the chassis towards −Z. 19": 482.6 mm
  across the ears, ear holes at ±232.55 mm (EIA-310), 1U = 44.45 mm.
- **Ports** `A_PORT_<KIND>_<n>`: at the mouth plane, +Z = where the plug comes from, meta `depth=` (plug travel).
  RJ45: the anchor's +Y points at the latch slot (`latch=+up`). Names follow the brief: an inlet is named by its
  own type (`A_PORT_C14_n` takes a C13 plug), an outlet by its own type (`A_PORT_C13_n` takes a C14 plug);
  the meta `plug=` says which cable end fits.
- **LEDs** `A_LED_<NAME>_<n>` carry their lens mesh (tag `led_*`), so the game can light each one.
- **Buttons** `A_BUTTON_<NAME>_<n>` carry their cap (moving piece), meta `press=-z_local,travel=<m>` (+`fn=`).
- **Rack screws:** fixed ears have `A_SCREW_RACK_<n>` at each ear hole (forward +z, meta `thread=M6,cage=1`).
- **Removable pieces** (trays, PSUs, lids, doors, bezels, rails) are `name@A_<ANCHOR>#tag`, modelled closed /
  installed, pivot at the anchor. Their anchors keep the model axes (fwd +z, up +y), so `pull=+z`, `slide=-z`
  and the hinge axes read the same in the model and in the anchor. Hinges follow the parts' rule: a positive angle
  about +x turns +y towards +z.

## ac_12k: FrostLine 12,000 BTU wall AC

- **Frame (install pose):** origin at the centre of the unit's width and height; +Z into the room; the wall face at
  z = −0.10. The room-side cabinet is 0.62 W × 0.40 H, from the wall to the front fascia at z = 0.227; the chassis
  (0.65 × 0.45, galvanised) continues through the sleeve to z = −0.40, where the outdoor face has a louvred grille
  over the condenser coil.
- **Front:** the intake grille with 13 angled slats and a filter (upper +x), the outlet with deflector vanes and the
  motorised louver `A_LOUVER_0` (`hinge=x`, a negative angle swings the lower edge out), the FrostLine brand plate
  (top +x), and the gloss-black control strip at −x: the display `A_SCREEN_0` (0.074 × 0.042, the dark screen quad is
  attached to it like the monitor's), the mode LED `A_LED_MODE_0` (`led_blue`) and the buttons `A_BUTTON_0..2`
  (`fn=power`, `temp_up`, `temp_down`, labelled POWER / TEMP + / TEMP −).
- **Sides:** louvred vents on both sides, the rating label and an energy-guide sticker on +x. The power cord leaves
  the −x side at the lower back through a grommet and strain-relief boot; `A_CORD_0` is the end of the boot (+Z along
  the cord, meta `r=0.0039,plug=nema5-15,len=1.8`). The game draws the cord from there.
- Textures: `ac_12k_print.png` (brand plate, strip legends, rating label, energy guide), `ac_12k_coil.png`
  (condenser fin tile).

- **Triangles:** 9,340 in 23 meshes.
- **Bounds:** min=(-0.3560, -0.2400, -0.4000) max=(0.3400, 0.2400, 0.2378) size=(0.6960, 0.4800, 0.6379)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BUTTON_0` | (-0.24, 0.012, 0.2262) | +z / +y | 0.02200,0.02200,0.00600 | press=-z_local,travel=0.0015,fn=power |
| `A_BUTTON_1` | (-0.24, -0.04, 0.2262) | +z / +y | 0.02200,0.02200,0.00600 | press=-z_local,travel=0.0015,fn=temp_up |
| `A_BUTTON_2` | (-0.24, -0.092, 0.2262) | +z / +y | 0.02200,0.02200,0.00600 | press=-z_local,travel=0.0015,fn=temp_down |
| `A_CORD_0` | (-0.356, -0.168, -0.072) | -x / +y | 0.01200,0.01200,0.02000 | r=0.0039,plug=nema5-15,len=1.8,awg=14 |
| `A_HIT_0` | (0, 0, 0.0635) | +z / +y | 0.62000,0.40000,0.32700 |  |
| `A_HIT_1` | (0, 0, -0.096) | +z / +y | 0.68000,0.48000,0.00800 |  |
| `A_LED_MODE_0` | (-0.24, 0.056, 0.2271) | +z / +y | 0.00520,0.00520,0.00300 | colour=blue,fn=mode |
| `A_LOUVER_0` | (0.06, -0.135, 0.234) | +z / +y | 0.42000,0.07000,0.01200 | hinge=x,open=-45,min=-60,max=10,motor=1 |
| `A_SCREEN_0` | (-0.24, 0.1, 0.233) | +z / +y | 0.07400,0.04200,0.00300 | kind=lcd,ref=296x168,digits=2,colour=blue |

Moving pieces: `button_n@A_BUTTON_n#grey_plastic` ×3, `button_n@A_BUTTON_n#white_plastic` ×3, `led_mode_n@A_LED_MODE_n#led_blue`, `louver_n@A_LOUVER_n#grey_plastic`, `louver_n@A_LOUVER_n#white_plastic`, `screen_n@A_SCREEN_n#black_plastic`.

**Deviations / notes**
- The brief calls −x the unit's "left" (its coordinates put the display at x = −0.24), so the control strip is at −x:
  that is on the viewer's right when facing the unit, as on most real units. The grille and brand plate are at +x.
- A wall trim ring (0.68 × 0.48, 8.5 mm, off-white) sits on the wall face round the cabinet. It covers the gap
  between the 0.62 × 0.40 cabinet and the 0.66 × 0.46 sleeve opening. It is part of the static mesh; `A_HIT_1` covers
  it.
- The box art of `box_ac_12k` (existing, unchanged) shows a split-type indoor unit; the model follows the brief's
  through-the-wall unit. The box is 0.68 × 0.48 × 0.62 and the unit 0.70 × 0.48 × 0.64 overall with its trim, cord
  boot and outdoor grille.

## server_1u and server_2u: STRATA SR110 (1U) and SR220 (2U) rack servers

- **Frame:** the rack device frame. The chassis is 0.434 wide (the slide rails take the last 8 mm per side to the
  rack's 0.450 opening), 43.6 / 87.3 mm high and centred in its U space (bottom at y = 0.000425 / 0.0008), 0.700 deep:
  the drive faces and ear fronts at z = +0.030, the rear face at z = −0.670. The ears (control-panel blocks) sit on
  the rack's front rails from z = 0 to 0.030.
- **Ears:** a captive thumbscrew in each ear, `A_SCREW_THUMB_0` (−x) and `A_SCREW_THUMB_1` (+x), at the rail holes
  (1U: the middle hole, y = 0.0222; 2U: y = 0.0381), with the knurled head as a moving piece (meta
  `thread=M6,captive=1`). −x ear: the power button `A_BUTTON_POWER_0` with its green ring `A_LED_POWER_0` (2U: plus
  a vertical front USB `A_PORT_USBA_FRONT_0`). +x ear: the ID button `A_BUTTON_ID_0` with `A_LED_ID_0` (blue),
  `A_LED_HEALTH_0` (green), `A_LED_FAULT_0` (amber), 2U also `A_LED_NET_0`.
- **Drive trays** `A_BAY_n` (`pull=+z`, meta `kind=sff|lff,slot=n`): 1U 8 × 2.5" in 2 rows × 4, 2U 12 × 3.5" in
  3 rows × 4, numbered from the bottom row, −x first. Each tray is a complete removable piece: the vented front, the
  lever with its green release, the carrier rails and the drive with its label. Each carries two LEDs,
  `A_LED_DRIVE_n@A_BAY_n` (green, activity) and `A_LED_DRIVEFAULT_n@A_BAY_n` (amber). Behind them: the cage tunnels and
  the backplane with a connector per bay.
- **1U front panel** (+x of the drives): vents, the STRATA badge, a front USB `A_PORT_USBA_FRONT_0` and the pull-out
  service tag (looks only).
- **2U bezel** `A_BEZEL_0` (`remove=+z,lock=1`): a hex-perforated front over the drives (alpha-cut texture
  `server_bezel_mesh.png`, dark holes, so it also reads opaque), the logo band, a key lock `A_LOCK_0@A_BEZEL_0` and a
  blue status light bar `A_LED_BEZEL_0@A_BEZEL_0`.
- **Rear:** two hot-swap CRPS PSUs `A_PSU_0/1` (`pull=-z,dist=0.195,watts=800`; 1U side by side at +x, 2U in both
  bottom corners), each a complete piece with its fan grille, release latch, pull handle, label, gold edge connector,
  `A_LED_PSU_n@A_PSU_n` and the C14 inlet `A_PORT_C14_n@A_PSU_n` (`plug=c13`). The I/O: 4 × RJ45 `A_PORT_ETH_0..3`
  (each with `A_LED_LINK_n` green and `A_LED_ACT_n` amber), `A_PORT_IPMI_0` (+`A_LED_IPMI_0`), `A_PORT_VGA_0`,
  `A_PORT_USBA_0..1`, a rear ID LED `A_LED_ID_1`, vented PCIe slot covers (1U 2 low-profile, 2U 6), vent slots and
  printed legends.
- **Top cover** `A_LID_0` (`slide=-z,dist=0.020,lift=+y`): the steel cover with side lips, the flush release latch
  and the service label (block diagram, service tag, QR). Under it: the board, two CPU sockets with copper-based fin
  heatsinks, 16 DIMMs (4 each side of each CPU) in slots with latches, the fan wall (1U 8 × 40 mm, 2U 6 × 60 mm, each
  rotor a moving piece of `A_FAN_n`, `axis=z,spin=1`, with a hot-swap handle), the air shroud `A_SHROUD_0`
  (`lift=+y`, a moving piece so it can come out), the drive backplane, SAS cables, PCIe risers with a card, the PSU
  cage and power distribution boards, the chipset heatsink, BMC and CMOS battery.
- **Slide rails** `A_RAIL_L_0` (−x) and `A_RAIL_R_0` (+x), in their installed pose: outer C-channel, intermediate
  and inner members, front and rear brackets with pins through the rack's square holes. They span z = −0.002 to
  −0.7385 (the rack's front rails at z = 0 and rear rails at z = −0.740, see the racks). Meta
  `kind=slide,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62`.
- Textures: `server_print.png` (labels, DIMM faces, logo, legends, service label), `server_bezel_mesh.png`; the green
  touch points use the shared `parts_c_palette.png` (not rewritten).

### server_1u

- **Triangles:** 22,984 in 140 meshes.
- **Bounds:** min=(-0.2415, 0.0004, -0.7425) max=(0.2415, 0.0441, 0.0367) size=(0.4831, 0.0437, 0.7792)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BAY_0..7 (8)` | (-0.1688, 0.0122, 0.03) … (0.0578, 0.0322, 0.03) | +z / +y | 0.07400,0.01900,0.10400 | pull=+z,dist=0.114,kind=sff,slot=0,latch=1 … pull=+z,dist=0.114,kind=sff,slot=7,latch=1 |
| `A_BUTTON_ID_0` | (0.2291, 0.0365, 0.0302) | +z / +y | 0.00900,0.00900,0.00600 | press=-z_local,travel=0.0010,fn=identify |
| `A_BUTTON_POWER_0` | (-0.2291, 0.0365, 0.0302) | +z / +y | 0.00980,0.00980,0.00600 | press=-z_local,travel=0.0012,fn=power,hold=4 |
| `A_FAN_0..7 (8)` | (-0.1767, 0.0218, -0.129) … (0.1767, 0.0218, -0.129) | +z / +y | 0.04000,0.04000,0.02800 | axis=z,spin=1,rpm=9000,hotswap=1,pull=+y |
| `A_HIT_0` | (0, 0.0222, -0.32) | +z / +y | 0.43400,0.04360,0.70000 |  |
| `A_HIT_1` | (-0.2291, 0.0222, 0.015) | +z / +y | 0.02430,0.04360,0.03000 |  |
| `A_HIT_2` | (0.2291, 0.0222, 0.015) | +z / +y | 0.02430,0.04360,0.03000 |  |
| `A_LED_ACT_0` | (-0.0402, 0.0079, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_1` | (-0.0242, 0.0079, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_2` | (-0.0082, 0.0079, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_3` | (0.0078, 0.0079, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_DRIVEFAULT_0@A_BAY_0` | (-0.2024, 0.0082, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_1@A_BAY_1` | (-0.127, 0.0082, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_2@A_BAY_2` | (-0.0515, 0.0082, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_3@A_BAY_3` | (0.024, 0.0082, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_4@A_BAY_4` | (-0.2024, 0.0282, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_5@A_BAY_5` | (-0.127, 0.0282, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_6@A_BAY_6` | (-0.0515, 0.0282, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_7@A_BAY_7` | (0.024, 0.0282, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVE_0@A_BAY_0` | (-0.2024, 0.0163, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_1@A_BAY_1` | (-0.127, 0.0163, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_2@A_BAY_2` | (-0.0515, 0.0163, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_3@A_BAY_3` | (0.024, 0.0163, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_4@A_BAY_4` | (-0.2024, 0.0363, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_5@A_BAY_5` | (-0.127, 0.0363, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_6@A_BAY_6` | (-0.0515, 0.0363, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_7@A_BAY_7` | (0.024, 0.0363, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_FAULT_0` | (0.2291, 0.0044, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=amber,fn=fault |
| `A_LED_HEALTH_0` | (0.2291, 0.0084, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=green,fn=health |
| `A_LED_ID_0` | (0.224, 0.0365, 0.0302) | +z / +y | 0.00200,0.00200,0.00300 | colour=blue,fn=identify |
| `A_LED_ID_1` | (-0.1265, 0.038, -0.6701) | -z / +y | 0.00300,0.00300,0.00300 | colour=blue,fn=identify |
| `A_LED_IPMI_0` | (-0.1165, 0.0077, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green |
| `A_LED_LINK_0` | (-0.0318, 0.0079, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_LINK_1` | (-0.0158, 0.0079, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_LINK_2` | (0.0002, 0.0079, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_LINK_3` | (0.0162, 0.0079, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_POWER_0` | (-0.2291, 0.0365, 0.0306) | +z / +y | 0.01000,0.01000,0.00300 | colour=green,fn=power,ring=1 |
| `A_LED_PSU_0@A_PSU_0` | (0.171, 0.0386, -0.6712) | -z / +y | 0.00240,0.00240,0.00300 | colour=green,fn=psu_ok |
| `A_LED_PSU_1@A_PSU_1` | (0.0963, 0.0386, -0.6712) | -z / +y | 0.00240,0.00240,0.00300 | colour=green,fn=psu_ok |
| `A_LID_0` | (0, 0.044, -0.327) | +z / +y | 0.43400,0.00400,0.68600 | slide=-z,dist=0.020,lift=+y,latch=1 |
| `A_PORT_C14_0@A_PSU_0` | (0.159, 0.0266, -0.6712) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_C14_1@A_PSU_1` | (0.0843, 0.0266, -0.6712) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_ETH_0` | (-0.036, 0.0129, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=1 |
| `A_PORT_ETH_1` | (-0.02, 0.0129, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=2 |
| `A_PORT_ETH_2` | (-0.004, 0.0129, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=3 |
| `A_PORT_ETH_3` | (0.012, 0.0129, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=4 |
| `A_PORT_IPMI_0` | (-0.112, 0.0129, -0.67) | -z / +y | 0.01600,0.01400,0.02000 | depth=0.012,rj45=1,latch=+up,net=bmc |
| `A_PORT_USBA_0` | (-0.06, 0.0089, -0.67) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_USBA_1` | (-0.06, 0.0169, -0.67) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_USBA_FRONT_0` | (0.205, 0.0129, 0.03) | +z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=2.0 |
| `A_PORT_VGA_0` | (-0.085, 0.0129, -0.6704) | -z / +y | 0.03200,0.01300,0.01200 | depth=0.006,vga=1 |
| `A_PSU_0` | (0.1772, 0.0226, -0.67) | +z / +y | 0.07350,0.04000,0.18500 | pull=-z,dist=0.195,watts=800,eff=platinum,slot=0 |
| `A_PSU_1` | (0.1026, 0.0226, -0.67) | +z / +y | 0.07350,0.04000,0.18500 | pull=-z,dist=0.195,watts=800,eff=platinum,slot=1 |
| `A_RAIL_L_0` | (-0.221, 0.0194, -0.002) | +z / +y | 0.00800,0.03000,0.73800 | kind=slide,side=l,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62 |
| `A_RAIL_R_0` | (0.221, 0.0194, -0.002) | +z / +y | 0.00800,0.03000,0.73800 | kind=slide,side=r,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62 |
| `A_SCREW_THUMB_0` | (-0.2326, 0.0222, 0.03) | +z / +y | 0.01200,0.01200,0.01200 | thread=M6,captive=1,len=0.032,turns=4 |
| `A_SCREW_THUMB_1` | (0.2326, 0.0222, 0.03) | +z / +y | 0.01200,0.01200,0.01200 | thread=M6,captive=1,len=0.032,turns=4 |
| `A_SHROUD_0` | (0, 0.0416, -0.2875) | +z / +y | 0.40000,0.00600,0.16000 | lift=+y,dist=0.06,order=1 |

Moving pieces: `bay_n@A_BAY_n#alu` ×8, `bay_n@A_BAY_n#black_plastic` ×8, `bay_n@A_BAY_n#dark_plastic` ×8, `bay_n@A_BAY_n#steel_dark` ×8, `bay_n@A_BAY_n#tex_parts_c_palette` ×8, `bay_n@A_BAY_n#tex_server_print` ×8, `button_id_n@A_BUTTON_ID_n#black_plastic`, `button_id_n@A_BUTTON_ID_n#grey_plastic`, `button_power_n@A_BUTTON_POWER_n#black_plastic`, `button_power_n@A_BUTTON_POWER_n#grey_plastic`, `fan_n@A_FAN_n#fan_black` ×8, `led_act_n@A_LED_ACT_n#led_yellow` ×4, `led_drive_n@A_LED_DRIVE_n@A_BAY_n#led_green` ×8, `led_drivefault_n@A_LED_DRIVEFAULT_n@A_BAY_n#led_yellow` ×8, `led_fault_n@A_LED_FAULT_n#led_yellow`, `led_health_n@A_LED_HEALTH_n#led_green`, `led_id_n@A_LED_ID_n#led_blue` ×2, `led_ipmi_n@A_LED_IPMI_n#led_green`, `led_link_n@A_LED_LINK_n#led_green` ×4, `led_power_n@A_LED_POWER_n#led_green`, `led_psu_n@A_LED_PSU_n@A_PSU_n#led_green` ×2, `lid_n@A_LID_n#black_plastic`, `lid_n@A_LID_n#dark_plastic`, `lid_n@A_LID_n#nickel`, `lid_n@A_LID_n#steel`, `lid_n@A_LID_n#tex_server_print`, `psu_n@A_PSU_n#black_plastic` ×2, `psu_n@A_PSU_n#dark_plastic` ×2, `psu_n@A_PSU_n#fan_black` ×2, `psu_n@A_PSU_n#gold` ×2, `psu_n@A_PSU_n#nickel` ×2, `psu_n@A_PSU_n#pcb_green` ×2, `psu_n@A_PSU_n#steel` ×2, `psu_n@A_PSU_n#steel_dark` ×2, `psu_n@A_PSU_n#tex_parts_c_palette` ×2, `psu_n@A_PSU_n#tex_server_print` ×2, `rail_l_n@A_RAIL_L_n#steel`, `rail_l_n@A_RAIL_L_n#steel_dark`, `rail_r_n@A_RAIL_R_n#steel`, `rail_r_n@A_RAIL_R_n#steel_dark`, `screw_thumb_n@A_SCREW_THUMB_n#steel` ×2, `shroud_n@A_SHROUD_n#black_plastic`, `shroud_n@A_SHROUD_n#tex_server_print`.

### server_2u

- **Triangles:** 25,164 in 189 meshes.
- **Bounds:** min=(-0.2415, 0.0008, -0.7425) max=(0.2415, 0.0882, 0.0534) size=(0.4831, 0.0874, 0.7959)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BAY_0..11 (12)` | (-0.1599, 0.0167, 0.03) … (0.1599, 0.0723, 0.03) | +z / +y | 0.10520,0.02680,0.15000 | pull=+z,dist=0.160,kind=lff,slot=0,latch=1 … pull=+z,dist=0.160,kind=lff,slot=11,latch=1 |
| `A_BEZEL_0` | (0, 0.0445, 0.052) | +z / +y | 0.43200,0.08730,0.01850 | remove=+z,dist=0.06,lock=1,key=A_LOCK_0 |
| `A_BUTTON_ID_0` | (0.2291, 0.0781, 0.0302) | +z / +y | 0.00900,0.00900,0.00600 | press=-z_local,travel=0.0010,fn=identify |
| `A_BUTTON_POWER_0` | (-0.2291, 0.0781, 0.0302) | +z / +y | 0.00980,0.00980,0.00600 | press=-z_local,travel=0.0012,fn=power,hold=4 |
| `A_FAN_0..5 (6)` | (-0.1683, 0.0322, -0.179) … (0.1683, 0.0322, -0.179) | +z / +y | 0.06000,0.06000,0.03800 | axis=z,spin=1,rpm=6500,hotswap=1,pull=+y |
| `A_HIT_0` | (0, 0.0445, -0.32) | +z / +y | 0.43400,0.08730,0.70000 |  |
| `A_HIT_1` | (-0.2291, 0.0445, 0.015) | +z / +y | 0.02430,0.08730,0.03000 |  |
| `A_HIT_2` | (0.2291, 0.0445, 0.015) | +z / +y | 0.02430,0.08730,0.03000 |  |
| `A_LED_ACT_0` | (-0.0182, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_1` | (-0.0022, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_2` | (0.0138, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_3` | (0.0298, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_BEZEL_0@A_BEZEL_0` | (0, 0.0063, 0.0521) | +z / +y | 0.12000,0.00200,0.00300 | colour=blue,fn=status |
| `A_LED_DRIVEFAULT_0@A_BAY_0` | (-0.2092, 0.0109, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_10@A_BAY_10` | (0.004, 0.0665, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_11@A_BAY_11` | (0.1106, 0.0665, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_1@A_BAY_1` | (-0.1026, 0.0109, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_2@A_BAY_2` | (0.004, 0.0109, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_3@A_BAY_3` | (0.1106, 0.0109, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_4@A_BAY_4` | (-0.2092, 0.0387, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_5@A_BAY_5` | (-0.1026, 0.0387, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_6@A_BAY_6` | (0.004, 0.0387, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_7@A_BAY_7` | (0.1106, 0.0387, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_8@A_BAY_8` | (-0.2092, 0.0665, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVEFAULT_9@A_BAY_9` | (-0.1026, 0.0665, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault |
| `A_LED_DRIVE_0@A_BAY_0` | (-0.2092, 0.0225, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_10@A_BAY_10` | (0.004, 0.0781, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_11@A_BAY_11` | (0.1106, 0.0781, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_1@A_BAY_1` | (-0.1026, 0.0225, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_2@A_BAY_2` | (0.004, 0.0225, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_3@A_BAY_3` | (0.1106, 0.0225, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_4@A_BAY_4` | (-0.2092, 0.0503, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_5@A_BAY_5` | (-0.1026, 0.0503, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_6@A_BAY_6` | (0.004, 0.0503, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_7@A_BAY_7` | (0.1106, 0.0503, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_8@A_BAY_8` | (-0.2092, 0.0781, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_DRIVE_9@A_BAY_9` | (-0.1026, 0.0781, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity |
| `A_LED_FAULT_0` | (0.2291, 0.0541, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=amber,fn=fault |
| `A_LED_HEALTH_0` | (0.2291, 0.0621, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=green,fn=health |
| `A_LED_ID_0` | (0.224, 0.0781, 0.0302) | +z / +y | 0.00200,0.00200,0.00300 | colour=blue,fn=identify |
| `A_LED_ID_1` | (0.05, 0.0308, -0.6701) | -z / +y | 0.00300,0.00300,0.00300 | colour=blue,fn=identify |
| `A_LED_IPMI_0` | (-0.1025, 0.0096, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green |
| `A_LED_LINK_0` | (-0.0098, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_LINK_1` | (0.0062, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_LINK_2` | (0.0222, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_LINK_3` | (0.0382, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_NET_0` | (0.2291, 0.0461, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=green,fn=network |
| `A_LED_POWER_0` | (-0.2291, 0.0781, 0.0306) | +z / +y | 0.01000,0.01000,0.00300 | colour=green,fn=power,ring=1 |
| `A_LED_PSU_0@A_PSU_0` | (0.171, 0.039, -0.6712) | -z / +y | 0.00240,0.00240,0.00300 | colour=green,fn=psu_ok |
| `A_LED_PSU_1@A_PSU_1` | (-0.1835, 0.039, -0.6712) | -z / +y | 0.00240,0.00240,0.00300 | colour=green,fn=psu_ok |
| `A_LID_0` | (0, 0.0881, -0.327) | +z / +y | 0.43400,0.00400,0.68600 | slide=-z,dist=0.020,lift=+y,latch=1 |
| `A_LOCK_0@A_BEZEL_0` | (0.2, 0.0445, 0.0532) | +z / +y | 0.01000,0.01000,0.00600 | key=1,turn=90 |
| `A_PORT_C14_0@A_PSU_0` | (0.159, 0.027, -0.6712) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_C14_1@A_PSU_1` | (-0.1955, 0.027, -0.6712) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_ETH_0` | (-0.014, 0.0148, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=1 |
| `A_PORT_ETH_1` | (0.002, 0.0148, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=2 |
| `A_PORT_ETH_2` | (0.018, 0.0148, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=3 |
| `A_PORT_ETH_3` | (0.034, 0.0148, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=4 |
| `A_PORT_IPMI_0` | (-0.098, 0.0148, -0.67) | -z / +y | 0.01600,0.01400,0.02000 | depth=0.012,rj45=1,latch=+up,net=bmc |
| `A_PORT_USBA_0` | (-0.04, 0.0108, -0.67) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_USBA_1` | (-0.04, 0.0188, -0.67) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_USBA_FRONT_0` | (-0.2283, 0.0168, 0.03) | +z / +x | 0.01450,0.00720,0.02000 | depth=0.009,usb=2.0 |
| `A_PORT_VGA_0` | (-0.068, 0.0148, -0.6704) | -z / +y | 0.03200,0.01300,0.01200 | depth=0.006,vga=1 |
| `A_PSU_0` | (0.1772, 0.023, -0.67) | +z / +y | 0.07350,0.04000,0.18500 | pull=-z,dist=0.195,watts=800,eff=platinum,slot=0 |
| `A_PSU_1` | (-0.1772, 0.023, -0.67) | +z / +y | 0.07350,0.04000,0.18500 | pull=-z,dist=0.195,watts=800,eff=platinum,slot=1 |
| `A_RAIL_L_0` | (-0.221, 0.0248, -0.002) | +z / +y | 0.00800,0.04000,0.73800 | kind=slide,side=l,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62 |
| `A_RAIL_R_0` | (0.221, 0.0248, -0.002) | +z / +y | 0.00800,0.04000,0.73800 | kind=slide,side=r,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62 |
| `A_SCREW_THUMB_0` | (-0.2326, 0.0381, 0.03) | +z / +y | 0.01200,0.01200,0.01200 | thread=M6,captive=1,len=0.032,turns=4 |
| `A_SCREW_THUMB_1` | (0.2326, 0.0381, 0.03) | +z / +y | 0.01200,0.01200,0.01200 | thread=M6,captive=1,len=0.032,turns=4 |
| `A_SHROUD_0` | (0, 0.0739, -0.33) | +z / +y | 0.40000,0.00600,0.16000 | lift=+y,dist=0.06,order=1 |

Moving pieces: `bay_n@A_BAY_n#alu` ×12, `bay_n@A_BAY_n#black_plastic` ×12, `bay_n@A_BAY_n#dark_plastic` ×12, `bay_n@A_BAY_n#steel` ×12, `bay_n@A_BAY_n#steel_dark` ×12, `bay_n@A_BAY_n#tex_parts_c_palette` ×12, `bay_n@A_BAY_n#tex_server_print` ×12, `bezel_n@A_BEZEL_n#black_plastic`, `bezel_n@A_BEZEL_n#dark_plastic`, `bezel_n@A_BEZEL_n#nickel`, `bezel_n@A_BEZEL_n#tex_server_bezel_mesh`, `bezel_n@A_BEZEL_n#tex_server_print`, `button_id_n@A_BUTTON_ID_n#black_plastic`, `button_id_n@A_BUTTON_ID_n#grey_plastic`, `button_power_n@A_BUTTON_POWER_n#black_plastic`, `button_power_n@A_BUTTON_POWER_n#grey_plastic`, `fan_n@A_FAN_n#fan_black` ×6, `led_act_n@A_LED_ACT_n#led_yellow` ×4, `led_bezel_n@A_LED_BEZEL_n@A_BEZEL_n#led_blue`, `led_drive_n@A_LED_DRIVE_n@A_BAY_n#led_green` ×12, `led_drivefault_n@A_LED_DRIVEFAULT_n@A_BAY_n#led_yellow` ×12, `led_fault_n@A_LED_FAULT_n#led_yellow`, `led_health_n@A_LED_HEALTH_n#led_green`, `led_id_n@A_LED_ID_n#led_blue` ×2, `led_ipmi_n@A_LED_IPMI_n#led_green`, `led_link_n@A_LED_LINK_n#led_green` ×4, `led_net_n@A_LED_NET_n#led_green`, `led_power_n@A_LED_POWER_n#led_green`, `led_psu_n@A_LED_PSU_n@A_PSU_n#led_green` ×2, `lid_n@A_LID_n#black_plastic`, `lid_n@A_LID_n#dark_plastic`, `lid_n@A_LID_n#nickel`, `lid_n@A_LID_n#steel`, `lid_n@A_LID_n#tex_server_print`, `psu_n@A_PSU_n#black_plastic` ×2, `psu_n@A_PSU_n#dark_plastic` ×2, `psu_n@A_PSU_n#fan_black` ×2, `psu_n@A_PSU_n#gold` ×2, `psu_n@A_PSU_n#nickel` ×2, `psu_n@A_PSU_n#pcb_green` ×2, `psu_n@A_PSU_n#steel` ×2, `psu_n@A_PSU_n#steel_dark` ×2, `psu_n@A_PSU_n#tex_parts_c_palette` ×2, `psu_n@A_PSU_n#tex_server_print` ×2, `rail_l_n@A_RAIL_L_n#steel`, `rail_l_n@A_RAIL_L_n#steel_dark`, `rail_r_n@A_RAIL_R_n#steel`, `rail_r_n@A_RAIL_R_n#steel_dark`, `screw_thumb_n@A_SCREW_THUMB_n#steel` ×2, `shroud_n@A_SHROUD_n#black_plastic`, `shroud_n@A_SHROUD_n#tex_server_print`.

**Deviations / notes**
- "L" is −x and "R" is +x, as for the AC.
- Extra anchors beyond the brief, for gameplay: the thumbscrews, the drive LEDs, link/activity LEDs on the rear
  ports, the rear ID LED, the shroud, the bezel lock and light bar, and `A_HIT_1/2` over the two ears.
- The interior is looks only (no DIMM, CPU or fan-socket anchors yet). If the game later lets players swap DIMMs or
  fans, only anchors need adding.

## rack_42u and rack_12u_open

- **Frame:** origin on the floor at the centre of the footprint; +Z is the front, +Y up.
- **Mounting:** two front rails whose front face is the front mounting plane (z = ZM) and two rear rails 0.740 behind
  it (their flange faces the rear, its rear face at ZM − 0.742). Square 9.5 mm cage-nut holes at the EIA-310 heights
  (6.35, 22.225 and 38.1 mm above the bottom of each U), centred ±232.55 mm, with the U numbers printed beside them
  (front and rear) and a tick at each U boundary. The servers' slide rails span exactly this 0.740.
- **`A_RACKU_n`** (n = 0 is U1 at the bottom): the install pose of a rack device. It sits at the centre of the front
  mounting plane, at the **bottom** of that U, +Z out of the front, size 0.4826 × 0.04445 × 0.740. Meta
  `u=<n+1>,pitch=0.04445,depth=0.74,extends=-z,base=bottom`. A k-U device installed at `A_RACKU_n` takes U n+1 … n+k,
  and its origin lands exactly on the anchor.
- **rack_42u** (600 × 1070 × 2000, black powder coat): ZM = 0.410, U1 bottom at y = 0.090, U42 top at y = 1.957.
  Corner posts, top and bottom frames, rail support beams, a roof with two brush cable entries and a blanking
  plate, a floor panel with a brushed cable entry, four casters and four levelling feet, the rating label and an
  earth stud inside.
  - `A_DOOR_FRONT_0` (`hinge=y,open=-110`, hinged on −x): a perforated door (hex perforation as an alpha-cut
    tiled texture, `rack_perf.png`, two-sided), its folded frame, three hinges, the swing handle with a key lock
    (`A_HANDLE_0@A_DOOR_FRONT_0`, `turn=90`) and the badge.
  - The split rear doors: `A_DOOR_REAR_0` (−x hinge, `open=110`) and `A_DOOR_REAR_1` (+x hinge, `open=-110`). Both
    open outwards; the preview `rack_42u_4/6` renders them open with these exact values.
  - `A_PANEL_SIDE_0` (−x) and `A_PANEL_SIDE_1` (+x): removable side panels (`remove=∓x,lift=+y`) with folded edges,
    inner ribs, two key latches and a grip.
  - `A_PDU_0` (−x) and `A_PDU_1` (+x): zero-U PDU places in the rear side channels, 0.115 behind the rear rails,
    at the bottom end of the PDU (y = 0.12), +Y along it, +Z (the outlet side) facing the rear door. This is the
    `pdu_0u` model's frame. The channel has the keyhole brackets at the PDU's mounting-button heights.
- **rack_12u_open:** a 4-post open frame, 593 × 795 × 691 overall on four castors. ZM = 0.371, U1 bottom at y = 0.115. The
  four posts are C-profile rails, with box-section top and bottom frames, a cable tie bar across the rear and an
  earth stud. `A_HIT_0/1` are the two sides, `A_HIT_2` the base.
- Texture `rack_print.png`: the U numbers, door badge, rating label and earth sticker.

### rack_42u

- **Triangles:** 20,442 in 29 meshes.
- **Bounds:** min=(-0.3052, -0.0005, -0.5480) max=(0.3052, 2.0015, 0.5510) size=(0.6104, 2.0020, 1.0990)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_DOOR_FRONT_0` | (-0.296, 1.02, 0.525) | +z / +y | 0.60000,1.90000,0.02000 | hinge=y,open=-110,lock=1,handle=A_HANDLE_0 |
| `A_DOOR_REAR_0` | (-0.296, 1.02, -0.525) | +z / +y | 0.30000,1.90000,0.02000 | hinge=y,open=110,lock=0,leaf=0 |
| `A_DOOR_REAR_1` | (0.296, 1.02, -0.525) | +z / +y | 0.30000,1.90000,0.02000 | hinge=y,open=-110,lock=1,leaf=1 |
| `A_HANDLE_0@A_DOOR_FRONT_0` | (0.26, 1.035, 0.551) | +z / +y | 0.02000,0.10000,0.02000 | turn=90,lock=1 |
| `A_HIT_0` | (0, 1, 0) | +z / +y | 0.60000,2.00000,1.07000 |  |
| `A_PANEL_SIDE_0` | (-0.3, 1.016, 0) | +z / +y | 0.02000,1.88800,1.01000 | remove=-x,dist=0.06,lift=+y,latch=2,order=0 |
| `A_PANEL_SIDE_1` | (0.3, 1.016, 0) | +z / +y | 0.02000,1.88800,1.01000 | remove=+x,dist=0.06,lift=+y,latch=2,order=0 |
| `A_PDU_0` | (-0.27, 0.12, -0.445) | -z / +y | 0.05600,1.80000,0.04400 | zeroU=1,len=1.80,side=l,mount=buttons,model=pdu_0u |
| `A_PDU_1` | (0.27, 0.12, -0.445) | -z / +y | 0.05600,1.80000,0.04400 | zeroU=1,len=1.80,side=r,mount=buttons,model=pdu_0u |
| `A_RACKU_0..41 (42)` | (0, 0.09, 0.41) … (0, 1.9124, 0.41) | +z / +y | 0.48260,0.04445,0.74000 | u=1,pitch=0.04445,depth=0.74,extends=-z,base=bottom,rear=-0.74 … u=42,pitch=0.04445,depth=0.74,extends=-z,base=bottom,rear=-0.74 |

Moving pieces: `door_front_n@A_DOOR_FRONT_n#black_plastic`, `door_front_n@A_DOOR_FRONT_n#dark_plastic`, `door_front_n@A_DOOR_FRONT_n#nickel`, `door_front_n@A_DOOR_FRONT_n#paint_black`, `door_front_n@A_DOOR_FRONT_n#steel_dark`, `door_front_n@A_DOOR_FRONT_n#tex_rack_perf`, `door_front_n@A_DOOR_FRONT_n#tex_rack_print`, `door_rear_n@A_DOOR_REAR_n#black_plastic` ×2, `door_rear_n@A_DOOR_REAR_n#paint_black` ×2, `door_rear_n@A_DOOR_REAR_n#steel_dark` ×2, `door_rear_n@A_DOOR_REAR_n#tex_rack_perf` ×2, `panel_side_n@A_PANEL_SIDE_n#black_plastic` ×2, `panel_side_n@A_PANEL_SIDE_n#nickel` ×2, `panel_side_n@A_PANEL_SIDE_n#paint_black` ×2.

### rack_12u_open

- **Triangles:** 5,274 in 8 meshes.
- **Bounds:** min=(-0.2965, 0.0003, -0.4190) max=(0.2965, 0.6914, 0.3760) size=(0.5930, 0.6911, 0.7950)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_HIT_0` | (-0.262, 0.345, 0.001) | +z / +y | 0.04000,0.69000,0.80000 |  |
| `A_HIT_1` | (0.262, 0.345, 0.001) | +z / +y | 0.04000,0.69000,0.80000 |  |
| `A_HIT_2` | (0, 0.07, 0.001) | +z / +y | 0.56000,0.07000,0.80000 |  |
| `A_RACKU_0..11 (12)` | (0, 0.115, 0.371) … (0, 0.6039, 0.371) | +z / +y | 0.48260,0.04445,0.74000 | u=1,pitch=0.04445,depth=0.74,extends=-z,base=bottom,rear=-0.74 … u=12,pitch=0.04445,depth=0.74,extends=-z,base=bottom,rear=-0.74 |

Moving pieces: none.

**Deviations / notes**
- **`A_RACKU_n` sits at the bottom of its U, not at the U's vertical centre.** The brief says both "the centre of
  that U's front mounting plane" (the rack) and "origin … at the bottom of the device's U space, so it installs
  directly at a rack's `A_RACKU_n`" (the devices). Only the bottom-of-U pose lets a device install directly, so I
  chose that. The anchor is horizontally centred. The game's click box for a U should be offset by +U/2 in y and
  by −0.37 in z if the game centres boxes on anchors; the meta `base=bottom,extends=-z` records this.
- No cage nuts or blanking panels are modelled; devices list their screw points as `A_SCREW_RACK_n` (fixed
  ears) or `A_SCREW_THUMB_n` (servers).

## switch_24: LINKWAVE LS-2804X, 24 × 1G + 4 × SFP+

- **Frame:** the rack device frame; body 0.440 × 0.0436 × 0.250, front panel face at z = 0.0045, ears on the
  rails (z 0..0.002) with `A_SCREW_RACK_0..3` at the 1st and 3rd holes.
- **Front** (+x is the viewer's left): the logo and status LEDs `A_LED_POWER_0`, `A_LED_SYS_0` (green),
  `A_LED_FAN_0` (amber) with printed legends. Two ganged 2 × 6 RJ45 blocks in metal shields: `A_PORT_ETH_0..23` is
  port n+1, with odd ports on the top row (latch up) and even ports below (latch down). Each anchor's +Y points at
  its latch (`latch=+up`), each port has `A_LED_LINK_n` (green) and `A_LED_ACT_n` (amber) at its corners, and the
  numbers are printed above and below. Then four SFP+ cages `A_PORT_SFP_0..3` (ports 25–28, `depth=0.042`) with EMI
  gaskets and `A_LED_SFP_n`; the console RJ45 `A_PORT_CONSOLE_0` in a light-blue surround; a reset pinhole; a
  vent grille.
- **Rear:** the C14 inlet `A_PORT_C14_0` (`plug=c13`), two 40 mm fans `A_FAN_0/1` behind hex grilles, an earth
  screw. Side vents, the rating label on the top cover.
- Texture `net_print.png` (shared with the patch panel): legends (transparent cells), logo, rating label.

- **Triangles:** 11,794 in 65 meshes.
- **Bounds:** min=(-0.2413, 0.0004, -0.2490) max=(0.2413, 0.0441, 0.0051) size=(0.4826, 0.0437, 0.2541)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_FAN_0` | (0.04, 0.0222, -0.2295) | -z / +y | 0.04000,0.04000,0.02000 | axis=z,spin=1,rpm=6000 |
| `A_FAN_1` | (0.12, 0.0222, -0.2295) | -z / +y | 0.04000,0.04000,0.02000 | axis=z,spin=1,rpm=6000 |
| `A_HIT_0` | (0, 0.0222, -0.1205) | +z / +y | 0.44000,0.04360,0.25000 |  |
| `A_HIT_1` | (0, 0.0222, 0.001) | +z / +y | 0.48260,0.04360,0.00400 |  |
| `A_LED_ACT_0..23 (24)` | (0.1355, 0.0365, 0.0048) … (-0.0255, 0.0087, 0.0048) | +z / +y | 0.00200,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_FAN_0` | (0.1735, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=amber,fn=fan |
| `A_LED_LINK_0..23 (24)` | (0.1445, 0.0365, 0.0048) … (-0.0165, 0.0087, 0.0048) | +z / +y | 0.00200,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_POWER_0` | (0.1985, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=green,fn=power |
| `A_LED_SFP_0` | (-0.068, 0.0376, 0.0048) | +z / +y | 0.00300,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_SFP_1` | (-0.068, 0.0076, 0.0048) | +z / +y | 0.00300,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_SFP_2` | (-0.0845, 0.0376, 0.0048) | +z / +y | 0.00300,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_SFP_3` | (-0.0845, 0.0076, 0.0048) | +z / +y | 0.00300,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_SYS_0` | (0.186, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=green,fn=sys |
| `A_PORT_C14_0` | (-0.15, 0.0224, -0.2455) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_CONSOLE_0` | (-0.115, 0.0141, 0.0045) | +z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,serial=rs232,baud=115200 |
| `A_PORT_ETH_0..23 (24)` | (0.14, 0.0311, 0.0045) … (-0.021, 0.0141, 0.0045) | +z / +y | 0.01420,0.01250,0.02000 | depth=0.012,rj45=1,latch=+up,port=1,speed=1g … depth=0.012,rj45=1,latch=+up,port=24,speed=1g |
| `A_PORT_SFP_0` | (-0.068, 0.0311, 0.0045) | +z / +y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp+,speed=10g,port=25 |
| `A_PORT_SFP_1` | (-0.068, 0.0141, 0.0045) | +z / +y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp+,speed=10g,port=26 |
| `A_PORT_SFP_2` | (-0.0845, 0.0311, 0.0045) | +z / +y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp+,speed=10g,port=27 |
| `A_PORT_SFP_3` | (-0.0845, 0.0141, 0.0045) | +z / +y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp+,speed=10g,port=28 |
| `A_SCREW_RACK_0` | (-0.2326, 0.0063, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l |
| `A_SCREW_RACK_1` | (-0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l |
| `A_SCREW_RACK_2` | (0.2326, 0.0063, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=r |
| `A_SCREW_RACK_3` | (0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=r |

Moving pieces: `fan_n@A_FAN_n#fan_black` ×2, `led_act_n@A_LED_ACT_n#led_yellow` ×24, `led_fan_n@A_LED_FAN_n#led_yellow`, `led_link_n@A_LED_LINK_n#led_green` ×24, `led_power_n@A_LED_POWER_n#led_green`, `led_sfp_n@A_LED_SFP_n#led_green` ×4, `led_sys_n@A_LED_SYS_n#led_green`.

## patch_panel_24: Cat6 keystone patch panel

- **Frame:** the rack device frame; the 2 mm panel is its own pair of ears (z 0..0.002), with
  `A_SCREW_RACK_0..3`. The top and bottom flanges and side returns are bent back 30 mm.
- **Front:** 24 Cat6 keystone jacks in four groups of 6 (16.5 mm pitch), each a separate jack (chamfered face,
  RJ45 mouth with the latch down, contacts, body) in a chamfered cut-out. `A_PORT_ETH_0..23` is port n+1, port 1 at
  +x (the viewer's left), +Y towards the latch (down), `latch=+up`, `cat=6`. Above them, the numbered white label
  strip under a clear cover (`clear_plastic`), and a "CAT 6" print below.
- **Rear:** each keystone's white 110 IDC block with its T568B colour code. `A_PUNCH_0..23` is at the back of the
  block, +Z towards the rear where the punch-down tool comes from (`idc=110,wires=8,scheme=T568B`). The cable
  management bar (a steel rod with 13 tie mounts) sits on two brackets 0.11 behind the panel; `A_BAR_0` marks it.

- **Triangles:** 6,232 in 7 meshes.
- **Bounds:** min=(-0.2413, 0.0006, -0.1105) max=(0.2413, 0.0438, 0.0033) size=(0.4826, 0.0432, 0.1138)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BAR_0` | (0, 0.0054, -0.106) | -z / +y | 0.43000,0.01200,0.01200 | ties=13,pitch=0.033 |
| `A_HIT_0` | (0, 0.0222, -0.012) | +z / +y | 0.48260,0.04360,0.03200 |  |
| `A_HIT_1` | (0, 0.0064, -0.06) | +z / +y | 0.43000,0.01200,0.12000 |  |
| `A_PORT_ETH_0..23 (24)` | (0.2018, 0.0206, 0.0026) … (-0.2018, 0.0206, 0.0026) | +z / -y | 0.01420,0.01250,0.02000 | depth=0.012,rj45=1,latch=+up,port=1,cat=6 … depth=0.012,rj45=1,latch=+up,port=24,cat=6 |
| `A_PUNCH_0..23 (24)` | (0.2018, 0.0194, -0.0374) … (-0.2018, 0.0194, -0.0374) | -z / +y | 0.01400,0.01500,0.01200 | idc=110,wires=8,scheme=T568B,port=1 … idc=110,wires=8,scheme=T568B,port=24 |
| `A_SCREW_RACK_0` | (-0.2326, 0.0063, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l |
| `A_SCREW_RACK_1` | (-0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l |
| `A_SCREW_RACK_2` | (0.2326, 0.0063, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=r |
| `A_SCREW_RACK_3` | (0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=r |

Moving pieces: none.

**Notes**
- The keystone contacts and the IDC slots are printed (`tex_net_print`) rather than modelled, to keep 24 jacks
  cheap. The switch keeps real gold contact combs.
- The previews leave the strip's clear cover out (the preview renderer has no transparent shader for
  `clear_plastic`); the model has it.

## ups_2u: AMPERE Smart 2200 RM, 2U rack UPS

- **Frame:** the rack device frame; body 0.432 × 0.0873 × 0.480, the chassis front plate at z = 0.004, the bezel
  face at z = 0.032, ears on the rails with `A_SCREW_RACK_0..3` (the bottom and top holes of the 2U).
- **Front:** the display module at +x (the viewer's left): the LCD `A_SCREEN_0` (0.058 × 0.026; its dark quad is
  attached to it), the power button `A_BUTTON_POWER_0`, the menu buttons `A_BUTTON_UP_0`, `A_BUTTON_DOWN_0`,
  `A_BUTTON_ENTER_0` and the LEDs `A_LED_ONLINE_0` (green), `A_LED_BATTERY_0` (amber), `A_LED_FAULT_0` (red).
  The removable bezel `A_BEZEL_0` (`remove=+z,order=0`), with ribbed vents and the logo, covers the battery pack
  `A_BATTERY_0` (`pull=+z,dist=0.38,order=1,under=A_BEZEL_0`). The pack is a complete piece: a steel tray, four
  12 V blocks with terminals and links, the front plate with its handle and screws, and the rear connector, which
  meets a socket at the back of the bay.
- **Rear:** 8 × C13 outlets `A_PORT_C13_0..7` in two numbered groups (`plug=c14,group=1|2`), the C20 inlet
  `A_PORT_C20_0` (`plug=c19`), `A_PORT_USBB_0`, `A_PORT_SERIAL_0` (RJ45), the input breaker `A_BUTTON_BREAKER_0`,
  the network-management-card slot cover, a 60 mm fan `A_FAN_0` behind its grille, an earth screw and legends.

- **Triangles:** 8,596 in 30 meshes.
- **Bounds:** min=(-0.2413, 0.0004, -0.4845) max=(0.2413, 0.0885, 0.0332) size=(0.4826, 0.0881, 0.5177)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BATTERY_0` | (-0.05, 0.0445, 0.004) | +z / +y | 0.30000,0.07530,0.36000 | pull=+z,dist=0.38,order=1,under=A_BEZEL_0,kind=vrla,cells=4x12v9ah,connector=anderson |
| `A_BEZEL_0` | (-0.052, 0.0445, 0.032) | +z / +y | 0.32400,0.08530,0.02800 | remove=+z,dist=0.05,order=0,clips=4 |
| `A_BUTTON_BREAKER_0` | (-0.2, 0.0688, -0.4815) | -z / +y | 0.01200,0.01200,0.01000 | press=-z_local,travel=0.003,fn=reset,rating=15a |
| `A_BUTTON_DOWN_0` | (0.1586, 0.0213, 0.0321) | +z / +y | 0.01300,0.01000,0.00600 | press=-z_local,travel=0.0010,fn=down |
| `A_BUTTON_ENTER_0` | (0.1426, 0.0213, 0.0321) | +z / +y | 0.01300,0.01000,0.00600 | press=-z_local,travel=0.0010,fn=enter |
| `A_BUTTON_POWER_0` | (0.1996, 0.0213, 0.0321) | +z / +y | 0.01260,0.01260,0.00600 | press=-z_local,travel=0.0012,fn=power,hold=2 |
| `A_BUTTON_UP_0` | (0.1746, 0.0213, 0.0321) | +z / +y | 0.01300,0.01000,0.00600 | press=-z_local,travel=0.0010,fn=up |
| `A_FAN_0` | (-0.1, 0.0458, -0.462) | -z / +y | 0.06000,0.06000,0.02500 | axis=z,spin=1,rpm=3200 |
| `A_HIT_0` | (0, 0.0445, -0.222) | +z / +y | 0.43200,0.08730,0.50800 |  |
| `A_HIT_1` | (0, 0.0445, 0.001) | +z / +y | 0.48260,0.08730,0.00400 |  |
| `A_LED_BATTERY_0` | (0.1963, 0.0563, 0.0317) | +z / +y | 0.00300,0.00300,0.00300 | colour=yellow,fn=battery |
| `A_LED_FAULT_0` | (0.1963, 0.0468, 0.0317) | +z / +y | 0.00300,0.00300,0.00300 | colour=red,fn=fault |
| `A_LED_ONLINE_0` | (0.1963, 0.0658, 0.0317) | +z / +y | 0.00300,0.00300,0.00300 | colour=green,fn=online |
| `A_PORT_C13_0..7 (8)` | (0.133, 0.0228, -0.4775) … (0.077, 0.0568, -0.4775) | -z / +y | 0.02600,0.01800,0.01200 | depth=0.007,plug=c14,outlet=c13,group=1 … depth=0.007,plug=c14,outlet=c13,group=2 |
| `A_PORT_C20_0` | (-0.17, 0.0308, -0.4775) | -z / +y | 0.03400,0.02500,0.01400 | depth=0.009,plug=c19,inlet=c20 |
| `A_PORT_SERIAL_0` | (-0.04, 0.0308, -0.4775) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=-up,serial=rs232 |
| `A_PORT_USBB_0` | (-0.04, 0.0608, -0.4775) | -z / +y | 0.01200,0.01200,0.01200 | depth=0.008,usb=b |
| `A_SCREEN_0` | (0.1573, 0.0568, 0.0317) | +z / +y | 0.05800,0.02600,0.00300 | kind=lcd,ref=256x112,colour=blue_white |
| `A_SCREW_RACK_0` | (-0.2326, 0.0063, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l |
| `A_SCREW_RACK_1` | (-0.2326, 0.0825, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l |
| `A_SCREW_RACK_2` | (0.2326, 0.0063, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=r |
| `A_SCREW_RACK_3` | (0.2326, 0.0825, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=r |

Moving pieces: `battery_n@A_BATTERY_n#black_plastic`, `battery_n@A_BATTERY_n#copper`, `battery_n@A_BATTERY_n#steel`, `battery_n@A_BATTERY_n#tex_parts_c_palette`, `battery_n@A_BATTERY_n#tex_power_print`, `bezel_n@A_BEZEL_n#black_plastic`, `bezel_n@A_BEZEL_n#dark_plastic`, `bezel_n@A_BEZEL_n#tex_power_print`, `button_breaker_n@A_BUTTON_BREAKER_n#white_plastic`, `button_down_n@A_BUTTON_DOWN_n#black_plastic`, `button_down_n@A_BUTTON_DOWN_n#grey_plastic`, `button_enter_n@A_BUTTON_ENTER_n#black_plastic`, `button_enter_n@A_BUTTON_ENTER_n#grey_plastic`, `button_power_n@A_BUTTON_POWER_n#black_plastic`, `button_power_n@A_BUTTON_POWER_n#grey_plastic`, `button_up_n@A_BUTTON_UP_n#black_plastic`, `button_up_n@A_BUTTON_UP_n#grey_plastic`, `fan_n@A_FAN_n#fan_black`, `led_battery_n@A_LED_BATTERY_n#led_yellow`, `led_fault_n@A_LED_FAULT_n#led_red`, `led_online_n@A_LED_ONLINE_n#led_green`, `screen_n@A_SCREEN_n#black_plastic`.

## ups_tower: AMPERE Smart 1500, tower UPS (basement)

- **Frame:** origin on the floor at the centre of the footprint, +Z the front; 0.170 W × 0.219 H × 0.439 D on
  four rubber feet.
- **Front:** the same controls as the rack UPS (`A_SCREEN_0`, `A_BUTTON_POWER_0`, `A_BUTTON_UP_0` /
  `DOWN_0` / `ENTER_0`, `A_LED_ONLINE_0`, `A_LED_BATTERY_0`, `A_LED_FAULT_0`) on a panel sloped back 25° at the top,
  so it reads from above when the UPS stands on the floor. The front bezel `A_BEZEL_0` covers the battery door and
  the two-block pack `A_BATTERY_0` (`pull=+z,under=A_BEZEL_0`).
- **Rear:** 8 × NEMA 5-15R receptacles `A_PORT_NEMA515_0..7` (meta `plug=nema5-15p`; 0–5 battery + surge, 6–7
  surge only), so the PC power cords plug straight in. Also the attached input cord `A_CORD_0` (the end of its
  boot, `plug=nema5-15p,len=1.8`), `A_PORT_USBB_0`, the breaker `A_BUTTON_BREAKER_0`, a fan `A_FAN_0`, and the
  rating label on the −x side.

- **Triangles:** 7,782 in 27 meshes.
- **Bounds:** min=(-0.0852, 0.0000, -0.2650) max=(0.0850, 0.2190, 0.2198) size=(0.1702, 0.2190, 0.4848)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BATTERY_0` | (0, 0.0825, 0.1895) | +z / +y | 0.12000,0.12310,0.18000 | pull=+z,dist=0.20,order=1,under=A_BEZEL_0,kind=vrla,cells=2x12v9ah |
| `A_BEZEL_0` | (0, 0.0827, 0.2195) | +z / +y | 0.17000,0.14910,0.03000 | remove=+z,dist=0.05,order=0,clips=4 |
| `A_BUTTON_BREAKER_0` | (-0.04, 0.205, -0.225) | -z / +y | 0.01200,0.01200,0.01000 | press=-z_local,travel=0.003,fn=reset,rating=15a |
| `A_BUTTON_DOWN_0` | (-0.0006, 0.1713, 0.2156) | (0.000, 0.423, 0.906) / (0.000, 0.906, -0.423) | 0.01300,0.01000,0.00600 | press=-z_local,travel=0.0010,fn=down |
| `A_BUTTON_ENTER_0` | (-0.0166, 0.1713, 0.2156) | (0.000, 0.423, 0.906) / (0.000, 0.906, -0.423) | 0.01300,0.01000,0.00600 | press=-z_local,travel=0.0010,fn=enter |
| `A_BUTTON_POWER_0` | (0.0554, 0.1713, 0.2156) | (0.000, 0.423, 0.906) / (0.000, 0.906, -0.423) | 0.01260,0.01260,0.00600 | press=-z_local,travel=0.0012,fn=power,hold=2 |
| `A_BUTTON_UP_0` | (0.0154, 0.1713, 0.2156) | (0.000, 0.423, 0.906) / (0.000, 0.906, -0.423) | 0.01300,0.01000,0.00600 | press=-z_local,travel=0.0010,fn=up |
| `A_CORD_0` | (-0.05, 0.022, -0.265) | -z / +y | 0.01200,0.01200,0.02000 | r=0.0040,plug=nema5-15p,len=1.8,awg=14 |
| `A_FAN_0` | (0.054, 0.186, -0.2075) | -z / +y | 0.04500,0.04500,0.02000 | axis=z,spin=1,rpm=2800 |
| `A_HIT_0` | (0, 0.1095, 0) | +z / +y | 0.17000,0.21900,0.43900 |  |
| `A_LED_BATTERY_0` | (0.0227, 0.1913, 0.2058) | (0.000, 0.423, 0.906) / (0.000, 0.906, -0.423) | 0.00300,0.00300,0.00300 | colour=yellow,fn=battery |
| `A_LED_FAULT_0` | (0.0227, 0.1827, 0.2098) | (0.000, 0.423, 0.906) / (0.000, 0.906, -0.423) | 0.00300,0.00300,0.00300 | colour=red,fn=fault |
| `A_LED_ONLINE_0` | (0.0227, 0.1999, 0.2018) | (0.000, 0.423, 0.906) / (0.000, 0.906, -0.423) | 0.00300,0.00300,0.00300 | colour=green,fn=online |
| `A_PORT_NEMA515_0..7 (8)` | (0.02, 0.05, -0.221) … (-0.02, 0.158, -0.221) | -z / +y | 0.02400,0.03000,0.01400 | depth=0.010,plug=nema5-15p,outlet=nema5-15r,group=battery … depth=0.010,plug=nema5-15p,outlet=nema5-15r,group=surge |
| `A_PORT_USBB_0` | (-0.06, 0.175, -0.221) | -z / +y | 0.01200,0.01200,0.01200 | depth=0.008,usb=b |
| `A_SCREEN_0` | (-0.0123, 0.1945, 0.2044) | (0.000, 0.423, 0.906) / (0.000, 0.906, -0.423) | 0.05000,0.02000,0.00300 | kind=lcd,ref=256x112,colour=blue_white |

Moving pieces: `battery_n@A_BATTERY_n#black_plastic`, `battery_n@A_BATTERY_n#copper`, `battery_n@A_BATTERY_n#steel`, `battery_n@A_BATTERY_n#tex_parts_c_palette`, `battery_n@A_BATTERY_n#tex_power_print`, `bezel_n@A_BEZEL_n#black_plastic`, `bezel_n@A_BEZEL_n#dark_plastic`, `bezel_n@A_BEZEL_n#tex_power_print`, `button_breaker_n@A_BUTTON_BREAKER_n#white_plastic`, `button_down_n@A_BUTTON_DOWN_n#black_plastic`, `button_down_n@A_BUTTON_DOWN_n#grey_plastic`, `button_enter_n@A_BUTTON_ENTER_n#black_plastic`, `button_enter_n@A_BUTTON_ENTER_n#grey_plastic`, `button_power_n@A_BUTTON_POWER_n#black_plastic`, `button_power_n@A_BUTTON_POWER_n#grey_plastic`, `button_up_n@A_BUTTON_UP_n#black_plastic`, `button_up_n@A_BUTTON_UP_n#grey_plastic`, `fan_n@A_FAN_n#fan_black`, `led_battery_n@A_LED_BATTERY_n#led_yellow`, `led_fault_n@A_LED_FAULT_n#led_red`, `led_online_n@A_LED_ONLINE_n#led_green`, `screen_n@A_SCREEN_n#black_plastic`.

## pdu_0u: AMPERE metered zero-U PDU, 24 × C13 + 4 × C19

- **Frame:** origin at the centre of the bottom end of the body, +Y along it, outlets on +Z, the mounting buttons on
  −Z. Body 0.044 × 1.80 × 0.056 (dark extruded aluminium, black end caps). This is the pose of the rack's
  `A_PDU_0/1`.
- From the bottom: the two bank breakers `A_SWITCH_BREAKER_0/1` (toggles as moving pieces,
  `hinge=x,on=-25,off=25,on_side=+y`), the 3-digit amp meter `A_SCREEN_0` (`kind=7seg`) and the logo. Then bank A
  (`A_PORT_C19_0` + 8 × C13), bank B (`A_PORT_C19_1`, 8 × C13, `A_PORT_C19_2`) and bank C (8 × C13 +
  `A_PORT_C19_3`). `A_PORT_C13_0..23` (`plug=c14,bank=A|B|C`) and `A_PORT_C19_0..3` (`plug=c20`) are numbered and
  labelled on the face.
- The input cord leaves the bottom end through a boot: `A_CORD_0` (`plug=l6-30p,len=3.0`). Two mounting buttons
  `A_MOUNT_0/1` on the back at y = 0.20 and 1.60 match the keyhole brackets in the rack's PDU channel.

- **Triangles:** 7,554 in 9 meshes.
- **Bounds:** min=(-0.0225, -0.0700, -0.0370) max=(0.0225, 1.8000, 0.0410) size=(0.0450, 1.8700, 0.0780)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_CORD_0` | (0, -0.07, -0.008) | -y / +z | 0.01600,0.01600,0.02000 | r=0.0062,plug=l6-30p,len=3.0,awg=10 |
| `A_HIT_0` | (0, 0.9, 0) | +z / +y | 0.04400,1.80000,0.05600 |  |
| `A_MOUNT_0` | (0, 0.2, -0.037) | -z / +y | 0.02000,0.02000,0.01200 | kind=button,keyhole=1 |
| `A_MOUNT_1` | (0, 1.6, -0.037) | -z / +y | 0.02000,0.02000,0.01200 | kind=button,keyhole=1 |
| `A_PORT_C13_0..23 (24)` | (0, 0.443, 0.028) … (0, 1.537, 0.028) | +z / +y | 0.02600,0.01800,0.01200 | depth=0.007,plug=c14,outlet=c13,bank=A,n=1 … depth=0.007,plug=c14,outlet=c13,bank=C,n=24 |
| `A_PORT_C19_0` | (0, 0.399, 0.028) | +z / +y | 0.03200,0.02400,0.01400 | depth=0.008,plug=c20,outlet=c19,bank=A,n=1 |
| `A_PORT_C19_1` | (0, 0.813, 0.028) | +z / +y | 0.03200,0.02400,0.01400 | depth=0.008,plug=c20,outlet=c19,bank=B,n=2 |
| `A_PORT_C19_2` | (0, 1.167, 0.028) | +z / +y | 0.03200,0.02400,0.01400 | depth=0.008,plug=c20,outlet=c19,bank=B,n=3 |
| `A_PORT_C19_3` | (0, 1.581, 0.028) | +z / +y | 0.03200,0.02400,0.01400 | depth=0.008,plug=c20,outlet=c19,bank=C,n=4 |
| `A_SCREEN_0` | (0, 0.256, 0.0284) | +z / +y | 0.02400,0.01000,0.00300 | kind=7seg,digits=3,colour=red,shows=amps |
| `A_SWITCH_BREAKER_0` | (0, 0.184, 0.032) | +z / +y | 0.02000,0.01600,0.01200 | hinge=x,on=-25,off=25,on_side=+y,rating=16a,mark_on=I,mark_off=O |
| `A_SWITCH_BREAKER_1` | (0, 0.224, 0.032) | +z / +y | 0.02000,0.01600,0.01200 | hinge=x,on=-25,off=25,on_side=+y,rating=16a,mark_on=I,mark_off=O |

Moving pieces: `screen_n@A_SCREEN_n#black_plastic`, `switch_breaker_n@A_SWITCH_BREAKER_n#white_plastic` ×2.

## pdu_1u: AMPERE 1U PDU, 8 × C13 with a lit switch

- **Frame:** the rack device frame; body 0.440 × 0.0436 × 0.180, the front at z = 0.003, ears with
  `A_SCREW_RACK_0..3`.
- **Front:** 8 × C13 `A_PORT_C13_0..7` numbered 1–8 from +x (`plug=c14`), the logo, and the lit rocker
  `A_SWITCH_POWER_0` (`hinge=x,on=-9,off=9,on_side=+y,lit=1`, like the PSU rocker: modelled in its neutral pose).
  Its red lamp window is `A_LED_SWITCH_0@A_SWITCH_POWER_0` (`led_red`), and an "O" mark sits on the lower half.
- **Rear:** the input cord `A_CORD_0` (`plug=c20,len=2.5`, to feed from a UPS's C19 or the zero-U PDU), the rating
  label on the top.

- **Triangles:** 2,972 in 8 meshes.
- **Bounds:** min=(-0.2413, 0.0004, -0.2290) max=(0.2413, 0.0441, 0.0063) size=(0.4826, 0.0437, 0.2353)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_CORD_0` | (0.15, 0.0222, -0.229) | -z / +y | 0.01400,0.01400,0.02000 | r=0.0045,plug=c20,len=2.5,awg=14 |
| `A_HIT_0` | (0, 0.0222, -0.087) | +z / +y | 0.44000,0.04360,0.18000 |  |
| `A_HIT_1` | (0, 0.0222, 0.001) | +z / +y | 0.48260,0.04360,0.00400 |  |
| `A_LED_SWITCH_0@A_SWITCH_POWER_0` | (-0.17, 0.0261, 0.0055) | (0.000, 0.225, 0.974) / (0.000, 0.974, -0.225) | 0.01800,0.00400,0.00300 | colour=red,fn=power_on |
| `A_PORT_C13_0..7 (8)` | (0.15, 0.0222, 0.003) … (-0.102, 0.0222, 0.003) | +z / +y | 0.02600,0.01800,0.01200 | depth=0.007,plug=c14,outlet=c13,n=1 … depth=0.007,plug=c14,outlet=c13,n=8 |
| `A_SCREW_RACK_0` | (-0.2326, 0.0063, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l |
| `A_SCREW_RACK_1` | (-0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l |
| `A_SCREW_RACK_2` | (0.2326, 0.0063, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=r |
| `A_SCREW_RACK_3` | (0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=r |
| `A_SWITCH_POWER_0` | (-0.17, 0.0222, 0.0035) | +z / +y | 0.02600,0.01800,0.01000 | hinge=x,on=-9,off=9,on_side=+y,mark_on=I,mark_off=O,lit=1,led=A_LED_SWITCH_0 |

Moving pieces: `led_switch_n@A_LED_SWITCH_n@A_SWITCH_POWER_n#led_red`, `switch_power_n@A_SWITCH_POWER_n#black_plastic`, `switch_power_n@A_SWITCH_POWER_n#white_plastic`.

**Notes**
- Texture `power_print.png` (shared by the four): legends (transparent cells), logos, rating labels.
- The tower UPS outlets are NEMA 5-15R and its input is an attached cord, because it serves the basement PCs
  (their cords end in NEMA 5-15P). The rack gear uses IEC C13/C19 throughout.

## Fit check (`datacenter_fit.py`)

The script imports the exported FBX files and installs the devices exactly as the game would: each device's
origin goes on `A_RACKU_n` and each `pdu_0u` on `A_PDU_n`. Then it checks:
- every `A_SCREW_RACK_n` and `A_SCREW_THUMB_n` of every device lands on a rack hole (within 1 mm);
- no two devices overlap in height.

Result: **FIT TOTAL: OK**.
- rack_42u: 12 devices. UPS ×2 at U1–U4, two 2U servers at U9–U12, three 1U servers at U15–U17, the 1U PDU at
  U31, the switch at U39, the patch panel at U40, and both zero-U PDUs in the rear channels.
- rack_12u_open: 4 devices. A UPS at U1–2, a 1U server at U5, the switch at U10, the patch panel at U11.

The servers' slide rails reach both racks' rear rails. The zero-U PDUs clear the rear doors, the side panels and
the rails. Renders: `Logs/ModelPreviews/datacentre_fit_0/1.png` (front, door and +x panel hidden),
`datacentre_fit_rear_0.png`, `datacentre_fit_12u_0.png`.
