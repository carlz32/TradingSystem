#!/bin/bash

# 确保安装 PyInstaller
echo "Checking/Installing PyInstaller..."
pip3 install pyinstaller

# 清理旧的构建文件
echo "Cleaning up old build files..."
rm -rf build dist *.spec

# 执行打包
echo "Building the application..."

# 设置本地 PyInstaller 配置目录，避免权限问题
export PYINSTALLER_CONFIG_DIR="$(pwd)/.pyinstaller_config"
mkdir -p "$PYINSTALLER_CONFIG_DIR"

# --windowed: 生成无控制台的 GUI 应用 (.app)
# --name: 指定应用名称
# --noconfirm: 覆盖输出目录不询问
# --clean: 清理 PyInstaller 缓存
python3 -m PyInstaller --name="MonteCarloRS" --windowed --noconfirm --clean run.py

echo "========================================"
echo "打包完成！"
echo "应用位置: $(pwd)/dist/MonteCarloRS.app"
echo "你可以双击运行该应用。"
echo "========================================"
