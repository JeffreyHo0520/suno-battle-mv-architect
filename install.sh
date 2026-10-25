#!/usr/bin/env bash
# One-click installer for suno-battle-mv-architect Skill
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/JeffreyHo0520/suno-battle-mv-architect/main/install.sh | bash
set -euo pipefail

REPO_URL="https://github.com/JeffreyHo0520/suno-battle-mv-architect.git"
SKILL_NAME="suno-battle-mv-architect"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"

IS_REMOTE=0
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR/skills" ]; then
  IS_REMOTE=1
  TMP_DIR="$(mktemp -d)"
  echo ">>> [$SKILL_NAME] Remote execution detected. Cloning repository..."
  git clone --depth 1 "$REPO_URL" "$TMP_DIR"
  SCRIPT_DIR="$TMP_DIR"
fi

cleanup() {
  if [ "$IS_REMOTE" -eq 1 ] && [ -d "${TMP_DIR:-}" ]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

echo "================================================================="
echo " 🎤 Installing Suno Battle MV Architect AI Agent Skill          "
echo "    - Speaker-Adaptive Theme Engine (HUD, Pills, Spectrum)      "
echo "    - Audio-Reactive Bass & 64-Band Smoothed Spectrum           "
echo "    - Zero-Tofu Glyph & Unicode-Safe OpenCV I/O                 "
echo "    - Intel QSV (-pix_fmt nv12) Accelerated 1080p / Shorts      "
echo "================================================================="

TARGET_ROOTS=(
  "$HOME/.gemini/config/skills"
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.agents/skills"
)

SRC="$SCRIPT_DIR/skills/$SKILL_NAME"
if [ ! -d "$SRC" ] && [ -f "$SCRIPT_DIR/SKILL.md" ]; then
  SRC="$SCRIPT_DIR"
fi

for root in "${TARGET_ROOTS[@]}"; do
  mkdir -p "$root"
  DEST="$root/$SKILL_NAME"
  echo ">>> Target Skills Root: $root"
  rm -rf "$DEST"
  cp -R "$SRC" "$DEST"
  find "$DEST" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  echo "  [+] Installed $SKILL_NAME successfully!"
done

echo ""
echo "-----------------------------------------------------------------"
echo "🔍 Checking environment prerequisites:"
echo "-----------------------------------------------------------------"
command -v python3 >/dev/null 2>&1 && echo "  [✓] Python: $(python3 --version)" || echo "  [!] Python 3 not found."
command -v ffmpeg >/dev/null 2>&1 && echo "  [✓] ffmpeg is installed." || echo "  [!] ffmpeg not found."

echo ""
echo "✨ Installation complete! You can now use /suno-battle-mv-architect in your AI agent."
