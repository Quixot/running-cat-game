import curses
import time
from functions import random_even
from pynput import keyboard
import random
# from wcwidth import wcwidth

# Размеры окна
SCREEN_HEIGHT = 20
SCREEN_WIDTH = 120

# Скорость игры
FPS = 30

# Начальная позиция игрока
PLAYER_START_X = 2
PLAYER_START_Y = SCREEN_HEIGHT - 2


# Игровые персонажи и объекты
PLAYER_CHAR = '😽'
ENEMY_CHAR = '💩'
BONUS_CHAR = (
    ('🍏','🍎'), 
    ('🍉','🍇'), 
    ('🍒','🍓'), 
    ('🌈', '🌞'),
    ('🌲', '🌳', '🌴', '🌵'),
    ('🍄'),
    ('🍻,🍺'),
    ('💳')
)
TERRAIN_CHAR = '🧇'
GROUND_CHAR = '🧇'

# Не использовать 2 раза клетку если на ней уже есть объект
USING_CELLS = set()




class Terrain:
    def __init__(self):
        self.map = [[' ' for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]
        self.generate()

    def generate(self):
        # Генерация нижнего ряда
        for x in range(SCREEN_WIDTH):
            self.map[SCREEN_HEIGHT - 1][x] = GROUND_CHAR

        # Случайные препятствия
        for _ in range(5):
            x = random_even(10, SCREEN_WIDTH - 10)

            # Уже занятые ячейки нельзя использовать
            USING_CELLS.add(x)
            USING_CELLS.add(x+2)
            USING_CELLS.add(x+4)

            self.map[SCREEN_HEIGHT - 2][x] = TERRAIN_CHAR
            self.map[SCREEN_HEIGHT - 2][x+2] = TERRAIN_CHAR
            self.map[SCREEN_HEIGHT - 3][x+2] = TERRAIN_CHAR
            self.map[SCREEN_HEIGHT - 2][x+4] = TERRAIN_CHAR



    def draw(self, screen):
        for y in range(SCREEN_HEIGHT):
            for x in range(0, SCREEN_WIDTH, 2):
                if self.map[y][x] == GROUND_CHAR:
                    screen.addstr(y, x, self.map[y][x]) , # curses.color_pair(2)
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
        self.bonus = random.choice(BONUS_CHAR) # Рандомный эмоджи бонуса

    def draw(self, screen):
        screen.addstr(self.y, self.x,random.choice(self.bonus))

class Player:
    def __init__(self, x, y, score=0, enemydown=0):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = True
        self.direction = 0  # -2 для влево, 2 для вправо, 0 для остановки
        self.score = score
        self.enemydown = enemydown

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
        if 0 <= new_x < SCREEN_WIDTH -1 and 0 <= new_y < SCREEN_HEIGHT and terrain.map[new_y][new_x] != TERRAIN_CHAR:
            self.x = new_x
            self.y = new_y
            self.on_ground = (terrain.map[self.y + 1][self.x] == GROUND_CHAR or terrain.map[self.y + 1][self.x] == TERRAIN_CHAR) if self.y + 1 < SCREEN_HEIGHT else True
        else:
            self.vel_y = 0
            self.on_ground = True

        # Проверка столкновения с врагами
        for enemy in enemies:
            
            # if (self.x == enemy.x and self.y + 1 == enemy.y)\
            #     or (self.x == enemy.x - 1 and self.y + 1 == enemy.y)\
            #     or (self.x == enemy.x + 1 and self.y + 1 == enemy.y) and not self.on_ground:
                
            #     self.enemydown += 1
            #     enemies.remove(enemy)

            #     self.vel_y = -3  # Пружинистое действие при ударе сверху

            if self.x == enemy.x and self.y == enemy.y:
                return "game over"
            
            elif self.x == SCREEN_WIDTH - 2:
                return "next level"
                

        # Проверка столкновения с бонусами
        for bonus in bonuses:
            if self.x == bonus.x and self.y == bonus.y:
                self.score += 1
                bonuses.remove(bonus)

        # Отрисовка игрока
        screen.addstr(self.y, self.x, str(PLAYER_CHAR))

    def move_left(self):
        self.direction = -2
        if self.on_ground:
            self.vel_x = -2

    def move_right(self):
        self.direction = 2
        if self.on_ground:
            self.vel_x = 2

    def stop_moving(self):
        self.direction = 0
        if self.on_ground:
            self.vel_x = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -3
            self.on_ground = False

class Game:
    def __init__(self, screen, score, enemydown):
        self.screen = screen
        self.player = Player(PLAYER_START_X, PLAYER_START_Y, score, enemydown)
        self.terrain = Terrain()

        
        # self.enemies = [Enemy(random.choice(list(set(range(SCREEN_HEIGHT)) - USING_CELLS)), SCREEN_HEIGHT - 2) for _ in range(3)]
        
        # Произвольно расставляем 3 врагов
        self.enemies = []
        
        for _ in range(3):
            enemy_pos = random.choice(list(set(range(6, SCREEN_WIDTH-6)) - USING_CELLS))
            
            if enemy_pos % 2 == 0:
                self.enemies.append(Enemy(enemy_pos, SCREEN_HEIGHT - 2))
                USING_CELLS.add(enemy_pos)
            else:
                self.enemies.append(Enemy(enemy_pos + 1, SCREEN_HEIGHT - 2))
                USING_CELLS.add(enemy_pos + 1)
            
            


        
        # self.bonuses = [Bonus(random_even(0, SCREEN_WIDTH - 10), SCREEN_HEIGHT - 2) for _ in range(3)]

        # Произвольно расставляем 3 бонуса
        self.bonuses = []

        for _ in range(3):
            bonus_pos = random.choice(list(set(range(6, SCREEN_WIDTH-6)) - USING_CELLS))
            
            if bonus_pos % 2 == 0:
                self.bonuses.append(Bonus(bonus_pos, SCREEN_HEIGHT - 2))
                USING_CELLS.add(bonus_pos)
            else:
                self.bonuses.append(Bonus(bonus_pos + 1, SCREEN_HEIGHT - 2))
                USING_CELLS.add(bonus_pos + 1)
            
            

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
        # self.screen.addstr(2, 0, f'Enemies terminated: {self.player.enemydown}')
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
            time.sleep(1)
            # self.stop()
            self.reload(0, 0)

        if result == "next level":
            self.screen.addstr(SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2 - 5, "NEXT LEVEL", curses.color_pair(1))
            self.screen.refresh()
            time.sleep(1)
            self.reload(self.player.score, self.player.enemydown)

    def stop(self):
        self.running = False

    def reload(self, score, enemydown):
        self.__init__(self.screen, score, enemydown)
        


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000 // FPS)

    # Инициализация цветовых пар
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Цвет нижнего ряда

    game = Game(stdscr, 0, 0)

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
