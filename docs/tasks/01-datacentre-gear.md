# Task 01: Data-centre gear

Read `docs/tasks/README.md` first: setup, rules, branches and the report.

Write a new script `Tools/Blender/build_datacenter.py`, plus `datacenter_*.py` helpers if you want. It takes `-- [ids] [--nopreview]`.
- Report: `docs/reports/datacentre.md`.
- Similar existing scripts: `build_psu.py` and `build_case.py` (sheet-metal boxes with ports).
- Budgets: servers and switches under about 25k triangles, racks under about 40k.

## Shared frame for rack devices
- Origin = the centre of the front mounting plane, at the bottom of the device's U space, so it installs directly at a rack's `A_RACKU_n`.
- +Z points out of the front, +Y up; the chassis extends towards −Z.
- Width 19" (482.6 mm across the ears, about 440 mm body). 1U = 44.45 mm.

## Models, in priority order
1. **`ac_12k`**: the "FrostLine 12,000 BTU Wall AC" the game already sells. It is a through-the-wall unit that slides into a wall sleeve with a 0.66 × 0.46 m opening.
   - **Frame (the game's install pose):** origin at the centre of the unit's width and height, +Z into the room, the wall face at z = −0.10.
   - **Body:** the visible body is 0.62 W × 0.40 H, with the front fascia plane at about z = 0.227. The chassis continues back through the sleeve to about z = −0.40, hidden in the wall.
   - **Front:**
     - an intake grille with angled slats in the upper right;
     - an outlet with a motorised louver as a moving piece `A_LOUVER_0` (`hinge=x`) at about (0.06, −0.135, 0.234);
     - a control strip on the left with a display `A_SCREEN_0` (0.074 × 0.042, at about (−0.24, 0.10, 0.233)), a mode LED `A_LED_MODE_0` (tag `led_blue`) and three buttons `A_BUTTON_0..2` below it;
     - a "FrostLine" brand plate at the top right.
   - Side vents, and a power cord exit `A_CORD_0` at the lower left back.
   - Off-white plastic. Add `A_HIT_*` boxes.
2. **`server_1u`** and **`server_2u`**: 19" rack servers (1U 43.6 mm / 2U 87.3 mm high, about 0.70 m deep).
   - **Ears** with captive thumbscrews.
   - **Front:**
     - hot-swap drive trays as moving pieces `A_BAY_n` (`pull=+z`): 8 × 2.5" on the 1U, 12 × 3.5" on the 2U;
     - `A_BUTTON_POWER_0`, an ID button, status LEDs `A_LED_<NAME>_0` with `led_*` tags, USB;
     - a removable front bezel `A_BEZEL_0` on the 2U.
   - **Rear:**
     - two hot-swap PSUs `A_PSU_0/1` (`pull=-z`), each with a handle and a C14 inlet `A_PORT_C14_n`;
     - 4 × RJ45 `A_PORT_ETH_n`, an IPMI port, VGA, USB, PCIe slot covers.
   - **Top cover** as a moving piece `A_LID_0` (`slide=-z`), with a believable interior under it (players will open it later): board, 2 CPU heatsinks, 16 DIMMs, a fan wall with `A_FAN_n` rotors, an air shroud.
   - Slide rails `A_RAIL_L_0` and `A_RAIL_R_0`.
3. **`rack_42u`**: a 19" 42U enclosed rack, 600 W × 1070 D × 2000 H mm, black powder coat.
   - Moving pieces: a perforated front door `A_DOOR_FRONT_0` (`hinge=y,open=-110`), split rear doors `A_DOOR_REAR_0/1`, and removable side panels `A_PANEL_SIDE_0/1`.
   - Four vertical mounting rails with square cage-nut holes at the real EIA-310 spacing, and printed U numbers.
   - Casters and levelling feet, top cable-entry brushes.
   - Anchors:
     - `A_RACKU_0..41`: U1 at the bottom, each at the centre of that U's front mounting plane, +Z out of the front, size = 0.4826 × 0.04445 × the usable depth;
     - `A_PDU_0/1`: zero-U PDU positions at the rear;
     - `A_HIT_*`.
4. **`rack_12u_open`**: a 12U open-frame 4-post rack on castors, for the basement stage. Same `A_RACKU` convention.
5. **`switch_24`**: a 1U 24-port gigabit switch with 4 SFP+ ports.
   - `A_PORT_ETH_0..23`, each with link/activity LEDs, and `A_PORT_SFP_0..3`.
   - A console port, a rear `A_PORT_C14_0`, ears.
6. **`patch_panel_24`**: a 1U Cat6 keystone panel with a numbered label strip and a rear cable bar. Front `A_PORT_ETH_0..23`; rear `A_PUNCH_n`.
7. **`ups_2u`** and **`ups_tower`**:
   - **`ups_2u`:** a rack UPS with a front LCD `A_SCREEN_0` and buttons, a removable bezel `A_BEZEL_0` over the battery tray `A_BATTERY_0`, rear outlets `A_PORT_C13_0..7`, a C20 or C14 inlet, and ears.
   - **`ups_tower`:** a 1500 VA tower for the basement.
8. **`pdu_0u`** and **`pdu_1u`**:
   - **`pdu_0u`:** a vertical PDU with 24 × C13 and 4 × C19 outlets (`A_PORT_C13_n`, `A_PORT_C19_n`), a breaker and a cord.
   - **`pdu_1u`:** horizontal, 8 × C13 and a lit switch.
