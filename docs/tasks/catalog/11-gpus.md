# Catalogue 11: Graphics cards (15)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_gpus.py` (new) and optional hooks in `build_gpu.py`. If you add hooks, prove that `gpu_rx66`, `gpu_rx77` and `gpu_rx88` re-export SAME.

**Delivers:** `docs/catalog/gpus.json` and `docs/reports/cat_gpus.md`.

## The contract (desktop cards)
The gpu_rx66 / rx77 / rx88 contract (docs/MODEL_PIPELINE.md §2 and their reports):
- The PCIe edge is at the origin and the full-height bracket at x +0.095. The cooler faces −y.
- `A_PORT_DP_0..2` and `A_PORT_HDMI_0` keep their bracket positions. Cards with a different output mix: say so in the report.
- Bracket screws, `A_HIT_1` (bracket) and `A_HIT_2` (the PCIe edge).
- `A_FAN_n` with hub stickers, `A_FILM_BACKPLATE_0` and `A_FILM_SHROUD_0`.

**What may vary:** length (along −x), height (+z), thickness (−y: 2, 2.5, 3 or 3.5 slots), fan count, colour and RGB.

**Power ports:**
- A 12V-2x6 port is `A_PORT_12V2X6_0`, as on rx88.
- PCIe 8-pin ports are `A_PORT_PCIE8_0..1`, as on rx77.
- The game supports one 12V-2x6, or one or two 8-pin ports. A card that really needs three 8-pins gets two, with a note.

## Desktop (13)
Every partner card has its own shroud language, matching its brand's look. Real numbering is fine (see the brand rules).
1. Verdia VTX 5060 8 GB: Zenith, compact dual fan, black.
2. Verdia VTX 5060 Ti 16 GB: Aegis, dual fan, white.
3. Verdia VTX 5070 12 GB: Mako, triple fan, black and silver.
4. Verdia VTX 5070 Ti 16 GB: Kestrel, triple fan, white with RGB.
5. Verdia VTX 5080 16 GB: Aegis flagship line, 3.5 slots, big RGB light bar.
6. Verdia VTX 5090 32 GB: the Verdia reference design, a 2-slot dual flow-through with a silver frame.
7. Verdia VTX 5090 32 GB: Mako's top line, a huge 4-slot card with RGB.
8. Verdia VTX 4060 8 GB low profile: Kestrel, half-height with 2 small fans. It ships with a full-height bracket fitted (keep the contract); mention its half-height bracket in the report.
9. Voltra RX 7600 8 GB: Zenith, dual fan, plain black, no RGB.
10. Voltra RX 9060 XT 16 GB: Zenith, dual fan, white.
11. Voltra RX 9070 XT 16 GB: Zenith's top line, triple fan, RGB.
12. Voltra RX 7900 XTX 24 GB: the Voltra reference design, triple fan, two 8-pin.
13. Tiron Lumen B580 12 GB: the Tiron reference design, dual fan, matte black and silver.

## Data-centre accelerators (2, new contract)
1. **Verdia T100 80 GB PCIe:** an H100-PCIe-style passive dual-slot card, no fans, gold and black, a 12V-2x6 port at the rear end. **No display outputs.**
2. **Voltra Instinct MI210-style 64 GB:** passive dual-slot.

Same frame as the desktop cards. The report notes that they have no `A_PORT_DP`/`A_PORT_HDMI` and no `A_FAN_n`, and that they need server airflow.
