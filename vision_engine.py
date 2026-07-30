import pyautogui
import time
import random
from config import config
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR


class VisionEngine:

    def __init__(self):
        # PaddleOCR 2.x + PaddlePaddle 2.6 无 oneDNN 兼容问题
        self.ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)

    def capture_area(self, x1, y1, x2, y2):
        # 截图指定区域，返回 PIL Image
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h <= 0:
            raise ValueError(f"截图区域无效: ({x1},{y1},{x2},{y2})")
        return pyautogui.screenshot(region=(x1, y1, w, h))

    def ocr_get_data(self, image):
        # PaddleOCR 识别，结果转为 Tesseract 兼容字典格式
        data = {'text': [], 'left': [], 'top': [], 'width': [], 'height': []}
        img_array = np.array(image)
        # 确保 RGB 三通道
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]

        try:
            result = self.ocr.ocr(img_array, cls=False)
        except Exception as e:
            print(f"PaddleOCR 识别失败: {e}")
            return data

        if not result or result[0] is None:
            return data

        # PaddleOCR 2.x 格式: [[[box, (text, score)], ...]]
        for line in result[0]:
            try:
                box = line[0]  # 四点坐标 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                text = line[1][0]  # 文字内容
                if not text or not text.strip():
                    continue

                x_coords = [p[0] for p in box]
                y_coords = [p[1] for p in box]
                left = int(min(x_coords))
                top = int(min(y_coords))
                width = int(max(x_coords) - left)
                height = int(max(y_coords) - top)
            except (IndexError, TypeError, ValueError):
                continue

            data['text'].append(text)
            data['left'].append(left)
            data['top'].append(top)
            data['width'].append(width)
            data['height'].append(height)

        return data

    def find_text_in_same_line(self, ocr_data, keyword1, keyword2):
        # 查找同行内两段文字，返回整体中心坐标
        n = len(ocr_data['text'])
        if n == 0:
            return None

        cx1, cy1 = None, None
        for i in range(n):
            if keyword1 in ocr_data['text'][i]:
                cx1 = ocr_data['left'][i] + ocr_data['width'][i] // 2
                cy1 = ocr_data['top'][i] + ocr_data['height'][i] // 2
                break
        if cx1 is None:
            return None

        cx2, cy2 = None, None
        for i in range(n):
            if keyword2 in ocr_data['text'][i]:
                cx2 = ocr_data['left'][i] + ocr_data['width'][i] // 2
                cy2 = ocr_data['top'][i] + ocr_data['height'][i] // 2
                break
        if cx2 is None:
            return None

        if abs(cy1 - cy2) < 15:
            return ((cx1 + cx2) // 2, cy1)
        return None

    def find_text_center(self, ocr_data, keyword):
        # 查找包含 keyword 的文字块中心坐标
        for i in range(len(ocr_data['text'])):
            if keyword in ocr_data['text'][i]:
                cx = ocr_data['left'][i] + ocr_data['width'][i] // 2
                cy = ocr_data['top'][i] + ocr_data['height'][i] // 2
                return (cx, cy)
        return None

    def get_pixel_color(self, x, y):
        try:
            img = pyautogui.screenshot(region=(x, y, 1, 1))
            return img.getpixel((0, 0))
        except Exception:
            return (0, 0, 0)

    def move_and_click(self, x, y):
        if x <= 0 or y <= 0:
            return
        try:
            pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.5))
            pyautogui.click()
        except pyautogui.FailSafeException:
            print(f"鼠标移动失败 (x={x}, y={y})")

    def scroll_down(self):
        # 自动将鼠标移动到详情框选区域的中心点进行滚动
        x1, y1, x2, y2 = config.region_detail
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        try:
            pyautogui.moveTo(center_x, center_y, duration=0.2)
            pyautogui.scroll(-300)
        except Exception:
            pass
        time.sleep(config.滚动等待秒数)

    def press_key(self, keys_str):
        try:
            pyautogui.hotkey(*keys_str.split('+'))
        except Exception as e:
            print(f"按键失败 ({keys_str}): {e}")
