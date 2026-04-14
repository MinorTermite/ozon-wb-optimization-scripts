# Agent Reset Memory 20260414

This folder stores operational memory for the next AI agent after context reset.

Goal:
- avoid reloading the full history for `WB`, `Ozon`, `Wibes`, `Gemini`, prompts, and visuals;
- restore the factual working state quickly;
- avoid repeating already-known bracelet and generation mistakes;
- continue from the correct operational baseline.

Read in this order:
1. `01_CURRENT_STATE.md`
2. `02_PRODUCT_TRUTH_AND_NON_NEGOTIABLES.md`
3. `03_WIBES_PLAYBOOK.md`
4. `04_GEMINI_AND_VIDEO_LIMITS.md`
5. `05_ASSET_AND_SCRIPT_MAP.md`
6. `06_RESET_PROTOCOL.md`
7. `07_LOCAL_BINARY_ASSETS.md`
8. `manifest.json`

Core rule:

For GravMix bracelets, do not trust generative output as the final product source when bracelet form, engraving, recipient meaning, or SKU truth matters.
