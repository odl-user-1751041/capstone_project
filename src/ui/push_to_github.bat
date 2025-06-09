@echo off
cd /d %~dp0

git add index.html
git commit -m "Auto-commit: updated index.html after agent approval"
git pull --rebase origin main
git push origin main
