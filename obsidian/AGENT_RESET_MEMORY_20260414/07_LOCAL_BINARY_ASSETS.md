# Local Binary Assets

Date: `2026-04-14`

Purpose:
- preserve awareness of render files that still exist locally after context reset;
- prevent unnecessary rebuilds of usable `.mp4` outputs;
- prevent accidental mass staging from a dirty worktree.

Status:
- these files exist in the workspace;
- they are referenced by tracked notes and JSON metadata;
- they are currently untracked by git on purpose.

Inventory:
- `obsidian/Wibes_Exact_Product_20260414/939855999_daughter_from_dad_exact/wibes_exact_product_939855999_20260414.mp4` - `5,177,300` bytes
- `obsidian/Wibes_Launch_20260410/939855999_brasshir51_moya_dochenka_ot_papy/renders/wibes_motion_939855999_20260410.mp4` - `1,236,795` bytes
- `obsidian/Wibes_Launch_20260410/939855999_brasshir51_moya_dochenka_ot_papy/renders/wibes_motion_939855999_20260411_4k.mp4` - `9,415,111` bytes
- `obsidian/Wibes_Launch_20260410/939855999_brasshir51_moya_dochenka_ot_papy/renders/wibes_motion_939855999_20260412_safe_crisp_4k.mp4` - `21,404,328` bytes
- `obsidian/Wibes_Trend_20260412/219234076_synu_ot_mamy_trend/wibes_trend_219234076_20260412.mp4` - `1,089,102` bytes
- `obsidian/Wibes_Trend_Motion_20260412/939855999_daughter_from_dad_reboot/wibes_trend_motion_939855999_20260412.mp4` - `9,450,209` bytes

Reuse priority:
1. Use `wibes_exact_product_939855999_20260414.mp4` first when the task needs the most truthful bracelet visual.
2. Use `wibes_motion_939855999_20260412_safe_crisp_4k.mp4` as the main launch fallback.
3. Use `wibes_motion_939855999_20260411_4k.mp4` only as backup.
4. Use trend videos only for channel testing, not as truth anchors for product fidelity.

Operational rule:
- If these files still exist locally, reuse them before rebuilding motion.
- If they are missing locally, rebuild from tracked JSON, prompts, and scripts, not from memory.
- Never sweep them into a commit through `git add .` from the repository root.
