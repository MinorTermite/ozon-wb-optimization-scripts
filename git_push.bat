@echo off
chcp 65001 > nul
cd /d "C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar"

echo [1/4] Adding all files...
"C:\Program Files\Git\bin\git.exe" add -A

echo [2/4] Committing...
"C:\Program Files\Git\bin\git.exe" commit -m "feat: full project sync - scripts, analytics, docs, strategies (27.02.2026)"

echo [3/4] Pushing to origin...
"C:\Program Files\Git\bin\git.exe" push origin ozon-wb-optimization-scripts

echo [4/4] Done!
"C:\Program Files\Git\bin\git.exe" log --oneline -3
pause
