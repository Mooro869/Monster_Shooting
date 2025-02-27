from datetime import datetime
import random
import os
import sys

import pygame
import sqlite3

import config

step = config.PLAYER_SPEED
clock = pygame.time.Clock()
player = None
bullets = []
coord_monster = [(6, 0), (12, 5), (6, 10), (0, 5)]
tile_width = tile_height = 50

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()


# Подключение к базе данных
def create_connection():
    conn = sqlite3.connect(config.BD_FILE)
    return conn


def insert_score(conn, score):
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Получаем текущую дату и время
    cursor.execute('''
        INSERT INTO Rating (score, date)
        VALUES (?, ?)
    ''', (score, date))
    conn.commit()


# Отображения экрана победы
def show_victory_screen():
    font = pygame.font.Font(config.FONT_FILE, 40)
    victory_text = font.render("Победа!", True, GREEN)
    text_rect = victory_text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))

    screen.fill(BLACK)
    screen.blit(victory_text, text_rect)
    pygame.display.flip()

    # Ждем нажатия клавиши, чтобы выйти
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False


# Отображения экрана поражения
def show_game_over_screen():
    font = pygame.font.Font(config.FONT_FILE, 40)
    game_over_text = font.render("Игра окончена", True, RED)
    text_rect = game_over_text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))

    screen.fill(BLACK)
    screen.blit(game_over_text, text_rect)
    pygame.display.flip()

    # Ждем нажатия клавиши, чтобы выйти
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False


def load_image(name, color_key=None):
    fullname = os.path.join('data/image/', name)
    image = pygame.image.load(fullname)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


tile_images = {
    'wall': load_image(config.BOX),
    'empty': load_image(config.GRASS)
}
player_image = load_image(config.PLAYER_UP)
monster_image = load_image(config.MONSTER_RIGHT)


# Класс для тайлов
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# Класс для пули
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(bullets_group, all_sprites)
        self.rect = pygame.Rect(x, y, 10, 5)  # Прямоугольник для пули
        self.speed = config.BULLET_SPEED  # Скорость пули
        self.rotation = None

    def check_rotation(self, rotation):
        self.rotation = rotation

    def update(self):
        if self.rotation == 'right':
            self.rect.x += self.speed
        elif self.rotation == 'left':
            self.rect.x -= self.speed
        elif self.rotation == 'up':
            self.rect.y -= self.speed
        elif self.rotation == 'down':
            self.rect.y += self.speed

    def draw(self, surface):

        pygame.draw.rect(surface, BLACK, self.rect)


# Класс для пули
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(bullets_group, all_sprites)
        self.rect = pygame.Rect(x, y, 10, 5)  # Прямоугольник для пули
        self.speed = config.BULLET_SPEED  # Скорость пули
        self.rotation = None

    def check_rotation(self, rotation):
        self.rotation = rotation

    def update(self):
        if self.rotation == 'right':
            self.rect.x += self.speed
        elif self.rotation == 'left':
            self.rect.x -= self.speed
        elif self.rotation == 'up':
            self.rect.y -= self.speed
        elif self.rotation == 'down':
            self.rect.y += self.speed

        # Проверяем столкновение с монстрами
        hit_monsters = pygame.sprite.spritecollide(self, monster_group, True)  # Удаляем столкнувшиеся монстры
        if hit_monsters:
            player.score += 1  # Увеличиваем счет на 1 при попадании
            self.kill()  # Удаляем пулю после столкновения

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)


# Класс для игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.health = 3  # Начальное здоровье игрока
        self.invincible = False  # Флаг неуязвимости
        self.invincible_time = 2000  # Время неуязвимости в миллисекундах
        self.last_hit_time = 0  # Время последнего касания
        self.score = 0  # Начальное количество очков

    def take_damage(self, amount):
        if not self.invincible:  # Если игрок не неуязвим
            self.health -= amount
            if self.health < 0:
                self.health = 0
            self.invincible = True  # Включаем неуязвимость
            self.last_hit_time = pygame.time.get_ticks()  # Запоминаем время последнего касания

    def update(self):
        # Проверяем, истекло ли время неуязвимости
        if self.invincible and pygame.time.get_ticks() - self.last_hit_time > self.invincible_time:
            self.invincible = False  # Сбрасываем неуязвимость

    def draw_health(self, surface):
        font = pygame.font.Font(config.FONT_FILE, 15)
        health_text = font.render(f"Health: {self.health}", True, WHITE)
        surface.blit(health_text, (10, 10))  # Отображаем здоровье в (10, 10)

    def draw_score(self, surface):
        font = pygame.font.Font(config.FONT_FILE, 15)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 30))  # Отображаем счет в (10, 30)

    def check_rotation(self, rotation):
        self.rotation = rotation
        if self.rotation == 'right':
            self.image = load_image(config.PLAYER_RIGHT)
        elif self.rotation == 'left':
            self.image = load_image(config.PLAYER_LEFT)
        elif self.rotation == 'up':
            self.image = load_image(config.PLAYER_UP)
        elif self.rotation == 'down':
            self.image = load_image(config.PLAYER_DOWN)


# Класс для монстров
class Monster(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(monster_group, all_sprites)
        self.image = load_image(config.MONSTER_RIGHT)
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = monster_image

        # Начальная позиция монстра
        self.start_x = self.rect.x
        # Задаем максимальное смещение по х
        self.max_distance = 500  # Используйте нужное вам значение
        self.direction = 1  # 1 для движения вправо, -1 для движения влево

    def move(self):
        # Изменяем положение в зависимости от направления
        self.rect.x += self.direction * config.MONSTER_SPEED

        # Проверяем, достигли ли мы максимальной дистанции
        if self.rect.x >= self.start_x + self.max_distance or self.rect.x <= self.start_x:
            self.direction *= -1  # Меняем направление при достижении границы

    def update(self):
        self.move()
        if self.direction == 1:
            self.image = load_image(config.MONSTER_RIGHT)  # Двигается вправо
        else:
            self.image = load_image(config.MONSTER_LEFT)  # Двигается влево

    @staticmethod
    def spawn_monster():
        pos_x = 1  # фиксированное значение x для спавна
        pos_y = random.randint(1, 9)  # случайное значение y от 1 до 9
        Monster(pos_x, pos_y)  # создание нового монстра


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def start_screen():
    intro_text = ["Monster Shooting",
                  'Добро пожаловать в "Monster Shooting"',
                  '',
                  "",
                  "Убивайте монстров чтобы не умереть!",
                  "Цель игры - набрать 1000 очков!!!",
                  "",
                  "",
                  "Чтобы начать игру нажмите на любую кнопку"]

    fon = pygame.transform.scale(load_image(config.BACKGROUND_IMAGE), (config.WIDTH, config.HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(config.FONT_FILE, 15)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                screen.fill(BLACK)
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(config.FPS)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Monster Shooting')

    # Создание объекта-плеера
    music = pygame.mixer.music

    # Загрузка музыкального файла
    music.load(config.MUSIC_FILE)

    # Установка громкости
    music.set_volume(0.05)

    # Включение музыки на повтор
    music.play(-1)

    size = width, height = config.WIDTH, config.HEIGHT
    screen = pygame.display.set_mode(size)

    running = True

    start_screen()  # Запуск заставки
    player, level_x, level_y = generate_level(load_level('lev1.txt'))  # Генерация уровня

    monster = Monster(1, 5)

    while running:
        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_w:
                    up = True
                    player.rect.y -= step
                    Player.check_rotation(player, 'up')
                if event.key == pygame.K_a:
                    left = True
                    player.rect.x -= step
                    Player.check_rotation(player, 'left')
                if event.key == pygame.K_d:
                    down = True
                    player.rect.x += step
                    Player.check_rotation(player, 'right')
                if event.key == pygame.K_s:
                    down = True
                    player.rect.y += step
                    Player.check_rotation(player, 'down')

                if event.key == pygame.K_w:
                    up = False
                    player.rect.y -= step
                    Player.check_rotation(player, 'up')

                if event.key == pygame.K_d:
                    right = False
                    player.rect.x += step
                    Player.check_rotation(player, 'right')

                if event.key == pygame.K_a:
                    left = False
                    player.rect.x -= step
                    Player.check_rotation(player, 'left')

                if event.key == pygame.K_s:
                    down = False
                    player.rect.y += step
                    Player.check_rotation(player, 'down')

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    bullet = Bullet(player.rect.centerx, player.rect.centery)
                    bullets.append(bullet)
                    bullet.check_rotation('left')

                if keys[pygame.K_RIGHT]:
                    bullet = Bullet(player.rect.centerx, player.rect.centery)
                    bullets.append(bullet)
                    bullet.check_rotation('right')

                if keys[pygame.K_UP]:
                    bullet = Bullet(player.rect.centerx, player.rect.centery)
                    bullets.append(bullet)
                    bullet.check_rotation('up')

                if keys[pygame.K_DOWN]:
                    bullet = Bullet(player.rect.centerx, player.rect.centery)
                    bullets.append(bullet)
                    bullet.check_rotation('down')

        # Проверяем столкновение между игроком и монстрами
        if pygame.sprite.spritecollideany(player, monster_group):
            player.take_damage(1)  # Уменьшаем здоровье на 1 при касании

        all_sprites.update()

        tiles_group.draw(screen)
        player_group.draw(screen)
        monster_group.draw(screen)

        monster.spawn_monster()

        player.draw_health(screen)
        player.draw_score(screen)

        # Ограничение передвижения для персонажа

        if player.rect.centerx <= 61:  # Правая стена
            player.rect.centerx += 1

        if player.rect.centerx >= 588:  # Левая стена
            player.rect.centerx -= 1

        if player.rect.centery <= 72:  # Верхняя стена
            player.rect.centery += 1

        if player.rect.centery >= 485:  # Нижняя стена
            player.rect.centery -= 1

        # Отрисовка пуль
        for bullet in bullets:
            bullet.draw(screen)

        # Обновление положения пуль
        for bullet in bullets:
            bullet.update()

        # Обновление движения монстров
        for el in monster_group:
            el.move()
            el.update()

        # Проверяем условия победы и поражения
        if player.score >= 1000:
            insert_score(create_connection(), player.score)  # Вставить очки и дату
            show_victory_screen()  # Показываем экран победы
            running = False  # Завершаем основной цикл

        elif player.health <= 0:
            insert_score(create_connection(), player.score)
            show_game_over_screen()  # Показываем экран поражения
            running = False  # Завершаем основной цикл

        clock.tick(config.FPS)
        pygame.display.flip()

    create_connection().close()
    pygame.quit()
