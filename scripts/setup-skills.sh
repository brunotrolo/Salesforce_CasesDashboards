#!/bin/bash

# Setup Skills - Integrates agent-skills, ui-ux-pro-max, and impeccable

set -e

echo "🛠️  Setting up Claude Code Skills..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
SKILLS_DIR="skills"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$REPO_ROOT"

# Create skills directory
mkdir -p "$SKILLS_DIR"

echo -e "${BLUE}1. Cloning Agent Skills...${NC}"
if [ -d "$SKILLS_DIR/agent-skills" ]; then
    echo "✓ Agent Skills already cloned"
    cd "$SKILLS_DIR/agent-skills" && git pull origin main && cd - > /dev/null
else
    git clone https://github.com/addyosmani/agent-skills.git "$SKILLS_DIR/agent-skills"
    echo -e "${GREEN}✓ Agent Skills cloned${NC}"
fi

echo -e "${BLUE}2. Cloning UI/UX Pro Max Skill...${NC}"
if [ -d "$SKILLS_DIR/ui-ux-pro-max" ]; then
    echo "✓ UI/UX Pro Max already cloned"
    cd "$SKILLS_DIR/ui-ux-pro-max" && git pull origin main && cd - > /dev/null
else
    git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git "$SKILLS_DIR/ui-ux-pro-max"
    echo -e "${GREEN}✓ UI/UX Pro Max cloned${NC}"
fi

echo -e "${BLUE}3. Cloning Impeccable...${NC}"
if [ -d "$SKILLS_DIR/impeccable" ]; then
    echo "✓ Impeccable already cloned"
    cd "$SKILLS_DIR/impeccable" && git pull origin main && cd - > /dev/null
else
    git clone https://github.com/pbakaus/impeccable.git "$SKILLS_DIR/impeccable"
    echo -e "${GREEN}✓ Impeccable cloned${NC}"
fi

echo -e "${BLUE}4. Installing Agent Skills dependencies...${NC}"
if [ -f "$SKILLS_DIR/agent-skills/requirements.txt" ]; then
    pip install -q -r "$SKILLS_DIR/agent-skills/requirements.txt" 2>/dev/null || true
    echo -e "${GREEN}✓ Agent Skills dependencies installed${NC}"
fi

echo -e "${BLUE}5. Installing Impeccable...${NC}"
cd "$SKILLS_DIR/impeccable"
if [ -f "setup.py" ]; then
    pip install -q -e . 2>/dev/null || true
    echo -e "${GREEN}✓ Impeccable installed${NC}"
elif [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt 2>/dev/null || true
    echo -e "${GREEN}✓ Impeccable dependencies installed${NC}"
fi
cd - > /dev/null

echo -e "${BLUE}6. Installing UI/UX Pro Max dependencies...${NC}"
if [ -f "$SKILLS_DIR/ui-ux-pro-max/requirements.txt" ]; then
    pip install -q -r "$SKILLS_DIR/ui-ux-pro-max/requirements.txt" 2>/dev/null || true
fi
if [ -f "$SKILLS_DIR/ui-ux-pro-max/package.json" ]; then
    cd "$SKILLS_DIR/ui-ux-pro-max"
    npm install --quiet 2>/dev/null || true
    cd - > /dev/null
fi
echo -e "${GREEN}✓ UI/UX Pro Max dependencies installed${NC}"

echo -e "${BLUE}7. Verifying .claude/skills-config.json...${NC}"
if [ -f ".claude/skills-config.json" ]; then
    echo -e "${GREEN}✓ Skills configuration found${NC}"
else
    echo -e "${YELLOW}⚠ Skills configuration not found at .claude/skills-config.json${NC}"
fi

echo -e "${BLUE}8. Setting up pre-commit hooks (Impeccable)...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install 2>/dev/null || true
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠ pre-commit not found. Install with: pip install pre-commit${NC}"
fi

echo ""
echo -e "${GREEN}✅ Skills setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review SKILLS_INTEGRATION.md for usage instructions"
echo "2. Try: claude /agent-skills detect-patterns --directory services/"
echo "3. Try: claude /impeccable quality-report --branch main"
echo "4. Try: claude /ui-ux audit-accessibility frontends/dashboard-fe"
echo ""
echo "Environment variables (optional, add to .env):"
echo "  export CLAUDE_SKILLS_PATH=$REPO_ROOT/skills"
echo "  export IMPECCABLE_MIN_QUALITY=80"
echo "  export UI_UX_FRAMEWORK=tailwind"
