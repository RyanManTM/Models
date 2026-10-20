# Cloud tasks

Three model-building tasks run in parallel, each in its own cloud session on its own branch:

| Task | Brief |
|---|---|
| Data-centre gear: racks, rack servers, switch, patch panel, UPS, PDU, wall AC | `01-datacentre-gear.md` |
| Small parts: cable coils, modular cable bundle, paste syringe, standoff bag, fan connectors | `02-small-parts.md` |
| New parts to buy: CPU, GPU, motherboard, case, each with its retail box | `03-new-parts.md` |

To start one, give a cloud session on this repository the prompt *"Do the task in docs/tasks/<file>."*

## Rules for every task
**About this repo**
- This repo holds only the 3D models of the game **Data Centre Tycoon**, a Unity 6 URP first-person PC-building and data-centre sim that starts in Mom's basement. The game code is private and not here.
- Every model comes from a Python script run headless in Blender 5.0.x (`Tools/Blender`, shared library `dct_common.py`).
- A script exports:
  - `Assets/Resources/Models/<id>.fbx` and its textures;
  - previews `Logs/ModelPreviews/<id>_<n>.png`;
  - an anchor report.
- **What the game reads:**
  - mesh names `name#tag` (the material tag);
  - anchors `A_KIND_NAME_INDEX` (empties with custom props `size` and `meta`);
  - moving pieces `name@A_ANCHOR#tag`, in a flat hierarchy.
- Coordinates are Unity's: metres, +Y up. `dct_common.conv()` converts them.

**Read first:** `README.md`, `docs/MODEL_PIPELINE.md`, the docstring of `Tools/Blender/dct_common.py`, and the existing script closest to your task.

**Set up Blender on Linux**
1. Install fonts and libraries (skip any that fail):
   `sudo apt-get update && sudo apt-get install -y fonts-liberation fonts-dejavu-core libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libegl1 libxkbcommon0 libsm6 libice6 xvfb libgl1-mesa-dri`
2. Download and unpack Blender:
   `curl -L -o /tmp/blender.tar.xz https://download.blender.org/release/Blender5.0/blender-5.0.1-linux-x64.tar.xz && sudo tar -xJf /tmp/blender.tar.xz -C /opt`
3. Run it as `/opt/blender-5.0.1-linux-x64/blender -b --factory-startup -P <script> -- <args>`.
4. **Smoke test:** `... -P Tools/Blender/build_plugs.py -- atx24`, then `git checkout -- .` to drop the rebuilt files.
5. If Workbench or EEVEE previews fail headless, prefix the command with `xvfb-run -a -s "-screen 0 1920x1080x24"`. As a last resort, render previews with Cycles on the CPU.
6. If download.blender.org is blocked, try `pip install bpy` (Blender as a Python module).
7. If Blender can't run at all, write your report saying what blocked you, then commit, push and stop.

**Working rules**
- **Work in your own new script** (named in your brief). Never edit `dct_common.py` or `parts_*.py`.
  - Only task 03 may edit `build_boxes.py`, `rig_common.py` and `rig_products.py`.
- **Never change or re-export an existing model.** `Tools/Blender/extras_compare.py` proves a re-export is unchanged.
- **Iterate on the look.** Build one model at a time and look at its previews (read the PNGs). Iterate until it looks like the real product at arm's length: real thickness, bevels and believable detail, labels via `tex_<file>` textures, the existing material tags.
- **Moving pieces:** model them in their closed pose, with their pivot at their anchor. Local +Z of a port anchor = the direction its plug comes from.
- **Save your work often: the owner's cloud tokens are limited and can run out mid-task.**
  - After every finished model: commit it (model, textures, previews, report, script) and push.
  - Never commit to `main`, never force-push. Use this session's branch.
- **Keep your report up to date** in `docs/reports/<task>.md`, and commit it with each model. It lists:
  - every model's id, size, triangles, frame, and anchors with their meta;
  - any deviations;
  - the rebuild command.
  - The owner reads this report when merging your branch into the game.
