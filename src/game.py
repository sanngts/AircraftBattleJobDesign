import pygame
import random
import sys
import os
from constants import *
from src.sprites import (Player, Enemy, EnemyType, spawn_random_powerup,
                           _try_load_image, BulletBox, Shield, WeaponUpgrade, LifeRecovery)
from game_music import MusicPlayer

class Game:
    """游戏主类，管理游戏循环和状态"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.state = "menu"  # menu / difficulty / playing / paused
        self.difficulty = "普通"
        self.running = True
        self.is_gameover = False  # 标记 paused 是否为游戏结束

        # 音乐播放器
        self.music_player = MusicPlayer()

        # 精灵组
        self.player_group = None
        self.enemy_group = None
        self.bullet_group = None
        self.enemy_bullet_group = None
        self.powerup_group = None
        self.all_sprites = None

        # 游戏数据
        self.score = 0
        self.enemy_spawn_timer = ENEMY_SPAWN_INTERVAL // 2  # 首波敌机更快出现
        self.boss_spawned = False
        self.boss_kill_count = 0
        self.kill_count = 0
        self.current_level = 1

        # 关卡切换公告
        self.stage_announce_timer = 0
        self.stage_announce_text = ""

        # 背景图片
        self.backgrounds = {}
        self._load_backgrounds()

        # 字体 — 尝试加载中文字体
        self._init_fonts()

        # 背景滚动偏移
        self.bg_scroll_y = 0
        self.bg_scroll_speed = 3

        # 背景星星（无背景图时使用）
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT),
                       random.randint(1, 3)) for _ in range(80)]

        # HUD 缓存：避免每帧从磁盘加载图片和重新渲染文字
        self.hud_icons = {}
        self.hud_text_cache = {}
        self._last_hud_values = {}

    def _init_fonts(self):
        """初始化字体，优先使用系统自带中文字体"""
        chinese_fonts = [
            "simhei", "simsun", "microsoftyahei", "msyh", "fangsong",
            "kaiti", "notosanscjk", "wenquanyi", "droid sans fallback",
        ]
        chosen = None
        for name in chinese_fonts:
            try:
                pygame.font.SysFont(name, 20)
                chosen = name
                break
            except Exception:
                continue

        if chosen:
            self.font_large = pygame.font.SysFont(chosen, 48)
            self.font_medium = pygame.font.SysFont(chosen, 32)
            self.font_small = pygame.font.SysFont(chosen, 22)
        else:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 22)

    def _load_backgrounds(self):
        """加载三张关卡背景图"""
        bg_files = [IMG_BACKGROUND_1, IMG_BACKGROUND_2, IMG_BACKGROUND_3]
        for i, filename in enumerate(bg_files):
            path = os.path.join(IMAGE_PATH, filename)
            try:
                bg = pygame.image.load(path).convert()
                bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.backgrounds[i + 1] = bg
            except (pygame.error, FileNotFoundError):
                self.backgrounds[i + 1] = None

    # ==================== 主循环 ====================

    def run(self):
        while self.running:
            if self.state == "menu":
                self._run_menu()
            elif self.state == "difficulty":
                self._run_difficulty_select()
            elif self.state == "playing":
                self._run_gameplay()
            elif self.state == "ready_intro":
                self._run_ready_intro()
            elif self.state == "paused":
                self._run_paused()

    # ==================== 菜单界面 ====================

    def _run_menu(self):
        while self.state == "menu" and self.running:
            self.clock.tick(FPS)
            self._handle_menu_events()
            self._draw_menu()

    def _handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 50)
                if btn_rect.collidepoint(mx, my):
                    self.music_player.play_button()
                    self.state = "difficulty"
                    return

    def _draw_menu(self):
        bg = self.backgrounds.get(1)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(COLOR_BLACK)
            self._draw_stars()

        title = self.font_large.render("飞机大战 2026", True, COLOR_GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 160))
        # 标题灰色半透明背景，仅覆盖标题文字范围
        padding = 16
        bg_rect = title_rect.inflate(padding * 2, padding * 2)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((60, 60, 60, 160))
        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(title, title_rect)

        btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 50)
        mx, my = pygame.mouse.get_pos()
        hover = btn_rect.collidepoint(mx, my)
        btn_color = COLOR_BLUE if hover else COLOR_GRAY
        pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 2, border_radius=10)
        btn_text = self.font_medium.render("开始战斗", True, COLOR_WHITE)
        self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

        tip = self.font_small.render("按 ESC 退出游戏", True, COLOR_GRAY)
        self.screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))

        pygame.display.flip()

    # ==================== 难度选择界面 ====================

    def _run_difficulty_select(self):
        while self.state == "difficulty" and self.running:
            self.clock.tick(FPS)
            self._handle_difficulty_events()
            self._draw_difficulty_select()

    def _handle_difficulty_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                difficulties = ["简单", "普通", "困难"]
                for i, diff in enumerate(difficulties):
                    btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 250 + i * 90, 200, 50)
                    if btn_rect.collidepoint(mx, my):
                        self.music_player.play_button()
                        self.difficulty = diff
                        self._init_game()
                        # 玩家飞机从屏幕底部飞入
                        self.player.rect.bottom = SCREEN_HEIGHT + 60
                        self.state = "ready_intro"
                        return

    def _draw_difficulty_select(self):
        bg = self.backgrounds.get(1)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(COLOR_BLACK)
            self._draw_stars()

        title = self.font_large.render("选择难度", True, COLOR_GOLD)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 140)))

        difficulties = ["简单", "普通", "困难"]
        colors = [COLOR_GREEN, COLOR_BLUE, COLOR_RED]
        mx, my = pygame.mouse.get_pos()

        for i, (diff, color) in enumerate(zip(difficulties, colors)):
            btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 250 + i * 90, 200, 50)
            hover = btn_rect.collidepoint(mx, my)
            btn_color = color if not hover else tuple(min(c + 40, 255) for c in color)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 2, border_radius=10)
            btn_text = self.font_medium.render(diff, True, COLOR_WHITE)
            self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

        tip = self.font_small.render("按 ESC 返回主菜单", True, COLOR_GRAY)
        self.screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))

        pygame.display.flip()

    # ==================== 入场动画 ====================

    def _run_ready_intro(self):
        """玩家飞机从屏幕底部飞到起始位置"""
        target_y = SCREEN_HEIGHT - 50
        while self.state == "ready_intro" and self.running:
            self.clock.tick(FPS)
            # 处理事件，允许退出
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
            # 飞机向上移动
            if self.player.rect.bottom > target_y:
                self.player.rect.bottom -= 5
            else:
                self.player.rect.bottom = target_y
                self.state = "playing"
                return
            # 绘制
            bg = self.backgrounds.get(1)
            if bg:
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill(COLOR_BLACK)
                self._draw_stars()
            self.player.draw(self.screen)
            pygame.display.flip()

    # ==================== 游戏初始化 ====================

    def _init_game(self):
        self.player = Player(self.difficulty)
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.player)

        self.score = 0
        self.enemy_spawn_timer = ENEMY_SPAWN_INTERVAL // 2  # 首波敌机更快出现
        self.boss_spawned = False
        self.boss_kill_count = 0
        self.kill_count = 0
        self.current_level = 1
        self.stage_announce_timer = 0
        self.stage_announce_text = ""
        self.is_gameover = False

        # 动态难度
        self.survival_frames = 0
        self.dynamic_difficulty = DYNAMIC_DIFFICULTY_BASE

        # 补给自动投放计时
        self.supply_spawn_timer = 0

        # 预加载 HUD 图标（避免每帧磁盘加载）
        self.hud_icons["ammo"] = _try_load_image(IMG_AMMO, default_size=(32, 32))
        self.hud_icons["hp"] = _try_load_image(IMG_PLAYER_PLANE, default_size=(32, 32))
        self.hud_text_cache = {}
        self._last_hud_values = {}

        # 开始背景音乐
        self.music_player.play_music()

    # ==================== 游戏进行中 ====================

    def _run_gameplay(self):
        while self.state == "playing" and self.running:
            self.clock.tick(FPS)

            result = self._handle_gameplay_events()
            if result == "quit":
                return

            self._update_gameplay()
            self._check_collisions()
            self._draw_gameplay()

    def _handle_gameplay_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "paused"
                    return "pause"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_j] or keys[pygame.K_SPACE]:
            for bullet in self.player.shoot():
                self.bullet_group.add(bullet)
                self.all_sprites.add(bullet)

        return None

    def _update_gameplay(self):
        self.survival_frames += 1
        self._update_dynamic_difficulty()

        # 关卡公告倒计时
        if self.stage_announce_timer > 0:
            self.stage_announce_timer -= 1

        self.player_group.update()
        self.enemy_group.update()
        self.bullet_group.update()
        self.enemy_bullet_group.update()
        self.powerup_group.update()

        # 敌机射击 — 传入玩家引用，支持追踪弹等智能弹道
        for enemy in self.enemy_group:
            if enemy.exploding:
                continue
            # 跳过冷却中或不能射击的敌机，减少不必要的函数调用开销
            if not enemy.can_shoot or enemy.shoot_timer > 0:
                continue
            bullets = enemy.shoot(self.player)
            for bullet in bullets:
                self.enemy_bullet_group.add(bullet)

        # 生成敌机
        self._spawn_enemies()

        # 自动投放补给道具
        self._spawn_supplies()

        # 关卡切换（每消灭一定数量敌机切换背景）
        self._update_level()

    def _update_dynamic_difficulty(self):
        """根据当前分数计算动态难度倍率，分数越高难度越大"""
        score_ratio = min(1.0, self.score / DYNAMIC_DIFFICULTY_RAMP_SCORE)
        self.dynamic_difficulty = DYNAMIC_DIFFICULTY_BASE + (DYNAMIC_DIFFICULTY_MAX - DYNAMIC_DIFFICULTY_BASE) * score_ratio

    def _update_level(self):
        """根据分数切换关卡背景"""
        prev_level = self.current_level
        if self.score >= LEVEL_3_SCORE and self.current_level < 3:
            self.current_level = 3
        elif self.score >= LEVEL_2_SCORE and self.current_level < 2:
            self.current_level = 2

        if self.current_level > prev_level:
            stage_names = {2: "第二关", 3: "第三关"}
            self.stage_announce_text = stage_names.get(self.current_level, "")
            self.stage_announce_timer = 45  # 显示 0.75 秒

    def _spawn_supplies(self):
        """自动投放弹药、护盾、武器升级、生命恢复等补给道具"""
        self.supply_spawn_timer += 1
        if self.supply_spawn_timer >= SUPPLY_SPAWN_INTERVAL:
            self.supply_spawn_timer = 0
            x = random.randint(30, SCREEN_WIDTH - 30)
            y = -20
            # 生命恢复概率随难度递增；武器升级大幅降低出现率
            life_bounds = {"简单": 0.35, "普通": 0.55, "困难": 0.75}
            shield_upper = {"简单": 0.93, "普通": 0.96, "困难": 0.97}
            r = random.random()
            if r < 0.35:
                p = BulletBox(x, y)
            elif r < life_bounds.get(self.difficulty, 0.55):
                p = LifeRecovery(x, y)
            elif r < shield_upper.get(self.difficulty, 0.80):
                p = Shield(x, y)
            else:
                p = WeaponUpgrade(x, y)
            self.powerup_group.add(p)
            self.all_sprites.add(p)

    def _spawn_enemies(self):
        # 屏幕敌机数量已达上限，不再生成（第一关按难度区分上限）
        max_enemies = MAX_ENEMIES_ON_SCREEN
        if self.current_level == 1:
            max_enemies = MAX_ENEMIES_LEVEL1.get(self.difficulty, MAX_ENEMIES_ON_SCREEN)
        if len(self.enemy_group) >= max_enemies:
            return

        mult = DIFFICULTY_MULTIPLIER[self.difficulty]
        # 动态难度影响生成间隔：难度越高，间隔越短（敌机越多）
        base_interval = ENEMY_SPAWN_INTERVAL / (mult["spawn_rate"] * self.dynamic_difficulty)
        spawn_interval = max(8, int(base_interval))  # 下限防止过于密集
        self.enemy_spawn_timer += 1

        if self.enemy_spawn_timer >= spawn_interval:
            self.enemy_spawn_timer = 0

            if self.kill_count >= BOSS_TRIGGER_KILLS and not self.boss_spawned:
                boss = Enemy(EnemyType.BOSS, mult["enemy_hp"], mult["enemy_speed"],
                             bullet_count_mult=mult.get("bullet_count", 1.0),
                             player=self.player, game_state=self)
                self.enemy_group.add(boss)
                self.all_sprites.add(boss)
                self.boss_spawned = True
                self.kill_count = 0
            else:
                # 根据游戏阶段调整敌机生成策略
                stage = self._get_game_stage()
                self._spawn_by_stage(stage, mult)

    def _get_game_stage(self):
        """获取当前游戏阶段，影响敌机生成策略"""
        if self.score < 100:
            return "early"
        elif self.score < 350:
            return "mid"
        else:
            return "late"

    def _spawn_by_stage(self, stage, mult):
        """根据游戏阶段和动态难度生成不同策略的敌机编队"""
        r = random.random()
        dyn = self.dynamic_difficulty  # 动态难度倍率 (0.35 ~ 1.6)
        bcm = mult.get("bullet_count", 1.0)  # 子弹数量缩放系数

        if stage == "early":
            # 第一关：仅生成 enemy_1 和 enemy_2，不生成 enemy_3
            if r < 0.85:
                enemy_type = EnemyType.ENEMY_1
            else:
                enemy_type = EnemyType.ENEMY_2
            enemy = Enemy(enemy_type, mult["enemy_hp"], mult["enemy_speed"],
                          bullet_count_mult=bcm, player=self.player, game_state=self)

        elif stage == "mid":
            # 中期：增加交叉封锁编队
            if r < 0.30:
                enemy_type = EnemyType.ENEMY_1
            elif r < 0.75:
                enemy_type = EnemyType.ENEMY_2
            else:
                enemy_type = EnemyType.ENEMY_3
            enemy = Enemy(enemy_type, mult["enemy_hp"], mult["enemy_speed"],
                          bullet_count_mult=bcm, player=self.player, game_state=self)

            # 偶尔生成交叉编队（同时生成两架 enemy_2），动态难度高时概率更大
            cross_chance = 0.1 + dyn * 0.18  # 0.16 ~ 0.39
            if random.random() < cross_chance:
                enemy2 = Enemy(EnemyType.ENEMY_2, mult["enemy_hp"], mult["enemy_speed"],
                               bullet_count_mult=bcm, player=self.player, game_state=self)
                # 让两架敌机初始处于交叉封锁状态
                enemy2._enter_state(STATE_CROSS)
                enemy2.ai_data["cross_target_x"] = SCREEN_WIDTH - enemy.rect.centerx
                enemy2.ai_data["cross_target_y"] = enemy.rect.centery + random.randint(-40, 40)
                enemy2.ai_data["cross_duration"] = 180
                self.enemy_group.add(enemy2)
                self.all_sprites.add(enemy2)

        else:  # late
            # 后期：高血量敌机 + 复杂行为，动态难度控制高级行为概率
            if r < 0.15:
                enemy_type = EnemyType.ENEMY_1
            elif r < 0.55:
                enemy_type = EnemyType.ENEMY_2
            else:
                enemy_type = EnemyType.ENEMY_3
            enemy = Enemy(enemy_type, mult["enemy_hp"], mult["enemy_speed"],
                          bullet_count_mult=bcm, player=self.player, game_state=self)

            # 后期预判射击型敌机概率随动态难度增长
            lead_chance = 0.1 + dyn * 0.2  # 0.17 ~ 0.42
            if random.random() < lead_chance:
                enemy._enter_state(STATE_LEAD_SHOT)

            # 后期悬停射击编队概率随动态难度增长
            hover_chance = 0.08 + dyn * 0.18  # 0.14 ~ 0.37
            if random.random() < hover_chance:
                hover_enemy = Enemy(EnemyType.ENEMY_2, mult["enemy_hp"], mult["enemy_speed"],
                                    bullet_count_mult=bcm, player=self.player, game_state=self)
                hover_enemy._enter_state(STATE_HOVER)
                hover_enemy.rect.x = random.randint(40, SCREEN_WIDTH - 40)
                hover_enemy.rect.y = random.randint(60, SCREEN_HEIGHT // 3)
                self.enemy_group.add(hover_enemy)
                self.all_sprites.add(hover_enemy)

        self.enemy_group.add(enemy)
        self.all_sprites.add(enemy)

    def _check_collisions(self):
        # 玩家子弹 vs 敌机 — 使用像素级碰撞
        for bullet in self.bullet_group:
            if not bullet.alive():
                continue
            for enemy in self.enemy_group:
                if not enemy.alive() or enemy.exploding:
                    continue
                if bullet.has_hit(enemy):
                    bullet.kill()
                    if enemy.take_damage(bullet.damage):
                        self.score += enemy.score_value
                        self.kill_count += 1
                        if enemy.is_boss:
                            self.boss_spawned = False
                            self.boss_kill_count += 1
                            self.music_player.play_enemy_down("enemy3")
                        else:
                            self.music_player.play_enemy_down(enemy.type_name)
                        # 掉落道具
                        powerup = spawn_random_powerup(enemy.rect.centerx, enemy.rect.centery, self.difficulty)
                        if powerup:
                            self.powerup_group.add(powerup)
                            self.all_sprites.add(powerup)
                        enemy.trigger_explosion()
                    break  # 一颗子弹只命中一个敌机

        # 敌机子弹 vs 玩家 — 像素级碰撞 + 伤害值
        for bullet in self.enemy_bullet_group:
            if not bullet.alive():
                continue
            if bullet.has_hit(self.player):
                bullet.kill()
                if self.player.take_damage(bullet.damage):
                    self.music_player.play_player_down()
                    self.is_gameover = True
                    self.state = "paused"

        # 敌机 vs 玩家（碰撞伤害 = 敌机类型的基础伤害）
        # 护盾期间：玩家不受伤，非Boss敌机每0.5秒受到1点伤害
        for enemy in self.enemy_group:
            if not enemy.alive() or enemy.exploding:
                continue
            if self.player.rect.colliderect(enemy.rect):
                if self.player.has_shield:
                    # 护盾撞击：对非Boss敌机造成持续伤害
                    if not enemy.is_boss:
                        enemy.shield_hit_timer -= 1
                        if enemy.shield_hit_timer <= 0:
                            enemy.shield_hit_timer = SHIELD_HIT_COOLDOWN
                            if enemy.take_damage(1):
                                self.score += enemy.score_value
                                self.kill_count += 1
                                self.music_player.play_enemy_down(enemy.type_name)
                                powerup = spawn_random_powerup(enemy.rect.centerx, enemy.rect.centery, self.difficulty)
                                if powerup:
                                    self.powerup_group.add(powerup)
                                    self.all_sprites.add(powerup)
                                enemy.trigger_explosion()
                else:
                    # 敌机撞击伤害 = 1，Boss 撞击伤害 = 2
                    collision_damage = 2 if enemy.is_boss else 1
                    if self.player.take_damage(collision_damage):
                        self.music_player.play_player_down()
                        self.is_gameover = True
                        self.state = "paused"

        # 玩家 vs 道具
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerup_group, True)
        for powerup in powerup_hits:
            powerup.apply(self.player)
            # 根据道具类型播放对应音效
            if powerup.powerup_type == "bullet_box":
                self.music_player.play_get_bullet()
            elif powerup.powerup_type == "life_recovery":
                self.music_player.play_supply()
            elif powerup.powerup_type == "shield":
                self.music_player.play_get_bomb()
            elif powerup.powerup_type == "weapon_upgrade":
                self.music_player.play_upgrade()

    def _draw_gameplay(self):
        # 背景 — 第一关循环滚动；第二关、第三关静态显示
        bg = self.backgrounds.get(self.current_level)
        if self.current_level >= 2:
            if bg:
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill(COLOR_BLACK)
                self._draw_stars()
        else:
            self.bg_scroll_y = (self.bg_scroll_y + self.bg_scroll_speed) % SCREEN_HEIGHT
            if bg:
                # 上下两张背景拼接实现无缝滚动
                self.screen.blit(bg, (0, self.bg_scroll_y - SCREEN_HEIGHT))
                self.screen.blit(bg, (0, self.bg_scroll_y))
            else:
                self.screen.fill(COLOR_BLACK)
                self._draw_stars()

        # 精灵
        self.player.draw(self.screen)
        for enemy in self.enemy_group:
            self.screen.blit(enemy.image, enemy.rect)
            if not enemy.exploding:
                enemy.draw_hp_bar(self.screen)
        for bullet in self.bullet_group:
            self.screen.blit(bullet.image, bullet.rect)
        for bullet in self.enemy_bullet_group:
            self.screen.blit(bullet.image, bullet.rect)

        # 道具 — 画在所有精灵之上，确保始终可见
        for powerup in self.powerup_group:
            self.screen.blit(powerup.image, powerup.rect)

        # 关卡公告 — 屏幕正上方居中
        if self.stage_announce_timer > 0:
            announce = self.font_large.render(self.stage_announce_text, True, COLOR_GOLD)
            self.screen.blit(announce, announce.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self):
        """左上角 HUD：弹药图标+数值 | 血量图标+数值 | 武器等级（缓存优化）"""
        margin_x = 16
        margin_y = 12
        row_gap = 40
        icon_size = 32

        # --- 弹药显示：ammo 图标 + 绝对数值 ---
        ammo_icon = self.hud_icons.get("ammo")
        if ammo_icon:
            self.screen.blit(ammo_icon, (margin_x, margin_y))
        ammo_str = str(self.player.ammo)
        if self._last_hud_values.get("ammo") != ammo_str:
            self.hud_text_cache["ammo"] = self.font_medium.render(ammo_str, True, COLOR_WHITE)
            self._last_hud_values["ammo"] = ammo_str
        self.screen.blit(self.hud_text_cache.get("ammo"), (margin_x + icon_size + 8, margin_y - 2))

        # --- 血量显示：玩家飞机图标 + 数值 ---
        hp_icon = self.hud_icons.get("hp")
        if hp_icon:
            self.screen.blit(hp_icon, (margin_x, margin_y + row_gap))
        hp_str = str(self.player.hp)
        if self._last_hud_values.get("hp") != hp_str:
            self.hud_text_cache["hp"] = self.font_medium.render(hp_str, True, COLOR_GREEN)
            self._last_hud_values["hp"] = hp_str
        self.screen.blit(self.hud_text_cache.get("hp"), (margin_x + icon_size + 8, margin_y + row_gap - 2))

        # --- 武器等级 ---
        lv = self.player.weapon_level
        if self._last_hud_values.get("weapon_level") != lv:
            self.hud_text_cache["weapon_level"] = self.font_small.render(f"Lv.{lv}", True, COLOR_GOLD)
            self._last_hud_values["weapon_level"] = lv
        self.screen.blit(self.hud_text_cache.get("weapon_level"), (margin_x, margin_y + row_gap * 2))

        # --- 右上角：分数 ---
        score_key = str(self.score)
        if self._last_hud_values.get("score") != score_key:
            self.hud_text_cache["score"] = self.font_medium.render(score_key, True, COLOR_GOLD)
            self._last_hud_values["score"] = score_key
        score_text = self.hud_text_cache.get("score")
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 16, 12))

        # --- 右上角：Boss 击杀数 ---
        if self.boss_kill_count > 0:
            bk = self.boss_kill_count
            if self._last_hud_values.get("boss_kill") != bk:
                self.hud_text_cache["boss_kill"] = self.font_small.render(f"Boss x{bk}", True, COLOR_GOLD)
                self._last_hud_values["boss_kill"] = bk
            boss_text = self.hud_text_cache.get("boss_kill")
            self.screen.blit(boss_text, (SCREEN_WIDTH - boss_text.get_width() - 16, 48))

        # --- 护盾状态 ---
        if self.player.has_shield:
            shield_remain = self.player.shield_timer / SHIELD_DURATION
            shield_seconds = max(0, self.player.shield_timer // FPS)
            # 最后3秒闪烁警告
            blink = self.player.shield_timer <= SHIELD_BLINK_START and (self.player.shield_timer // 15) % 2 == 0
            shield_key = f"shield_{shield_seconds}_{blink}"
            if self._last_hud_values.get("shield_key") != shield_key:
                shield_color = (255, 80, 80) if blink else (0, 200, 255)
                self.hud_text_cache["shield"] = self.font_small.render(f"护盾 {shield_seconds}s", True, shield_color)
                self._last_hud_values["shield_key"] = shield_key
            self.screen.blit(self.hud_text_cache.get("shield"), (margin_x, margin_y + row_gap * 2 + 28))

            # 护盾进度条
            bar_w = 100
            bar_h = 6
            bar_x = margin_x
            bar_y = margin_y + row_gap * 2 + 52
            pygame.draw.rect(self.screen, COLOR_GRAY, (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.screen, COLOR_WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
            fill_color = (255, 80, 80) if blink else (0, 200, 255)
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, int(bar_w * shield_remain), bar_h))

        # --- 底部提示已移除 ---

    # ==================== 暂停/游戏结束界面 ====================

    def _run_paused(self):
        # 暂停背景音乐
        self.music_player.pause_music()
        while self.state == "paused" and self.running:
            self.clock.tick(FPS)
            self._handle_pause_events()
            self._draw_paused()
        # 恢复背景音乐
        if self.state == "playing":
            self.music_player.unpause_music()

    def _handle_pause_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not self.is_gameover:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        self.state = "playing"
                        return
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.is_gameover = False
                        self.music_player.stop_music()
                        self.state = "menu"
                        return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if not self.is_gameover:
                    # 普通暂停：继续 / 重新开始 / 返回主菜单
                    if self._pause_btn_rect(BTN_Y_RESUME).collidepoint(mx, my):
                        self.music_player.play_button()
                        self.state = "playing"
                        return
                    if self._pause_btn_rect(BTN_Y_RESTART).collidepoint(mx, my):
                        self.music_player.play_button()
                        self._init_game()
                        self.state = "playing"
                        return
                    if self._pause_btn_rect(BTN_Y_BACK).collidepoint(mx, my):
                        self.music_player.play_button()
                        self.is_gameover = False
                        self.music_player.stop_music()
                        self.state = "menu"
                        return
                else:
                    # 游戏结束：重新开始 / 返回主菜单
                    if self._pause_btn_rect(BTN_Y_RESTART).collidepoint(mx, my):
                        self.music_player.play_button()
                        self._init_game()
                        self.state = "playing"
                        return
                    if self._pause_btn_rect(BTN_Y_BACK).collidepoint(mx, my):
                        self.music_player.play_button()
                        self.is_gameover = False
                        self.music_player.stop_music()
                        self.state = "menu"
                        return

    def _pause_btn_rect(self, y):
        return pygame.Rect(SCREEN_WIDTH//2 - BTN_WIDTH//2, y, BTN_WIDTH, BTN_HEIGHT)

    def _draw_paused(self):
        # 先绘制当前关卡背景
        bg = self.backgrounds.get(self.current_level)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(COLOR_BLACK)
            self._draw_stars()

        # 绘制半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(PAUSE_OVERLAY_ALPHA)
        overlay.fill(PAUSE_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

        if self.is_gameover:
            # 游戏结束标题 + 分数
            title = self.font_large.render("游戏结束", True, COLOR_RED)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 140)))

            score_text = self.font_medium.render(f"最终得分：{self.score}", True, COLOR_GOLD)
            self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, 220)))

            # 难度和关卡信息
            info_text = self.font_small.render(f"难度：{self.difficulty}    关卡：{self.current_level}", True, COLOR_WHITE)
            self.screen.blit(info_text, info_text.get_rect(center=(SCREEN_WIDTH//2, 260)))

            # 按钮：重新开始 / 返回主菜单
            mx, my = pygame.mouse.get_pos()
            buttons = [
                ("重新开始", BTN_Y_RESTART),
                ("返回主菜单", BTN_Y_BACK),
            ]
            for text, y in buttons:
                btn_rect = self._pause_btn_rect(y)
                hover = btn_rect.collidepoint(mx, my)
                color = COLOR_BLUE if hover else COLOR_GRAY
                pygame.draw.rect(self.screen, color, btn_rect, border_radius=8)
                pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 2, border_radius=8)
                btn_text = self.font_medium.render(text, True, COLOR_WHITE)
                self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

            tip = self.font_small.render("按 ESC 返回主菜单", True, COLOR_GRAY)
            self.screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))
        else:
            # 普通暂停
            title = self.font_large.render("游戏暂停", True, COLOR_WHITE)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 150)))

            mx, my = pygame.mouse.get_pos()
            buttons = [
                ("继续", BTN_Y_RESUME),
                ("重新开始", BTN_Y_RESTART),
                ("返回主菜单", BTN_Y_BACK),
            ]
            for text, y in buttons:
                btn_rect = self._pause_btn_rect(y)
                hover = btn_rect.collidepoint(mx, my)
                color = COLOR_BLUE if hover else COLOR_GRAY
                pygame.draw.rect(self.screen, color, btn_rect, border_radius=8)
                pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 2, border_radius=8)
                btn_text = self.font_medium.render(text, True, COLOR_WHITE)
                self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

        pygame.display.flip()

    # ==================== 背景效果 ====================

    def _draw_stars(self):
        for i, (x, y, speed) in enumerate(self.stars):
            pygame.draw.circle(self.screen, (200, 200, 200), (x, int(y)), speed)
            y += speed * 0.5
            if y > SCREEN_HEIGHT:
                y = 0
                x = random.randint(0, SCREEN_WIDTH)
            self.stars[i] = (x, y, speed)
