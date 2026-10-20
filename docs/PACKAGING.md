# Packaging models: contract and contents

The retail boxes (`box_<partid>`), shipping cartons and packaging bits are rigs: solid models whose removable pieces and content places are anchors the game reads. This is that contract, and what really comes in each box.

## 2. The model contract (Blender ↔ Unity)

All models go through the existing pipeline: `dct_common.py`, flat `@` pieces, anchors with size and meta, tags.

### 2.1 New material tags
The Unity side adds these to `ModelLibrary`'s tag table; Blender uses them.

| Tag | Look |
|---|---|
| `clear_plastic` | Clear PET (clamshells, caps, guards): transparent, glossy, slight blue-grey tint |
| `smoke_plastic` | Smoked clear plastic (some clamshells, lids) |
| `antistatic_pink` | Translucent pink polyethylene bag, slightly crinkly, glossy |
| `antistatic_silver` | Metallised shielding bag: dark grey translucent, semi-metallic |
| `bag_clear` | Clear LDPE bag (case bag, screw bags): very transparent, glossy |
| `bubble_wrap` | Clear with bubble highlights (an optional `tex_bubble` normal map is fine) |
| `eps_foam` | White expanded polystyrene, matte, slightly grainy |
| `pe_foam` | Soft black or charcoal PE foam (GPU cradles). The existing `foam` tag is fine too. |
| `pulp` | Grey-beige moulded paper pulp, matte, rough |
| `kraft_paper` | Brown crumpled packing paper, matte |
| `paper_white` | Plain white paper (paper edges, inner pages) |
| `tape_brown` | Brown packing tape: translucent, glossy |
| `tape_clear` | Clear packing tape |
| `film_clear` | Protective film: clear, glossy, faint haze |
| `seal_clear` | Round or rectangular clear seal stickers (with a printed `tex_` variant) |
| `fabric_black` | Non-woven black fabric (PSU cloth bag, case dust bag) |
| `velcro_black` | Black velcro strap |
| `doc_cover`, `doc_back` | **Runtime** materials: the game puts the generated cover and back page here (UV 0..1 over the face) |

### 2.2 Packaging rigs (anchor kinds read by the game)
Every packaging model (shipping cartons, retail boxes) is a **rig**:
- a solid model, origin at the bottom centre, front at +z, closed pose;
- pieces that come off are anchors with meta;
- places where content sits are anchors with meta.

The game turns anchors into interactive steps. **`order=<n>`** gives the layer: a step is reachable once every *removable* piece with a lower order that **covers** it is open or removed. Cover is explicit with `under=<anchor,anchor,...>`. If `under` is missing, it means everything with a lower order.

| Anchor | Meaning | Meta |
|---|---|---|
| `A_HIT_<n>` | Hitbox of the closed box (as today) | |
| `A_TAPE_<n>` | A packing-tape segment. Its mesh is built by **code** as a peel strip lying in the anchor's XY plane, facing +Z, size (w, len, t). Segments with the same `strip=` chain into one continuous peel, in `seg` order. | `strip=<k>,seg=<i>,peel=<+y|-y|+x|-x>` (the direction you pull along the segment), `order=0` |
| `A_SEAL_<n>` | Seal sticker (round or rect), code-built peel mesh, size (w, h, t) | `shape=round\|rect,peel=<dir>,order=0,print=<text>` |
| `A_FLAP_<n>` | Flap (as today) | `hinge=x\|z,open=<deg>,order=<n>,tuck=1` (tuck = a tuck flap: pull it out first) |
| `A_LID_<n>` | A lift-off lid, or a hinged lid when `hinge` is given | `lift=+y,dist=<m>` or `hinge=<axis>,open=<deg>`, `order` |
| `A_SLEEVE_<n>` | Printed outer sleeve that slides off the inner box | `slide=<+x\|-x>,dist=<m>,order` |
| `A_INSERT_<KIND>_<n>` | A removable insert. KIND is FOAM, CARD (cardboard tray or divider), PULP, CLAM (clamshell base), BLISTER, ACCBOX (accessory box) or WRAP (bubble wrap). | `lift=<dir>,order,label=<text>,parent=<anchor>`; `with=<anchor>` means it travels with that anchor when that one is lifted out (foam end caps on the case) |
| `A_CLAMLID_<n>` | Hinged half of a clamshell or blister | `hinge=<axis>,open=<deg>,parent=A_INSERT_CLAM_<n>,order` |
| `A_ITEM_PART_<n>` | Where the part sits: the **part model's own frame**, at its packed pose. The game spawns the real part here; `n` counts PerBox. | `bag=antistatic_pink\|antistatic_silver\|clear\|fabric\|none,guard=1` (RAM guard on), `parent`, `order` |
| `A_ITEM_ACC_<n>` | An accessory from `PartDef.InBox` | `id=<partdef id>,bag=<…>,parent,order` |
| `A_ITEM_DOC_<n>` | A paper | `doc=guide\|manual\|warranty\|sticker\|driver\|safety\|slip,order,parent`; size = (w, h, t) of the folded paper |
| `A_ITEM_CORD_0` | Coiled cord or cable bundle with a twist tie (PSU power cord, DP cable, SATA cables) | `kind=c13\|dp\|sata,tie=twist\|velcro` |
| `A_ITEM_HW_<n>` | Small hardware bag (screws, cable ties) | `label=<text>` |
| `A_ITEM_POUCH_0` | Modular cable pouch (psu_750) | |
| `A_SPACE_0` | Shipping cartons: the inner volume the game packs boxes and filler into | size = inner dims |
| `A_LABEL_0` | Shipping cartons: where the shipping label goes (the code prints it) | size |

**Pieces:**
- Pieces belonging to a removable anchor are `name@A_<ANCHOR>#tag`, modelled at the closed or packed pose with the pivot at the anchor.
- Flaps and lids hinge at their anchor.
- **Bags are not in the rig model.** The code builds them around the part from its bounds (§2.4).
- **The part is not in the rig model.** The code spawns it at `A_ITEM_PART_n`.
- Papers are separate models (§2.3) that the code places at `A_ITEM_DOC_n`.

**Every removable piece must look right on its own**, because it becomes a loose object: inside faces, real thickness, no open edges where it was hidden.

### 2.3 Separate models (Blender A)
All have their origin at the bottom centre unless stated, with `A_HIT_0`.

**Shipping cartons:** `ship_carton_s`, `ship_carton_m`, `ship_carton_l`
- Plain brown corrugated cardboard (a `tex_ship_carton` with a corrugated edge, print marks, "THIS SIDE UP", the recycling logo and a fragile stamp). Two long top flaps, two short ones, and a taped bottom.
- Anchors:
  - `A_FLAP_0..3`
  - `A_TAPE_*`: the top strip and both end tabs, as one `strip=0`
  - bottom tape `A_TAPE_*`, `strip=1`, peelable after break-down
  - `A_SPACE_0`, `A_LABEL_0`, `A_HIT_0`
- `ship_carton_<s|m|l>_flat`: the broken-down flat carton (both halves folded flat, its creases visible). Origin at the bottom centre of the flat panel.

**Filler:**
- `filler_paper_0..2`: three crumpled kraft paper wads (different shapes, about 0.12–0.2 m).
- `air_pillow_strip`: a strip of 4 inflated pillows, each pillow its own `A_PILLOW_<n>` piece. Plus `air_pillow_flat`, the look of one popped pillow, which the code swaps in.
- `bubble_wrap_sheet`: a flat sheet, about 0.4 × 0.3, with modelled bubbles on a grid. The code finds each bubble from `A_BUBBLE_<n>` anchors, or from a grid meta `grid=cols,rows,pitch` on `A_HIT_0`.
- `bubble_wrap_wrapped`: a variant wrapped loosely around a box shape, scaled by code.

**Papers** (code applies `doc_cover`/`doc_back`):
- `doc_leaflet`: a tri-fold leaflet, folded, with a slight spring.
- `doc_booklet`: a stapled booklet, about 3 mm thick, with a slightly curled cover.
- `doc_card`: a single card.
- `doc_sticker_sheet`: a backing card with 1–2 badge stickers as `A_STICKER_<n>`.
- `doc_slip`: an A4 folded in three.
- Sizes are nominal; the code scales them to `A_ITEM_DOC` size.

**Crumpled trash looks:** `crumple_tape`, `crumple_film`, `crumple_paper`, `crumple_bag`
- Small balls of different shapes; the code tints them.

**Small bits:**
- `twist_tie`: a coiled tie in its closed pose, plus `twist_tie_open`.
- `velcro_strap`.
- `hw_bag`: a small zip bag with a printed label area, and a `bag_clear` mesh of screws inside.
- `cable_pouch`: a black zip pouch.

**Tools and furniture:**
- `box_cutter`: a yellow utility knife with the blade out, `A_GRIP_0`, `A_BLADE_0`.
- `unbox_table`: a folding table (white plastic top or plywood, steel legs). Its top surface anchor is `A_TOP_0`.
- `wheelie_bin`:
  - a 240 L green or grey wheelie bin;
  - its lid is a moving piece `A_LID_0`, `hinge=x,open=-110`;
  - `A_MOUTH_0` is the opening (size = the trigger volume);
  - `A_LINER_0` is the liner rim pose;
  - `A_HANDLE_0`.
- `bin_bag_full`: a tied black bag, about 0.5 × 0.7 × 0.4, with `A_KNOT_0`.
- `bin_bag_roll`: a roll of bags.
- `paperwork_tray`: a black mesh desk letter tray.

### 2.4 Code-built pieces (Unity)
- **Peel strips** (tape, films, seals, sticker backings) are a subdivided grid mesh, at least 24 segments along the peel. The code deforms them (§4).
- **Bags around parts:**
  - an open-ended flat bag from the part's bounds plus a margin;
  - a crinkle normal (a ProcTex noise);
  - the tag colour from `bag=`;
  - a printed warning (an "ESD" symbol and text for anti-static bags);
  - a fold-over flap with a sticker seal.
  - When the part slides out, the bag collapses flat (scale and noise) and becomes trash.
- **Caps and guards on parts** come from Blender B (§2.5), or a code fallback (simple clear boxes).
- **Films on parts:**
  - the code builds the peel grid from the target's anchor or mesh bounds;
  - glass film: the `A_PANEL_SIDE_0` glass mesh bounds, one film per side;
  - fan hub film: a disc at `A_FAN_n` over the hub sticker, radius from the sticker mesh;
  - backplate film: the GPU bounds' back face.

### 2.5 Retail packaging models (Blender B): `box_<partid>` rebuilt as rigs, and part caps
- **Keep `PartFactory.BoxSize` per box** (the shelf packing uses it). If a size really has to change for realism, say so in the report, and the Unity agent updates `BoxSize`.
- Keep the printed box art (`tex_box_<partid>`, the product shot) and improve it where it helps.
- See §3 for each product's packaging. Model what really comes in the box.
- **Part caps** (separate small models, placed by code on the part):

| Model | What | Origin |
|---|---|---|
| `cap_pcie16` | Clear U-channel over the GPU edge fingers | The GPU frame origin's edge centre. The x16 edge is about 89 mm long. Check the GPU model's `A_HIT_2`. |
| `cap_dp` | Black rubber DisplayPort plug cap with a pull tab | The port anchor's face, oriented like a plug (+z out) |
| `cap_hdmi` | Black rubber HDMI cap with a pull tab | As `cap_dp` |
| `guard_ram_ddr5` | Clear clip over the DDR5 gold fingers, with a notch matching `A_NOTCH_0` | The RAM edge |
| `guard_ram_ddr4` | As `guard_ram_ddr5`, for DDR4 | The RAM edge |
| `cap_paste` | Clear dome over the stock cooler's pre-applied paste | At `A_PASTE_PRE_0` |
| `sticker_psu_voltage` | Yellow warning sticker over the PSU switch | At `A_SWITCH_PSU_0` (peel mesh by code; this model is only the printed look, optional) |

- Report every cap's exact placement relative to the part anchors in your report (it's needed for the Unity side).
- **If a part model needs a new anchor** for a cap or film (for example `A_EDGE_PCIE_0` on the GPU, or `A_EDGE_0` on RAM), add **only the anchor** to that part's build script, re-export, and list it. Do not change anything else on finished part models.

---

## 3. Per product packaging (what's really in the box)

Each retail box below says how it opens (top to bottom, in `order`) and lists its papers. Sizes are `BoxSize`.

- **CPU** (`cpu_arc5`, `cpu_arc7`, `cpu_tiron5`): 0.11 × 0.07 × 0.11, printed cube.
  1. Two round clear **seal stickers** over the tuck flap.
  2. Open the **tuck top flap**.
  3. Slide out the **cardboard sleeve tray**.
  4. On it, a **black plastic clamshell** with the CPU in a moulded recess (`A_INSERT_CLAM_0` + `A_CLAMLID_0`, snaps open with a click).
  5. Take the **CPU**.
  - Beside the tray: the **quick install guide** (a leaflet), the **warranty card** and the **case badge sticker** sheet.
- **Motherboard** (`mb_ridge_b5`, `mb_ridge_z4`): 0.32 × 0.07 × 0.27.
  1. Two rect **seals** on the sides.
  2. A **hinged lid**, flip-top along the back edge.
  3. Inside: the board in an **anti-static pink bag** (b5 silver, z4 pink, for variety) lying on a **white foam pad** on a **cardboard divider tray**.
  4. Lift the board in its bag, then slide the board out of the bag.
  5. Under the tray, the accessory compartment:
     - the **I/O shield** in a thin clear bag (`A_ITEM_ACC_0`, id io_ridge_*);
     - **2 SATA data cables** coiled with a twist tie (`A_ITEM_CORD_0`, kind=sata);
     - an **M.2 screw bag** (`A_ITEM_HW_0`);
     - the **user manual** (a booklet), a **quick install poster** (a leaflet), the **warranty card** and a **case badge sticker**.
  - Fittings on the board: the PnP cap (exists), the M.2 film (exists), and the I/O cover and chipset films (new).
- **RAM** (`ram_ddr5_16`, `ram_ddr4_8`; 2 sticks): 0.16 × 0.03 × 0.12.
  1. A thin printed box: open the **tuck end flap**.
  2. Slide out the **clear blister tray** (`A_INSERT_BLISTER_0` + `A_CLAMLID_0`) with two moulded cavities.
  3. Peel the **seal sticker** on the blister.
  4. Open the blister.
  5. Each stick carries its **gold-finger guard** and a **spreader film**.
  - Papers: a small **installation card** (slots and XMP/EXPO).
- **GPU** (`gpu_rx66`, `gpu_rx88`): 0.36 × 0.09 × 0.17.
  1. The printed **outer sleeve** slides off (along x).
  2. A plain **black inner box** with a **lift-off lid** and a ribbon pull tab.
  3. Inside, a **black PE foam cradle** (die-cut) holding the card in an **anti-static silver bag**.
  4. Lift the card in its bag, then slide it out.
  5. The card has:
     - the **PCIe cap**;
     - **DP/HDMI dust caps**;
     - **backplate and shroud films**;
     - **fan hub films**.
  - Under the foam: the **quick install guide** (a leaflet), the **driver note** (a card) and a **case badge sticker**.
- **SSD M.2** (`ssd_1tb`): 0.11 × 0.025 × 0.08.
  1. A **seal sticker**, then a **tuck flap**.
  2. A **clear blister tray** with the drive.
  3. A tiny **installation card** and a **warranty card**.
- **SSD SATA** (`ssd_sata_500`):
  1. A **seal sticker**, then a **tuck flap**.
  2. A **black plastic tray** with the drive in a **clear bag**.
  3. The drive has a **label film**.
  4. An **installation card**.
- **PSU** (`psu_450`, `psu_750`): 0.21 × 0.12 × 0.18.
  1. **Top flaps** (taped retail box).
  2. Two **moulded pulp end caps** (or white EPS on the 750).
  3. The PSU in a **clear bag** (450) or a **black fabric drawstring bag** (750).
  4. Beside it:
     - the **power cord** (C13) coiled with a **twist tie**;
     - the 750 adds a **modular cable pouch**, whose cables are bundled with **velcro straps**;
     - a **screw bag** (4 × 6-32);
     - the **user manual** (a booklet) and a **safety sheet**.
  - On the PSU: the **voltage warning sticker** over the switch.
- **Cooler, stock** (`cooler_stock`): 0.12 × 0.09 × 0.12.
  1. **Tuck flap**.
  2. A **clear clamshell** holding the cooler, fan up.
  3. The cooler has a **paste cap** and a **fan hub film**.
  4. A **leaflet**.
- **Cooler, tower** (`cooler_tower`): 0.16 × 0.20 × 0.14.
  1. **Top flaps**.
  2. The heatsink sits in a **die-cut white EPS foam** pair (top and bottom).
  3. The fan is clipped on; the cooler has a **fan hub film**, a **top cover film** and the **base film** (exists).
  4. An **accessory box** (`A_INSERT_ACCBOX_0`) holds:
     - a **mounting kit bag** (`A_ITEM_HW_0`, "MOUNTING KIT V5/L17");
     - a **paste syringe** (the existing paste item, if that fits the game; otherwise a look only);
     - the **manual** (a booklet).
- **Case** (`case_brickhouse`, `case_breeze`): 0.52 × 0.56 × 0.30, printed brown corrugated carton. It ships alone, with a shipping label.
  1. **Tape** and **top flaps**.
  2. The top **EPS foam end caps** are visible. The case stands in the box with two EPS caps: front and rear (`A_INSERT_FOAM_0/1`, `with=A_ITEM_PART_0`).
  3. The case is in a **clear bag** (`bag=clear`).
  4. Lift the case out by the foam; it stands on the mat.
  5. Remove the two caps.
  6. Pull the bag off.
  7. The case lies down on the mat (the existing `PlacePc` pose).
  - **Inside the case**, behind the glass: an **accessory box** (small white box) holding:
    - the **standoff bag** (`InBox`);
    - a **screw bag** and **cable ties** (`A_ITEM_HW`);
    - the **manual**.
  - The **glass panel films** (both sides) and the front panel film.
  - Model the accessory box as part of the case rig (an anchor inside the case footprint) and let the code re-home it inside the case after the case is out. Or simpler: the box sits in the top foam's cut-out. Pick the realistic one you can do well, and say which in the report.
- **USB installer** (`usb_installer`): blister card (exists).
  - Peel the **card back** (the existing seal becomes a peel) or crush the blister.
  - The stick, then a **quick start card**.
- **DisplayPort cable** (`cable_dp`) and **fan splitter** (`fan_splitter`): each a **clear zip bag** with a printed header card and the item coiled with a **twist tie**.
  - Model them as small rigs `box_cable_dp` and `box_fan_splitter`, using the bag as the box.
- **AC unit:** unchanged. It is installed straight from its box at the wall. Its empty box is trash after install, and nothing vanishes: the box stays at the mount.

---

