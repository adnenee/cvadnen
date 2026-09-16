#!/usr/bin/env bash
# Push the CV site to GitHub Pages -> https://adnenee.github.io/cvadnen/
# Run from anywhere:   ./deploy-github.sh
set -euo pipefail
cd "$(dirname "$0")"

REMOTE_URL="https://github.com/adnenee/cvadnen.git"
EXPECTED_USER="adnenee"

echo "== CV deploy =="
echo "target: $REMOTE_URL"

# 1. sign-in check
if ! gh auth status >/dev/null 2>&1; then
  echo
  echo "Not signed in to GitHub."
  echo "  1) run:  gh auth login"
  echo "  2) choose github.com -> HTTPS -> Login with a web browser"
  echo "  3) sign in as '$EXPECTED_USER'"
  echo "  4) run this script again"
  exit 1
fi

USER="$(gh api user --jq .login)"
echo "signed in as: $USER"

if [ "$USER" != "$EXPECTED_USER" ]; then
  echo
  echo "You are signed in as '$USER', but the repo belongs to '$EXPECTED_USER'."
  echo "Pick one:"
  echo "  A) sign in as $EXPECTED_USER:   gh auth login   (then re-run)"
  echo "  B) add '$USER' as a collaborator with Write access on"
  echo "     https://github.com/adnenee/cvadnen/settings/access  (then re-run)"
  exit 1
fi

# 2. push
git remote set-url origin "$REMOTE_URL" 2>/dev/null || git remote add origin "$REMOTE_URL"
git branch -M main

if ! git push -u origin main 2>/dev/null; then
  echo
  echo "Push rejected - the remote already has history this branch does not."
  echo "If you are happy to make this version the live one, run:"
  echo "    git push -u origin main --force"
  exit 1
fi

echo
echo "Pushed to main."
echo "Live at: https://adnenee.github.io/cvadnen/  (allow ~1 minute)"
echo
echo "If this is the first deploy, enable Pages once:"
echo "  https://github.com/adnenee/cvadnen/settings/pages"
echo "  Source: Deploy from a branch  ->  Branch: main  ->  Folder: / (root)  ->  Save"
