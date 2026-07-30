import json
import os


class ConfigManager:

    # 预设的 AI 服务商列表
    AI_PROVIDERS = {
        "OpenAI": {"url": "https://api.openai.com/v1", "model": "gpt-3.5-turbo"},
        "Deepseek (深度求索)": {"url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
        "Moonshot (Kimi)": {"url": "https://api.moonshot.cn/v1", "model": "moonshot-v1-8k"},
        "智谱 AI (GLM)": {"url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4"},
        "通义千问 (Qwen)": {"url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-turbo"},
        "自定义": {"url": "", "model": ""}
    }

    def __init__(self, file_path='rpa_config.json'):
        self.file_path = file_path
        # 默认参数
        self.BOSS_绿展开RGB = (0, 179, 138)
        self.滚动等待秒数 = 1.5
        self.API_URL = "https://api.deepseek.com"
        self.API_KEY = "sk-88e89e90f96747398dd4d9c5f3889e5d"
        self.MODEL_NAME = "deepseek-v4-flash"  # 模型名，按服务商填写
        self.region_list = (0, 0, 0, 0)  # 统一用 tuple，避免类型混乱
        self.region_detail = (0, 0, 0, 0)
        self.detail_click_pos = (0, 0)  # 详情页激活点击坐标

    def save_config(self):
        data = {
            "BOSS_绿展开RGB": self.BOSS_绿展开RGB,
            "滚动等待秒数": self.滚动等待秒数,
            "API_URL": self.API_URL,
            "API_KEY": self.API_KEY,
            "MODEL_NAME": self.MODEL_NAME,
            "region_list": self.region_list,
            "region_detail": self.region_detail,
            "detail_click_pos": self.detail_click_pos,
        }
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def load_config(self):
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"读取配置失败，使用默认值: {e}")
            return

        self.BOSS_绿展开RGB = tuple(data.get("BOSS_绿展开RGB", self.BOSS_绿展开RGB))
        self.滚动等待秒数 = data.get("滚动等待秒数", self.滚动等待秒数)
        self.API_URL = data.get("API_URL", self.API_URL)
        self.API_KEY = data.get("API_KEY", self.API_KEY)
        self.MODEL_NAME = data.get("MODEL_NAME", self.MODEL_NAME)
        self.region_list = tuple(data.get("region_list", self.region_list))
        self.region_detail = tuple(data.get("region_detail", self.region_detail))
        self.detail_click_pos = tuple(data.get("detail_click_pos", self.detail_click_pos))

    def set_region(self, name, x1, y1, x2, y2):
        coords = (x1, y1, x2, y2)
        if name == 'list':
            self.region_list = coords
        elif name == 'detail':
            self.region_detail = coords
        self.save_config()

    def is_region_valid(self, name):
        # 检查区域坐标是否已配置（非全零）
        coords = self.region_list if name == 'list' else self.region_detail
        return len(coords) == 4 and any(v != 0 for v in coords)

    def reset_regions(self):
        # 重置区域坐标
        self.region_list = (0, 0, 0, 0)
        self.region_detail = (0, 0, 0, 0)
        self.detail_click_pos = (0, 0)
        self.save_config()


# 全局配置实例
config = ConfigManager()
config.load_config()
