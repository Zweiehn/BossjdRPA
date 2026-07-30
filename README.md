# BossjdRPA

BOSS直聘 RPA 自动化工具，基于 PaddleOCR + AI 大模型，自动采集、解析和保存招聘职位 JD 描述。

## 目录

- [首次使用（必读）](#首次使用必读)
- [两个 bat 的分工](#两个-bat-的分工)
- [离线安装（无网络环境）](#离线安装无网络环境)
- [使用流程](#使用流程)
- [从零手动搭建（高级）](#从零手动搭建高级)
- [快捷键](#快捷键)
- [项目结构](#项目结构)
- [常见问题](#常见问题)
- [技术栈](#技术栈)

---

## 首次使用（必读）

无论你的电脑有没有装 Python，拿到项目后只需做**一件事**：

**双击 `setup_and_run.bat`**

它会自动完成以下全部工作：

| 步骤 | 做了什么 |
|---|---|
| ① | 检测你的电脑有没有 Python 3.12 |
| ② | 没有就**自动下载并安装完整 Python 3.12**（约 25 MB，含 tkinter GUI 支持） |
| ③ | 创建虚拟环境（`venv/`），隔离项目依赖 |
| ④ | 安装全部 Python 依赖包（优先用离线包，没有就走网络） |
| ⑤ | 安装 PaddleOCR 中文识别模型 |
| ⑥ | 启动 RPA 控制台 |

**整个过程全自动，你只需要双击一次，之后再也不需要这个文件。** 首次运行需要网络下载 Python 和依赖（约 300 MB），之后的使用不需要网络。

## 两个 bat 的分工

| 文件 | 什么时候用 | 要不要网络 |
|---|---|---|
| `setup_and_run.bat` | **只在新电脑上跑一次** | 首次需要（下载 Python + 依赖），有离线包则不需要 |
| `start_rpa.bat` | **日常启动** | 不需要 |

记住这条规则就够：**新电脑跑 `setup_and_run`，日常用 `start_rpa`。**

## 离线安装（无网络环境）

如果目标电脑**完全没有网络**，先在**有网络的电脑**上：

1. 从 [Releases](https://github.com/Zweiehn/BossjdRPA/releases) 下载 `ocr_offline_pack.zip`（约 314 MB）
2. 把 `ocr_offline_pack.zip` 解压到项目目录（和 `main.py` 同级），目录结构如下：

```
BossjdRPA/
├── main.py
├── setup_and_run.bat
├── start_rpa.bat
├── ocr_offline_pack/          ← 离线包解压在这儿
│   ├── wheels/                ← 所有 .whl 文件
│   └── models/                ← PP-OCRv4 中文模型
└── ...
```

3. 把整个 `BossjdRPA` 文件夹拷贝到目标电脑
4. 双击 `setup_and_run.bat`（仍需首次网络下载 Python 安装器 ~25 MB；如果连这个网络都没有，先手动装 Python 3.12 再跑）

---

## 从零手动搭建（高级）

> 正常情况下你不需要看这一节——`setup_and_run.bat` 已经全自动了。
> 以下适合想理解每一步在做什么、或者 bat 脚本无法运行时手动排查的人。

### 环境要求

- **操作系统**：仅限 Windows 10 / 11
- **Python**：必须是 **3.12.x**（PaddlePaddle 最高只支持到 3.12）
- **内存**：建议 8 GB 以上
- **前置条件**：BOSS 直聘聊天页面需在屏幕上可见

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

**方式 A — 直接下载 ZIP（不需要 Git）：**

1. 浏览器打开 https://github.com/Zweiehn/BossjdRPA
2. 点击绿色的 **「<> Code」** 按钮 → **「Download ZIP」**
3. 将下载的 `BossjdRPA-main.zip` 解压到你想放的目录，例如 `D:\BossjdRPA`
4. 解压后的文件夹应该包含 `main.py`、`setup_and_run.bat` 等文件

**方式 B — 使用 Git（如果你装了 Git）：**

```bash
git clone https://github.com/Zweiehn/BossjdRPA.git
cd BossjdRPA
```

**（可选）下载离线依赖包：**

从 [Releases](https://github.com/Zweiehn/BossjdRPA/releases) 下载 `ocr_offline_pack.zip`，解压到项目目录（和 `main.py` 同级）。目录结构会变成：

```
BossjdRPA/
├── main.py
├── setup_and_run.bat
├── ocr_offline_pack/
│   ├── wheels/             # 所有 .whl 依赖文件
│   ├── models/             # PP-OCRv4 中文模型
│   └── install_offline.bat
└── ...
```

有这个包就可以全程离线安装。

### 第三步：创建虚拟环境

虚拟环境能将这个项目的依赖与系统隔离，互不污染。按 `Win + R`，输入 `cmd` 回车，在黑色窗口中输入：

```
cd D:\BossjdRPA          # 进入项目目录（改成你实际的路径）
python -m venv venv      # 创建虚拟环境，会生成一个 venv 文件夹
```

激活虚拟环境：

```
venv\Scripts\activate
```

激活后，命令行前面会出现 `(venv)` 字样，表示虚拟环境已生效。
> 每次打开新的 cmd 窗口运行本项目前，都要先 `cd` 到项目目录然后执行激活命令。

### 第四步：安装依赖

确保 `(venv)` 已激活（命令行前面有 `(venv)`），然后：

**在线安装（有网络）：**

```bash
pip install pyautogui pillow numpy opencv-python requests keyboard
pip install paddlepaddle==2.6.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install "paddleocr<3.0" -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**离线安装（已解压 ocr_offline_pack.zip 到项目目录）：**

直接双击 `ocr_offline_pack\install_offline.bat`，会自动完成依赖和模型安装。

### 第五步：验证安装

在 `(venv)` 激活状态下，依次运行以下命令，确保没有报错：

```bash
python -c "import pyautogui; print('pyautogui OK')"
python -c "from paddleocr import PaddleOCR; print('paddleocr OK')"
python -c "from PIL import Image; print('pillow OK')"
python -c "import cv2; print('opencv OK')"
```

全部显示 OK 表示环境就绪。

### 第六步：配置 AI API

程序依赖大模型 API 来合并 OCR 文本碎片，支持所有 **OpenAI 兼容接口**（Deepseek、Kimi、通义千问、智谱等）。

**方式一（推荐）：** 启动程序后，点击界面上的 **「AI 设置」** 按钮，选择服务商并填入 API Key，点「测试连接」验证。

**方式二：** 第一次运行程序后，项目目录会生成 `rpa_config.json`，用记事本打开，填入：

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

也可以直接双击项目目录下的 `setup_and_run.bat`，它会自动完成激活、检查依赖、启动。

---

## 使用流程

1. 打开 BOSS 直聘聊天页面，确保列表和右侧详情区域在屏幕上可见
2. 点击 RPA 控制台的 **「开始」** → 弹出全屏遮罩，用鼠标框选左侧聊天列表区域
3. 程序自动 OCR 识别候选人列表后，点击第一条记录进入详情
4. 弹出提示后，在右侧详情页内点击一次鼠标（程序记录这个位置用于后续激活焦点）
5. 再框选职位详情的内容区域（从岗位名称到底部）
6. 程序开始自动循环：点击候选人 → 激活详情页 → 滚动采集 JD → AI 合并 → 保存到 `JD_Output/`
7. 处理完当前屏幕后自动向下滚动列表，继续扫描新候选人

后续再次运行时，区域坐标和点击位置都已保存，无需重新框选。如果窗口位置变了，点击 **「重置区域」** 按钮即可重新配置。已处理过的候选人会自动跳过，不会重复采集。

## 快捷键

| 快捷键 | 功能 |
|---|---|
| `Ctrl + Shift + Alt + P` | 暂停 / 继续 |
| `ESC`（框选时） | 取消框选 |

## 项目结构

```
├── main.py                 # GUI 控制台主入口
├── boss_actions.py         # 核心业务逻辑（列表解析、详情采集、缓存管理）
├── vision_engine.py        # PaddleOCR 视觉引擎（截图、OCR、鼠标键盘操作）
├── ai_service.py           # AI 大模型服务（文本去重拼凑）
├── config.py               # 配置管理（区域坐标、API 设置）
├── screen_selector.py      # 屏幕区域框选工具
├── setup_and_run.bat       # 一键安装启动脚本（自动建 venv + 装依赖 + 启动）
├── start_rpa.bat           # 简单启动脚本（需要已有 venv）
├── rpa_config.json         # 运行时配置（自动生成，含 API Key，不要上传 GitHub）
├── processed_cache.json    # 已处理候选人缓存（防重复采集）
├── JD_Output/              # 采集结果输出目录
└── ocr_offline_pack/       # 离线依赖包（可选，从 Release 下载后解压在这里）
    ├── wheels/              #   所有 .whl 离线安装文件
    ├── models/              #   PP-OCRv4 中文模型
    └── install_offline.bat  #   离线安装脚本
```

## 常见问题

**Q: 运行时报错 "No module named 'xxx'"？**
A: 确认虚拟环境已激活（命令行有 `(venv)` 前缀），然后重新执行第四步安装依赖。

**Q: PaddleOCR 报错 "tuple index out of range"？**
A: Python 版本不对。必须使用 Python 3.12.x，用 `python --version` 检查。

**Q: 报错包含 "oneDNN" 或 "ConvertPirAttribute"？**
A: 安装了 PaddlePaddle 3.x 而不是 2.6.2。卸载后重装：`pip uninstall paddlepaddle paddleocr -y`，再执行第四步。

**Q: 快捷键 Ctrl+Shift+Alt+P 没反应？**
A: 以管理员身份运行 cmd 再启动程序，keyboard 库需要管理员权限才能注册全局热键。

**Q: 程序无法识别列表中的候选人？**
A: 检查 BOSS 直聘窗口是否在最前面、框选区域是否准确。查看控制台日志中 OCR 识别到的文字来排查。

**Q: 新电脑不想重新下载所有依赖？**
A: 从 Release 下载离线包 `ocr_offline_pack.zip`，解压到项目目录后双击 `setup_and_run.bat`，全程离线安装。或者直接把整个项目文件夹（含 `venv/`）拷贝到新电脑。

## 技术栈

- **OCR**: PaddleOCR 2.x (PP-OCRv4) + PaddlePaddle 2.6.2
- **AI**: OpenAI 兼容接口（Deepseek / Kimi / 通义千问 / 智谱 等）
- **GUI**: Tkinter + ScrolledText
- **自动化**: PyAutoGUI + keyboard
- **图像**: OpenCV + Pillow + NumPy
