# ============================================================
# constants.py — 全局常量定义（纯配置文件，不含逻辑）
# ============================================================

# ---------- 窗口设置 ----------
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "飞机大战"

# ---------- 资源路径 ----------
IMAGE_PATH = "assets/images/"
SOUND_PATH = "assets/sounds/"
FONT_PATH = "temp_place_fonts/"

# ============================================================
# 图片素材名称定义（对应 temp_place_game_assets/ 下的 .png 文件）
# ============================================================

# --- 游戏界面 UI ---
IMG_BACKGROUND_1 = "background_1.png"
IMG_BACKGROUND_2 = "background_2.png"
IMG_BACKGROUND_3 = "background_3.jpg"
IMG_PAUSE = "pause.png"
IMG_RESUME = "resume.png"
IMG_BACK = "back.png"
IMG_RESTART = "restart.png"
IMG_LIFE = "life.png"
IMG_BULLET = "bullet.png"
IMG_AMMO = "ammo.png"

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
IMG_BOSS_PLANE = "boss.png"
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
BTN_Y_RESUME = 280
BTN_Y_RESTART = 350
BTN_Y_BACK = 420

# ---------- 玩家属性 ----------
PLAYER_INIT_HP = 8          # 初始生命值
PLAYER_SPEED = 7            # 移动速度（像素/帧）
PLAYER_INIT_SCORE = 0       # 初始分数
PLAYER_INVINCIBLE_TIME = 60 # 受伤后无敌帧数（约1秒）
PLAYER_AMMO_MAX = 300        # 最大弹药

# 弹药补给量（按难度）
AMMO_PER_PICKUP = {
    "简单": 200,
    "普通": 100,
    "困难": 50,
}

# ---------- 敌机属性 ----------
ENEMY_SPEED_MIN = 3         # 敌机最低速度（px/帧）
ENEMY_SPEED_MAX = 6         # 敌机最高速度（px/帧）
ENEMY_SPAWN_INTERVAL = 30   # 敌机生成间隔（帧）
ENEMY_HP_BASE = 1           # 敌机基础血量（将被 EnemyType 中具体值覆盖）
ENEMY_SCORE_BASE = 10       # 击毁敌机基础得分
BOSS_TRIGGER_KILLS = 30     # 消灭多少敌机后触发Boss

# 各敌机类型基础血量（未乘难度倍率）
ENEMY_HP = {
    "enemy_1": 8,    # 低血量：2~3发子弹击落（简单模式）
    "enemy_2": 14,    # 中等血量
    "enemy_3": 25,    # 高血量
    "boss": 50,      # Boss 高血量
}

# ---------- 子弹属性 ----------
BULLET_SPEED = 12           # 玩家子弹速度（px/帧 @60fps，向上）
ENEMY_BULLET_SPEED = 9      # 敌机子弹速度（px/帧，向下）
BULLET_COOLDOWN = 6         # 玩家射击冷却（帧）
BULLET_DAMAGE = 2           # 子弹伤害

# ---------- 追踪弹限制 ----------
AIMED_TRACK_DURATION = 90   # 追踪持续时间（帧，约1.5秒@60fps）
AIMED_TURN_RATE = 0.08      # 追踪弹初始转向速率
AIMED_TURN_RATE_MIN = 0.01  # 追踪弹最小转向速率（结束时极弱追踪）

# ---------- 动态难度 ----------
DYNAMIC_DIFFICULTY_BASE = 0.7      # 动态难度起点倍率（开局快速进入战斗）
DYNAMIC_DIFFICULTY_MAX = 1.6       # 动态难度上限倍率
DYNAMIC_DIFFICULTY_RAMP_SCORE = 600  # 达到最大难度的分数阈值
SHOOT_TIMER_MIN = 14                # 敌机射击间隔下限（帧），防止后期过于密集

# ---------- 敌方子弹类型 ----------
ENEMY_BULLET_NORMAL = "normal"          # 普通直线弹
ENEMY_BULLET_AIMED = "aimed"            # 追踪弹（有限追踪）
ENEMY_BULLET_SPREAD = "spread"          # 扇形散弹
ENEMY_BULLET_LASER = "laser"            # 激光束（长条光束，替换波弹）
ENEMY_BULLET_BURST = "burst"            # 爆发圆环弹

ENEMY_BULLET_DAMAGE = {
    ENEMY_BULLET_NORMAL: 1,
    ENEMY_BULLET_AIMED: 1,
    ENEMY_BULLET_SPREAD: 1,
    ENEMY_BULLET_LASER: 2,
    ENEMY_BULLET_BURST: 2,
}

ENEMY_BULLET_SPEEDS = {
    ENEMY_BULLET_NORMAL: 9,
    ENEMY_BULLET_AIMED: 7,
    ENEMY_BULLET_SPREAD: 7,
    ENEMY_BULLET_LASER: 22.0,   # 激光束高速飞行，远快于普通子弹
    ENEMY_BULLET_BURST: 8,
}

# 散弹参数
SPREAD_COUNT = 5            # 扇形子弹数量
SPREAD_ANGLE = 30           # 扇形总角度（度）

# 激光束参数
LASER_WIDTH = 8             # 激光束宽度
LASER_HEIGHT = 90           # 激光束高度（长条光束）
LASER_COUNT = 2             # 一次发射的激光束数量

# 爆发弹参数
BURST_COUNT = 8             # 圆环子弹数量

# Boss 弹幕参数
BOSS_BARRAGE_INTERVAL = 60  # Boss 弹幕间隔（帧）

# ---------- 敌机行为模式 ----------
# 敌机状态机
STATE_ENTER = "enter"          # 入场：从屏幕上方进入
STATE_ORBIT = "orbit"          # 环绕飞行：绕玩家圆周运动
STATE_CROSS = "cross"          # 交叉封锁：交叉飞行形成弹幕
STATE_HOVER = "hover"          # 定点悬停射击
STATE_CHARGE = "charge"        # 冲刺：朝玩家冲刺
STATE_RETREAT = "retreat"      # 撤退：离开屏幕重新入场
STATE_LEAD_SHOT = "lead_shot"  # 预判射击：预判玩家走位

# 各模式参数
ORBIT_RADIUS_MIN = 80          # 环绕最小半径
ORBIT_RADIUS_MAX = 150         # 环绕最大半径
ORBIT_SPEED = 0.03             # 环绕角速度
HOVER_DURATION_MIN = 60        # 悬停最短时间（帧）
HOVER_DURATION_MAX = 180       # 悬停最长时间（帧）
CROSS_SPEED = 4                # 交叉飞行速度
CHARGE_SPEED = 5               # 冲刺速度
RETREAT_SPEED = 3              # 撤退速度

# ---------- 屏幕敌机上限 ----------
MAX_ENEMIES_ON_SCREEN = 10      # 屏幕上同时存在的最大敌机数量

# ---------- 道具属性 ----------
POWERUP_DROP_CHANCE = 0.2   # 敌机死亡掉落道具概率
POWERUP_FALL_SPEED = 5      # 道具下落速度（px/帧 @120fps）
SHIELD_DURATION = 600       # 护盾持续时间（帧 @60fps = 10秒）
SHIELD_BLINK_START = 180    # 护盾最后3秒开始闪烁提示
ENEMY_EXPLOSION_DURATION = 12  # 敌机爆炸动画持续时间（帧 @60fps = 0.2秒）
SHIELD_HIT_COOLDOWN = 30    # 护盾撞击敌机伤害冷却（帧 @60fps = 0.5秒）
SUPPLY_SPAWN_INTERVAL = 420  # 补给道具自动投放间隔（帧 @60fps ≈ 7秒）

# ---------- 难度倍率 ----------
DIFFICULTY_MULTIPLIER = {
    "简单": {"hp": 1.0, "spawn_rate": 0.5, "enemy_hp": 0.6, "enemy_speed": 0.6, "score": 0.8},
    "普通": {"hp": 1.0, "spawn_rate": 1.0, "enemy_hp": 1.0, "enemy_speed": 1.0, "score": 1.0},
    "困难": {"hp": 0.7, "spawn_rate": 1.4, "enemy_hp": 1.5, "enemy_speed": 1.3, "score": 1.5},
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
