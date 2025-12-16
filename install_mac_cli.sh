#!/bin/bash
# XJTLU PDF Downloader - macOS CLI 安装脚本
# 仅安装 CLI 所需的最小依赖，无需 Tkinter

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  XJTLU PDF Downloader - macOS CLI 安装程序                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python 3
echo "🔍 检查 Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✓ 找到 Python $PYTHON_VERSION"
else
    echo "✗ 未找到 Python 3"
    echo ""
    echo "请先安装 Python 3:"
    echo "  使用 Homebrew: brew install python3"
    echo "  或从官网下载: https://www.python.org/downloads/"
    exit 1
fi

# 检查 pip
echo ""
echo "🔍 检查 pip..."
if python3 -m pip --version &> /dev/null; then
    echo "✓ pip 可用"
else
    echo "✗ pip 不可用，尝试安装..."
    python3 -m ensurepip --upgrade
fi

# 安装依赖（仅 playwright，不需要其他 GUI 依赖）
echo ""
echo "📦 安装 Python 依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install playwright

# 安装 Playwright 浏览器
echo ""
echo "🌐 安装 Playwright Chromium 浏览器..."
echo "   (这可能需要几分钟，请耐心等待)"
python3 -m playwright install chromium

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✓ 安装完成！"
echo ""
echo "使用方法:"
echo "  交互模式: ./run_mac_cli.sh"
echo "  或直接:   python3 cli.py"
echo ""
echo "更多选项:   python3 cli.py --help"
echo "═══════════════════════════════════════════════════════════"
