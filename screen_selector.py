import tkinter as tk
import sys


class RegionSelector:
    # 屏幕区域选择器：全屏半透明遮罩，拖拽拉框选择区域，返回矩形坐标

    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)  # 全屏
        self.root.attributes("-topmost", True)  # 置顶
        self.root.attributes("-alpha", 0.3)  # 透明度
        self.root.configure(bg="black")  # 背景色

        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", self.on_cancel)  # ESC 取消选择

        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        self.coords = (0, 0, 0, 0)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        # 创建红色边框矩形（不填充）
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_drag(self, event):
        # 容错：如果 rect_id 不存在则重新创建
        if self.rect_id is None:
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y,
                event.x, event.y,
                outline="red", width=2
            )
            return
        # 删除旧矩形，按当前坐标重绘
        self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            event.x, event.y,
            outline="red", width=2
        )

    def on_release(self, event):
        # 计算最终坐标，确保 x1 < x2, y1 < y2
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        # 忽略过小的选区（可能是误点击）
        if x2 - x1 < 10 and y2 - y1 < 10:
            self.coords = (0, 0, 0, 0)
        else:
            self.coords = (x1, y1, x2, y2)
        self.root.destroy()

    def on_cancel(self, event):
        # ESC 取消，返回全零坐标
        self.coords = (0, 0, 0, 0)
        self.root.destroy()

    def select(self) -> tuple:
        self.root.mainloop()
        return self.coords


    def select_click(self):
        # 引导用户进行一次鼠标点击，返回点击的 (x, y) 坐标
        click_root = tk.Tk()
        click_root.attributes('-fullscreen', True, '-alpha', 0.3)
        click_root.attributes('-topmost', True)
        click_root.configure(bg='gray')

        label = tk.Label(click_root, text="请在右侧详情页内点击一次鼠标（作为激活焦点）",
                         font=("微软雅黑", 24), fg="blue", bg="gray")
        label.pack(expand=True)

        click_pos = []

        def on_click(event):
            click_pos.append((event.x_root, event.y_root))
            click_root.destroy()

        click_root.bind('<Button-1>', on_click)
        click_root.bind('<Escape>', lambda e: click_root.destroy())
        click_root.mainloop()

        if click_pos:
            return click_pos[0]
        return (0, 0)


if __name__ == "__main__":
    selector = RegionSelector()
    result = selector.select()
    print(result)
