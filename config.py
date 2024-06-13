# 游戏配置常量
BOARD_WIDTH = 10  # 游戏板的宽度（单位：单元格）
BOARD_HEIGHT = 20  # 游戏板的高度（单位：单元格）
CELL_SIZE = 30  # 每个单元格的像素大小
INITIAL_DELAY = 20  # 初始方块下落的延迟时间（毫秒）
PIXELS_PER_FRAME = 2  # 每帧方块下落的像素数
LINES_PER_LEVEL = 3  # 每升一级所需消除的行数
SPEED_MULTIPLIER = 1.2  # 每升一级后方块下落速度的倍率

# 俄罗斯方块形状和颜色
SHAPES = [
    {'shape': [[1, 1, 1], [0, 1, 0]], 'color': 'yellow'},  # T形
    {'shape': [[1, 1, 1, 1]], 'color': 'red'},  # I形
    {'shape': [[1, 1, 0], [0, 1, 1]], 'color': 'blue'},  # Z形
    {'shape': [[0, 1, 1], [1, 1, 0]], 'color': 'green'},  # S形
    {'shape': [[1, 1], [1, 1]], 'color': 'yellow'},  # O形
    {'shape': [[1, 1, 1], [1, 0, 0]], 'color': 'red'},  # L形
    {'shape': [[1, 1, 1], [0, 0, 1]], 'color': 'blue'}  # J形
]

RANKING_FILE = "ranking.json"
