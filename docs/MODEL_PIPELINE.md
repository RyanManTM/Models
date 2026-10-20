# Model pipeline and part contracts

How the models in this repo are built, and the frame and anchors each part model must have so the game can use it.

## 1. Model pipeline (fixed; verified end to end)

Tools live in `Tools/Blender/`. `dct_common.py` is the shared library. Read its docstring and code before writing anything.
- Scripts run headless: `"D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/<script>.py -- <args>`.
- Every helper takes **Unity coordinates** (metres, +Y up, left-handed). `conv()` does the Blender conversion.
- Output:
  - `Assets/Resources/Models/<id>.fbx` (the game loads `Resources.Load<GameObject>("Models/<id>")`).
  - Textures as PNG in `Assets/Resources/Models/Textures/`.
  - Preview renders in `Logs/ModelPreviews/<id>_<n>.png`.
- **Look at your previews** (read the PNGs) and iterate until the part looks like the real thing at bench distance (0.3–0.8 m).
- **Mesh naming:** `<name>#<tag>`, exactly one material per object. Use `c.join_by_tag(root, "<id>")` at the end, so a part has roughly 5–20 renderers (joining keeps moving pieces separate).
- **Material tags** (the game maps them to URP materials):
  - Plain: gold, copper, steel, steel_dark, alu, alu_dark, nickel, black_plastic, dark_plastic, grey_plastic, white_plastic, rubber, fan_black, paint_black, paint_white, glass, mesh_black, thermal_pad, paste, film_blue, cardboard, foam, connector_black, connector_white, connector_beige, pcb_green, pcb_black, solder, ceramic, chip_black.
  - Emissive (off until the game lights them): led_red, led_yellow, led_white, led_green, led_blue, rgb.
  - **Textured: `tex_<file>`** uses `Models/Textures/<file>.png` as the albedo, mapped through the mesh's UVs. Use it for PCB artwork, labels, box art and silkscreen. Give textured meshes proper 0..1 UVs (planar projection is fine).
  - Ask for a new plain tag only if nothing fits, and say so in your report.
- **Anchors:** `c.anchor("A_<KIND>_<NAME>_<INDEX>", pos, size, parent, forward, up, meta)`.
  - Local +Z = the direction a part, plug or tool comes from (outward). Local +Y = up.
  - `size` is the clickable hitbox, in the anchor's own axes.
  - Anchors on moving pieces and pieces belonging to anchors are linked by name, `@<anchor>` (flat export; see the dct_common docstring). The game re-parents them.
- **Moving pieces** (lever arm, latches, slot covers, side panel, PSU rocker, fan rotors, covers) are separate meshes attached to their anchor (`parent=anchor`), modelled in the **closed/installed** pose with the pivot at the anchor. The game animates them.
- **Hitboxes:** `A_HIT_<n>` anchors cover the part's body for clicking: a few boxes, not one per detail. No colliders are exported.

---

## 2. Frames and anchors per part (the contract)

Frames must match today's game (PartFactory.cs) so installed parts line up. Below, "board" means the motherboard's frame, and so on. All values are in metres, Unity axes.

### Motherboard: `mb_ridge_b5` (Socket V5, DDR5) and `mb_ridge_z4` (Socket L17, DDR4)
**Frame:**
- Origin at the PCB centre. The PCB spans z 0..0.0016.
- +z is the component side, +x the rear I/O edge, +y the top edge.
- ATX size: 0.244 (x) by 0.305 (y).
- Real layout:
  - The CPU socket sits upper middle, towards the rear.
  - Four DIMM slots run vertically, in front of the socket (towards −x).
  - The 24-pin is on the front edge beside the DIMMs. The EPS 8-pin is at the top edge, above the VRM, towards the rear.
  - The PCIe x16 slot is below the socket, and the M.2 slot is between the socket and the x16 slot.
  - The rear I/O shroud runs along +x. The chipset heatsink is lower front. SATA ports point out of the front edge (−x), lower half.
  - Headers along the bottom edge: F_PANEL at the bottom front corner, USB 3.0 and HD_AUDIO at the bottom rear, SYS_FAN headers along the edges. CPU_FAN is near the top, by the socket.

**Anchors:**
- `A_SOCKET_CPU_0` is the seating plane at the socket centre (forward +z). `A_MARK_SOCKET_0` is the socket's pin-1 triangle corner.
- `A_LEVER_CPU_0` is the retention lever hinge, with the lever arm and load plate as moving pieces in the closed pose. The meta says how it opens, e.g. `hinge=x,open=-110`.
- `A_COVER_CPU_0` is the protective plastic socket cap (moving piece).
- `A_SOCKET_COOLER_0` is the cooler base contact pose: the top of the installed CPU's IHS (forward +z). Its size is the cooler footprint keep-out.
- `A_SOCKET_RAM_0..3`: slots A1, A2, B1, B2, the stick's bottom-edge centre (forward +z). Use real slot spacing, about 0.0075 m.
  - `A_LATCH_RAM_<i>_0` and `_1` are the latch at each end (moving pieces, closed pose). A single-sided-latch design is also fine; say which.
  - The meta of each socket gives the notch: `notch=<y>` along the slot. DDR4 and DDR5 notches differ.
- `A_SOCKET_M2_0`: an M.2 2280 slot. The socket is the SSD's PCB centre when installed, lying flat, so the connector end is where the slot is.
  - `A_STANDOFF_M2_0` is where the SSD screw goes.
  - `A_COVER_M2_0` is the M.2 heatsink (moving piece), with its screws `A_SCREW_PH0_<n>@A_COVER_M2_0` and its thermal pad film `A_FILM_M2_0@A_COVER_M2_0`.
- `A_SOCKET_PCIE16_0` is the GPU contact origin (see GPU frame), with `A_LATCH_PCIE_0`. Also `A_SOCKET_PCIE1_0..1` for x1 slots (looks only).
- `A_HOLE_0..8` are the nine ATX mounting holes (standard ATX positions). Each has `A_SCREW_PH2_<n>` at the same spot (forward +z).
- Internal ports and headers: `A_PORT_ATX24_0`, `A_PORT_EPS8_0` (8-pin; meta `split=4+4`), `A_PORT_FANCPU_0`, `A_PORT_FANSYS_0..2`, `A_PORT_FPANEL_0` (a 2×5 pin header, with the pinout in the meta and printed on the silkscreen), `A_PORT_USB3HDR_0`, `A_PORT_AUDIOHDR_0`, `A_PORT_SATA_0..3`, `A_PORT_RGB_0`.
- Rear I/O: `A_PORT_USBA_0..5`, `A_PORT_HDMI_0`, `A_PORT_DP_0`, `A_PORT_ETH_0`, `A_PORT_AUDIOJACK_0`, and `A_BUTTON_FLASHBACK_0`.
- `A_LED_DEBUG_CPU_0`, `A_LED_DEBUG_DRAM_0`, `A_LED_DEBUG_VGA_0` and `A_LED_DEBUG_BOOT_0` each carry an LED mesh with an led_* tag. The CMOS battery and BIOS chip are looks only.

**Looks:**
- PCB artwork (`tex_<id>_pcb`): matte black or dark solder mask with traces, pads, vias, white silkscreen labels (CPU_FAN, SYS_FAN1, F_PANEL with the pinout, DIMM A1 A2 B1 B2, M2_1, PCIEX16, SATA6G_1-4, BAT, brand "RIDGE B5 GAMING").
- Black VRM heatsinks with fins and chokes.
- Capacitors, MOSFETs and chipset heatsink with a logo.
- An I/O shroud with an RGB strip.
- A steel-armoured PCIe x16 slot.
- DIMM slots with latches.
- The LGA socket with its frame, lever, load plate and cap.
- Headers with real pins.
- A detailed rear I/O panel.

**I/O shield:** a separate small part, `io_ridge_b5` and `io_ridge_z4`. It's a steel plate with the port cutouts matching the board, origin at the plate centre. Its pose in the case is `A_SOCKET_IOSHIELD_0` (see the case).

### CPU: `cpu_arc5`, `cpu_arc7` (V5: 40×40 mm LGA package) and `cpu_tiron5` (L17: 37.5×45 mm)
- Origin at the centre of the bottom (contact) face, +z up; the IHS top is at about z 0.006.
- Anchors: `A_MARK_PIN1_0` (the gold triangle corner), `A_PASTE_0` (the IHS top centre) and `A_HIT_0`.
- Looks:
  - A nickel IHS with the real shape (V5: octopus-style cut-outs with capacitors showing; L17: a rectangular IHS with side notches).
  - Laser-etched text as a `tex_` texture: "ARC 5 7600 / 6-CORE", the serial, the pin-1 triangle.
  - The green or black substrate, and gold LGA pads underneath, which are visible when held.
  - Alignment notches on the substrate edges.

### Cooler: `cooler_stock` (Wraith-style round shroud with a top fan, pre-applied paste) and `cooler_tower` (120 mm tower, 4 heat pipes)
- Origin at the centre of the base contact face, +z away from the board.
- Anchors:
  - `A_SCREW_PH2_0..3` (spring-loaded mounting screws, in their installed positions).
  - The tower has `A_FILM_0` (the protective film on the base, a moving piece). The stock cooler has `A_PASTE_PRE_0`: the grey pre-applied paste square (a moving piece, so it can be wiped).
  - `A_FAN_0` (a rotor moving piece with real curved blades).
  - `A_PLUG_FAN_0`: where the fan cable's 4-pin plug rests when unplugged, with the cable leaving the fan.
  - `A_HIT_0..`.
- Looks:
  - Stock cooler: a black plastic shroud, an aluminium fin core and a copper base insert.
  - Tower cooler: 40+ thin aluminium fins, polished nickel-plated heat pipes (bent U shapes, made with `tube`), the base, the fan on clips, and a top cover with the brand.

### RAM: `ram_ddr5_16` (Volt DDR5 with RGB) and `ram_ddr4_8` (Volt DDR4, red spreader)
- Frame as today: origin at the bottom-edge centre. Thickness runs along x, the 0.13335 m length along y, the 0.03125 m height along z (heat spreaders make it taller).
- Anchors: `A_NOTCH_0` (the key notch, meta `y=<offset>`), `A_HIT_0`, plus RGB meshes tagged `rgb`.
- Looks: a PCB with gold fingers (with the real notch gap), memory chips, aluminium heat spreaders with a printed label (`tex_`) and a diffuser bar for RGB.

### GPU: `gpu_rx66` (2 fans, 0.2 m, one 8-pin) and `gpu_rx88` (3 fans, 0.3 m, 12V-2x6)
- Frame as today: origin at the PCIe contact edge.
  - The card runs from the bracket end at x +0.095 towards −x.
  - The cooler faces −y (down when mounted); the height runs along +z away from the board.
  - The gold fingers are at about y −0.001, z −0.002.
- Anchors:
  - Power: `A_PORT_PCIE8_0` or `A_PORT_12V2X6_0`, on the top edge (+z), facing +z.
  - Bracket outputs: `A_PORT_DP_0..2` and `A_PORT_HDMI_0`.
  - `A_SCREW_PH2_0..1`, the bracket screw tabs in the case's slot positions.
  - `A_FAN_0..n` (rotor moving pieces).
  - `A_HIT_0..`.
- Looks: the shroud with real styling (angles, cut-outs), fans with 9–11 blades and a hub sticker, fin stacks visible through the shroud, heat pipes, a backplate with cut-outs, the bracket with vent holes and port openings, the PCIe fingers, a brand logo (`tex_`) and an RGB strip.

### PSU: `psu_450` (non-modular, Bronze) and `psu_750` (fully modular, Gold)
- Frame as today: origin at the box centre.
  - x is the depth (0.14), with the rear face at +x (switch and inlet).
  - y is the height (0.086), with the fan grille at −y.
  - z is the width (0.15).
- Anchors:
  - `A_SWITCH_PSU_0` (an I/O rocker, moving piece; meta `on=…,off=…`) and `A_PORT_C13_0` (power inlet).
  - `A_SCREW_PH2_0..3`, the four rear-face screw holes in their case-bay positions.
  - The 450 has `A_CABLE_EXIT_0`, the sleeve bundle exit on the −x face. The 750 has modular sockets on the −x face: `A_PORT_MOD_ATX_0`, `A_PORT_MOD_CPU_0..1`, `A_PORT_MOD_PCIE_0..2`, `A_PORT_MOD_12V2X6_0`, `A_PORT_MOD_SATA_0..1`.
  - `A_HIT_0`.
- Looks: a powder-coated housing, a honeycomb rear vent, a fan grille with a fan behind it, a spec label (`tex_`, 80+ badge, wattage), and the switch with its I/O symbols.

### SSD: `ssd_1tb` (M.2 2280 NVMe) and the new `ssd_sata_500` (2.5" SATA)
- **M.2:** frame as today: origin at the PCB centre, connector end at −x, the screw notch at +x (0.042). `A_SCREW_PH0_0` at the notch. Looks: a controller, NAND chips, a label (`tex_`), the gold M-key fingers.
- **2.5":** origin at the body centre. The SATA data and power sockets face −x: `A_PORT_SATADATA_0` and `A_PORT_SATAPWR_0`. Four side screw holes: `A_SCREW_PH2_0..3`.

### Case: `case_brickhouse` (solid front, 1 rear fan) and `case_breeze` (mesh front, 3 front fans plus 1 rear)
**Frame as today:**
- Origin at the bottom centre. The case is 0.42 (x) by 0.45 (y) by 0.21 (z).
- −x is the front and +x the rear. The window side faces +z. The motherboard tray is at z −0.1 and faces +z. The PSU bay is bottom rear.

**Anchors:**
- `A_SOCKET_MOBO_0` is the board origin pose, about (0.068, 0.2675, −0.0885). Keep it close to today, so that `A_HOLE_*` on the board lines up with the standoffs.
- `A_STANDOFF_0..8` are the ATX standoff positions on the tray. The meta `pre=1` marks the ones pre-installed (the brass standoff mesh is a moving piece of the anchor). Pre-install about 6; the rest come in the bag.
- `A_SOCKET_PSU_0` is the PSU origin pose. `A_SOCKET_IOSHIELD_0` is the I/O opening at the rear.
- `A_SLOTCOVER_0..6` are the PCIe slot covers (moving pieces), each with its screw `A_SCREW_PH2_<n>`. They line up with the board's x16 slot. They're the same parts the GPU bracket screws go into.
- `A_PANEL_SIDE_0` is the tempered glass side panel: a moving piece with a glass mesh and frame, with thumbscrews `A_SCREW_THUMB_0..1@A_PANEL_SIDE_0` on the rear edge. Also `A_PANEL_BACK_0`, the solid right-side panel (moving piece), for later cable management.
- Front I/O: `A_BUTTON_POWER_0`, `A_BUTTON_RESET_0`, `A_LED_POWER_0`, `A_LED_HDD_0` and `A_PORT_USBA_FRONT_0..1`. Put them on the front-top edge, where they are reachable when the case lies on its side (window up): put the I/O on the **front face**, near the top.
- Case fans: `A_FAN_<n>` (rotor moving pieces), with `A_PLUG_FAN_<n>` where each loose 3/4-pin plug rests.
- Loose front-panel cable ends, near the bottom front, resting on the tray: `A_PLUG_PWRSW_0`, `A_PLUG_RESET_0`, `A_PLUG_PLED_0`, `A_PLUG_HDDLED_0`, `A_PLUG_USB3_0`, `A_PLUG_AUDIO_0`.
- `A_SOCKET_SSD25_0..1` are 2.5" mounts on the PSU shroud or the back of the tray. `A_GROMMET_0..n` are the cable cut-outs with rubber grommets. `A_HIT_<n>` are the body hitboxes (not the glass).

**Looks:**
- Folded painted steel with real thickness and bends.
- The PSU shroud with a vent and logo, cable cut-outs with grommets, the CPU cooler cut-out.
- Rear: the PCIe slot covers with vent slots, the PSU opening and the I/O opening.
- Feet with rubber, a dust filter under the PSU.
- Breeze: a mesh front panel (`mesh_black` with real perforation, or `tex_`) and white paint.
- The tempered glass panel: a dark tint, a black silkscreen border, thumbscrews.

### Retail boxes: `box_<partid>` for every catalog item, plus `box_ac_12k`
- Origin at the bottom centre, size as `PartFactory.BoxSize` (keep).
- **Box art (`tex_box_<partid>`):** render the part's own model into the art (a product shot), plus the brand, the product name, key specs, the category stripe colour (`PackageBox.CategoryColor`) and a barcode. Do this in Blender with an orthographic artwork render.
- Top flaps as moving pieces: `A_FLAP_0..3`, each with its flap mesh, closed pose.
- `A_TAPE_0` is the tape strip (moving piece; the game hides it when cut).
- Cardboard edges with real thickness, and a cardboard tag for the inside.

### Small items and plugs: `plug_<kind>`
- Each plug's origin is the contact face centre, with +z pointing back along the cable.
- Kinds: atx24, eps8, pcie8, p12v2x6, sata_data, sata_power, fan4, fan3, fp_pwrsw (a 2-pin "POWER SW" label), fp_reset, fp_pled (+/−), fp_hddled, usb3hdr, audiohdr, c13 (the wall cable), dp (DisplayPort), hdmi, eth, usba (a USB stick plug end), mod_* (modular PSU-side ends).
- Plus `screw_ph2`, `screw_ph0`, `screw_thumb`, `standoff_brass`, and `usb_stick` (the OS installer stick, labelled "BASEMENT OS 1.0 INSTALLER").
- Plus `monitor_24`: a 24" bench test monitor with a stand. `A_SCREEN_0` is the screen surface centre (forward +z = towards the viewer; size = visible area 0.53 × 0.30). It also has `A_PORT_DP_0` and `A_PORT_C13_0` at the back, and `A_BUTTON_POWER_0`.

---

