import pygame
import random
import sys
import os
from constants import *
from src.sprites import Player, Enemy, EnemyType, PowerUp, spawn_random_powerup

class Game:
    """游戏主类，管理游戏循环和状态"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.state = "menu"  # menu / difficulty / playing / paused / gameover
        self.difficulty = "普通"
        self.running = True

        # 精灵组
        self.player_group = None
        self.enemy_group = None
        self.bullet_group = None
        self.enemy_bullet_group = None
        self.powerup_group = None
        self.all_sprites = None

        # 游戏数据
        self.score = 0
        self.enemy_spawn_timer = 0
        self.boss_spawned = False
        self.boss_kill_count = 0
        self.kill_count = 0
        self.current_level = 1

        # 背景图片
        self.backgrounds = {}
        self._load_backgrounds()

        # 字体
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)

        # 背景星星（无背景图时使用）
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT),
                       random.randint(1, 3)) for _ in range(80)]

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
            elif self.state == "paused":
                self._run_paused()
            elif self.state == "gameover":
                self._run_gameover()

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
                btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 260, 200, 50)
                if btn_rect.collidepoint(mx, my):
                    self.state = "difficulty"
                    return

    def _draw_menu(self):
        self.screen.fill(COLOR_BLACK)
        self._draw_stars()

        title = self.font_large.render("飞机大战 2026", True, COLOR_GOLD)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 120)))

        subtitle = self.font_small.render("Aircraft Battle", True, COLOR_WHITE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH//2, 180)))

        btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 260, 200, 50)
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
                    btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 200 + i * 80, 200, 50)
                    if btn_rect.collidepoint(mx, my):
                        self.difficulty = diff
                        self._init_game()
                        self.state = "playing"
                        return

    def _draw_difficulty_select(self):
        self.screen.fill(COLOR_BLACK)
        self._draw_stars()

        title = self.font_large.render("选择难度", True, COLOR_GOLD)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 100)))

        difficulties = ["简单", "普通", "困难"]
        colors = [COLOR_GREEN, COLOR_BLUE, COLOR_RED]
        descs = ["敌人较弱，适合新手", "标准挑战", "敌人更强，高分奖励"]
        mx, my = pygame.mouse.get_pos()

        for i, (diff, color, desc) in enumerate(zip(difficulties, colors, descs)):
            btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 200 + i * 80, 200, 50)
            hover = btn_rect.collidepoint(mx, my)
            btn_color = color if not hover else tuple(min(c + 40, 255) for c in color)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 2, border_radius=10)
            btn_text = self.font_medium.render(diff, True, COLOR_WHITE)
            self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))
            desc_text = self.font_small.render(desc, True, color)
            self.screen.blit(desc_text, desc_text.get_rect(center=(SCREEN_WIDTH//2, 230 + i * 80)))

        tip = self.font_small.render("按 ESC 返回主菜单", True, COLOR_GRAY)
        self.screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))

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
        self.enemy_spawn_timer = 0
        self.boss_spawned = False
        self.boss_kill_count = 0
        self.kill_count = 0
        self.current_level = 1

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
                if event.key == pygame.K_SPACE:
                    for bullet in self.player.shoot():
                        self.bullet_group.add(bullet)
                        self.all_sprites.add(bullet)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_j] or keys[pygame.K_SPACE]:
            for bullet in self.player.shoot():
                self.bullet_group.add(bullet)
                self.all_sprites.add(bullet)

        return None

    def _update_gameplay(self):
        self.player_group.update()
        self.enemy_group.update()
        self.bullet_group.update()
        self.enemy_bullet_group.update()
        self.powerup_group.update()

        # 敌机射击
        for enemy in self.enemy_group:
            bullet = enemy.shoot()
            if bullet:
                self.enemy_bullet_group.add(bullet)

        # 生成敌机
        self._spawn_enemies()

        # 关卡切换（每消灭一定数量敌机切换背景）
        self._update_level()

    def _update_level(self):
        """根据分数切换关卡背景"""
        if self.score >= 500 and self.current_level < 3:
            self.current_level = 3
        elif self.score >= 200 and self.current_level < 2:
            self.current_level = 2

    def _spawn_enemies(self):
        mult = DIFFICULTY_MULTIPLIER[self.difficulty]
        spawn_interval = int(ENEMY_SPAWN_INTERVAL / mult["spawn_rate"])
        self.enemy_spawn_timer += 1

        if self.enemy_spawn_timer >= spawn_interval:
            self.enemy_spawn_timer = 0

            if self.kill_count >= BOSS_TRIGGER_KILLS and not self.boss_spawned:
                boss = Enemy(EnemyType.BOSS, mult["enemy_hp"])
                self.enemy_group.add(boss)
                self.all_sprites.add(boss)
                self.boss_spawned = True
                self.kill_count = 0
            else:
                r = random.random()
                if r < 0.5:
                    enemy_type = EnemyType.ENEMY_1
                elif r < 0.85:
                    enemy_type = EnemyType.ENEMY_2
                else:
                    enemy_type = EnemyType.ENEMY_3

                enemy = Enemy(enemy_type, mult["enemy_hp"])
                self.enemy_group.add(enemy)
                self.all_sprites.add(enemy)

    def _check_collisions(self):
        # 玩家子弹 vs 敌机
        hits = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, False)
        for bullet, enemies in hits.items():
            for enemy in enemies:
                if enemy.take_damage(BULLET_DAMAGE):
                    self.score += enemy.score_value
                    self.kill_count += 1
                    if enemy.is_boss:
                        self.boss_spawned = False
                        self.boss_kill_count += 1
                    # 掉落道具
                    powerup = spawn_random_powerup(enemy.rect.centerx, enemy.rect.centery)
                    if powerup:
                        self.powerup_group.add(powerup)
                        self.all_sprites.add(powerup)
                    enemy.kill()
                    self.all_sprites.remove(enemy)

        # 敌机子弹 vs 玩家
        if pygame.sprite.spritecollide(self.player, self.enemy_bullet_group, True):
            if self.player.take_damage():
                self.state = "gameover"

        # 敌机 vs 玩家
        hits = pygame.sprite.spritecollide(self.player, self.enemy_group, False)
        for enemy in hits:
            if self.player.take_damage():
                self.state = "gameover"

        # 玩家 vs 道具
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerup_group, True)
        for powerup in powerup_hits:
            powerup.apply(self.player)

    def _draw_gameplay(self):
        # 背景
        bg = self.backgrounds.get(self.current_level)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(COLOR_BLACK)
            self._draw_stars()

        # 道具
        for powerup in self.powerup_group:
            self.screen.blit(powerup.image, powerup.rect)

        # 精灵
        self.player.draw(self.screen)
        for enemy in self.enemy_group:
            self.screen.blit(enemy.image, enemy.rect)
            enemy.draw_hp_bar(self.screen)
        for bullet in self.bullet_group:
            self.screen.blit(bullet.image, bullet.rect)
        for bullet in self.enemy_bullet_group:
            self.screen.blit(bullet.image, bullet.rect)

        self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self):
        # 分数
        score_text = self.font_medium.render(f"分数: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (20, 10))

        # 生命值（用 life.png 图标 + 文字）
        hp_text = self.font_medium.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, COLOR_GREEN)
        self.screen.blit(hp_text, (20, 50))

        # 弹药值
        ammo_color = COLOR_YELLOW if self.player.ammo > 10 else COLOR_RED
        ammo_text = self.font_medium.render(f"弹药: {self.player.ammo}/{self.player.max_ammo}", True, ammo_color)
        self.screen.blit(ammo_text, (20, 90))

        # 武器等级
        weapon_text = self.font_small.render(f"武器 Lv.{self.player.weapon_level}", True, COLOR_GOLD)
        self.screen.blit(weapon_text, (20, 130))

        # Boss击杀数
        if self.boss_kill_count > 0:
            boss_text = self.font_small.render(f"击败Boss: {self.boss_kill_count}", True, COLOR_GOLD)
            self.screen.blit(boss_text, (SCREEN_WIDTH - 200, 10))

        # 关卡/难度
        level_text = self.font_small.render(f"关卡: {self.current_level}  难度: {self.difficulty}", True, COLOR_GRAY)
        self.screen.blit(level_text, (SCREEN_WIDTH - 250, 40))

        # 护盾状态
        if self.player.has_shield:
            shield_text = self.font_small.render("护盾 ON", True, (0, 200, 255))
            self.screen.blit(shield_text, (SCREEN_WIDTH - 150, 70))

        tip = self.font_small.render("方向键移动 空格/J射击 ESC暂停", True, COLOR_GRAY)
        self.screen.blit(tip, (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT - 30))

    # ==================== 暂停界面 ====================

    def _run_paused(self):
        while self.state == "paused" and self.running:
            self.clock.tick(FPS)
            self._handle_pause_events()
            self._draw_paused()

    def _handle_pause_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.state = "playing"
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self._pause_btn_rect(BTN_Y_RESUME).collidepoint(mx, my):
                    self.state = "playing"
                    return
                if self._pause_btn_rect(BTN_Y_RESTART).collidepoint(mx, my):
                    self._init_game()
                    self.state = "playing"
                    return
                if self._pause_btn_rect(BTN_Y_BACK).collidepoint(mx, my):
                    self.state = "menu"
                    return

    def _pause_btn_rect(self, y):
        return pygame.Rect(SCREEN_WIDTH//2 - BTN_WIDTH//2, y, BTN_WIDTH, BTN_HEIGHT)

    def _draw_paused(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(PAUSE_OVERLAY_ALPHA)
        overlay.fill(PAUSE_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

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
            btn_text = self.font_small.render(text, True, COLOR_WHITE)
            self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

        pygame.display.flip()

    # ==================== 游戏结束界面 ====================

    def _run_gameover(self):
        while self.state == "gameover" and self.running:
            self.clock.tick(FPS)
            self._handle_gameover_events()
            self._draw_gameover()

    def _handle_gameover_events(self):
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
                if pygame.Rect(SCREEN_WIDTH//2 - 100, 320, 200, 50).collidepoint(mx, my):
                    self._init_game()
                    self.state = "playing"
                    return
                if pygame.Rect(SCREEN_WIDTH//2 - 100, 390, 200, 50).collidepoint(mx, my):
                    self.state = "menu"
                    return

    def _draw_gameover(self):
        self.screen.fill(COLOR_BLACK)
        self._draw_stars()

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("游戏结束", True, COLOR_RED)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 120)))

        score_text = self.font_medium.render(f"最终得分: {self.score}", True, COLOR_GOLD)
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, 200)))

        mx, my = pygame.mouse.get_pos()
        for text, y in [("重新开始", 320), ("返回主菜单", 390)]:
            btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, y, 200, 50)
            hover = btn_rect.collidepoint(mx, my)
            color = COLOR_BLUE if hover else COLOR_GRAY
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 2, border_radius=10)
            btn_text = self.font_small.render(text, True, COLOR_WHITE)
            self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

        tip = self.font_small.render("按 ESC 返回主菜单", True, COLOR_GRAY)
        self.screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))

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
