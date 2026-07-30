import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import sys
import requests
import json
from boss_actions import BossActions


class TextRedirector:
    # 将 print 输出重定向到 ScrolledText 控件

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # 保留换行符以保证日志格式
        self.text_widget.insert('end', string)
        self.text_widget.see('end')  # 自动滚动到底部

    def flush(self):
        pass


class RPAGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("RPA 控制台")
        self.root.geometry("550x380")
        self.root.resizable(False, False)  # 禁止拉伸

        # 顶部按钮区域
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=6)

        self.btn_start = tk.Button(top_frame, text="开始", command=self.toggle_run, width=10)
        self.btn_start.pack(side=tk.LEFT, padx=4)
        self.btn_pause = tk.Button(top_frame, text="暂停", command=self.toggle_pause, width=10)
        self.btn_pause.pack(side=tk.LEFT, padx=4)

        # 重置按钮
        self.btn_reset = tk.Button(top_frame, text="重置区域", command=self.reset_regions, width=10)
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        self.btn_quit = tk.Button(top_frame, text="强制退出", command=self.safe_quit, width=10)
        self.btn_quit.pack(side=tk.LEFT, padx=4)

        # AI 设置按钮
        self.btn_ai_settings = tk.Button(top_frame, text="AI 设置", command=self.open_ai_settings, width=10, bg="#8e44ad", fg="white")
        self.btn_ai_settings.pack(side=tk.LEFT, padx=4)

        # 日志显示区域
        self.log_area = scrolledtext.ScrolledText(self.root, height=12, wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # 底部状态栏，显示当前坐标
        self.lbl_status = tk.Label(self.root, text="", fg="gray", anchor='w', font=("微软雅黑", 8))
        self.lbl_status.pack(fill=tk.X, padx=6, pady=(0, 6))
        self.update_region_status()  # 初始化显示

        # 注册全局快捷键 Ctrl+Shift+Alt+P
        try:
            import keyboard
            keyboard.add_hotkey('ctrl+shift+alt+p', self.toggle_pause)
            print("✅ 全局快捷键 Ctrl+Shift+Alt+P 已注册，随时可按此键暂停/继续")
        except Exception as e:
            print(f"⚠️ 快捷键注册失败（可能需管理员权限）: {e}")

        # 状态变量
        self.is_running = False
        self.is_paused = False
        self.boss = BossActions()

        # 注入 GUI 控制器到业务层
        import boss_actions
        boss_actions.gui_controller = self

        # 保存原始 stdout，重定向 print 到日志框
        self._original_stdout = sys.stdout
        sys.stdout = TextRedirector(self.log_area)

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.safe_quit)

    def safe_quit(self):
        # 释放全局快捷键
        try:
            import keyboard
            keyboard.unhook_all()
        except Exception:
            pass
        # 安全退出：恢复 stdout、停止任务、销毁窗口
        self.is_running = False
        sys.stdout = self._original_stdout
        print("RPA 控制台已退出")  # 回到终端输出
        self.root.destroy()

    def toggle_run(self):
        if not self.is_running:
            self.is_running = True
            self.btn_start.config(state='disabled')  # 运行中禁用开始按钮
            threading.Thread(target=self.run_rpa, daemon=True).start()
        else:
            self.is_running = False
            self.btn_start.config(state='normal')

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="继续")
            print("\n⏸️ 程序已暂停 (按 Ctrl+Shift+P 继续)")
        else:
            self.btn_pause.config(text="暂停")
            print("\n▶️ 程序继续运行")

    def update_region_status(self):
        # 从 config 读取最新坐标并显示
        from config import config
        list_c = config.region_list
        detail_c = config.region_detail
        status_text = f"列表区域: {list_c}  |  详情区域: {detail_c}"
        self.lbl_status.config(text=status_text)

    def reset_regions(self):
        from config import config
        if self.is_running:
            print("运行中无法重置，请先暂停或停止任务")
            return
        config.reset_regions()
        print("已清除区域配置，下次点击「开始」将重新框选")
        self.update_region_status()

    def open_ai_settings(self):
        AISettingsWindow(self.root)

    def run_rpa(self):
        try:
            print("开始执行任务...")
            self.update_region_status()  # 框选完后立刻刷新底部状态栏
            self.boss.run()
            print("任务全部完成！")
        except Exception as e:
            print(f"任务中断报错: {str(e)}")
        finally:
            self.is_running = False
            # 用 after 确保在 GUI 线程更新
            self.root.after(0, lambda: self.btn_start.config(text="开始", state='normal'))


class AISettingsWindow:
    # AI 大模型设置弹窗
    def __init__(self, master):
        from config import config

        self.top = tk.Toplevel(master)
        self.top.title("AI 大模型设置")
        self.top.geometry("450x350")
        self.top.grab_set()  # 模态窗口

        tk.Label(self.top, text="选择 AI 服务商:").pack(pady=(10, 0))
        self.provider_var = tk.StringVar()
        self.provider_combobox = ttk.Combobox(self.top, textvariable=self.provider_var, state="readonly", width=30)
        self.provider_combobox['values'] = list(config.AI_PROVIDERS.keys())
        self.provider_combobox.pack(pady=5)
        self.provider_combobox.bind("<<ComboboxSelected>>", self.on_provider_change)

        tk.Label(self.top, text="API 地址 (Base URL):").pack()
        self.url_entry = tk.Entry(self.top, width=45)
        self.url_entry.pack(pady=5)

        tk.Label(self.top, text="模型名称:").pack()
        self.model_entry = tk.Entry(self.top, width=45)
        self.model_entry.pack(pady=5)

        tk.Label(self.top, text="API Key:").pack()
        self.key_entry = tk.Entry(self.top, width=45, show="*")  # 密码模式
        self.key_entry.pack(pady=5)

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="测试连接", command=self.test_connection, bg="#2980b9", fg="white", width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="保存配置", command=self.save_settings, bg="#27ae60", fg="white", width=12).pack(side=tk.LEFT, padx=10)

        self.load_current_settings()

    def load_current_settings(self):
        from config import config
        current_url = config.API_URL
        matched_provider = "自定义"
        for name, info in config.AI_PROVIDERS.items():
            if info['url'] == current_url:
                matched_provider = name
                break

        self.provider_var.set(matched_provider)
        self.url_entry.insert(0, config.API_URL)
        self.model_entry.insert(0, config.MODEL_NAME)
        self.key_entry.insert(0, config.API_KEY)

    def on_provider_change(self, event):
        from config import config
        provider = self.provider_var.get()
        info = config.AI_PROVIDERS.get(provider, {})
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, info.get("url", ""))
        self.model_entry.delete(0, tk.END)
        self.model_entry.insert(0, info.get("model", ""))

    def test_connection(self):
        base_url = self.url_entry.get().strip().rstrip('/')
        api_key = self.key_entry.get().strip()
        model = self.model_entry.get().strip()

        if not base_url or not api_key or not model:
            messagebox.showerror("错误", "请先填写 URL、模型和 API Key！")
            return

        try:
            test_url = f"{base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5
            }

            response = requests.post(test_url, headers=headers, json=payload, timeout=15)

            if response.status_code == 200:
                messagebox.showinfo("成功", f"连接成功！\n服务商响应正常。\n模型: {model}")
            elif response.status_code == 401:
                messagebox.showerror("失败", "认证失败！\nAPI Key 无效或已过期。")
            else:
                error_msg = response.json().get("error", {}).get("message", response.text)
                messagebox.showwarning("警告", f"返回状态码: {response.status_code}\n信息: {error_msg}")

        except requests.exceptions.Timeout:
            messagebox.showerror("错误", "请求超时，请检查网络或代理设置。")
        except Exception as e:
            messagebox.showerror("错误", f"连接异常:\n{str(e)}")

    def save_settings(self):
        from config import config
        config.API_URL = self.url_entry.get().strip().rstrip('/')
        config.API_KEY = self.key_entry.get().strip()
        config.MODEL_NAME = self.model_entry.get().strip()
        config.save_config()
        messagebox.showinfo("成功", "配置已保存！")
        self.top.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RPAGUI(root)
    root.mainloop()
