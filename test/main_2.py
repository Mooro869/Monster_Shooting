import pygame
import sqlite3
import os
import sys

import config

# Инициализация Pygame
pygame.init()
clock = pygame.time.Clock()

# Задаем размеры окна
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
# Задаем заголовок окна
pygame.display.set_caption("Zombie Shooting")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

bullet_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
tile_width = tile_height = 50
bullets = []


# Класс для персонажа
class Player:
    def __init__(self, x, y):
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * x + 15, tile_height * y + 5)  # Прямоугольник для персонажа
        self.speed = config.PLAYER_SPEED  # Скорость персонажа

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)


# Класс для пули
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 5)  # Прямоугольник для пули
        self.speed = config.BULLET_SPEED  # Скорость пули
        self.rotarion = None

    def check_rotation(self, rotation):
        self.rotarion = rotation

    def bullet_left(self):
        self.rect.x -= self.speed

    def bullet_right(self):
        self.rect.x += self.speed

    def bullet_up(self):
        self.rect.y -= self.speed

    def bullet_down(self):
        self.rect.y += self.speed

    def update(self):
        if self.rotarion == 'right':
            self.rect.x += self.speed
        elif self.rotarion == 'left':
            self.rect.x -= self.speed
        elif self.rotarion == 'up':
            self.rect.y -= self.speed
        elif self.rotarion == 'down':
            self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)


# Класс для клетки
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


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
    intro_text = ["Zombie Shooting", "",
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
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                screen.fill((0, 0, 0))
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(config.FPS)


# Главная функция
def main():
    start_screen()  # Запуск заставки
    player, level_x, level_y = generate_level(load_level('lev1.txt'))

    tiles_group.draw(screen)
    player.draw(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.move(-player.speed, 0)
        if keys[pygame.K_d]:
            player.move(player.speed, 0)
        if keys[pygame.K_w]:
            player.move(0, -player.speed)
        if keys[pygame.K_s]:
            player.move(0, player.speed)

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

        # Обновление положения пуль
        for bullet in bullets:
            bullet.update()

        # Отрисовка
        for bullet in bullets:
            bullet.draw(screen)

        if Bullet.rect.y >= 800:
            print(True)


        clock.tick(config.FPS)  # Ограничение кадров в секунду
        pygame.display.flip()


if __name__ == "__main__":
    main()
