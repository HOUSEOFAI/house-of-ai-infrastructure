#!/usr/bin/env bash
# House of AI™ — Higgsfield Creative Engine Setup
# Run this once to connect Higgsfield to Claude Code

set -e

echo ""
echo "========================================"
echo "  HOUSE OF AI™ — HIGGSFIELD SETUP"
echo "========================================"
echo ""

# 1. Install Higgsfield CLI (Hermes)
echo "Step 1: Installing Higgsfield CLI (Hermes)..."
npm install -g @higgsfield/cli
echo "✓ Higgsfield CLI installed"
echo ""

# 2. Authenticate
echo "Step 2: Connecting your Higgsfield account..."
echo "   (A browser window will open — log in with your Higgsfield account)"
higgsfield auth login
echo "✓ Higgsfield authenticated"
echo ""

# 3. Add as Claude Code skill
echo "Step 3: Adding Higgsfield as a Claude Code skill..."
npx @higgsfield/cli skills add
echo "✓ Higgsfield skill added to Claude Code"
echo ""

# 4. Verify
echo "Step 4: Verifying installation..."
higgsfield --version
echo ""

echo "========================================"
echo "  SETUP COMPLETE"
echo ""
echo "  Higgsfield (Hermes) is now wired into"
echo "  your Claude Code agent."
echo ""
echo "  Next: Run the creative studio:"
echo "  python bots/creative-studio/pinterest_agent.py"
echo "========================================"
echo ""
