import tkinter as tk
import time
from tkinter import messagebox, simpledialog
from gui import TetrisGUI
from config import BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE, INITIAL_DELAY, PIXELS_PER_FRAME, LINES_PER_LEVEL, SPEED_MULTIPLIER, SHAPES, RANKING_FILE
import random
import json

class TetrisGame:
    def __init__(self):
        """初始化游戏"""
        self.game_over_called = False
        self.root = tk.Tk()
        self.root.title("Tetris")

        # 设置窗口在屏幕中央
        self.center_window(BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE + 70)

        self.level = 1
        self.lines_cleared = 0
        self.drop_delay = INITIAL_DELAY
        self.pixel_offset = 0
        self.can_replace_shape = True
        self.is_paused = False
        self.pause_start_time = None

        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_shape = None
        self.current_position = [0, 0]

        # 初始化排行榜
        self.ranking = self.load_ranking()

        # 初始化GUI
        self.gui = TetrisGUI(self.root, self.board, self.current_shape, self.current_position, self.pixel_offset)
        self.gui.bind_keys(self.handle_key_press)

        # 创建开始菜单
        self.create_start_menu()

    def center_window(self, width, height):
        """将窗口置于屏幕中央"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_start_menu(self):
        """创建开始菜单"""
        self.start_menu = tk.Frame(self.root)
        self.start_menu.pack(expand=True)

        button_options = {'padx': 20, 'pady': 10, 'font': ('SimHei', 16, 'bold')}

        start_button = tk.Button(self.start_menu, text="开始游戏", command=self.start_game, **button_options)
        start_button.pack(pady=10)

        ranking_button = tk.Button(self.start_menu, text="查看排行榜", command=self.show_ranking, **button_options)
        ranking_button.pack(pady=10)

        quit_button = tk.Button(self.start_menu, text="退出游戏", command=self.root.quit, **button_options)
        quit_button.pack(pady=10)

        self.start_menu.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def create_pause_menu(self):
        """创建暂停菜单"""
        self.pause_menu = tk.Frame(self.root)
        self.pause_menu.pack(expand=True)

        button_options = {'padx': 20, 'pady': 10, 'font': ('SimHei', 16, 'bold')}

        resume_button = tk.Button(self.pause_menu, text="继续游戏", command=self.resume_game, **button_options)
        resume_button.pack(pady=10)

        main_menu_button = tk.Button(self.pause_menu, text="返回标题", command=self.reset_to_main_menu,
                                     **button_options)
        main_menu_button.pack(pady=10)

        quit_button = tk.Button(self.pause_menu, text="退出游戏", command=self.root.quit, **button_options)
        quit_button.pack(pady=10)

        self.pause_menu.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def reset_to_main_menu(self):
        """重置游戏并返回开始菜单"""
        # 销毁所有当前的窗口内容
        for widget in self.root.winfo_children():
            widget.destroy()

        # 重置游戏状态
        self.level = 1
        self.lines_cleared = 0
        self.drop_delay = INITIAL_DELAY
        self.pixel_offset = 0
        self.can_replace_shape = True
        self.is_paused = False
        self.pause_start_time = None
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_shape = None
        self.current_position = [0, 0]
        self.ranking = self.load_ranking()

        # 重新创建 GUI 和开始菜单
        self.gui = TetrisGUI(self.root, self.board, self.current_shape, self.current_position, self.pixel_offset)
        self.gui.bind_keys(self.handle_key_press)
        self.create_start_menu()

    def start_game(self):
        """开始游戏"""
        self.start_menu.destroy()
        self.start_time = time.time()
        self.create_new_shape()
        self.root.after(self.drop_delay, self.game_loop)

    def show_ranking(self):
        """显示排行榜"""
        ranking_window = tk.Toplevel(self.root)
        ranking_window.title("排行榜")

        # 创建滚动条
        scrollbar = tk.Scrollbar(ranking_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ranking_frame = tk.Frame(ranking_window)
        ranking_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(ranking_frame, yscrollcommand=scrollbar.set)
        scrollbar.config(command=canvas.yview)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        title_label = tk.Label(inner_frame, text="排行榜:", font=('SimHei', 16, 'bold'))
        title_label.pack(pady=10, anchor='w')

        for idx, entry in enumerate(self.ranking, start=1):
            entry_label = tk.Label(inner_frame,
                                   text=f"{idx}. {entry['name']} - Level: {entry['level']} - Time: {entry['time']}s",
                                   font=('SimHei', 14), anchor='w')
            entry_label.pack(fill='x', pady=5, padx=10)

        close_button = tk.Button(ranking_window, text="关闭", command=ranking_window.destroy, font=('SimHei', 14))
        close_button.pack(pady=10)

        # 更新滚动区域大小
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def pause_game(self):
        """暂停游戏"""
        self.is_paused = True
        self.pause_start_time = time.time()
        self.create_pause_menu()

    def resume_game(self):
        """继续游戏"""
        self.is_paused = False
        self.pause_menu.destroy()
        self.start_time += time.time() - self.pause_start_time
        self.root.after(self.drop_delay, self.game_loop)

    def create_new_shape(self):
        """生成一个新的方块"""
        shape_info = self.get_random_shape()
        self.current_shape = shape_info['shape']
        self.current_color = shape_info['color']
        self.current_position = [0, BOARD_WIDTH // 2 - len(self.current_shape[0]) // 2]
        self.pixel_offset = 0
        if not self.valid_move(self.current_position[1], self.current_position[0]):
            self.game_over()
            return False  # 确保不继续游戏循环
        return True

    def replace_current_shape(self):
        """替换当前方块"""
        shape_info = self.get_random_shape()
        self.current_shape = shape_info['shape']
        self.current_color = shape_info['color']
        self.can_replace_shape = False

    def move_shape(self, dx, dy):
        """移动方块"""
        new_x = self.current_position[1] + dx
        new_y = self.current_position[0] + dy
        if self.valid_move(new_x, new_y):
            self.current_position = [new_y, new_x]
            return True
        return False

    def rotate_shape(self):
        """旋转方块"""
        new_shape = list(zip(*self.current_shape[::-1]))
        if self.valid_move(self.current_position[1], self.current_position[0], new_shape):
            self.current_shape = new_shape

    def valid_move(self, x, y, shape=None):
        """检查方块移动是否合法"""
        shape = shape or self.current_shape
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (
                            x + j < 0 or x + j >= BOARD_WIDTH or
                            y + i >= BOARD_HEIGHT or
                            (y + i >= 0 and self.board[y + i][x + j])
                    ):
                        print(f"Invalid move: x={x}, y={y}, i={i}, j={j}")  # 添加调试日志
                        return False
        return True

    def place_shape(self):
        """将方块放置到游戏板上"""
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell and self.current_position[0] + i >= 0:
                    self.board[self.current_position[0] + i][self.current_position[1] + j] = self.current_color
        self.clear_lines()
        self.create_new_shape()

    def clear_lines(self):
        """清除已填满的行"""
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared_now = BOARD_HEIGHT - len(new_board)
        self.lines_cleared += lines_cleared_now
        self.board = [[0] * BOARD_WIDTH for _ in range(lines_cleared_now)] + new_board
        self.update_level()
        if lines_cleared_now > 0:
            self.can_replace_shape = True

    def update_level(self):
        """更新等级"""
        new_level = self.lines_cleared // LINES_PER_LEVEL + 1
        if new_level > self.level:
            self.level = new_level
            self.drop_delay = int(self.drop_delay / SPEED_MULTIPLIER)
            self.gui.update_level(self.level)

    def handle_key_press(self, event):
        """处理键盘按键事件"""
        if event.keysym == "Left":
            self.move_shape(-1, 0)
        elif event.keysym == "Right":
            self.move_shape(1, 0)
        elif event.keysym == "Down":
            self.move_shape(0, 1)
        elif event.keysym == "Up":
            self.rotate_shape()
        elif event.keysym == "space" and self.can_replace_shape:
            self.replace_current_shape()
        elif event.keysym == "Escape":
            if self.is_paused:
                self.resume_game()
            else:
                self.pause_game()
        self.gui.update_board(self.board, self.current_shape, self.current_position, self.pixel_offset,
                              self.current_color)

    def game_loop(self):
        """游戏主循环"""
        if self.is_paused:
            return

        if self.pixel_offset + PIXELS_PER_FRAME >= CELL_SIZE:
            if not self.valid_move(self.current_position[1], self.current_position[0] + 1):
                self.place_shape()
                self.pixel_offset = 0
                if not self.create_new_shape():  # 新增调用，确保在无法生成新方块时结束游戏
                    return
            else:
                self.current_position[0] += 1
                self.pixel_offset = 0
        else:
            self.pixel_offset += PIXELS_PER_FRAME

        if not self.valid_move(self.current_position[1], self.current_position[0] + 1):
            self.place_shape()
            self.pixel_offset = 0
            if not self.create_new_shape():  # 新增调用，确保在无法生成新方块时结束游戏
                return

        self.gui.update_board(self.board, self.current_shape, self.current_position, self.pixel_offset,
                              self.current_color)
        self.gui.update_time(int(time.time() - self.start_time))
        self.root.after(self.drop_delay, self.game_loop)

    def game_over(self):
        """处理游戏结束"""
        if not self.game_over_called:
            self.game_over_called = True
            elapsed_time = int(time.time() - self.start_time)
            self.update_ranking(self.level, elapsed_time)
            self.gui.clear_board()
            self.root.after_cancel(self.game_loop)
            response = messagebox.askyesno("Game Over", f"Game Over! Level: {self.level}, Time: {elapsed_time}s. Do you want to play again?")
            if response:
                self.reset_game()
            else:
                self.root.destroy()  # 使用destroy完全关闭窗口

    def update_ranking(self, level, elapsed_time):
        """更新排行榜并保存"""
        if not hasattr(self, 'player_name'):
            self.player_name = self.get_player_name()
        self.ranking.append({'name': self.player_name, 'level': level, 'time': elapsed_time})
        self.ranking.sort(key=lambda x: (-x['level'], x['time']))
        self.ranking = self.ranking[:30]  # 只保留前30名
        self.save_ranking(self.ranking)

    def get_player_name(self):
        """获取玩家名称"""
        return simpledialog.askstring("Player Name", "Enter your name:")

    def reset_game(self):
        """重置游戏"""
        if hasattr(self, 'after_id'):
            self.root.after_cancel(self.after_id)  # 取消任何现有的 after 调用

        self.start_time = time.time()
        self.level = 1
        self.lines_cleared = 0
        self.drop_delay = INITIAL_DELAY
        self.pixel_offset = 0
        self.can_replace_shape = True
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_shape = None
        self.create_new_shape()
        self.gui.update_level(self.level)
        self.game_over_called = False  # 重置标记

        self.after_id = self.root.after(self.drop_delay, self.game_loop)

    def get_random_shape(self):
        """随机获取一种俄罗斯方块形状"""
        return random.choice(SHAPES)

    def load_ranking(self):
        try:
            with open(RANKING_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_ranking(self, ranking):
        with open(RANKING_FILE, 'w') as f:
            json.dump(ranking, f, indent=4)

    def run(self):
        """运行游戏"""
        self.root.mainloop()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
