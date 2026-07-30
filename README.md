# BossjdRPA

BOSS直聘 RPA 自动化工具，基于 PaddleOCR + AI 大模型，自动采集、解析和保存招聘职位 JD 描述。

## 功能

- **智能列表识别**：PaddleOCR 多策略解析聊天列表，自动识别候选人姓名和公司
- **详情页采集**：自动点击进入详情页，滚动截取完整 JD 文本
- **AI 合并去重**：调用大模型 API 将多段 OCR 碎片拼凑成通顺的完整 JD
- **指纹去重**：自动记录已处理候选人，避免重复采集
- **桌面控制台**：tkinter GUI 界面，实时日志显示，全局快捷键暂停/继续

## 环境要求

- **操作系统**：仅限 Windows（依赖 PyAutoGUI 和 keyboard 库的 Windows API）
- **Python**：3.8 ~ 3.12
- **前置条件**：BOSS 直聘聊天页面需在屏幕上可见（网页版或桌面客户端均可）
- **首次启动**会自动下载 PaddleOCR 模型文件（约 100MB，仅一次），需要网络连接

## 安装

```bash
# 1. 克隆仓库
git clone https://github.com/Zweiehn/BossjdRPA.git
cd BossjdRPA

# 2. 安装依赖
pip install pyautogui pillow numpy opencv-python requests
pip install paddlepaddle==2.6.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install "paddleocr<3.0" -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install keyboard -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 配置 AI API

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
