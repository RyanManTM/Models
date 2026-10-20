# Catalogue 18: Server add-ins and gear (14)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_server.py` (new) and optional hooks in `build_datacenter.py`. If you add hooks, prove that every existing data-centre model re-exports SAME, and re-run `datacenter_fit.py`.

**Rack gear** uses the rack-device frame of `docs/reports/datacentre.md`: origin at the bottom of the U space on the front mounting plane, +Z out of the front. Run the fit check for each new rack device.

**Delivers:** `docs/catalog/server.json` and `docs/reports/cat_server.md`.

## PCIe add-in cards (6, new contract)
- **Frame:** as the GPU contract (the PCIe edge at the origin, the bracket at x +0.095). Document the edge length per card (x4, x8 or x16).
- **Brackets:** each card ships with a full-height bracket fitted, plus a separate low-profile bracket model (`<id>_lpbracket`).
- **Port anchors:** `A_PORT_ETH_n` / `A_PORT_SFP_n` / `A_PORT_QSFP_n` / `A_PORT_SAS_n`, each with its LEDs.

1. Linkwave dual-port 1 GbE RJ45 (x4)
2. Linkwave X710-style dual 10 GbE SFP+ (x8)
3. Melnet ConnectX-6-style dual 25 GbE SFP28 (x8)
4. Melnet 100 GbE dual QSFP28 (x16)
5. Broadline 9500-style 16-port HBA (x8): two internal SFF-8654 connectors.
6. Broadline RAID card (x8): cache module plus a supercap pack on a cable.

## Rack gear (8)
1. **Strata 4U GPU server:** 8 double-width GPU bays, 4 × CRPS PSUs, a fan wall. Moving pieces: the top lid, the GPU sleds and the PSUs.
2. **Strata 2U storage server:** 24 × 2.5" front bays.
3. **Linkwave 48-port 1 GbE switch** with 4 × SFP+.
4. **Linkwave 16-port 10 GbE SFP+ aggregation switch.**
5. **1U cantilever rack shelf.**
6. **Blanking panels**, 1U and 2U (two ids).
7. **Cable management arm**, for the servers' rails. Its frame matches the rails' rear ends.
8. **1U KVM console drawer:** a slide-out LCD and keyboard. The lid opens as a moving piece; `A_SCREEN_0`.
