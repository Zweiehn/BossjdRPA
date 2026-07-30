import os
import json
import time
import re
import pyautogui
from vision_engine import VisionEngine
from ai_service import AIService
from config import config
from screen_selector import RegionSelector

# GUI 控制器引用，由 main.py 注入
gui_controller = None

CACHE_FILE = "processed_cache.json"
BACKUP_FILE = "processed_cache.json.bak"
OUTPUT_DIR = "JD_Output"


class CacheManager:
    @staticmethod
    def load_cache():
        # 加载缓存，如果主文件损坏则从备份恢复
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                print("⚠️ 主缓存文件损坏，尝试从备份恢复...")
                if os.path.exists(BACKUP_FILE):
                    import shutil
                    shutil.copy(BACKUP_FILE, CACHE_FILE)
                    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                        return json.load(f)
        return {}

    @staticmethod
    def backup_cache():
        # 启动时自动备份一次缓存
        import shutil
        if os.path.exists(CACHE_FILE):
            shutil.copy(CACHE_FILE, BACKUP_FILE)

    @staticmethod
    def save_cache(cache_data):
        # 保存缓存到文件
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def generate_fingerprint(raw_text):
        # 生成特征指纹：提取姓名和公司名，忽略时间和干扰词
        noise_words = ["招聘者", "招聘", "HR", "人事", "经理", "总监", "专员", "主管", "顾问", "先生", "女士"]
        clean_text = raw_text
        for word in noise_words:
            clean_text = clean_text.replace(word, "")

        if "|" in clean_text or "丨" in clean_text:
            parts = re.split(r'[|丨]', clean_text)
            if len(parts) >= 2:
                name = parts[0].strip()
                company = parts[1].strip().split(" ")[0]
                return f"{name}_{company}"

        return clean_text.strip()[:10]


class BossActions:

    def __init__(self):
        self.engine = VisionEngine()
        self.ai = AIService()

    def init_regions(self):
        # 只检查列表区域
        if not config.is_region_valid('list'):
            print("请框选聊天列表区域")
            coords = RegionSelector().select()
            if coords != (0, 0, 0, 0):
                config.set_region('list', *coords)

    def _scroll_list(self):
        # 滚动左侧聊天列表
        x1, y1, x2, y2 = config.region_list
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        pyautogui.moveTo(center_x, center_y, duration=0.2)
        pyautogui.scroll(-600)  # 向下滚动较多刻度
        time.sleep(2)

    def run(self):
        self.init_regions()

        # 初始化缓存系统
        CacheManager.backup_cache()
        archived_cache = CacheManager.load_cache()
        print(f"📦 已加载缓存，历史记录 {len(archived_cache)} 条。")

        no_new_count = 0  # 防死循环计数器

        while gui_controller and gui_controller.is_running:
            while gui_controller and gui_controller.is_paused:
                time.sleep(0.5)

            print("\n--- 开始扫描列表 ---")

            # 1. 截图列表与多策略识别
            x1, y1, x2, y2 = config.region_list
            img = self.engine.capture_area(x1, y1, x2, y2)
            ocr_data = self.engine.ocr_get_data(img)

            boxes = []
            for i in range(len(ocr_data['text'])):
                t = ocr_data['text'][i].strip()
                if not t:
                    continue
                cx = ocr_data['left'][i] + ocr_data['width'][i] // 2 + x1
                cy = ocr_data['top'][i] + ocr_data['height'][i] // 2 + y1
                boxes.append({'text': t, 'x': cx, 'y': cy})

            # 策略 A：同行拼接找特征词
            keywords = ["先生", "女士", "招聘", "HR", "人事", "经理", "总监", "专员", "主管", "顾问"]
            lines = {}
            for b in boxes:
                matched_y = None
                for line_y in lines.keys():
                    if abs(b['y'] - line_y) < 20:
                        matched_y = line_y
                        break
                if matched_y is None:
                    lines[b['y']] = [b]
                else:
                    lines[matched_y].append(b)

            all_items = []
            for line_y, line_boxes in lines.items():
                line_boxes.sort(key=lambda b: b['x'])
                full_text = "".join([b['text'] for b in line_boxes])
                if any(k in full_text for k in keywords):
                    all_items.append({'raw_text': full_text, 'x': line_boxes[0]['x'], 'y': line_boxes[0]['y']})

            # 策略 B：独立找分隔符
            for b in boxes:
                if "|" in b['text'] or "丨" in b['text']:
                    all_items.append({'raw_text': b['text'], 'x': b['x'], 'y': b['y']})

            # 坐标去重排序
            all_items.sort(key=lambda item: item['y'])
            items = []
            for item in all_items:
                if items and abs(item['y'] - items[-1]['y']) < 20:
                    continue
                items.append(item)

            # 生成特征指纹并比对缓存
            new_items = []
            for item in items:
                fingerprint = CacheManager.generate_fingerprint(item['raw_text'])
                item['fingerprint'] = fingerprint

                if fingerprint and fingerprint not in archived_cache:
                    new_items.append(item)
                else:
                    print(f"  ⏭️ 跳过已缓存: {fingerprint}")

            if not new_items:
                no_new_count += 1
                if no_new_count >= 3:
                    print("⚠️ 连续 3 次未发现新候选人，列表可能到底。任务自动暂停。")
                    if gui_controller:
                        gui_controller.is_paused = True
                    no_new_count = 0
                    continue

                print("当前屏幕无新候选人，向下滚动...")
                self._scroll_list()
                continue

            no_new_count = 0
            print(f"✅ 本次新发现 {len(new_items)} 位候选人")

            # 逐个处理详情
            for i, item in enumerate(new_items):
                if gui_controller and not gui_controller.is_running:
                    break
                while gui_controller and gui_controller.is_paused:
                    time.sleep(0.5)

                print(f"处理: {item['fingerprint']} -> 坐标({item['x']}, {item['y']})")
                self.engine.move_and_click(item['x'], item['y'])
                time.sleep(1.5)

                # 引导点击与框选 (仅第一次)
                if config.detail_click_pos == (0, 0):
                    print("请在右侧详情页内【点击一次鼠标】...")
                    click_xy = RegionSelector().select_click()
                    if click_xy != (0, 0):
                        config.detail_click_pos = click_xy
                        config.save_config()
                        self.engine.move_and_click(*click_xy)
                        time.sleep(1.5)
                    else:
                        continue

                if not config.is_region_valid('detail'):
                    print("请框选右侧职位详情区域...")
                    coords = RegionSelector().select()
                    if coords != (0, 0, 0, 0):
                        config.set_region('detail', *coords)
                    else:
                        continue

                # 每次循环必须激活焦点
                if config.detail_click_pos != (0, 0):
                    self.engine.move_and_click(*config.detail_click_pos)
                    time.sleep(0.8)

                # 执行详情提取，传入指纹作为文件名
                self.process_detail(item['fingerprint'])

                # 处理完成后，立刻写入缓存防重
                timestamp = time.strftime("%m%d-%H%M")
                archived_cache[item['fingerprint']] = f"{OUTPUT_DIR}/{item['fingerprint']}_{timestamp}.txt"
                CacheManager.save_cache(archived_cache)

                self.engine.press_key('ctrl+w')
                time.sleep(1)

            print("当前批次处理完毕，滚动列表加载下一页...")
            self._scroll_list()

        print("批量处理任务已停止。")

    def process_detail(self, record_name="未命名"):
        text_fragments = []
        text_seen = set()
        rd = config.region_detail
        if not all(v > 0 for v in rd):
            print("详情区域坐标无效，跳过")
            return

        time.sleep(0.5)
        scroll_count = 0

        # 底部结束语标志
        end_keywords = ["看到该职位的人还看了", "精选职位"]

        while True:
            if gui_controller and not gui_controller.is_running:
                return
            while gui_controller and gui_controller.is_paused:
                time.sleep(0.5)

            scroll_count += 1
            print(f"  [详情滚动] 第 {scroll_count} 次...")

            try:
                detail_img = self.engine.capture_area(*rd)
                detail_ocr = self.engine.ocr_get_data(detail_img)

                current_texts = []
                for text in detail_ocr['text']:
                    t = text.strip()
                    if t:
                        current_texts.append(t)
                        if t not in text_seen:
                            text_seen.add(t)
                            text_fragments.append(t)

                # 检测是否到底部
                full_screen_text = "".join(current_texts)
                if any(kw in full_screen_text for kw in end_keywords):
                    print("  识别到底部特征词，停止滚动。")
                    break

                # 兼容"展开"和"查看全部"按钮
                expand_pos = self.engine.find_text_center(detail_ocr, '展开')
                if expand_pos is None:
                    expand_pos = self.engine.find_text_center(detail_ocr, '查看全部')

                if expand_pos is not None:
                    ex, ey = expand_pos
                    abs_ex = rd[0] + ex
                    abs_ey = rd[1] + ey
                    try:
                        color = self.engine.get_pixel_color(abs_ex, abs_ey)
                        r, g, b = color
                        # 绿色字体判断
                        if abs(r - 0) < 30 and abs(g - 179) < 50 and abs(b - 138) < 50:
                            print(f"  发现绿色展开/查看全部按钮，点击 ({abs_ex}, {abs_ey})")
                            self.engine.move_and_click(abs_ex, abs_ey)
                            time.sleep(0.8)
                            detail_img = self.engine.capture_area(*rd)
                            detail_ocr = self.engine.ocr_get_data(detail_img)
                            for text in detail_ocr['text']:
                                t = text.strip()
                                if t and t not in text_seen:
                                    text_seen.add(t)
                                    text_fragments.append(t)
                    except Exception:
                        pass

                if scroll_count > 30:
                    print("  达到最大滚动次数(30)，强制停止。")
                    break

                self.engine.scroll_down()

            except Exception as e:
                print(f"  截图或识别异常: {e}")
                time.sleep(1)

        # 限制碎片数量
        if len(text_fragments) > 500:
            text_fragments = text_fragments[:500]
            print("  文本碎片过多，已截断至500条")

        if not text_fragments:
            print(f"  未获取到详情文本，跳过保存")
            return

        # AI 合并去重
        try:
            final_jd = self.ai.clean_and_merge_text(text_fragments)
        except Exception as e:
            print(f"  AI 合并失败: {e}，保存原始文本")
            final_jd = "\n".join(text_fragments)

        # 核心清洗：砍掉底部推荐信息
        cut_off_phrase = "看过该职位的人还看了"
        if cut_off_phrase in final_jd:
            final_jd = final_jd.split(cut_off_phrase)[0].strip()
            print("  已截断底部推荐信息。")

        safe_name = re.sub(r'[\\/*?:"<>|]', "", record_name)
        timestamp = time.strftime("%m%d-%H%M")

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        file_path = os.path.join(OUTPUT_DIR, f"{safe_name}_{timestamp}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_jd)
        print(f"💾 已保存: {file_path}")
