# Catalogue 19: Retail and OEM boxes for the catalogue

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first, plus `docs/PACKAGING.md`.

**Run this after the family branches (10–18) are merged into `main`.** It boxes every part those families made.

**You own** `Tools/Blender/build_boxes.py`, `rig_common.py` and `rig_products.py`. Add a catalogue-driven path that reads `docs/catalog/*.json` to make the box items, rather than hand-writing 100 entries.

**Proof:** the existing 24 rigs (box_cpu_*, box_gpu_*, box_mb_*, box_ram_*, box_ssd_*, box_psu_*, box_cooler_*, box_case_*, box_usb_installer, box_cable_dp, box_fan_splitter) must re-export SAME with `extras_compare.py`. Don't commit those re-exports.

## Every box is a full unboxing rig
No simplified boxes. The game's unboxing is real life step by step, and nothing vanishes, so every box needs all of this:
- **The seal:** tape `A_TAPE_*` (with `strip`/`seg`) or seal stickers `A_SEAL_*`.
- **Every way in:** flaps, tuck lids, hinged or lift-off lids, sleeves.
- **Every insert** as its own removable piece, with real inside faces: foam cradles, pulp trays, cardboard dividers, clamshells, blisters, accessory boxes.
- **Content anchors** for the part (`A_ITEM_PART_n`, with `bag=`), its accessories (`A_ITEM_ACC`), cables and cords (`A_ITEM_CORD`), screw bags (`A_ITEM_HW`), pouches, and **one `A_ITEM_DOC_n` for every paper** in the part's `"docs"` list.
- **Order and covering:** each piece has its `order=` and `under=` so the game knows what covers what.

Read the family's `"unbox"` and `"docs"` entries in its JSON: the part's films and caps are on the part, the box holds the rest. **Prove** each new rig opens in a sensible order by rendering an opened preview and an exploded preview.

## For every consumer part (category CPU, GPU, Motherboard, RAM, Storage, PSU, Cooler, Case, and fans)
- **Make `box_<id>`** following the existing rig of the same kind (docs/PACKAGING.md §3): same opening sequence, inserts and papers.
  - CPU box: seals, tuck lid, tray, clamshell.
  - GPU box: sleeve, inner box, foam.
  - RAM box: tuck box with blister.
  - … and so on for each kind.
- **Printed art** is rendered from the part's own FBX, in the brand's style (the brand table in the catalogue README): colours, logo treatment, product shot, key specs, barcode.
- **Size:** the box is sized to its part. Put the size in the catalogue as `"box": "box_<id>"` and `"box_size": [x, y, z]`, so the game's `BoxSize` can use it.
- **New kinds need new rigs, designed in the same style:**
  - **AIO box:** the radiator and pump in a moulded pulp tray, tubes coiled, fans in a separate compartment.
  - **3.5" HDD:** a retail box or a brown bulk box with an anti-static bag.
  - **Fan packs:** a window box.
  - **SFX PSU:** a box with an SFX-to-ATX bracket.

## For server parts (CPUs, RDIMMs, CRPS PSUs, U.2, NICs, HBA, server boards, accelerators, rack gear)
- **Plain OEM packaging, but still a full rig:** white or brown boxes with a printed label (part number, barcode, a "Strata"/brand sticker), tape, inner foam, an anti-static bag, and a quick-start sheet plus a warranty card as papers.
  - One rig design per size class (small, card, board, PSU, 1U, 2U, 4U), scaled.
  - Server CPUs come in a clamshell tray, the carrier visible.

## The earlier gear that has no box yet
- **Full rigs for the data-centre models from task 01:** server_1u, server_2u, switch_24, patch_panel_24, ups_2u, ups_tower, pdu_0u and pdu_1u.
  - Servers come in a big brown carton with end foam, an anti-static bag, a rail-kit box and a quick-start sheet.
  - UPSs come with their battery shipped disconnected, plus a warning tag.
- **rack_12u_open:** flat-packed in a long carton, with a hardware bag of cage nuts and screws.
- **rack_42u:** on a wooden pallet. It is wrapped in stretch film (peelable, in big sheets) with cardboard corner posts and strapping bands (cut or pull), and the keys are taped to the door.
- **Rebuild `box_ac_12k` as a full rig.** It is exempt from the SAME proof. It still has the old 4-flap design and art showing a split-type unit; make the art match the through-the-wall `ac_12k`. Inside: EPS end caps, the unit in a bag, the wall trim and a hardware bag, the manual, the warranty card.

## Data and report
- Update each family's `docs/catalog/<family>.json` with `box` and `box_size`. Only add those two keys.
- Write the report `docs/reports/cat_boxes.md`.
