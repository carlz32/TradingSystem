# 交易盈亏比蒙特卡洛桌面程序

- 简介：使用 Python + Tkinter 构建的桌面工具，通过蒙特卡洛模拟分析交易盈亏比（单位 R）的分布与风险，支持最大回撤估计与直方图/曲线可视化，并提供数据持久化功能。
- 适用：你已记录了至少 10 个历史盈亏比数据（R 值，如 -1、2、-0.5…），希望评估在一定交易笔数下的最终盈亏与回撤的可能区间。

## 功能
- 输入历史盈亏比数据（≥ 10），支持逗号、空格、换行分隔
- 支持列数据粘贴：
  - 可直接从 Excel/表格复制多列数据，每行最后一列为盈亏比 R
  - 程序会自动从每一行提取最后一个数值作为本行的 R
- 设置交易笔数与模拟次数，运行蒙特卡洛模拟（有放回抽样）
- 输出分布统计：
  - 平均值、中位数、最差/最好、5%/25%/75%/95% 分位数
- 最大回撤估计：
  - 从 0R 起累积权益，记录路径中的最大回撤（负值）
- 图表可视化（嵌入窗口标签页）：
  - 最终盈亏 R 分布直方图 + 曲线
  - 最大回撤 R 分布直方图 + 曲线
- 数据持久化：
  - 本地保存输入数据到 rr_history.json
  - 自动维护最近 10 条历史记录（去重），并在启动时加载
  - 提供“历史记录列表 + 载入选中”功能，方便快速切换不同数据集
- 中文字体修复：
  - 已为 matplotlib 设置常见中文字体，避免显示为方框

## 环境要求
- Python 3（需可用 Tkinter）
- 可选依赖：matplotlib 用于绘图

## 安装与运行
- 安装绘图依赖（可选）：
  ```bash
  pip3 install matplotlib
  ```
- 启动程序：
  ```bash
  python3 run.py
  ```
  或：
  ```bash
  python3 main.py
  ```

## 使用步骤
- 在顶部文本框粘贴你的历史盈亏比数据（单位 R）
- 设置交易笔数与模拟次数（例如：100、1000）
- 点击“运行模拟”，查看“统计报告”与“分布图表”两个标签页
- 点击“保存数据”持久化到 rr_history.json，程序下次启动会自动加载

## 目录结构
- [mcdesk/core.py](file:///Users/carlz/Documents/TradingSystem/mcdesk/core.py)：蒙特卡洛核心逻辑与统计
- [mcdesk/ui.py](file:///Users/carlz/Documents/TradingSystem/mcdesk/ui.py)：桌面界面、标签页与嵌入式图表、数据保存/加载
- [mcdesk/config.py](file:///Users/carlz/Documents/TradingSystem/mcdesk/config.py)：配置（数据文件路径）
- [run.py](file:///Users/carlz/Documents/TradingSystem/run.py)：入口脚本（推荐）
- [main.py](file:///Users/carlz/Documents/TradingSystem/main.py)：兼容性入口，调用新模块
- [rr_history.json](file:///Users/carlz/Documents/TradingSystem/rr_history.json)：持久化的历史盈亏比数据
- [rules.md](file:///Users/carlz/Documents/TradingSystem/rules.md)：交易规则
- [montecarlosim.md](file:///Users/carlz/Documents/TradingSystem/montecarlosim.md)：（可选文档）


## 打包为桌面应用 (macOS App)
如果你希望将脚本打包为独立的 `.app` 应用，请按以下步骤操作：

1. **安装 PyInstaller**
   ```bash
   pip3 install pyinstaller
   ```

2. **执行打包命令**
   在项目根目录下运行：
   ```bash
   python3 -m PyInstaller --name "MonteCarloRS" --windowed --clean --noconfirm run.py
   ```
   *注：打包过程可能需要几分钟。*

3. **运行应用**
   打包完成后，应用位于 `dist/MonteCarloRS.app`。
   你可以直接双击运行它，或将其拖入 `/Applications` 文件夹。

4. **关于数据存储**
   - **脚本模式运行**：数据保存在项目目录下的 `rr_history.json`。
   - **打包应用运行**：数据将保存在 `~/Documents/MonteCarloRS/rr_history.json`（用户文档目录），以确保应用即使被移动也能正常读写历史数据。

## 常见问题
- 无法启动 Tkinter（_tkinter 模块缺失）：
  - macOS 可尝试使用系统自带的 `python3`，或安装包含 Tcl/Tk 的 Python
- 图表中文显示为方框：
  - 已在代码中配置中文字体；若仍异常，请确保系统安装了对应字体（如 PingFang/Arial Unicode MS）

## 说明
- 模拟采用有放回抽样，最终盈亏与最大回撤仅用于区间评估与风险提示，不代表确定性结果
- R 为单位化盈亏（相对止损的倍数），请保持数据一致性与准确记录
