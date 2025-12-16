#!/bin/bash
# XJTLU PDF Downloader - macOS CLI 运行脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 运行 CLI 程序，传递所有参数
python3 cli.py "$@"
