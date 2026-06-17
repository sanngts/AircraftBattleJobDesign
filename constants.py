SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 120
GAME_TITLE = "飞机大战2026"

IMAGE_PATH = "temp_place_game_assets/"
SOUND_PATH = "temp_place_music/"
FONT_PATH = "temp_place_fonts/"

#暂停界面按钮图片
BTN_RESUME_IMG = "resume.png"
BTN_RESTART_IMG = "restart.png"
BTN_BACK_IMG = "back.png"

# ---------- 暂停界面布局 ----------
BTN_WIDTH = 200
BTN_HEIGHT = 50
BTN_CENTER_X = SCREEN_WIDTH // 2
BTN_Y_RESUME = 250
BTN_Y_RESTART = 320
BTN_Y_BACK = 390

# ---------- 玩家属性 ----------
PLAYER_INIT_HP = 3          # 初始生命值
PLAYER_SPEED = 5            # 移动速度（像素/帧）
PLAYER_INIT_SCORE = 0       # 初始分数
PLAYER_INVINCIBLE_TIME = 60 # 受伤后无敌帧数（约1秒）

# ---------- 敌机属性 ----------
ENEMY_SPEED_MIN = 2         # 敌机最低速度
ENEMY_SPEED_MAX = 6         # 敌机最高速度
ENEMY_SPAWN_INTERVAL = 40   # 敌机生成间隔（帧）
ENEMY_HP_BASE = 1           # 敌机基础血量
ENEMY_SCORE_BASE = 10       # 击毁敌机基础得分

# ---------- 子弹属性 ----------
BULLET_SPEED = 8            # 玩家子弹速度
ENEMY_BULLET_SPEED = 5      # 敌机子弹速度
BULLET_COOLDOWN = 15        # 玩家射击冷却（帧）
BULLET_DAMAGE = 1           # 子弹伤害

# ---------- 难度倍率 ----------
DIFFICULTY_MULTIPLIER = {
    "简单": {"hp": 1.5, "spawn_rate": 0.7, "enemy_hp": 0.7, "score": 0.8},
    "普通": {"hp": 1.0, "spawn_rate": 1.0, "enemy_hp": 1.0, "score": 1.0},
    "困难": {"hp": 0.7, "spawn_rate": 1.4, "enemy_hp": 1.5, "score": 1.5},
}

# ---------- 界面遮罩 ----------
PAUSE_OVERLAY_ALPHA = 160   # 暂停遮罩透明度 (0-255)
PAUSE_OVERLAY_COLOR = (0, 0, 0)  # 暂停遮罩颜色（黑色）

# ---------- 颜色常量 ----------
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (80, 80, 80)
COLOR_RED = (200, 50, 50)
COLOR_GREEN = (0, 180, 0)
COLOR_BLUE = (0, 120, 200)
COLOR_YELLOW = (255, 215, 0)
COLOR_GOLD = (255, 255, 100)
