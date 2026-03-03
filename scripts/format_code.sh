#!/bin/bash
# Auto-format code script

set -e

echo "🎨 Auto-formatting Code"
echo "======================="
echo ""

# Black - Format code
echo "1️⃣  Running Black..."
black apps/ config/
echo "✅ Black formatting complete"
echo ""

# Ruff - Auto-fix issues
echo "2️⃣  Running Ruff auto-fix..."
ruff check --fix apps/ config/
echo "✅ Ruff auto-fix complete"
echo ""

# Sort imports
echo "3️⃣  Running Ruff import sorting..."
ruff check --select I --fix apps/ config/
echo "✅ Import sorting complete"
echo ""

echo "✅ Code formatting complete!"
echo ""
echo "Run './scripts/check_code.sh' to verify all checks pass."
