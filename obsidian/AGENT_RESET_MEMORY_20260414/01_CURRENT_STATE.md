# Current State

Snapshot date: `2026-04-14`

## Git

- Active handoff branch: `codex/ozon-obsidian-reset-memory-20260414`
- The repository is dirty. There are many unrelated `modified` and `untracked` files outside this handoff package.
- Do not run `git add .` from the repository root.
- Commit only explicit paths related to the current task.

## Reset-memory layers

- Marketplace reset memory already exists:
  - `obsidian/06_Marketplace_Context_Reset_Memory_20260414.md`
  - `obsidian/07_Ozon_Context_Reset_Memory_20260414.md`
- `AGENT_RESET_MEMORY_20260414` does not replace those files.
- This folder compresses the product, content, Wibes, Gemini, and render-state handoff needed after reset.

## Wibes state

- Public profile: [https://wibes.ru/author/4275108](https://wibes.ru/author/4275108)
- Profile pack state:
  - brand name: `GravMix`
  - handle: `@gravmix-gifts-ru`
  - bio was already set
- Confirmation log:
  - `output/playwright/wibes_profile_finalize_20260412.json`

## Wibes publication state

- One earlier clip for SKU `939855999` was already published before this reset-memory pass.
- One native article was already submitted for moderation:
  - topic: `Как выбрать подарок ребенку, который не забудут`
  - log: `output/playwright/wibes_publish_article_20260412.json`
- A newer exact-product clip was built locally without Gemini redraw:
  - `obsidian/Wibes_Exact_Product_20260414/939855999_daughter_from_dad_exact/wibes_exact_product_939855999_20260414.mp4`
- This note set does not mark that exact-product clip as re-published. Treat it as a ready local asset, not as confirmed live content.

## Video generation truth

- Browser-driven `Gemini Pro` video generation was made operational.
- Final Gemini output was still commercially unsafe for bracelet truth:
  - it drifted into the wrong object;
  - it changed product form;
  - it failed exact engraving fidelity.
- Safe production path for bracelet content:
  - use real bracelet photos;
  - build safe/crisp stills;
  - assemble motion locally;
  - use generated tools only where they do not alter the bracelet itself.

## Business priority

- Wibes should be run as a senior content funnel, not as a marketplace catalog mirror.
- Priority content logic:
  - family-first emotional hooks;
  - native warming articles;
  - truthful product visuals;
  - no filler slideshow content;
  - no approximate fake bracelet renders.

## Local binary state

- Six `.mp4` render assets exist locally and remain untracked on purpose.
- They are referenced by tracked markdown and JSON files.
- Read `obsidian/AGENT_RESET_MEMORY_20260414/07_LOCAL_BINARY_ASSETS.md` before deciding any render was lost.
- Do not stage those files accidentally from a dirty worktree.
