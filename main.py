import pygame
import sqlite3
import os
import sys
import random

import config

step = config.PLAYER_SPEED
clock = pygame.time.Clock()
player = None
bullets = []
coord_monster = [(327, 26), (630, 269), (335, 530), (30, 274)]
tile_width = tile_height = 50

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()


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
monster_image = load_image(config.MONSTER_UP)
bullet_image = load_image(config.BULLET_IMAGE)


# Класс для тайлов
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# Класс для пули
class Bullet:
    def __init__(self, x, y):
        self.image = bullet_image
        self.rect = pygame.Rect(x, y, 10, 5)  # Прямоугольник для пули
        self.speed = config.BULLET_SPEED  # Скорость пули
        self.rotation = None

    def check_rotation(self, rotation):
        self.rotation = rotation

    def bullet_left(self):
        self.rect.x -= self.speed

    def bullet_right(self):
        self.rect.x += self.speed

    def bullet_up(self):
        self.rect.y -= self.speed

    def bullet_down(self):
        self.rect.y += self.speed

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


# Класс для игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)

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


# Класс для игрока
class Monster(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(monster_group, all_sprites)
        self.image = monster_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)


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
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

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

    size = width, height = config.WIDTH, config.HEIGHT
    screen = pygame.display.set_mode(size)

    running = True

    start_screen()  # Запуск заставки
    player, level_x, level_y = generate_level(load_level('lev1.txt'))

    left = right = up = down = False

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

        tiles_group.draw(screen)
        player_group.draw(screen)
        monster_group.draw(screen)


        '''
        Ограничение передвижения для персонажа
        '''
        if player.rect.centerx <= 61:  # Правая стена
            player.rect.centerx += 1

        if player.rect.centerx >= 588:  # Левая стена
            player.rect.centerx -= 1

        if player.rect.centery <= 72:  # Верхняя стена
            player.rect.centery += 1

        if player.rect.centery >= 485:  # Нижняя стена
            player.rect.centery -= 1

        # Отрисовка
        for bullet in bullets:
            bullet.draw(screen)

        # Обновление положения пуль
        for bullet in bullets:
            bullet.update()

        clock.tick(config.FPS)
        pygame.display.flip()
    pygame.quit()
