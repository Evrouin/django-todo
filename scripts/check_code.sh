#!/bin/bash
# Code quality check script

set -e

echo "🔍 Running Code Quality Checks"
echo "==============================="
echo ""

# Black - Code formatting
echo "1️⃣  Running Black (code formatter)..."
black --check --diff apps/ config/ || {
    echo "❌ Black formatting issues found. Run 'black .' to fix."
    exit 1
}
echo "✅ Black passed"
echo ""

# Flake8 - Linting
echo "2️⃣  Running Flake8 (linter)..."
flake8 apps/ config/ || {
    echo "❌ Flake8 found issues."
    exit 1
}
echo "✅ Flake8 passed"
echo ""

# Ruff - Fast linter
echo "3️⃣  Running Ruff (fast linter)..."
ruff check apps/ config/ || {
    echo "❌ Ruff found issues. Run 'ruff check --fix .' to auto-fix."
    exit 1
}
echo "✅ Ruff passed"
echo ""

# MyPy - Type checking
echo "4️⃣  Running MyPy (type checker)..."
mypy apps/ config/ || {
    echo "⚠️  MyPy found type issues (non-blocking)"
}
echo "✅ MyPy completed"
echo ""

echo "✅ All code quality checks passed!"
