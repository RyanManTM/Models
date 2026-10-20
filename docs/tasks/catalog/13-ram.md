# Catalogue 13: Memory (20)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_ram.py` (new) and optional hooks in `build_ram.py`. If you add hooks, prove that `ram_ddr5_16` and `ram_ddr4_8` re-export SAME.

**Delivers:** `docs/catalog/ram.json` and `docs/reports/cat_ram.md`.

## Rules
- **One model per stick type.** Kits are 2 sticks: `per_box: 2` in the catalogue; `ram_gb` is the size of one stick.
- **The contract** is ram_ddr5_16 / ram_ddr4_8: frame and `A_NOTCH_0` (DDR5 or DDR4 notch).
- **What may vary:** spreader height (low profile about 32 mm up to tall RGB about 44–56 mm), spreader shape and finish, colour, RGB diffuser (`rgb` tag), and a bare PCB (no spreader).
- **Labels:** each stick carries a printed spec label (capacity, speed, CL, voltage, part number).

## Desktop DDR5 kits (10)
1. Corvex "Vector" 2 × 16 GB 6000 CL30: black, no RGB.
2. Corvex "Vector RGB" 2 × 16 GB 6000: white, RGB.
3. G.Stride "Trine" RGB 2 × 24 GB 7200: silver and black.
4. G.Stride "Flare" 2 × 16 GB 6000: low profile, black.
5. Kingsland "Ferox" 2 × 32 GB 5600: black, no RGB.
6. Kingsland "Ferox RGB" 2 × 16 GB 6000: white.
7. Crux Pro 2 × 48 GB 5600: black, no RGB.
8. Crux 2 × 8 GB 5600: bare green PCB, no spreader.
9. TeamForge "Delta RGB" 2 × 16 GB 6400: white.
10. Volt RGB 2 × 32 GB 6400: black.

## Desktop DDR4 kits (6)
1. Corvex "Vector LPX" 2 × 8 GB 3200: black, low profile.
2. Corvex "Vector RGB Pro" 2 × 16 GB 3600.
3. G.Stride "Riptide" 2 × 8 GB 3200: red.
4. Kingsland "Ferox" 2 × 16 GB 3200: black.
5. Crux "Tracer" 2 × 32 GB 3200.
6. TeamForge "Vulcan" 2 × 16 GB 3600: red.

## Server RDIMMs (4, new contract)
Registered ECC: the RCD chip in the middle, 10 DRAM packages per side, no spreader, a thermal sensor and an SPD hub. **DDR5 RDIMMs have their own key notch** (they don't fit desktop slots), so document the notch in a new contract.
1. Kingsland DDR5-4800 RDIMM 32 GB
2. Sorin DDR5-4800 RDIMM 64 GB
3. Crux DDR5-5600 RDIMM 128 GB (taller, dual-rank 3DS)
4. Kingsland DDR4-3200 RDIMM 32 GB
