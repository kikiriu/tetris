import tkinter as tk
from config import BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE

class TetrisGUI:
    def __init__(self, root, board, current_shape, current_position, pixel_offset):
        """初始化GUI"""
        self.root = root
        self.board = board
        self.current_shape = current_shape
        self.current_position = current_position
        self.pixel_offset = pixel_offset

        # 创建画布
        self.canvas = tk.Canvas(self.root, width=BOARD_WIDTH * CELL_SIZE, height=BOARD_HEIGHT * CELL_SIZE)
        self.canvas.pack(pady=20)

        # 创建时间和等级标签
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(side=tk.TOP, fill=tk.X)

        self.time_label = tk.Label(self.info_frame, text="Time: 0s", font=('Arial', 14))
        self.time_label.pack(side=tk.RIGHT, padx=10)

        self.level_label = tk.Label(self.info_frame, text="Level: 1", font=('Arial', 14))
        self.level_label.pack(side=tk.LEFT, padx=10)

    def bind_keys(self, handler):
        """绑定按键事件处理器"""
        self.root.bind("<KeyPress>", handler)

    def update_board(self, board, current_shape, current_position, pixel_offset, color):
        """更新游戏板"""
        self.canvas.delete(tk.ALL)
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if board[y][x]:
                    self.draw_cell(x, y, board[y][x])
        for y, row in enumerate(current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(current_position[1] + x, current_position[0] + y + pixel_offset / CELL_SIZE, color)

    def draw_cell(self, x, y, color):
        """绘制单个单元格"""
        self.canvas.create_rectangle(
            x * CELL_SIZE,
            y * CELL_SIZE,
            (x + 1) * CELL_SIZE,
            (y + 1) * CELL_SIZE,
            fill=color,
            outline="black"
        )

    def update_time(self, elapsed_time):
        """更新时间标签"""
        self.time_label.config(text=f"Time: {elapsed_time}s")

    def update_level(self, level):
        """更新等级标签"""
        self.level_label.config(text=f"Level: {level}")

    def clear_board(self):
        """清空游戏板"""
        self.canvas.delete(tk.ALL)
