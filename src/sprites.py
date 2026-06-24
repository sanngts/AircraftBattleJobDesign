import pygame
import random
import math
import os
from constants import *
#占位图片
def _try_load_image(filename, default_size=(50, 50)):
    """尝试加载图片并缩放到 default_size，不存在则返回带文字标记的占位 surface"""
    path = os.path.join(IMAGE_PATH, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, default_size)
        return img
    except (pygame.error, FileNotFoundError):
        w, h = default_size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((100, 100, 100))
        pygame.draw.rect(surf, (180, 180, 180), (0, 0, w, h), 2)
        return surf


def _load_image_set(normal, damaged=None, low_life=None, explosion=None, default_size=(50, 50)):
    """一次性加载一组素材（正常/受损/低血/爆炸），不存在则返回占位"""
    imgs = {"normal": _try_load_image(normal, default_size)}
    if damaged:
        imgs["damaged"] = _try_load_image(damaged, default_size)
    if low_life:
        imgs["low_life"] = _try_load_image(low_life, default_size)
    if explosion:
        imgs["explosion"] = _try_load_image(explosion, default_size)
    return imgs

class Player(pygame.sprite.Sprite):
    def __init__(self, difficulty="普通"):
        super().__init__()
        self.images = _load_image_set(
            IMG_PLAYER_PLANE,
            IMG_PLAYER_PLANE_DAMAGED,
            IMG_PLAYER_PLANE_LOW_LIFE,
            IMG_PLAYER_PLANE_EXPLOSION,
            default_size=(60, 68)
        )
        self.image = self.images["normal"]
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 50
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 0
        self.shoot_delay = BULLET_COOLDOWN

        # 难度调整
        mult = DIFFICULTY_MULTIPLIER[difficulty]
        self.max_hp = int(PLAYER_INIT_HP * mult["hp"])
        self.hp = self.max_hp
        self.ammo = PLAYER_AMMO_MAX
        self.max_ammo = PLAYER_AMMO_MAX
        self.invincible_timer = 0
        self.invincible_duration = PLAYER_INVINCIBLE_TIME
        self.shield_timer = 0
        self.has_shield = False
        self.shield_duration = SHIELD_DURATION  # 当前护盾的总时长（帧），可能被作弊模式覆盖
        self.weapon_level = 1
        self.difficulty = difficulty
        self._shield_cache = None  # 护盾光环 surface 缓存

    def _update_image(self):
    #根据敌机血量切换图片
        hp_ratio = self.hp / self.max_hp
        if hp_ratio <= 0.3 and "low_life" in self.images:
            self.image = self.images["low_life"]
        elif hp_ratio <= 0.6 and "damaged" in self.images:
            self.image = self.images["damaged"]
        else:
            self.image = self.images["normal"]

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.has_shield = False

        self._update_image()

    def shoot(self):
        if self.shoot_cooldown > 0 or self.ammo <= 0:
            return []
        self.shoot_cooldown = self.shoot_delay
        self.ammo -= self.weapon_level  # 按子弹数量消耗弹药

        bullets = []
        if self.weapon_level == 1:
            bullets.append(Bullet(self.rect.centerx, self.rect.top,
                                  ENEMY_BULLET_NORMAL, "player",
                                  damage=BULLET_DAMAGE))
        elif self.weapon_level == 2:
            bullets.append(Bullet(self.rect.centerx - 10, self.rect.top,
                                  ENEMY_BULLET_NORMAL, "player",
                                  damage=BULLET_DAMAGE))
            bullets.append(Bullet(self.rect.centerx + 10, self.rect.top,
                                  ENEMY_BULLET_NORMAL, "player",
                                  damage=BULLET_DAMAGE))
        else:  # level 3+
            bullets.append(Bullet(self.rect.centerx, self.rect.top,
                                  ENEMY_BULLET_NORMAL, "player",
                                  damage=BULLET_DAMAGE))
            bullets.append(Bullet(self.rect.centerx - 15, self.rect.top + 5,
                                  ENEMY_BULLET_NORMAL, "player",
                                  damage=BULLET_DAMAGE))
            bullets.append(Bullet(self.rect.centerx + 15, self.rect.top + 5,
                                  ENEMY_BULLET_NORMAL, "player",
                                  damage=BULLET_DAMAGE))
        # 设置玩家子弹的垂直速度（向上）
        for b in bullets:
            b.vel_x = 0
            b.vel_y = -b.speed
        return bullets

    def trigger_explosion(self):
        self.exploding = True
        self.explode_timer = ENEMY_EXPLOSION_DURATION
        # 替换为共享爆炸素材，缩放至敌机尺寸
        explode_img = _get_explode_image()
        self.image = pygame.transform.scale(
            explode_img, (self.rect.width, self.rect.height))

    def take_damage(self, damage=1):
        """受到伤害，返回是否死亡。护盾持续期间完全无敌。"""
        if self.invincible_timer > 0:
            return False
        if self.has_shield:
            return False
        self.hp -= damage
        self.invincible_timer = self.invincible_duration
        return self.hp <= 0

    def add_ammo(self, amount=None):
        if amount is None:
            amount = AMMO_PER_PICKUP.get(self.difficulty, 20)
        self.ammo = min(self.ammo + amount, self.max_ammo)

    def heal(self, amount=1):
        self.hp = min(self.hp + amount, self.max_hp)

    def activate_shield(self, duration=None):
        new_duration = duration if duration is not None else SHIELD_DURATION
        # 已有护盾且剩余时间更长时，不覆盖（防止作弊护盾被普通护盾缩短）
        if self.shield_timer >= new_duration:
            self.has_shield = True
            return
        self.has_shield = True
        self.shield_duration = new_duration
        self.shield_timer = new_duration

    def upgrade_weapon(self):
        self.weapon_level = min(self.weapon_level + 1, 3)

    def draw(self, screen):
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return
        screen.blit(self.image, self.rect)
        # 护盾光环效果
        if self.has_shield:
            shield_ratio = self.shield_timer / max(1, self.shield_duration)
            alpha = int(100 + 80 * shield_ratio) 
            radius = max(self.rect.width, self.rect.height) // 2 + 8
            if self.shield_timer <= SHIELD_BLINK_START and (self.shield_timer // 15) % 2 == 0:
                color = (255, 60, 60, alpha) 
            else:
                color = (0, 200, 255, alpha)

            surf_w = radius * 2 + 10
            surf_h = radius * 2 + 10
            if self._shield_cache is None or self._shield_cache.get_size() != (surf_w, surf_h):
                self._shield_cache = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            else:
                self._shield_cache.fill((0, 0, 0, 0))
            shield_surf = self._shield_cache
            # 护盾光环
            for offset in range(3):
                r = radius + offset * 3
                a = alpha // (offset + 1)
                pygame.draw.circle(shield_surf, (*color[:3], a),
                                   (surf_w // 2, surf_h // 2), r, 2)
            screen.blit(shield_surf, (self.rect.centerx - shield_surf.get_width() // 2,
                                       self.rect.centery - shield_surf.get_height() // 2))

            # 粒子效果
            particle_count = 6
            for i in range(particle_count):
                angle = (pygame.time.get_ticks() * 0.003 + i * math.pi * 2 / particle_count) % (math.pi * 2)
                px = self.rect.centerx + radius * math.cos(angle)
                py = self.rect.centery + radius * math.sin(angle)
                pygame.draw.circle(screen, (*color[:3], min(255, alpha + 40)), (int(px), int(py)), 2)

# 子弹系统 — 支持多种轨迹形态、伤害值与运动模式
BULLET_COLORS = {
    "player": {
        ENEMY_BULLET_NORMAL: None,  # 玩家子弹用玩家颜色
    },
    "enemy": {
        ENEMY_BULLET_NORMAL: COLOR_RED,
        ENEMY_BULLET_AIMED: (255, 100, 0),
        ENEMY_BULLET_SPREAD: (255, 140, 0),
        ENEMY_BULLET_LASER: (0, 220, 255),
        ENEMY_BULLET_BURST: (255, 0, 100),
    },
}

BULLET_SIZES = {
    ENEMY_BULLET_NORMAL: (5, 14),
    ENEMY_BULLET_AIMED: (5, 14),
    ENEMY_BULLET_SPREAD: (4, 12),
    ENEMY_BULLET_LASER: (LASER_WIDTH, LASER_HEIGHT),
    ENEMY_BULLET_BURST: (6, 6),
}


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_type=ENEMY_BULLET_NORMAL, owner="player",
                 damage=None, target=None, spread_angle=0, burst_angle=0):
        super().__init__()
        self.owner = owner
        self.bullet_type = bullet_type
        self.start_x = x
        self.start_y = y

        # 外观
        size = BULLET_SIZES.get(bullet_type, (5, 14))
        if owner == "player":
            self.image = _try_load_image(IMG_BULLET, default_size=size)
            if self.image.get_width() == size[0] and self.image.get_height() == size[1] and self.image.get_at((0, 0)) == (100, 100, 100, 255):
                self.image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
                self.image.fill(COLOR_YELLOW)
        else:
            color = BULLET_COLORS["enemy"].get(bullet_type, COLOR_RED)
            if bullet_type == ENEMY_BULLET_LASER:
                self.image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
                r, g, b = color
                h = size[1]
                for row in range(h):
                    ratio = 1.0 - abs(row - h // 2) / (h // 2)
                    alpha = int(80 + 175 * ratio)
                    pygame.draw.line(self.image, (r, g, b, alpha), (0, row), (size[0], row))
                pygame.draw.line(self.image, (255, 255, 255, 200), (size[0] // 2, 0), (size[0] // 2, h), max(1, size[0] // 4))
            elif bullet_type == ENEMY_BULLET_BURST:
                self.image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
                pygame.draw.circle(self.image, color, (size[0] // 2, size[1] // 2), size[0] // 2)
            else:
                self.image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self.image, color, (0, 0, size[0], size[1]), border_radius=2)

        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        # 物理属性
        self.speed = ENEMY_BULLET_SPEEDS.get(bullet_type, ENEMY_BULLET_SPEED)
        self.damage = damage if damage is not None else ENEMY_BULLET_DAMAGE.get(bullet_type, 1)
        self.target = target
        self.spread_angle = spread_angle
        self.burst_angle = burst_angle
        self.distance_traveled = 0

        # 根据子弹类型初始化速度分量
        self._init_velocity()

        # 子弹存活时间
        self.max_lifetime = 600  # 5秒 @ 60fps
        self.lifetime = 0

        # 追踪弹：有限追踪计时器
        self.track_lifetime = 0

    def _init_velocity(self):
        """根据子弹类型初始化速度分量"""
        owner_sign = -1 if self.owner == "player" else 1

        if self.bullet_type == ENEMY_BULLET_AIMED:
            # 追踪弹
            if self.target:
                dx = self.target.rect.centerx - self.rect.centerx
                dy = self.target.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.vel_x = self.speed * dx / dist
                    self.vel_y = self.speed * dy / dist
                else:
                    self.vel_x, self.vel_y = 0, self.speed * owner_sign
            else:
                self.vel_x, self.vel_y = 0, self.speed * owner_sign
        elif self.bullet_type == ENEMY_BULLET_SPREAD:
            # 散弹
            rad = math.radians(self.spread_angle + 90)
            self.vel_x = self.speed * math.cos(rad)
            self.vel_y = self.speed * math.sin(rad)
        elif self.bullet_type == ENEMY_BULLET_BURST:
            # 圆环爆发弹
            rad = math.radians(self.burst_angle)
            self.vel_x = self.speed * math.cos(rad)
            self.vel_y = self.speed * math.sin(rad)
        elif self.bullet_type == ENEMY_BULLET_LASER:
            # 激光束
            self.vel_x = 0
            self.vel_y = self.speed * owner_sign
            self.target = None  # 禁止追踪，仅垂直发射
        else:
            # 普通弹：初始垂直向下
            self.vel_x = 0
            self.vel_y = self.speed * owner_sign

    def update(self):
        self.lifetime += 1

        # 根据类型更新位置
        if self.bullet_type == ENEMY_BULLET_AIMED:
            self._update_aimed()
        elif self.bullet_type == ENEMY_BULLET_LASER:
            self._update_linear()
        elif self.bullet_type == ENEMY_BULLET_SPREAD:
            self._update_linear()
        elif self.bullet_type == ENEMY_BULLET_BURST:
            self._update_linear()
        else:
            self._update_linear()

        #超出屏幕四周任意方向则销毁
        margin = 40
        if (self.rect.bottom < -margin or self.rect.top > SCREEN_HEIGHT + margin or
                self.rect.right < -margin or self.rect.left > SCREEN_WIDTH + margin):
            self.kill()
            return

        # 超时回收
        if self.lifetime > self.max_lifetime:
            self.kill()

    def _update_linear(self):
        """直线运动"""
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.distance_traveled += abs(self.vel_x) + abs(self.vel_y)

    def _update_aimed(self):
        self.track_lifetime += 1
        track_elapsed = self.track_lifetime / AIMED_TRACK_DURATION  # 0 → 1

        # 追踪能力随时间线性衰减
        if self.target and self.track_lifetime <= AIMED_TRACK_DURATION:
            current_turn = AIMED_TURN_RATE_MIN + (AIMED_TURN_RATE - AIMED_TURN_RATE_MIN) * (1.0 - track_elapsed)
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                desired_x = self.speed * dx / dist
                desired_y = self.speed * dy / dist
                self.vel_x += (desired_x - self.vel_x) * current_turn
                self.vel_y += (desired_y - self.vel_y) * current_turn

        # 禁止追踪弹向上回飞：强制保留向下分量（弹药只能向前发射）
        MIN_DOWN = self.speed * 0.22
        if self.vel_y < MIN_DOWN:
            self.vel_y = MIN_DOWN

        # 归一化速度，防止追踪过程中速度畸变
        current_speed = math.hypot(self.vel_x, self.vel_y)
        if current_speed > 0:
            self.vel_x = self.vel_x / current_speed * self.speed
            self.vel_y = self.vel_y / current_speed * self.speed

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.distance_traveled += abs(self.vel_x) + abs(self.vel_y)

    def has_hit(self, target_sprite):
        """像素级碰撞检测：判断是否命中目标精灵"""
        if not self.alive():
            return False
        if not target_sprite.alive():
            return False
        offset_x = target_sprite.rect.x - self.rect.x
        offset_y = target_sprite.rect.y - self.rect.y
        target_mask = getattr(target_sprite, 'mask', None)
        if target_mask is None:
            return self.rect.colliderect(target_sprite.rect)
        return self.mask.overlap(target_mask, (offset_x, offset_y)) is not None


# ---------- 敌方子弹工厂函数 ----------

def create_enemy_bullet(bullet_type, x, y, target=None, speed_mult=1.0, **kwargs):
    """工厂函数：创建敌方子弹实例，统一入口"""
    bullet = Bullet(x, y, bullet_type=bullet_type, owner="enemy",
                    target=target, **kwargs)
    bullet.speed *= speed_mult
    bullet.vel_x *= speed_mult
    bullet.vel_y *= speed_mult
    return bullet


def create_enemy_bullet_volley(volley_type, x, y, target=None, speed_mult=1.0, count_mult=1.0):
    """创建子弹阵列（散弹/激光束/爆发弹等），返回子弹列表。count_mult 缩放数量。"""
    bullets = []

    if volley_type == ENEMY_BULLET_SPREAD:
        actual_count = max(1, int(SPREAD_COUNT * count_mult))
        half = (actual_count - 1) / 2
        for i in range(actual_count):
            angle = (i - half) * (SPREAD_ANGLE / (actual_count - 1)) if actual_count > 1 else 0
            bullets.append(create_enemy_bullet(ENEMY_BULLET_SPREAD, x, y, target, speed_mult,
                                               spread_angle=angle))
    elif volley_type == ENEMY_BULLET_BURST:
        actual_count = max(2, int(BURST_COUNT * count_mult))
        for i in range(actual_count):
            angle = i * (360 / actual_count)
            bullets.append(create_enemy_bullet(ENEMY_BULLET_BURST, x, y, target, speed_mult,
                                               burst_angle=angle))
    elif volley_type == ENEMY_BULLET_LASER:
        # 激光束阵列：并排发射多条长条光束，数量受 count_mult 缩放
        actual_count = max(1, int(LASER_COUNT * count_mult))
        for i in range(actual_count):
            offset_x = (i - (actual_count - 1) / 2) * (LASER_WIDTH + 4)
            bullets.append(create_enemy_bullet(ENEMY_BULLET_LASER, x + offset_x, y, target, speed_mult))
    elif volley_type == ENEMY_BULLET_AIMED:
        bullets.append(create_enemy_bullet(ENEMY_BULLET_AIMED, x, y, target, speed_mult))
    else:
        bullets.append(create_enemy_bullet(ENEMY_BULLET_NORMAL, x, y, target, speed_mult))

    return bullets

class PowerUp(pygame.sprite.Sprite):
    """道具基类"""
    def __init__(self, x, y, image_name, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = _try_load_image(image_name, default_size=(54, 54))
        self.rect = self.image.get_rect(center=(x, y))
        self.fall_speed = POWERUP_FALL_SPEED

    def update(self):
        self.rect.y += self.fall_speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def apply(self, player):
        """应用道具效果，子类重写"""
        pass


class BulletBox(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, IMG_BULLET_BOX, "bullet_box")

    def apply(self, player):
        player.add_ammo(20)


class LifeRecovery(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, IMG_LIFE_RECOVERY, "life_recovery")

    def apply(self, player):
        player.heal(1)


class Shield(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, IMG_SHIELD, "shield")

    def apply(self, player):
        player.activate_shield()


class WeaponUpgrade(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, IMG_WEAPON_UPGRADE, "weapon_upgrade")

    def apply(self, player):
        player.upgrade_weapon()


def spawn_random_powerup(x, y, difficulty="普通"):
    """根据概率随机生成道具。难度越高，生命恢复出现概率越大"""
    if random.random() > POWERUP_DROP_CHANCE:
        return None
    # 生命恢复概率随难度递增；武器升级大幅降低出现率
    life_chances = {"简单": 0.50, "普通": 0.60, "困难": 0.70}
    shield_chances = {"简单": 0.92, "普通": 0.94, "困难": 0.95}
    r = random.random()
    if r < 0.35:
        return BulletBox(x, y)
    elif r < life_chances.get(difficulty, 0.60):
        return LifeRecovery(x, y)
    elif r < shield_chances.get(difficulty, 0.80):
        return Shield(x, y)
    else:
        return WeaponUpgrade(x, y)

# 共享爆炸素材（所有敌机共用）
_EXPLODE_IMAGE = None

def _get_explode_image():
    """懒加载共享爆炸图片"""
    global _EXPLODE_IMAGE
    if _EXPLODE_IMAGE is None:
        _EXPLODE_IMAGE = _try_load_image("explode.png", default_size=(80, 80))
    return _EXPLODE_IMAGE


class EnemyType:
    """敌机类型定义 — 与图片素材一一对应"""
    ENEMY_1 = ("enemy_1", IMG_ENEMY_PLANE_1, IMG_ENEMY_PLANE_1_DAMAGED,
               IMG_ENEMY_PLANE_1_LOW_LIFE, IMG_ENEMY_PLANE_1_EXPLOSION,
               ENEMY_HP["enemy_1"], (4.0, 6.5), 10, False, (45, 45))
    ENEMY_2 = ("enemy_2", IMG_ENEMY_PLANE_2, IMG_ENEMY_PLANE_2_DAMAGED,
               IMG_ENEMY_PLANE_2_LOW_LIFE, IMG_ENEMY_PLANE_2_EXPLOSION,
               ENEMY_HP["enemy_2"], (1.5, 3.5), 30, True, (50, 48))
    ENEMY_3 = ("enemy_3", IMG_ENEMY_PLANE_3, IMG_ENEMY_PLANE_3_DAMAGED,
               IMG_ENEMY_PLANE_3_LOW_LIFE, IMG_ENEMY_PLANE_3_EXPLOSION,
               ENEMY_HP["enemy_3"], (1.2, 2.8), 60, True, (65, 58))
    BOSS = ("boss", IMG_BOSS_PLANE, IMG_BOSS_PLANE_DAMAGED,
            IMG_BOSS_PLANE_LOW_LIFE, IMG_BOSS_PLANE_EXPLOSION,
            ENEMY_HP["boss"], (1, 2), 200, True, (110, 85))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, difficulty_mult=1.0, difficulty_speed_mult=1.0,
                 bullet_count_mult=1.0, player=None, game_state=None):
        super().__init__()
        name, img_n, img_d, img_l, img_e, hp, speed_range, score, can_shoot, size = enemy_type
        self.type_name = name
        self.images = _load_image_set(img_n, img_d, img_l, img_e, default_size=size)
        self.image = self.images["normal"]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        w, h = size

        # 入场位置：屏幕上方随机
        self.rect.x = random.randint(0, SCREEN_WIDTH - w)
        self.rect.y = -h - random.randint(0, 100)

        speed_min, speed_max = speed_range
        self.base_speed_y = random.uniform(speed_min, speed_max) * difficulty_speed_mult
        self.base_speed_x = random.uniform(-0.6, 0.6) * difficulty_speed_mult
        self.speed_mult = difficulty_speed_mult
        self.bullet_count_mult = bullet_count_mult
        self.max_hp = max(1, int(hp * difficulty_mult))
        self.hp = self.max_hp
        self.score_value = int(score)
        self.can_shoot = can_shoot
        self.shoot_timer = random.randint(30, 90)
        self.is_boss = (name == "boss")
        self.barrage_timer = 0
        self.barrage_phase = 0
        self.forward_only = (name in ("enemy_1", "enemy_2"))  # 只能往前飞的敌机
        self.shield_hit_timer = 0        # 被玩家护盾撞击的伤害冷却（帧）
        self.exploding = False           # 是否处于爆炸状态
        self.explode_timer = 0           # 爆炸剩余帧数

        # ---- AI 状态机 ----
        self.ai_state = STATE_ENTER       # 当前状态
        self.ai_timer = 0                 # 当前状态计时器
        self.ai_data = {}                 # 状态上下文数据
        self.player_ref = player          # 玩家引用（用于动态行为）
        self.game_state = game_state      # 游戏全局状态（关卡/分数等）

        # 入场行为：先进入可视区域
        self._init_enter_state()

    def _init_enter_state(self):
        """入场：从上方进入屏幕，直到 y 坐标到达可视区域"""
        self.ai_state = STATE_ENTER
        self.ai_timer = 0
        self.speed_y = self.base_speed_y
        self.speed_x = random.uniform(-0.5, 0.5) * self.speed_mult
        # 到达屏幕 15%~40% 区域时切换状态
        self.ai_data["enter_target_y"] = random.randint(
            int(SCREEN_HEIGHT * 0.15), int(SCREEN_HEIGHT * 0.40)
        )
    def _select_next_state(self):
        """根据敌机类型和当前上下文选择下一行为模式"""
        if self.is_boss:
            return

        # 只能往前飞的敌机（enemy_1、enemy_2）：简化为正面飞越行为
        if self.forward_only:
            # 到达屏幕中下部时直接俯冲飞离
            if self.rect.y > SCREEN_HEIGHT * 0.65:
                self._enter_state(STATE_CROSS)
                return
            if self.type_name == "enemy_1":
                # enemy_1 必须一直向前飞，不悬停
                self._enter_state(STATE_CROSS)
            else:
                r = random.random()
                if r < 0.55:
                    self._enter_state(STATE_CROSS)
                else:
                    self._enter_state(STATE_HOVER)
            return

        # enemy_3 保持多样化行为
        weights = {STATE_ENTER: 0, STATE_ORBIT: 10, STATE_CROSS: 30,
                   STATE_HOVER: 25, STATE_CHARGE: 10, STATE_LEAD_SHOT: 25}

        # 如果在屏幕上半部，提高交叉封锁概率
        if self.rect.y < SCREEN_HEIGHT * 0.35:
            weights[STATE_CROSS] = int(weights.get(STATE_CROSS, 0) * 1.5)

        # 如果玩家在附近，提高悬停射击概率
        if self.player_ref:
            dx = self.player_ref.rect.centerx - self.rect.centerx
            dy = self.player_ref.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist < 200:
                weights[STATE_HOVER] = int(weights.get(STATE_HOVER, 0) * 1.8)
                weights[STATE_CHARGE] = int(weights.get(STATE_CHARGE, 0) * 1.5)

        choices = list(weights.keys())
        total = sum(weights.values())
        if total <= 0:
            return STATE_HOVER
        r = random.uniform(0, total)
        cumulative = 0
        for state in choices:
            cumulative += weights[state]
            if r <= cumulative:
                self._enter_state(state)
                return
        self._enter_state(STATE_HOVER)

    def _enter_state(self, state):
        """进入新状态时初始化参数"""
        self.ai_state = state
        self.ai_timer = 0
        self.ai_data = {}

        if state == STATE_ORBIT:
            # 环绕：设定环绕半径、角速度和起始角度
            self.ai_data["orbit_radius"] = random.randint(ORBIT_RADIUS_MIN, ORBIT_RADIUS_MAX)
            self.ai_data["orbit_speed"] = ORBIT_SPEED * random.uniform(0.8, 1.2)
            self.ai_data["orbit_angle"] = random.uniform(0, math.pi * 2)
            self.ai_data["orbit_duration"] = random.randint(90, 240)
            # 确定环绕中心偏移（在玩家附近）
            self.ai_data["orbit_center_x"] = self.rect.centerx
            self.ai_data["orbit_center_y"] = self.rect.centery

        elif state == STATE_CROSS:
            # 交叉封锁：设定目标位置（屏幕另一侧）
            self.ai_data["cross_target_x"] = random.choice([
                self.rect.centerx + SCREEN_WIDTH // 2 + random.randint(0, 60),
                self.rect.centerx - SCREEN_WIDTH // 2 - random.randint(0, 60)
            ])
            self.ai_data["cross_target_x"] = max(20, min(SCREEN_WIDTH - 20,
                                                         self.ai_data["cross_target_x"]))
            if self.forward_only:
                # 只能往前飞：目标y一定在下方或屏幕外
                if self.type_name == "enemy_1":
                    # enemy_1 只往前飞，目标位置大幅偏下
                    self.ai_data["cross_target_y"] = max(
                        self.rect.centery + 80,
                        random.randint(int(SCREEN_HEIGHT * 0.6), SCREEN_HEIGHT + 40)
                    )
                else:
                    self.ai_data["cross_target_y"] = max(
                        self.rect.centery + 40,
                        random.randint(int(SCREEN_HEIGHT * 0.5), SCREEN_HEIGHT + 40)
                    )
            else:
                self.ai_data["cross_target_y"] = random.randint(
                    int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.7)
                )
            self.ai_data["cross_duration"] = random.randint(120, 240)
            # 交叉飞行时密集射击
            self.shoot_timer = min(self.shoot_timer, 15)

        elif state == STATE_HOVER:
            # 悬停：停在当前位置或微调
            self.speed_x = 0
            self.speed_y = 0
            self.ai_data["hover_duration"] = random.randint(HOVER_DURATION_MIN, HOVER_DURATION_MAX)
            self.ai_data["hover_origin_x"] = self.rect.centerx
            self.ai_data["hover_origin_y"] = self.rect.centery
            # 悬停时提高射击频率
            self.shoot_timer = min(self.shoot_timer, 10)

        elif state == STATE_CHARGE:
            # 冲刺：朝玩家当前位置冲刺
            self.ai_data["charge_duration"] = random.randint(30, 80)
            if self.player_ref:
                dx = self.player_ref.rect.centerx - self.rect.centerx
                dy = self.player_ref.rect.centery - self.rect.centery
                dist = max(1, math.hypot(dx, dy))
                self.speed_x = CHARGE_SPEED * self.speed_mult * dx / dist
                self.speed_y = CHARGE_SPEED * self.speed_mult * dy / dist
            else:
                self.speed_x = 0
                self.speed_y = CHARGE_SPEED * self.speed_mult
            self.shoot_timer = min(self.shoot_timer, 8)

        elif state == STATE_LEAD_SHOT:
            # 预判射击：微移到侧方，朝玩家移动趋势方向射击
            self.ai_data["lead_duration"] = random.randint(60, 150)
            # 移到玩家侧面
            if self.player_ref:
                side = random.choice([-1, 1])
                self.speed_x = side * 1.5 * self.speed_mult
                self.speed_y = -0.3 * self.speed_mult  # 缓慢上移保持距离
            else:
                self.speed_x = 1.5 * self.speed_mult
                self.speed_y = -0.3 * self.speed_mult
            self.ai_data["lead_side"] = side if self.player_ref else 1
            self.ai_data["last_player_x"] = self.player_ref.rect.centerx if self.player_ref else SCREEN_WIDTH // 2
            self.ai_data["last_player_y"] = self.player_ref.rect.centery if self.player_ref else SCREEN_HEIGHT // 2
            self.shoot_timer = min(self.shoot_timer, 20)

        elif state == STATE_RETREAT:
            self.speed_y = -RETREAT_SPEED * self.speed_mult
            self.speed_x = random.uniform(-1, 1) * self.speed_mult
            self.ai_data["retreat_target_y"] = -60

        elif state == STATE_ENTER:
            self._init_enter_state()

    def _update_ai(self):
        """每帧更新 AI 状态机"""
        if self.is_boss:
            return  # Boss 保持原有弹幕系统

        self.ai_timer += 1

        if self.ai_state == STATE_ENTER:
            self._update_enter()
        elif self.ai_state == STATE_ORBIT:
            self._update_orbit()
        elif self.ai_state == STATE_CROSS:
            self._update_cross()
        elif self.ai_state == STATE_HOVER:
            self._update_hover()
        elif self.ai_state == STATE_CHARGE:
            self._update_charge()
        elif self.ai_state == STATE_LEAD_SHOT:
            self._update_lead_shot()
        elif self.ai_state == STATE_RETREAT:
            self._update_retreat()

    def _update_enter(self):
        """入场：向下移动直到到达目标位置"""
        if self.rect.y >= self.ai_data.get("enter_target_y", SCREEN_HEIGHT * 0.3):
            self._select_next_state()
            return
        # 入场期间轻微左右摆动
        self.speed_x += random.uniform(-0.05, 0.05)
        self.speed_x = max(-1.5, min(1.5, self.speed_x)) * self.speed_mult

    def _update_orbit(self):
        """环绕飞行：绕一个动态中心点做圆周运动"""
        duration = self.ai_data.get("orbit_duration", 180)
        if self.ai_timer > duration:
            self._select_next_state()
            return

        radius = self.ai_data["orbit_radius"]
        speed = self.ai_data["orbit_speed"]
        self.ai_data["orbit_angle"] += speed

        # 环绕中心逐渐向玩家位置靠拢
        if self.player_ref:
            cx, cy = self.player_ref.rect.centerx, self.player_ref.rect.centery
        else:
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        old_cx = self.ai_data.get("orbit_center_x", cx)
        old_cy = self.ai_data.get("orbit_center_y", cy)
        new_cx = old_cx + (cx - old_cx) * 0.02
        new_cy = old_cy + (cy - old_cy) * 0.02
        self.ai_data["orbit_center_x"] = new_cx
        self.ai_data["orbit_center_y"] = new_cy

        angle = self.ai_data["orbit_angle"]
        target_x = new_cx + radius * math.cos(angle)
        target_y = new_cy + radius * math.sin(angle)

        # 平滑移向目标位置
        self.speed_x = (target_x - self.rect.centerx) * 0.08
        self.speed_y = (target_y - self.rect.centery) * 0.08

        # 环绕时定时射击
        if self.can_shoot and self.shoot_timer <= 0:
            self.shoot_timer = random.randint(35, 70)

    def _update_cross(self):
        """交叉封锁：飞向屏幕另一侧，形成交叉火力"""
        duration = self.ai_data.get("cross_duration", 180)
        target_x = self.ai_data.get("cross_target_x", SCREEN_WIDTH // 2)
        target_y = self.ai_data.get("cross_target_y", SCREEN_HEIGHT // 3)

        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        dist = max(1, math.hypot(dx, dy))

        self.speed_x = CROSS_SPEED * self.speed_mult * dx / dist
        self.speed_y = CROSS_SPEED * self.speed_mult * dy / dist

        if dist < 15 or self.ai_timer > duration:
            # 到达或超时，反向交叉或换新状态
            if self.forward_only:
                # 只能往前飞：下一个目标继续向下
                self.ai_data["cross_target_x"] = SCREEN_WIDTH - target_x
                self.ai_data["cross_target_y"] = max(
                    self.rect.centery + 40,
                    random.randint(int(SCREEN_HEIGHT * 0.5), SCREEN_HEIGHT + 40)
                )
                self.ai_data["cross_duration"] = random.randint(90, 180)
                self.ai_timer = 0
            elif random.random() < 0.6:
                # 反向交叉
                self.ai_data["cross_target_x"] = SCREEN_WIDTH - target_x
                self.ai_data["cross_target_y"] = random.randint(
                    int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.7)
                )
                self.ai_data["cross_duration"] = random.randint(90, 180)
                self.ai_timer = 0
            else:
                self._select_next_state()

        # 交叉时密集射击
        if self.can_shoot and self.shoot_timer <= 0:
            self.shoot_timer = random.randint(15, 40)

    def _update_hover(self):
        """定点悬停：在原地微动 + 持续射击"""
        duration = self.ai_data.get("hover_duration", 120)
        if self.ai_timer > duration:
            self._select_next_state()
            return

        # 微小抖动模拟悬停
        self.speed_x = math.sin(self.ai_timer * 0.1) * 0.5 * self.speed_mult
        self.speed_y = math.cos(self.ai_timer * 0.13) * 0.3 * self.speed_mult

        # 高频率射击
        if self.can_shoot and self.shoot_timer <= 0:
            self.shoot_timer = random.randint(20, 50)

    def _update_charge(self):
        """冲刺：朝玩家快速移动"""
        duration = self.ai_data.get("charge_duration", 60)
        if self.ai_timer > duration:
            self._select_next_state()
            return

        # 微调方向追踪玩家
        if self.player_ref and self.ai_timer % 8 == 0:
            dx = self.player_ref.rect.centerx - self.rect.centerx
            dy = self.player_ref.rect.centery - self.rect.centery
            dist = max(1, math.hypot(dx, dy))
            # 逐渐转向
            target_vx = CHARGE_SPEED * self.speed_mult * dx / dist
            target_vy = CHARGE_SPEED * self.speed_mult * dy / dist
            self.speed_x += (target_vx - self.speed_x) * 0.3
            self.speed_y += (target_vy - self.speed_y) * 0.3

        # 冲刺时偶尔射击
        if self.can_shoot and self.shoot_timer <= 0:
            self.shoot_timer = random.randint(25, 60)

    def _update_lead_shot(self):
        """预判射击：移动到侧方，预判玩家走位"""
        duration = self.ai_data.get("lead_duration", 120)
        if self.ai_timer > duration or self.rect.top < -20:
            self._select_next_state()
            return

        # 保持在屏幕侧方，与玩家保持水平距离
        if self.player_ref:
            side = self.ai_data.get("lead_side", 1)
            target_x = self.player_ref.rect.centerx + side * 120
            target_x = max(20, min(SCREEN_WIDTH - 20, target_x))
            target_y = self.player_ref.rect.centery - random.randint(30, 100)

            # 更新预判数据
            cur_x = self.player_ref.rect.centerx
            cur_y = self.player_ref.rect.centery
            last_x = self.ai_data.get("last_player_x", cur_x)
            last_y = self.ai_data.get("last_player_y", cur_y)
            self.ai_data["player_dx"] = cur_x - last_x  # 玩家 x 方向趋势
            self.ai_data["player_dy"] = cur_y - last_y
            self.ai_data["last_player_x"] = cur_x
            self.ai_data["last_player_y"] = cur_y

            # 移向侧方位置
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            dist = max(1, math.hypot(dx, dy))
            self.speed_x = 2 * self.speed_mult * dx / dist
            self.speed_y = 2 * self.speed_mult * dy / dist

            # 预判射击
            if self.can_shoot and self.shoot_timer <= 0:
                self.shoot_timer = random.randint(25, 55)

    def _update_retreat(self):
        """撤退：向上飞出屏幕，然后重新入场"""
        if self.rect.bottom < -20:
            # 重新入场
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = -self.rect.height - random.randint(0, 60)
            self._init_enter_state()
            return
        # 边界反弹
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x = -self.speed_x

    def _update_image(self):
        """根据血量比例动态切换素材"""
        hp_ratio = self.hp / self.max_hp
        old_image = self.image
        if hp_ratio <= 0.3 and "low_life" in self.images:
            self.image = self.images["low_life"]
        elif hp_ratio <= 0.6 and "damaged" in self.images:
            self.image = self.images["damaged"]
        else:
            self.image = self.images["normal"]
        if self.image is not old_image:
            self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """主更新：AI 状态机 + 物理"""
        # 爆炸状态：只倒计时，不移动/不射击/不碰撞
        if self.exploding:
            self.explode_timer -= 1
            if self.explode_timer <= 0:
                self.kill()
            return

        self._update_ai()

        # 只能往前飞的敌机：强制速度向下，不可后退
        if self.forward_only:
            self.speed_y = max(ENEMY_SPEED_MIN * 0.5, self.speed_y)

        # 应用速度
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 屏幕边界约束（入场状态不约束 y 上界）
        if self.ai_state != STATE_ENTER:
            if self.rect.left < 0:
                self.rect.left = 0
                self.speed_x = abs(self.speed_x)
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
                self.speed_x = -abs(self.speed_x)

        # 超出屏幕底部过多则回收
        if self.rect.top > SCREEN_HEIGHT + 80:
            self.kill()

        if self.can_shoot:
            self.shoot_timer -= 1
        if self.is_boss:
            self.barrage_timer -= 1
        self._update_image()

    def shoot(self, player=None):
        """射击：根据 AI 状态选择不同弹道模式，受动态难度影响频率和数量"""
        bullets = []

        if self.is_boss:
            return self._boss_shoot(player)

        if not self.can_shoot or self.shoot_timer > 0:
            return bullets

        # 动态难度影响射击频率：难度低时间隔长，难度高时间隔短
        dyn_diff = 1.0
        if self.game_state:
            dyn_diff = max(0.3, getattr(self.game_state, 'dynamic_difficulty', 1.0))
        freq_mult = 1.0 / dyn_diff  # 低难度→倍率大(间隔长)，高难度→倍率小(间隔短)
        bc = self.bullet_count_mult   # 子弹数量缩放系数

        cx, cy = self.rect.centerx, self.rect.bottom

        if self.ai_state == STATE_HOVER:
            # 悬停射击：散弹 + 普通弹交替
            if random.random() < 0.4:
                self.shoot_timer = max(SHOOT_TIMER_MIN, int(random.randint(40, 70) * freq_mult))
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_SPREAD, cx, cy, player, self.speed_mult, bc)
            else:
                self.shoot_timer = max(SHOOT_TIMER_MIN, int(random.randint(20, 35) * freq_mult))
                count = max(1, int((5 if dyn_diff > 0.7 else 3) * bc))
                for _ in range(count):
                    ox = cx + random.randint(-20, 20)
                    bullets.append(create_enemy_bullet(ENEMY_BULLET_NORMAL, ox, cy, player, self.speed_mult))

        elif self.ai_state == STATE_CROSS:
            # 交叉封锁：激光束 或 普通弹齐射
            self.shoot_timer = max(SHOOT_TIMER_MIN, int(random.randint(30, 55) * freq_mult))
            if dyn_diff > 0.5 and random.random() < 0.45:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx, cy, player, self.speed_mult, bc)
            else:
                count = max(1, int(5 * bc))
                for i in range(count):
                    ox = cx + (i - (count - 1) / 2) * 12
                    bullets.append(create_enemy_bullet(ENEMY_BULLET_NORMAL, ox, cy, player, self.speed_mult))

        elif self.ai_state == STATE_ORBIT:
            # 环绕飞行：普通弹齐射
            self.shoot_timer = max(SHOOT_TIMER_MIN, int(random.randint(50, 90) * freq_mult))
            count = max(1, int(3 * bc))
            for i in range(count):
                ox = cx + (i - (count - 1) / 2) * 14
                bullets.append(create_enemy_bullet(ENEMY_BULLET_NORMAL, ox, cy, player, self.speed_mult))

        elif self.ai_state == STATE_CHARGE:
            # 冲刺：偶尔爆发弹或普通弹
            self.shoot_timer = max(SHOOT_TIMER_MIN, int(random.randint(35, 70) * freq_mult))
            if dyn_diff > 0.6 and random.random() < 0.4:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_BURST, cx, cy, player, self.speed_mult, bc)
            else:
                count = max(1, int(3 * bc))
                for i in range(count):
                    ox = cx + (i - (count - 1) / 2) * 12
                    bullets.append(create_enemy_bullet(ENEMY_BULLET_NORMAL, ox, cy, player, self.speed_mult))

        elif self.ai_state == STATE_LEAD_SHOT:
            # 预判射击：朝玩家移动趋势方向发射激光束
            self.shoot_timer = max(SHOOT_TIMER_MIN, int(random.randint(35, 65) * freq_mult))
            # 计算预判位置
            lead_x = cx
            lead_y = cy
            if player and "player_dx" in self.ai_data:
                pdx = self.ai_data.get("player_dx", 0)
                pdy = self.ai_data.get("player_dy", 0)
                lead_distance = 35
                lead_x = player.rect.centerx + pdx * lead_distance
                lead_y = player.rect.centery + pdy * lead_distance
            # 朝预判方向发射激光束，数量受难度缩放
            base_count = 2 if dyn_diff > 0.6 else 1
            count = max(1, int(base_count * bc))
            for i in range(count):
                ox = cx + (i - (count - 1) / 2) * 20  # 错位发射
                bullet = create_enemy_bullet(ENEMY_BULLET_LASER, ox, cy, None, self.speed_mult)
                if player:
                    dx = lead_x - ox
                    dy = lead_y - cy
                    dist = max(1, math.hypot(dx, dy))
                    # 激光只朝该方向直射（不追踪），确保向下
                    bullet.vel_x = bullet.speed * dx / dist * 0.6  # 水平分量打折
                    bullet.vel_y = max(bullet.speed * 0.8, bullet.speed * dy / dist)
                bullets.append(bullet)

        else:
            # 默认：普通直线弹
            self.shoot_timer = max(SHOOT_TIMER_MIN, int(random.randint(60, 130) * freq_mult))
            count = max(1, int(2 * bc))
            for i in range(count):
                ox = cx + (i - (count - 1) / 2) * 8
                bullets.append(create_enemy_bullet(ENEMY_BULLET_NORMAL, ox, cy, player, self.speed_mult))

        return bullets

    def _boss_shoot(self, player):
        """Boss 弹幕系统 — 根据血量阶段切换攻击模式，子弹数量受难度缩放"""
        bullets = []

        if self.barrage_timer > 0:
            return bullets

        hp_ratio = self.hp / self.max_hp
        cx, cy = self.rect.centerx, self.rect.bottom
        bc = self.bullet_count_mult  # 难度缩放系数

        # 阶段 1: 高血量 — 扇形散弹 + 普通弹
        if hp_ratio > 0.6:
            self.barrage_timer = BOSS_BARRAGE_INTERVAL
            self.barrage_phase = (self.barrage_phase + 1) % 3
            if self.barrage_phase == 0:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_SPREAD, cx, cy, player, self.speed_mult, bc)
            elif self.barrage_phase == 1:
                count = max(1, int(5 * bc))
                for _ in range(count):
                    ox = cx + random.randint(-40, 40)
                    bullets.append(create_enemy_bullet(ENEMY_BULLET_NORMAL, ox, cy, player, self.speed_mult))
            else:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx, cy, player, self.speed_mult, bc)

        # 阶段 2: 中血量 — 激光束 + 散弹
        elif hp_ratio > 0.3:
            self.barrage_timer = BOSS_BARRAGE_INTERVAL // 2
            self.barrage_phase = (self.barrage_phase + 1) % 3
            if self.barrage_phase == 0:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx, cy, player, self.speed_mult, bc)
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_SPREAD, cx, cy, player, self.speed_mult, bc)
            elif self.barrage_phase == 1:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx - 20, cy, player, self.speed_mult, bc)
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx + 20, cy, player, self.speed_mult, bc)
            else:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_BURST, cx, cy, player, self.speed_mult, bc)

        # 阶段 3: 低血量 — 全弹幕倾泻
        else:
            self.barrage_timer = BOSS_BARRAGE_INTERVAL // 3
            self.barrage_phase = (self.barrage_phase + 1) % 4
            if self.barrage_phase == 0:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_BURST, cx, cy, player, self.speed_mult, bc)
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx, cy, player, self.speed_mult, bc)
            elif self.barrage_phase == 1:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_SPREAD, cx - 30, cy, player, self.speed_mult, bc)
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_SPREAD, cx + 30, cy, player, self.speed_mult, bc)
            elif self.barrage_phase == 2:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx - 25, cy, player, self.speed_mult, bc)
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx + 25, cy, player, self.speed_mult, bc)
            else:
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx - 30, cy, player, self.speed_mult, bc)
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_LASER, cx + 30, cy, player, self.speed_mult, bc)
                bullets += create_enemy_bullet_volley(ENEMY_BULLET_BURST, cx, cy, player, self.speed_mult, bc)

        return bullets

    def trigger_explosion(self):
        """触发爆炸状态：显示爆炸图片 0.5 秒后消失"""
        self.exploding = True
        self.explode_timer = ENEMY_EXPLOSION_DURATION
        # 替换为共享爆炸素材，缩放至敌机尺寸
        explode_img = _get_explode_image()
        self.image = pygame.transform.scale(
            explode_img, (self.rect.width, self.rect.height))

    def take_damage(self, damage=1):
        self.hp -= damage
        return self.hp <= 0

    def get_explosion_image(self):
        """获取爆炸图片（用于死亡特效）"""
        return self.images.get("explosion", None)

    def draw_hp_bar(self, screen):
        """在所有敌机头顶绘制血量条"""
        bar_width = self.rect.width
        bar_height = 5
        bar_x = self.rect.x
        bar_y = self.rect.y - 8
        hp_ratio = self.hp / self.max_hp
        # 底色
        pygame.draw.rect(screen, COLOR_GRAY, (bar_x, bar_y, bar_width, bar_height))
        # 边框
        pygame.draw.rect(screen, COLOR_WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        # 血量
        if hp_ratio > 0.5:
            hp_color = COLOR_GREEN
        elif hp_ratio > 0.25:
            hp_color = COLOR_YELLOW
        else:
            hp_color = COLOR_RED
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
