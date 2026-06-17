# ============================================================
# constants.py — 全局常量定义（纯配置文件，不含逻辑）
# ============================================================

# ---------- 窗口设置 ----------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 120
GAME_TITLE = "飞机大战2026"

# ---------- 资源路径 ----------
IMAGE_PATH = "temp_place_game_assets/"
SOUND_PATH = "temp_place_music/"
FONT_PATH = "temp_place_fonts/"

# ============================================================
# 图片素材名称定义（对应 temp_place_game_assets/ 下的 .png 文件）
# ============================================================

# --- 游戏界面 UI ---
IMG_BACKGROUND_1 = "background_1.png"
IMG_BACKGROUND_2 = "background_2.png"
IMG_BACKGROUND_3 = "background_3.png"
IMG_PAUSE = "pause.png"
IMG_RESUME = "resume.png"
IMG_BACK = "back.png"
IMG_RESTART = "restart.png"
IMG_LIFE = "life.png"
IMG_BULLET = "bullet.png"

# --- 道具 ---
IMG_BULLET_BOX = "bullet_box.png"
IMG_LIFE_RECOVERY = "life_recovery.png"
IMG_SHIELD = "shield.png"
IMG_WEAPON_UPGRADE = "weapon_upgrade.png"

# --- 玩家飞机 ---
IMG_PLAYER_PLANE = "player_plane.png"
IMG_PLAYER_PLANE_DAMAGED = "player_plane_damaged.png"
IMG_PLAYER_PLANE_LOW_LIFE = "player_plane_low_life.png"
IMG_PLAYER_PLANE_EXPLOSION = "player_plane_explosion.png"

# --- 敌机1 ---
IMG_ENEMY_PLANE_1 = "enemy_plane_1.png"
IMG_ENEMY_PLANE_1_DAMAGED = "enemy_plane_1_damaged.png"
IMG_ENEMY_PLANE_1_LOW_LIFE = "enemy_plane_1_low_life.png"
IMG_ENEMY_PLANE_1_EXPLOSION = "enemy_plane_1_explosion.png"

# --- 敌机2 ---
IMG_ENEMY_PLANE_2 = "enemy_plane_2.png"
IMG_ENEMY_PLANE_2_DAMAGED = "enemy_plane_2_damaged.png"
IMG_ENEMY_PLANE_2_LOW_LIFE = "enemy_plane_2_low_life.png"
IMG_ENEMY_PLANE_2_EXPLOSION = "enemy_plane_2_explosion.png"

# --- 敌机3 ---
IMG_ENEMY_PLANE_3 = "enemy_plane_3.png"
IMG_ENEMY_PLANE_3_DAMAGED = "enemy_plane_3_damaged.png"
IMG_ENEMY_PLANE_3_LOW_LIFE = "enemy_plane_3_low_life.png"
IMG_ENEMY_PLANE_3_EXPLOSION = "enemy_plane_3_explosion.png"

# --- BOSS ---
IMG_BOSS_PLANE = "boss_plane.png"
IMG_BOSS_PLANE_DAMAGED = "boss_plane_damaged.png"
IMG_BOSS_PLANE_LOW_LIFE = "boss_plane_low_life.png"
IMG_BOSS_PLANE_EXPLOSION = "boss_plane_explosion.png"

# ---------- 暂停界面按钮图片 ----------
BTN_RESUME_IMG = IMG_RESUME
BTN_RESTART_IMG = IMG_RESTART
BTN_BACK_IMG = IMG_BACK

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
PLAYER_AMMO_MAX = 50        # 最大弹药

# ---------- 敌机属性 ----------
ENEMY_SPEED_MIN = 2         # 敌机最低速度
ENEMY_SPEED_MAX = 6         # 敌机最高速度
ENEMY_SPAWN_INTERVAL = 40   # 敌机生成间隔（帧）
ENEMY_HP_BASE = 1           # 敌机基础血量
ENEMY_SCORE_BASE = 10       # 击毁敌机基础得分
BOSS_TRIGGER_KILLS = 30     # 消灭多少敌机后触发Boss

# ---------- 子弹属性 ----------
BULLET_SPEED = 8            # 玩家子弹速度
ENEMY_BULLET_SPEED = 5      # 敌机子弹速度
BULLET_COOLDOWN = 15        # 玩家射击冷却（帧）
BULLET_DAMAGE = 1           # 子弹伤害

# ---------- 道具属性 ----------
POWERUP_DROP_CHANCE = 0.15  # 敌机死亡掉落道具概率
POWERUP_FALL_SPEED = 2      # 道具下落速度
SHIELD_DURATION = 300       # 护盾持续时间（帧）

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
