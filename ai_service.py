import requests
import json
from config import config


class AIService:

    def _validate_config(self):
        if not config.API_URL or not config.API_KEY:
            raise RuntimeError("API_URL 或 API_KEY 未配置，请在 config.py 或 rpa_config.json 中填写")

    def clean_and_merge_text(self, text_list):
        # 拼接 OCR 文本片段，发送给大模型去重拼凑
        self._validate_config()
        raw_text = "\n".join(text_list)
        if len(raw_text) > 30000:
            raw_text = raw_text[:30000]  # 截断防止超出 token 限制
            print("  文本过长已截断至30000字符")

        headers = {"Authorization": f"Bearer {config.API_KEY}"}
        payload = {
            "model": config.MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": f"以下是多张重叠截图的OCR文本，请去重并拼凑成完整通顺的JD，只返回纯文本。\n\n{raw_text}"
                }
            ],
            "temperature": 0.3
        }
        try:
            resp = requests.post(config.API_URL, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content.strip()
        except requests.exceptions.Timeout:
            raise RuntimeError("AI API 请求超时，请检查网络或 API 服务状态")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"无法连接到 {config.API_URL}，请检查 API_URL 配置")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"AI API 返回错误 ({resp.status_code}): {resp.text[:200]}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise RuntimeError(f"AI API 返回格式异常: {e}")

    def check_duplicate(self, text1, text2):
        # 判断两段文本是否描述同一岗位
        self._validate_config()
        headers = {"Authorization": f"Bearer {config.API_KEY}"}
        payload = {
            "model": config.MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": f"判断文本A和文本B是否描述同一个岗位，只返回 '是' 或 '否'。\n\n文本A: {text1}\n\n文本B: {text2}"
                }
            ],
            "temperature": 0.0
        }
        try:
            resp = requests.post(config.API_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return "是" in answer
        except Exception as e:
            print(f"查重请求失败: {e}")
            return False  # 失败时默认不重复，避免误删
