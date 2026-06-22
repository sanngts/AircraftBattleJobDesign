import os
import pygame
from constants import SOUND_PATH

class MusicPlayer:
    """音乐播放器 — 管理背景音乐与游戏音效"""

    def __init__(self):
        pygame.mixer.init()

        # --- 1. 背景音乐 ---
        self.bg_music_file = "game_music.ogg"
        self._load_bg_music()

        # --- 2. 音效字典 ---
        self.sound_dict = {}
        self._load_sounds()

    def _load_bg_music(self):
        """加载并循环播放背景音乐"""
        path = os.path.join(SOUND_PATH, self.bg_music_file)
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.3)
        except (pygame.error, FileNotFoundError):
            pass  # 音乐文件不存在时静默

    def _load_sounds(self):
        """遍历 sounds 目录，加载所有 .wav 音效文件"""
        try:
            files = os.listdir(SOUND_PATH)
        except FileNotFoundError:
            return

        for file_name in files:
            # 只加载 .wav 音效，跳过背景音乐 .ogg
            if not file_name.endswith(".wav"):
                continue
            file_path = os.path.join(SOUND_PATH, file_name)
            try:
                sound = pygame.mixer.Sound(file_path)
                # 使用文件名（不含扩展名）作为 key
                key = os.path.splitext(file_name)[0]
                self.sound_dict[key] = sound
            except (pygame.error, FileNotFoundError):
                pass

    # ==================== 背景音乐控制 ====================

    def play_music(self):
        """开始/恢复背景音乐"""
        try:
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def pause_music(self):
        """暂停背景音乐"""
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            pass

    def unpause_music(self):
        """恢复背景音乐"""
        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            pass

    def stop_music(self):
        """停止背景音乐"""
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

    # ==================== 音效播放 ====================

    def play_sound(self, sound_name):
        """播放指定音效（通过文件名 key）

        :param sound_name: 音效文件名（不含扩展名），如 'bullet', 'enemy1_down'
        """
        sound = self.sound_dict.get(sound_name)
        if sound:
            sound.play()

    # ==================== 便捷接口 ====================

    def play_bullet(self):
        """玩家射击音效"""
        self.play_sound("bullet")

    def play_enemy_down(self, enemy_type="enemy1"):
        """敌机击毁音效"""
        self.play_sound(f"{enemy_type}_down")

    def play_enemy_flying(self):
        """敌机飞行音效"""
        self.play_sound("enemy3_flying")

    def play_player_down(self):
        """玩家被击毁音效"""
        self.play_sound("me_down")

    def play_get_bullet(self):
        """拾取弹药音效"""
        self.play_sound("get_bullet")

    def play_get_bomb(self):
        """拾取炸弹音效"""
        self.play_sound("get_bomb")

    def play_supply(self):
        """拾取补给音效"""
        self.play_sound("supply")

    def play_upgrade(self):
        """武器升级音效"""
        self.play_sound("upgrade")

    def play_button(self):
        """按钮点击音效"""
        self.play_sound("button")

    def play_use_bomb(self):
        """使用炸弹音效"""
        self.play_sound("use_bomb")
