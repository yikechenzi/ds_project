# 电商选品管理系统

基于 **Python + PySide6** 开发的电商选品桌面管理软件，界面美观，支持自适应窗口，数据本地存储。

## 功能模块

| 模块 | 功能 |
|------|------|
| **🏠 首页** | 6 张统计卡片（总订单数、销售额、利润、今日利润、供货商数、商品数）+ 最近订单列表，支持自动刷新 |
| **🏭 供货商管理** | 添加/编辑/删除供货商，支持线上/线下分类，记录名称与备注 |
| **📦 商品管理** | 关联供货商，录入名称、拿货价格、运费、商品链接，自动计算成本 |
| **📋 订单管理** | 选择商品自动显示成本，输入售价和数量实时计算利润，支持编辑与删除 |

## 项目结构

```
xuanping_exe/
├── main.py                 # 主入口（导航栏 + 全局样式）
├── database.py             # SQLite 数据库与数据访问层
├── build_exe.py            # PyInstaller 打包脚本
├── requirements.txt        # Python 依赖
├── xuanping.db             # SQLite 数据文件（自动生成）
└── ui/
    ├── __init__.py
    ├── home_page.py        # 首页仪表盘
    ├── supplier_page.py    # 供货商管理
    ├── product_page.py     # 商品管理
    └── order_page.py       # 订单管理
```

## 环境要求

- Python 3.8+
- Windows / macOS / Linux

## 快速开始

```bash
# 1. 克隆或进入项目目录
cd xuanping_exe

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python main.py
```

首次运行会自动在项目目录下创建 `xuanping.db` 数据库文件。

## 操作指南

### 通用交互
- **添加**：填写表单后点击按钮
- **编辑**：双击表格行 或 选中行后点击「编辑选中」
- **保存**：编辑状态下点击「💾 保存修改」
- **取消编辑**：点击「取消编辑」或切换到其他页面
- **删除**：选中行后点击「删除选中」

### 订单利润计算
选择商品后系统自动填入成本（拿货价 + 运费），输入售价和数量后利润实时计算。

## 打包为 EXE

```bash
python build_exe.py
```

打包完成后，`dist/电商选品管理系统.exe` 即为可分发的单文件程序，无需安装 Python 环境即可运行。

## 技术栈

- **UI 框架**：[PySide6](https://pypi.org/project/PySide6/)（Qt for Python）
- **数据库**：SQLite
- **打包工具**：[PyInstaller](https://pyinstaller.org/)
