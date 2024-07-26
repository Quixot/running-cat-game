import curses
import time
import random
from pynput import keyboard

# Размеры окна
SCREEN_HEIGHT = 20
SCREEN_WIDTH = 120

# Игровой персонаж
PLAYER_CHAR = '🧑'

# Начальная позиция игрока
PLAYER_START_X = 5
PLAYER_START_Y = SCREEN_HEIGHT - 2

# Символы террейна, врагов и бонусов
# ⛰ 
TERRAIN_CHAR = '█' 
ENEMY_CHAR = '💩'
BONUS_CHAR = '🍓'
GROUND_CHAR = '█'

# Скорость игры
FPS = 30

class Terrain:
    def __init__(self):
        self.map = [[' ' for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]
        self.generate()

    def generate(self):
        # Генерация нижнего ряда и случайных препятствий
        for x in range(SCREEN_WIDTH):
            self.map[SCREEN_HEIGHT - 1][x] = GROUND_CHAR
        for _ in range(5):  # Несколько невысоких препятствий
            x = random.randint(0, SCREEN_WIDTH - 1)
            self.map[SCREEN_HEIGHT - 2][x] = TERRAIN_CHAR

    def draw(self, screen):
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                if self.map[y][x] == GROUND_CHAR:
                    screen.addstr(y, x, self.map[y][x], curses.color_pair(2))
                else:
                    screen.addstr(y, x, self.map[y][x])

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        screen.addstr(self.y, self.x, ENEMY_CHAR)

class Bonus:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        screen.addstr(self.y, self.x, BONUS_CHAR)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = True
        self.direction = 0  # -1 для влево, 1 для вправо, 0 для остановки
        self.score = 0

    def update(self, screen, terrain, enemies, bonuses):
        # Применение гравитации
        if not self.on_ground:
            self.vel_y += 1
        else:
            self.vel_y = 0

        # Обновление позиции игрока
        new_x = self.x + self.vel_x
        new_y = self.y + self.vel_y

        # Проверка столкновения с террейном
        if 0 <= new_x < SCREEN_WIDTH and 0 <= new_y < SCREEN_HEIGHT and terrain.map[new_y][new_x] != TERRAIN_CHAR:
            self.x = new_x
            self.y = new_y
            self.on_ground = (terrain.map[self.y + 1][self.x] == GROUND_CHAR or terrain.map[self.y + 1][self.x] == TERRAIN_CHAR) if self.y + 1 < SCREEN_HEIGHT else True
        else:
            self.vel_y = 0
            self.on_ground = True

        # Проверка столкновения с врагами
        for enemy in enemies:
            if self.x == enemy.x and self.y == enemy.y:
                return "game over"
            elif self.x == enemy.x and self.y + 1 == enemy.y and not self.on_ground:
                enemies.remove(enemy)
                self.vel_y = -3  # Пружинистое действие при ударе сверху

        # Проверка столкновения с бонусами
        for bonus in bonuses:
            if self.x == bonus.x and self.y == bonus.y:
                self.score += 1
                bonuses.remove(bonus)

        # Отрисовка игрока
        screen.addstr(self.y, self.x, str(PLAYER_CHAR))

    def move_left(self):
        self.direction = -1
        if self.on_ground:
            self.vel_x = -1

    def move_right(self):
        self.direction = 1
        if self.on_ground:
            self.vel_x = 1

    def stop_moving(self):
        self.direction = 0
        if self.on_ground:
            self.vel_x = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -3
            self.on_ground = False

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.terrain = Terrain()
        self.enemies = [Enemy(random.randint(0, SCREEN_WIDTH - 1), SCREEN_HEIGHT - 2) for _ in range(3)]
        self.bonuses = [Bonus(random.randint(0, SCREEN_WIDTH - 1), SCREEN_HEIGHT - 2) for _ in range(3)]
        self.running = True

    def update(self):
        self.screen.clear()
        self.terrain.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for bonus in self.bonuses:
            bonus.draw(self.screen)
        result = self.player.update(self.screen, self.terrain, self.enemies, self.bonuses)
        self.screen.addstr(0, 0, f'Score: {self.player.score}')
        self.screen.refresh()

        # Продолжение движения в воздухе
        if not self.player.on_ground:
            if self.player.direction == -1:
                self.player.vel_x = -1
            elif self.player.direction == 1:
                self.player.vel_x = 1

        if result == "game over":
            self.screen.addstr(SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2 - 5, "GAME OVER", curses.color_pair(1))
            self.screen.refresh()
            time.sleep(2)
            self.stop()

    def stop(self):
        self.running = False

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000 // FPS)

    # Инициализация цветовых пар
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Цвет нижнего ряда

    game = Game(stdscr)

    def on_press(key):
        try:
            if key == keyboard.Key.left:
                game.player.move_left()
            elif key == keyboard.Key.right:
                game.player.move_right()
            elif key == keyboard.Key.space:
                game.player.jump()
        except AttributeError:
            pass

    def on_release(key):
        try:
            if key in (keyboard.Key.left, keyboard.Key.right):
                game.player.stop_moving()
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while game.running:
        game.update()
        time.sleep(1 / FPS)

        # Проверка нажатия клавиши ESC
        try:
            if stdscr.getch() == 27:  # Код клавиши ESC
                game.stop()
        except curses.error:
            pass

    listener.stop()

curses.wrapper(main)
