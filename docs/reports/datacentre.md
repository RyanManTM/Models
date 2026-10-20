# Task 01 report: data-centre gear

Script: `Tools/Blender/build_datacenter.py` with the helpers `datacenter_common.py` (ports, ears, LEDs, buttons,
low-poly fans, print atlases), `datacenter_ac.py`, `datacenter_server.py`, `datacenter_rack.py`, `datacenter_net.py`
and `datacenter_power.py`.

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_datacenter.py -- [ids...] [--nopreview]
```

With no ids it builds every model below. Each model writes `Assets/Resources/Models/<id>.fbx`, its textures in
`Assets/Resources/Models/Textures/`, previews `Logs/ModelPreviews/<id>_<n>.png` (0–1 Workbench, the rest Cycles) and
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
