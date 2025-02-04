import pygame
import sqlite3
import os
import sys

import config

clock = pygame.time.Clock()
player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

bullet_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
tile_width = tile_height = 50


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bullet_group, all_sprites)
        self.image = load_image(config.BULLET_IMAGE)
        self.rect = self.image.get_rect().move(5 * pos_x + 15, 13 * pos_y)
        self.speed = config.BULLET_SPEED  # Скорость пули

    def update(self):
        self.rect.x += self.speed  # Движение пули вправо

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color(0, 0, 0), self.rect)


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    fullname = os.path.join('../data/image/', name)
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

'''
Загрузка уровня из txt-файла
'''


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


'''
Генерация уровня
'''


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


'''
Настройка заставки
'''


def start_screen():
    intro_text = ["Monster Shooting", "",
                  'Добро пожаловать в "Zombie Shooting"',
                  '',
                  "Правила игры:",
                  "Убивайте монстров до окончания таймера ",
                  "чтобы перейти на другой уровень!",
                  "",
                  "Если у вас закончатся жизни, вы проиграете!",
                  "",
                  "",
                  "",
                  "Для начала игры нажмите на любую кнопку"]

    fon = pygame.transform.scale(load_image(config.BACKGROUND_IMAGE), (config.WIDTH, config.HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(config.FONT_FILE, 14)
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
                screen.fill((0, 0, 0))
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(config.FPS)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Zombie Shooting')

    size = width, height = config.WIDTH, config.HEIGHT
    screen = pygame.display.set_mode(size)

    running = True
    left = right = up = down = False

    start_screen()  # Запуск заставки
    player, level_x, level_y = generate_level(load_level('lev1.txt'))
    bullets = []
    '''
    Игровой цикл
    '''
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_w:
                    up = True
                    player.rect.y -= config.PLAYER_SPEED
                if event.key == pygame.K_a:
                    left = True
                    player.rect.x -= config.PLAYER_SPEED
                if event.key == pygame.K_d:
                    right = True
                    player.rect.x += config.PLAYER_SPEED

                if event.key == pygame.K_w:
                    up = False
                    player.rect.y -= config.PLAYER_SPEED
                if event.key == pygame.K_d:
                    right = False
                    player.rect.x += config.PLAYER_SPEED
                if event.key == pygame.K_a:
                    left = False
                    player.rect.x -= config.PLAYER_SPEED
                if event.key == pygame.K_s:
                    down = False
                    player.rect.y += config.PLAYER_SPEED

                if event.key == pygame.K_SPACE:  # При нажатии пробела создаем пулю
                    bullet = Bullet(player.rect.x, player.rect.y)
                    bullets.append(bullet)

                # Обновление положения пуль
                for bullet in bullets:
                    bullet.update()

                for bullet in bullets:
                    bullet.draw(screen)

        tiles_group.draw(screen)
        player_group.draw(screen)
        clock.tick(config.FPS)
        pygame.display.flip()
    pygame.quit()
