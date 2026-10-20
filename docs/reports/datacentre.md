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
