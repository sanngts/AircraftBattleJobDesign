import pygame
import random
import os
from constants import *

# ============================================================
# 图片加载工具 — 素材未就绪时返回占位图形
# ============================================================

def _try_load_image(filename, default_size=(50, 50)):
    """尝试加载图片，不存在则返回带文字标记的占位 surface"""
    path = os.path.join(IMAGE_PATH, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        return img
    except (pygame.error, FileNotFoundError):
        # 占位图形：灰色矩形 + 文件名缩写
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


# ============================================================
# 玩家飞机
# ============================================================

class Player(pygame.sprite.Sprite):
    def __init__(self, difficulty="普通"):
        super().__init__()
        self.images = _load_image_set(
            IMG_PLAYER_PLANE,
            IMG_PLAYER_PLANE_DAMAGED,
            IMG_PLAYER_PLANE_LOW_LIFE,
            IMG_PLAYER_PLANE_EXPLOSION,
            default_size=(50, 60)
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
        self.weapon_level = 1

    def _update_image(self):
        """根据血量切换图片"""
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
        """射击，返回子弹列表（武器升级后可多发）"""
        if self.shoot_cooldown > 0 or self.ammo <= 0:
            return []
        self.shoot_cooldown = self.shoot_delay
        self.ammo -= 1

        bullets = []
        if self.weapon_level == 1:
            bullets.append(Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED, "player"))
        elif self.weapon_level == 2:
            bullets.append(Bullet(self.rect.centerx - 10, self.rect.top, -BULLET_SPEED, "player"))
            bullets.append(Bullet(self.rect.centerx + 10, self.rect.top, -BULLET_SPEED, "player"))
        else:  # level 3+
            bullets.append(Bullet(self.rect.centerx, self.rect.top, -BULLET_SPEED, "player"))
            bullets.append(Bullet(self.rect.centerx - 15, self.rect.top + 5, -BULLET_SPEED, "player"))
            bullets.append(Bullet(self.rect.centerx + 15, self.rect.top + 5, -BULLET_SPEED, "player"))
        return bullets

    def take_damage(self):
        """受到伤害，返回是否死亡"""
        if self.invincible_timer > 0:
            return False
        if self.has_shield:
            self.has_shield = False
            self.shield_timer = 0
            return False
        self.hp -= 1
        self.invincible_timer = self.invincible_duration
        return self.hp <= 0

    def add_ammo(self, amount=20):
        self.ammo = min(self.ammo + amount, self.max_ammo)

    def heal(self, amount=1):
        self.hp = min(self.hp + amount, self.max_hp)

    def activate_shield(self):
        self.has_shield = True
        self.shield_timer = SHIELD_DURATION

    def upgrade_weapon(self):
        self.weapon_level = min(self.weapon_level + 1, 3)

    def draw(self, screen):
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return
        screen.blit(self.image, self.rect)
        # 护盾光环
        if self.has_shield:
            pygame.draw.circle(screen, (0, 200, 255), self.rect.center, max(self.rect.width, self.rect.height)//2 + 5, 2)


# ============================================================
# 子弹
# ============================================================

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, owner="player"):
        super().__init__()
        self.owner = owner
        self.image = _try_load_image(IMG_BULLET if owner == "player" else "", default_size=(4, 12))
        # 如果 bullet.png 不存在，用纯色代替
        if self.image.get_width() == 4 and self.image.get_height() == 12 and self.image.get_at((0, 0)) == (100, 100, 100, 255):
            self.image = pygame.Surface((4, 12), pygame.SRCALPHA)
            self.image.fill(COLOR_YELLOW if owner == "player" else COLOR_RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


# ============================================================
# 道具
# ============================================================

class PowerUp(pygame.sprite.Sprite):
    """道具基类"""
    def __init__(self, x, y, image_name, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = _try_load_image(image_name, default_size=(30, 30))
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


def spawn_random_powerup(x, y):
    """根据概率随机生成道具"""
    if random.random() > POWERUP_DROP_CHANCE:
        return None
    r = random.random()
    if r < 0.35:
        return BulletBox(x, y)
    elif r < 0.60:
        return LifeRecovery(x, y)
    elif r < 0.80:
        return Shield(x, y)
    else:
        return WeaponUpgrade(x, y)


# ============================================================
# 敌机
# ============================================================

class EnemyType:
    """敌机类型定义 — 与图片素材一一对应"""
    ENEMY_1 = ("enemy_1", IMG_ENEMY_PLANE_1, IMG_ENEMY_PLANE_1_DAMAGED,
               IMG_ENEMY_PLANE_1_LOW_LIFE, IMG_ENEMY_PLANE_1_EXPLOSION,
               1, (2, 4), 10, False, (30, 30))
    ENEMY_2 = ("enemy_2", IMG_ENEMY_PLANE_2, IMG_ENEMY_PLANE_2_DAMAGED,
               IMG_ENEMY_PLANE_2_LOW_LIFE, IMG_ENEMY_PLANE_2_EXPLOSION,
               3, (1, 3), 30, True, (45, 40))
    ENEMY_3 = ("enemy_3", IMG_ENEMY_PLANE_3, IMG_ENEMY_PLANE_3_DAMAGED,
               IMG_ENEMY_PLANE_3_LOW_LIFE, IMG_ENEMY_PLANE_3_EXPLOSION,
               5, (1, 2), 60, True, (60, 55))
    BOSS = ("boss", IMG_BOSS_PLANE, IMG_BOSS_PLANE_DAMAGED,
            IMG_BOSS_PLANE_LOW_LIFE, IMG_BOSS_PLANE_EXPLOSION,
            20, (1, 1), 200, True, (100, 80))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, difficulty_mult=1.0):
        super().__init__()
        name, img_n, img_d, img_l, img_e, hp, speed_range, score, can_shoot, size = enemy_type
        self.type_name = name
        self.images = _load_image_set(img_n, img_d, img_l, img_e, default_size=size)
        self.image = self.images["normal"]
        self.rect = self.image.get_rect()
        w, h = size
        self.rect.x = random.randint(0, SCREEN_WIDTH - w)
        self.rect.y = -h - random.randint(0, 100)

        speed_min, speed_max = speed_range
        self.speed_y = random.uniform(speed_min, speed_max)
        self.speed_x = random.uniform(-1, 1) if name != "boss" else random.uniform(-2, 2)
        self.max_hp = int(hp * difficulty_mult)
        self.hp = self.max_hp
        self.score_value = int(score)
        self.can_shoot = can_shoot
        self.shoot_timer = random.randint(30, 90)
        self.is_boss = (name == "boss")

    def _update_image(self):
        hp_ratio = self.hp / self.max_hp
        if hp_ratio <= 0.3 and "low_life" in self.images:
            self.image = self.images["low_life"]
        elif hp_ratio <= 0.6 and "damaged" in self.images:
            self.image = self.images["damaged"]

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()
        if self.can_shoot:
            self.shoot_timer -= 1
        self._update_image()

    def shoot(self):
        if self.can_shoot and self.shoot_timer <= 0:
            self.shoot_timer = random.randint(50, 120)
            return Bullet(self.rect.centerx, self.rect.bottom, ENEMY_BULLET_SPEED, "enemy")
        return None

    def take_damage(self, damage=1):
        self.hp -= damage
        return self.hp <= 0

    def get_explosion_image(self):
        """获取爆炸图片（用于死亡特效）"""
        return self.images.get("explosion", None)

    def draw_hp_bar(self, screen):
        if self.max_hp <= 1:
            return
        bar_width = self.rect.width
        bar_height = 5
        bar_x = self.rect.x
        bar_y = self.rect.y - 8
        pygame.draw.rect(screen, COLOR_GRAY, (bar_x, bar_y, bar_width, bar_height))
        hp_ratio = self.hp / self.max_hp
        hp_color = COLOR_GREEN if hp_ratio > 0.5 else COLOR_YELLOW if hp_ratio > 0.25 else COLOR_RED
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, bar_width * hp_ratio, bar_height))
