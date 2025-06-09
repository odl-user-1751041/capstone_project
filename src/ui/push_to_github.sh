#!/bin/bash
# -----------------------------
# push_to_github.sh
# -----------------------------
# Stage, commit, and push index.html to your GitHub repo.
#
# Prereqs:
#  1. You already ran:
#       git init
#       git remote add origin https://github.com/odl-user-1751041/capstone_project.git
#       git branch -M main
#       git push -u origin main
#  2. SSH keys or credentials are set for non‐interactive pushes.
# -----------------------------

set -e

# 1) Stage the file
git add index.html

# 2) Commit with a timestamped message
commit_msg="Auto-push index.html on APPROVAL at $(date +'%Y-%m-%d %H:%M:%S')"
git commit -m "$commit_msg"

# 3) Push to origin/main
git push origin main

echo "✅ index.html has been pushed to origin/main."
