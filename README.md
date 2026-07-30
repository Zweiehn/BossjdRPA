# BossjdRPA

BOSS直聘 RPA 自动化工具，基于 PaddleOCR + AI 大模型，自动采集、解析和保存招聘职位 JD 描述。

## 功能

- **智能列表识别**：PaddleOCR 多策略解析聊天列表，自动识别候选人姓名和公司
- **详情页采集**：自动点击进入详情页，滚动截取完整 JD 文本
- **AI 合并去重**：调用大模型 API 将多段 OCR 碎片拼凑成通顺的完整 JD
- **指纹去重**：自动记录已处理候选人，避免重复采集
- **桌面控制台**：tkinter GUI 界面，实时日志显示，全局快捷键暂停/继续

## 环境要求

- **操作系统**：仅限 Windows 10 / 11（依赖 PyAutoGUI 和 keyboard 的 Windows API）
- **Python**：必须是 **3.12.x**（PaddlePaddle 目前最高只支持到 3.12）
- **内存**：建议 8 GB 以上
- **前置条件**：BOSS 直聘聊天页面需在屏幕上可见（网页版或桌面客户端均可）
- **工具**：本指南只假设你有一台新电脑、一个浏览器和一个记事本，不需要任何 IDE

---

## 从零开始搭建运行环境

以下步骤适合**完全没有编程环境**的新电脑。你只需要浏览器、文件资源管理器和命令提示符（cmd）。

### 第一步：安装 Python 3.12

1. 打开浏览器，访问 https://www.python.org/downloads/
2. 找到 **Python 3.12.x**（例如 3.12.10），点击下载 **Windows installer (64-bit)**
   > 不要下载 3.13 或 3.14，PaddlePaddle 不支持
3. 双击下载的安装包（`python-3.12.x-amd64.exe`）
4. **关键**：安装界面最下方勾选 **「Add Python to PATH」**，然后点击 **「Install Now」**
5. 等待安装完成

验证安装：按 `Win + R`，输入 `cmd` 回车，在黑色窗口中输入：
```
python --version
```
如果显示 `Python 3.12.x`，说明安装成功。

### 第二步：获取项目文件

**方式 A — 直接下载 ZIP（推荐，不需要 Git）：**

1. 浏览器打开 https://github.com/Zweiehn/BossjdRPA
2. 点击绿色的 **「<> Code」** 按钮 → **「Download ZIP」**
3. 将下载的 `BossjdRPA-main.zip` 解压到你想要的目录，例如 `D:\BossjdRPA`
4. 解压后的文件夹结构应该包含 `main.py`、`boss_actions.py` 等文件

**方式 B — 使用 Git（如果你装了 Git）：**

```bash
git clone https://github.com/Zweiehn/BossjdRPA.git
cd BossjdRPA
```

### 第三步：创建虚拟环境

虚拟环境能让这个项目的依赖与系统隔离，不会污染你的电脑。在 cmd 中：

```
cd D:\BossjdRPA          # 进入项目目录（改成你实际的路径）
python -m venv venv      # 创建虚拟环境，会生成一个 venv 文件夹
```

激活虚拟环境：
```
venv\Scripts\activate
```

激活后，命令行前面会出现 `(venv)` 字样，表示虚拟环境已生效。
> 每次打开新 cmd 窗口运行本项目前，都要先执行这一步。

### 第四步：安装依赖

确保 `(venv)` 已激活，然后：

**在线安装（有网络）：**

```bash
# 核心依赖
pip install pyautogui pillow numpy opencv-python requests keyboard

# PaddleOCR（指定国内镜像源更快）
pip install paddlepaddle==2.6.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install "paddleocr<3.0" -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**离线安装（无网络 / 永久存档）：**

1. 从 [Releases](https://github.com/Zweiehn/BossjdRPA/releases) 下载 `ocr_offline_pack.zip`
2. 解压到任意位置（例如桌面）
3. 双击 `install_offline.bat`，会自动安装全部依赖和模型
4. 回到项目目录继续下面的步骤

### 第五步：验证安装

在 `(venv)` 激活状态下，依次运行以下命令，确保没有报错：

```bash
python -c "import pyautogui; print('pyautogui OK')"
python -c "from paddleocr import PaddleOCR; print('paddleocr OK')"
python -c "from PIL import Image; print('pillow OK')"
python -c "import cv2; print('opencv OK')"
```

全部显示 OK 即表示环境就绪。

### 第六步：配置 AI API

程序依赖大模型 API 来合并 OCR 文本碎片，支持 **OpenAI 兼容接口**（Deepseek、Kimi、通义千问、智谱等）。

**方式一（推荐）：** 启动程序后，点击界面上的 **「AI 设置」** 按钮，选择服务商并填入 API Key，点「测试连接」验证。

**方式二：** 第一次运行程序后，项目目录会生成 `rpa_config.json`，用记事本打开，填入你的 API 信息：

```json
{
  "API_URL": "https://api.deepseek.com/v1",
  "API_KEY": "sk-你的密钥",
  "MODEL_NAME": "deepseek-chat"
}
```

> `API_URL` 填 Base URL（**不含** `/chat/completions`），程序会自动拼接完整路径。

### 第七步：启动

确保虚拟环境已激活（命令行前面有 `(venv)`），然后：

```bash
pythonw main.py          # 无黑框启动，仅 GUI 界面
# 或
python main.py           # 带终端日志启动，方便调试
```

也可以双击项目目录下的 `start_rpa.bat` 直接启动。

---

## 使用流程

1. 打开 BOSS 直聘聊天页面，确保列表和右侧详情区域可见
2. 点击 **「开始」** → 鼠标框选左侧聊天列表区域
3. 程序自动识别候选人列表后，点击第一条记录
4. 在右侧详情页内点击一次鼠标（程序会记录这个激活位置）
5. 框选职位详情的内容区域（从岗位名称到底部）
6. 程序自动循环处理所有新候选人，结果保存在 `JD_Output/` 目录

后续再运行时，区域和点击位置都已记录，无需重新框选。如果窗口位置变了，点击 **「重置区域」** 按钮即可重新配置。

## 快捷键

| 快捷键 | 功能 |
|---|---|
| `Ctrl + Shift + Alt + P` | 暂停 / 继续 |
| ESC（框选时） | 取消框选 |

## 项目结构

```
├── main.py              # GUI 控制台主入口
├── boss_actions.py      # 核心业务逻辑（列表解析、详情采集、缓存管理）
├── vision_engine.py     # PaddleOCR 视觉引擎（截图、OCR、鼠标键盘操作）
├── ai_service.py        # AI 大模型服务（文本去重、拼凑）
├── config.py            # 配置管理（区域坐标、API 设置）
├── screen_selector.py   # 屏幕区域框选工具
├── start_rpa.bat        # Windows 启动脚本（无黑框）
├── rpa_config.json      # 运行时配置（自动生成，首次运行后出现）
├── processed_cache.json # 已处理候选人缓存（防重复采集）
└── JD_Output/           # 采集结果输出目录
```

## 常见问题

**Q: 运行时报错 "No module named 'xxx'"？**
A: 确认虚拟环境已激活（命令行有 `(venv)` 前缀），然后重新执行第四步安装依赖。

**Q: PaddleOCR 报错 "tuple index out of range"？**
A: Python 版本不对。必须使用 Python 3.12.x，检查 `python --version`。

**Q: 报错包含 "oneDNN" 或 "ConvertPirAttribute"？**
A: 你安装了 PaddlePaddle 3.x 而不是 2.6.2。卸载后重装：`pip uninstall paddlepaddle paddleocr -y`，然后重新执行第四步。

**Q: 快捷鍵 Ctrl+Shift+Alt+P 没反应？**
A: 以管理员身份运行 cmd / PowerShell 再启动程序，keyboard 库需要管理员权限才能注册全局热键。

**Q: 程序无法识别列表中的候选人？**
A: 检查 BOSS 直聘窗口是否在屏幕最前面、框选区域是否准确。查看控制台日志中的 OCR 识别结果来排查。

**Q: 想在新电脑上用，必须重新下载所有依赖吗？**
A: 不需要。把整个项目文件夹 + `venv` 目录一起拷贝过去、或者下载离线安装包 `ocr_offline_pack.zip` 在新电脑上运行 `install_offline.bat` 即可。

## 技术栈

- **OCR**: PaddleOCR 2.x (PP-OCRv4)
- **AI**: OpenAI 兼容接口（Deepseek / Kimi / 通义千问 等）
- **GUI**: Tkinter
- **自动化**: PyAutoGUI
- **图像**: OpenCV, Pillow

程序依赖大模型 API 来合并 OCR 文本碎片。支持所有 **OpenAI 兼容接口**（Deepseek、Kimi、通义千问、智谱等）。

**方式一**：启动程序后点击界面上的 **「AI 设置」** 按钮，选择服务商并填入 API Key，点「测试连接」验证。

**方式二**：手动编辑 `rpa_config.json`（首次运行后自动生成），填入：
```json
{
  "API_URL": "https://api.deepseek.com/v1",
  "API_KEY": "sk-你的密钥",
  "MODEL_NAME": "deepseek-chat"
}
```

> 注意：`API_URL` 填 Base URL（不含 `/chat/completions`），程序会自动拼接完整路径。

## 启动

```bash
pythonw main.py
# 或双击 start_rpa.bat
```

## 使用流程

1. 点击 **开始** → 框选左侧聊天列表区域
2. 自动识别列表中的候选人后，点击第一条记录
3. 在右侧详情页点击一次（激活焦点）→ 框选详情内容区域
4. 程序自动循环处理所有新候选人，结果保存在 `JD_Output/` 目录

## 快捷键

| 快捷键 | 功能 |
|---|---|
| `Ctrl + Shift + Alt + P` | 暂停 / 继续 |

## 项目结构

```
├── main.py              # GUI 控制台主入口
├── boss_actions.py      # 核心业务逻辑（列表解析、详情采集、缓存管理）
├── vision_engine.py     # PaddleOCR 视觉引擎（截图、OCR、鼠标键盘操作）
├── ai_service.py        # AI 大模型服务（文本去重、拼凑）
├── config.py            # 配置管理（区域坐标、API 设置）
├── screen_selector.py   # 屏幕区域框选工具
├── start_rpa.bat        # Windows 启动脚本（无黑框）
├── rpa_config.json      # 运行时配置（自动生成）
└── JD_Output/           # 采集结果输出目录
```

## 技术栈

- **OCR**: PaddleOCR 2.x (PP-OCRv4)
- **AI**: OpenAI 兼容接口（Deepseek / Kimi / 通义千问 等）
- **GUI**: Tkinter
- **自动化**: PyAutoGUI
- **图像**: OpenCV, Pillow
