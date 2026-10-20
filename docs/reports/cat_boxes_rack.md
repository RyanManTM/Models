# Catalogue 19, helper group "rack": boxes for the rack gear, the task-01 data-centre gear, the racks and the AC

Module `Tools/Blender/rig_rack.py` (a `build_boxes.RIG_MODULES` entry), branch `claude/boxes-rack`.

## Status
**All 20 boxes are built**, each with four previews (`_0`/`_1` closed, `_2` opened, `_3` exploded) that I looked at. No box
printed a `RIG CHECK` line.
- Catalogue (`oem_rack`): srv_strata_sg840_4u, srv_strata_sr224_2u, srv_linkwave_ls4804x, srv_linkwave_ls1600x,
  srv_strata_shelf_1u, srv_strata_blank_1u, srv_strata_blank_2u, srv_strata_cma, srv_strata_kvm_1u.
- Task-01 gear (hand-written `ITEMS` in the module): server_1u, server_2u, switch_24, patch_panel_24, pdu_1u, ups_2u,
  ups_tower, pdu_0u, rack_12u_open, rack_42u, and ac_12k (it replaces the old 4-flap `box_ac_12k`).

Not done: nothing in this group. I did not touch the catalogue JSON (the coordinator writes `box`/`box_size`).

## Rebuild
```bash
~/bpyenv/bin/python ~/run_bpy.py Tools/Blender/build_boxes.py -- kind:oem_rack server_1u server_2u switch_24 \
  patch_panel_24 pdu_1u ups_2u ups_tower pdu_0u rack_12u_open rack_42u ac_12k
```
(`kind:oem_rack` also selects the hand-written items of that kind; add `--noshots` to reuse the product shots.)

## Boxes
Size is A_HIT_0 (x × y × z, m); the opening sequence gives each step's `order`, from the rig's notes.

| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_server_1u | 0.85 x 0.125 x 0.52 | 2340 | 21 | 1U carton (pe foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> rail-kit box A_INSERT_ACCBOX_0, 2 x C13 power cord A_ITEM_CORD_0 (7) -> its tuck flap A_FLAP_4, the device in its antistatic pink bag, lifted out WITH its end caps (8) -> rail screws in the box, end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9) -> slide rails A_ITEM_HW (kind=rail, look meshes) (10). |
| box_server_2u | 0.88 x 0.175 x 0.525 | 3148 | 22 | 2U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> rail-kit box A_INSERT_ACCBOX_0, 2 x C13 power cord A_ITEM_CORD_0 (7) -> its tuck flap A_FLAP_4, the device in its antistatic pink bag, lifted out WITH its end caps (8) -> rail screws and bezel keys in the box, end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9) -> slide rails A_ITEM_HW (kind=rail, look meshes) (10). |
| box_srv_strata_sr224_2u | 0.865 x 0.175 x 0.525 | 2336 | 21 | 2U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> rail-kit box A_INSERT_ACCBOX_0, 2 x C13 power cord A_ITEM_CORD_0 (7) -> its tuck flap A_FLAP_4, the device in its antistatic pink bag, lifted out WITH its end caps (8) -> rail screws in the box, end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9) -> slide rails A_ITEM_HW (kind=rail, look meshes) (10). |
| box_srv_strata_sg840_4u | 0.895 x 0.275 x 0.535 | 2340 | 21 | 4U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> rail-kit box A_INSERT_ACCBOX_0, 4 x C19 power cord A_ITEM_CORD_0 (7) -> its tuck flap A_FLAP_4, the server in its antistatic pink bag, lifted out WITH its end caps (8) -> rail screws in the box, end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9) -> slide rails A_ITEM_HW (kind=rail, look meshes) (10). |
| box_ups_2u | 0.6 x 0.16 x 0.525 | 928 | 19 | 2U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> C19 power cord A_ITEM_CORD_0, USB cable A_ITEM_CORD_1, hardware bag A_ITEM_HW_0 (7) -> the device in its clear bag, lifted out WITH its end caps (8) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x, the battery warning tag A_STICKER_0@A_ITEM_PART_0 on the bezel (blocks A_BEZEL_0: peel it, take the bezel off, connect the battery) (9). |
| box_ups_tower | 0.57 x 0.275 x 0.21 | 924 | 17 | 2U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> USB cable A_ITEM_CORD_0 (7) -> the device in its clear bag, lifted out WITH its end caps (8) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x, the battery warning tag A_STICKER_0@A_ITEM_PART_0 on the bezel (blocks A_BEZEL_0: peel it, take the bezel off, connect the battery) (9). |
| box_switch_24 | 0.555 x 0.1 x 0.29 | 908 | 18 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> C13 power cord A_ITEM_CORD_0, console cable A_ITEM_CORD_1, hardware bags A_ITEM_HW_0/A_ITEM_HW_1 (6) -> the device in its antistatic pink bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_srv_linkwave_ls4804x | 0.555 x 0.1 x 0.32 | 908 | 18 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> C13 power cord A_ITEM_CORD_0, console cable A_ITEM_CORD_1, hardware bags A_ITEM_HW_0/A_ITEM_HW_1 (6) -> the device in its antistatic pink bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_srv_linkwave_ls1600x | 0.555 x 0.1 x 0.34 | 908 | 16 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> 2 x C13 power cord A_ITEM_CORD_0, hardware bag A_ITEM_HW_0 (6) -> the device in its antistatic pink bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_srv_strata_kvm_1u | 0.855 x 0.105 x 0.525 | 908 | 18 | 1U carton (pe foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> C13 power cord A_ITEM_CORD_0, VGA + USB console cable A_ITEM_CORD_1, hardware bag A_ITEM_HW_0 (7) -> the device in its antistatic pink bag, lifted out WITH its end caps (8) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9). |
| box_pdu_1u | 0.555 x 0.09 x 0.27 | 908 | 15 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> hardware bag A_ITEM_HW_0 (6) -> the device in its clear bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_srv_strata_shelf_1u | 0.555 x 0.09 x 0.44 | 908 | 14 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bag A_ITEM_HW_0 (5) -> the device in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_patch_panel_24 | 0.52 x 0.075 x 0.185 | 1076 | 15 | Panel carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bags A_ITEM_HW_0/A_ITEM_HW_1 (5) -> the panel in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_srv_strata_blank_1u | 0.52 x 0.05 x 0.115 | 516 | 14 | Panel carton (pe foam end caps, up-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bag A_ITEM_HW_0 (5) -> the panel in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_srv_strata_blank_2u | 0.52 x 0.05 x 0.16 | 516 | 14 | Panel carton (pe foam end caps, up-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bag A_ITEM_HW_0 (5) -> the panel in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_srv_strata_cma | 0.485 x 0.07 x 0.215 | 916 | 14 | Panel carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bag A_ITEM_HW_0 (5) -> the panel in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_pdu_0u | 1.94 x 0.125 x 0.08 | 908 | 15 | 1U carton (pe foam end caps, pdu-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> hardware bag A_ITEM_HW_0 (6) -> the device in its clear bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_ac_12k | 0.78 x 0.535 x 0.7 | 1068 | 15 | AC carton (eps foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> wall trim A_ITEM_KIT_0 (look piece), hardware bag A_ITEM_HW_0 (5) -> the AC unit in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_rack_12u_open | 0.825 x 0.17 x 0.595 | 4136 | 22 | 12U open frame, flat-packed: tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers on the hardware bags (3..4) -> castor bag A_ITEM_KIT_0, cage nuts A_ITEM_HW_0 and screws A_ITEM_HW_1 (5) -> 4 posts A_ITEM_KIT_1..4, tie bar A_ITEM_KIT_5 and the top frame A_ITEM_KIT_6 (6) -> cardboard divider A_INSERT_CARD_0 (7) -> bottom frame A_ITEM_KIT_7 (8) -> assembly: the rack A_ITEM_PART_0 spawns standing in front of the carton (spawn=assembled), the KIT look pieces go (9). |
| box_rack_42u | 0.8 x 2.1664 x 1.2 | 1532 | 21 | 42U rack on a pallet: strapping bands A_STRAP_0..3 (cut) (0) -> stretch film in five sheets A_INSERT_WRAP_0..4 (front, +x, back, -x, top) (1) -> top cap A_INSERT_CARD_4, the tape A_TAPE_0 over the keys on the front door (2) -> corner posts A_INSERT_CARD_0..3, on the roof: 2 papers (3..4) and the cage-nut kit A_ITEM_HW_0, the door keys A_ITEM_HW_1 (kind=keys, for the front door lock) (3) -> the rack A_ITEM_PART_0 rolls off the pallet (4). |

## Rig designs
### `build_carton` (kinds `oem_rack` and `ac`): one design per size class, scaled
A taped regular slotted carton (`rig_products.rsc_box`), printed with `build_boxes.compose_oem`: plain kraft or white
board, the brand on every side, the product label (brand sticker, name, P/N, bar code, S/N, QTY, ESD mark) on the front
and one end, and handling marks on the big ones. The AC uses `compose` in the carton style instead (see below).
- **The device** lies in it (`A_ITEM_PART_0`, the part's own frame) in its bag:
  - `antistatic_pink`: the servers, the switches and the KVM;
  - `clear`: the UPSs, the PDUs, the passive metalwork and the AC.
- **Two foam end caps** (`A_INSERT_FOAM_0/1`, `with=A_ITEM_PART_0`) hold its ends: the part comes out with them, then
  they pull off along −x/+x. Each cap is die-cut with a pocket for the part's measured section, two recesses on the wall
  side, and a finger notch on its inner face.
- **The top layer**, between the caps on top of the bag, is shelf-packed from the part's facts (`RIGCFG`):
  - the rail-kit box `A_INSERT_ACCBOX_0` with its tuck flap `A_FLAP_4`. It holds the slide rails, the rail screws and
    (server_2u) the bezel keys;
  - the cords `A_ITEM_CORD_n` (`kind=`, `n=` = how many are coiled together);
  - the hardware bags `A_ITEM_HW_n`;
  - look-only kit pieces `A_ITEM_KIT_n`.
- **The papers** lie in a pile on the first (largest) layer item, the top one first, one `A_ITEM_DOC` per entry of the
  part's `docs`.
- **Order:** tape (0) → long flaps (1) → short flaps (2) → papers (3..) → the layer items → the part with its caps →
  the caps.
- **Orientation:** the part's longest horizontal side runs along the box x (`ORIENT`), so the flaps meet across the
  short side as on a real carton:
  - deep devices (servers, UPSs, KVM) lie front to +x;
  - wide ones (switches, PDU, shelf, patch panel, CMA) lie front to +z;
  - the blanking panels lie face up;
  - the zero-U PDU lies along x with its outlets up.
- **Size classes** (`CLASSES`); the box size comes from the measured bounds plus the class margins, in 5 mm steps:

| Class | Board | Caps | Cap end / pocket | Used by |
|---|---|---|---|---|
| 1U | 4 mm, kraft or white | black PE | 30 / 40 mm | server_1u, KVM, switches, pdu_1u, pdu_0u, shelf |
| 2U | 5 mm kraft | white EPS | 35 / 45 mm | server_2u, sr224, ups_2u, ups_tower |
| 4U | 7 mm (double wall) kraft | white EPS | 45 / 55 mm | sg840 |
| panel | 3 mm white, clear tape | black PE | 15 / 20 mm, 30 mm side walls | patch panel, blanks, CMA |
| AC | 5 mm kraft, printed | white EPS | 35 / 40 mm, 25 mm side walls | ac_12k |

- **Servers** (server_1u, server_2u, sr224, sg840): a big brown carton with end foam, the anti-static bag, a rail-kit
  box and the quick-start sheet plus the rest of the part's papers. **The rails are look meshes on `A_ITEM_HW` anchors**
  (`kind=rail,side=l|r,len=0.62,look=1`), because there is no rail model. Each one shows the collapsed outer and inner
  members, the end brackets with pins, and the release tabs; the rail kit's label is `tex_box_<id>_kit`.
  - The KVM has its slides fixed on the model, so it brings rear brackets (HW) instead of a rail kit.
  - The sg840's four C19 cords are one coil, `n=4`.
- **UPSs** (ups_2u, ups_tower): `A_ITEM_PART_0` carries `battery=disconnected`. The battery warning tag is
  `A_STICKER_0@A_ITEM_PART_0`, a yellow printed tag with a tape strip stuck on the front bezel (the part's frame:
  ups_2u (−0.052, 0.0445, 0.0334), ups_tower (0, 0.095, 0.220)). Its meta is
  `shape=rect,peel=+y,kind=warning_tag,print=BATTERY DISCONNECTED,blocks=A_BEZEL_0`. It is reachable once the UPS is out
  of the box, and it blocks the bezel, so the order is: peel the tag → take off the bezel → connect the battery
  `A_BATTERY_0`. The game moves it with the part (it is parented to the part).
- **ac_12k** (exempt from the SAME proof): the old box was the generic size with a stand-in shot of a split-type unit.
  - The new art is the carton style (`compose`): the FrostLine brand and a flexo line drawing rendered from `ac_12k.fbx`
    (the through-the-wall unit), "THROUGH-THE-WALL AIR CONDITIONER", TW-12K, the specs and handling marks.
  - Inside: the EPS end caps, the unit in a clear bag (front +z), the wall trim (look piece `A_ITEM_KIT_0`,
    `member=wall_trim`), the hardware bag `A_ITEM_HW_0`, the manual and the warranty card.

### `build_flatpack` (kind `rack_flatpack`): rack_12u_open
The open frame flat-packed in a long kraft carton, from the bottom:
- the bottom frame (with its castor plates);
- a cardboard divider `A_INSERT_CARD_0`;
- the top frame, with the four C-profile posts and the cable tie bar nested in its opening;
- on top: the castor bag, the cage-nut bag and the screw bag, with the papers on the bags.

**The mapping to the part:** the members are look pieces on `A_ITEM_KIT_n`, with `kit=rack_12u_open`,
`member=bottom_frame|top_frame|post|tie_bar|castors` and `look=1`, plus `lift`/`order`/`under` like any insert. The
assembled rack is `A_ITEM_PART_0`, standing in front of the carton (its own frame, on the floor), with meta
`kit=1,spawn=assembled` and `under=` every KIT anchor. So the game spawns the built rack there once every member is out
(the assembly step) and deletes the KIT look pieces. The opened preview hides the assembled rack; the exploded preview
shows it.

### `build_pallet` (kind `rack_pallet`): rack_42u
- **The body** is a wooden EUR pallet (1200 × 800 × 144: 3 bottom boards, 9 blocks, 3 cross boards, 5 deck boards). It
  has its own atlas `tex_box_rack_42u`: the wood grain and knots, the IPPC/EPAL stamps on the front blocks, the corner
  post and top cap print, the product label and the key tag.
- **The rack** stands on the deck (`A_ITEM_PART_0`, `bag=none`).
- **Order:**
  - 0: the strapping bands `A_STRAP_0..3` (`kind=pp_band,cut=1`): two over the top and through the pallet's fork
    openings, two round the posts, each with a metal seal.
  - 1: the stretch film in five big sheets `A_INSERT_WRAP_0..4` (front, +x, back, −x, top;
    `kind=stretch_film,peel=+y,lift=<outward>`), each `under` the bands that cross it.
  - 2: the top cap `A_INSERT_CARD_4` (a corrugated tray upside down over the roof and the post tops), and the tape
    `A_TAPE_0@A_ITEM_PART_0` over the keys.
  - 3: the corner posts `A_INSERT_CARD_0..3` (printed cardboard L angles); the papers and the cage-nut kit lying on the
    roof under the cap (parented to the part); and the door keys `A_ITEM_HW_1@A_ITEM_PART_0` (`kind=keys,look=1`, two
    keys on a ring in a clear bag), taped to the front door by the handle.
  - 4: the rack rolls off the pallet.
- The closed views show the empty wrap, because the rack is spawned by the game, not part of the rig model.

## Deviations
- **New anchor kinds** beyond the contract table: `A_ITEM_KIT_n` (look-only loose contents with no PartDef model: the
  flat-pack members, the AC wall trim), `A_STRAP_n` (bands to cut) and `A_STICKER_0@A_ITEM_PART_0` (the UPS warning tag).
  `A_INSERT_WRAP` is used for the stretch film (the contract has it for bubble wrap).
- **Anchors that carry their own look mesh** (rails, keys, kit pieces) have `look=1`, so the game can keep the mesh
  rather than spawning a bag.
- **New cord kinds:** `c19`, `usb`, `console` and `kvm`, plus a second cord anchor `A_ITEM_CORD_1`. Cords carry `n=` for
  several cords coiled together.
- **ac_12k box size** grows from the old `BoxSize` 0.68 × 0.48 × 0.62 to **0.78 × 0.535 × 0.70**: the through-the-wall
  unit is 0.70 × 0.48 × 0.64, plus its caps. The wall trim is also part of the AC model's static mesh, so the box's trim
  is a look piece the game removes at install.
- The rack_12u and rack_42u items are hand-written (`kind` rack_flatpack/rack_pallet); their art does not use the
  product shot.

## Requests for the shared code
- The Unity contract (PACKAGING.md 2.2) should add: `A_ITEM_KIT_n`, `A_STRAP_n`, `A_STICKER_n` on a part
  (`blocks=`), `A_INSERT_WRAP` with `kind=stretch_film`, `look=1`, `A_ITEM_CORD_n` for n > 0, the cord kinds
  c19/usb/console/kvm with `n=`, `A_ITEM_PART_0` with `spawn=assembled,kit=1` and `battery=disconnected`.
- `rig_products.previews` could take a fill for the closed views and a list of anchors to hide in the opened view.
  `rig_rack.previews` copies it with those two additions.
- `rig_products.add_contents` could skip anchors with `look=1`. `rig_rack.add_contents` filters them out.
- The OEM print (`compose_oem`) prints the side faces' logo very small on long, low boxes. It reads at arm's length,
  but a size relative to the face height would read better.
