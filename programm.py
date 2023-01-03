import pygame
import os
import sys
from random import choice


FPS, WIDTH, HEIGHT = 50, 640, 640
tile_width = tile_height = 32
tile_size = tile_width, tile_height
pygame.init()
size = width, height = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_images = {
    '.': load_image('Tile_12.png'),
    'T': load_image('Tile_01.png'),
    '-': load_image('Tile_33.png'),
    '|': load_image('Tile_55.png'),
    'C': load_image('Tile_32.png'),
    '7': load_image('Tile_03.png'),
    'L': load_image('Tile_21.png'),
    'A': load_image('Tile_54.png'),
    'J': load_image('Tile_23.png'),
    't': load_image('Tile_11.png'),
    'D': load_image('Tile_34.png'),
    'U': load_image('Tile_56.png')
}
'''Символы стен. Например, Символ Т означает, что блок -  стена, у которой справа, слева и внизу
 есть продолжения. Символ 7 означает правый верхний угол. Символ D означает конец стены, которая шла слева направо.
 Дальше по аналогии.'''
wall_tiles = ['T', '-', '|', 'C', '7', 'L', 'A', 'J', 't', 'D', 'U']
#  . @ T - | C 7 L A J t D U - все использующиеся символы
player_image = load_image('mario.png')
artefacts_images = {
    '1': load_image('artefact1.png')
}


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == '.':
            super().__init__(ground_group, all_sprites)
        else:
            super().__init__(walls_group, all_sprites)
        self.image = tile_images[tile_type]
        self.image = pygame.transform.scale(self.image, tile_size)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.mask = pygame.mask.from_surface(player_image)
        self.image = player_image
        self.image = pygame.transform.scale(self.image, tile_size)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.x, self.y = pos_x, pos_y

    def find_current_tile(self):
        pass

    def move(self, dx, dy):
        self.rect = self.rect.move(dx, dy)

    def return_x_y(self):
        return self.x, self.y


class Artefact(pygame.sprite.Sprite):
    def __init__(self, artefact_type, pos_x, pos_y):
        super().__init__(artefacts_group)
        self.image = artefacts_images[artefact_type]
        self.rect = self.image.get_rect().move(pos_x * tile_width, pos_y * tile_height)


player = None

all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
artefacts_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('.', x, y)
            elif level[y][x] == '@':
                Tile('.', x, y)
                new_player = Player(x * tile_width, y * tile_height)
            elif level[y][x] == 'T':
                Tile('T', x, y)
            elif level[y][x] == '-':
                Tile('-', x, y)
            elif level[y][x] == '|':
                Tile('|', x, y)
            elif level[y][x] == 'C':
                Tile('C', x, y)
            elif level[y][x] == '7':
                Tile('7', x, y)
            elif level[y][x] == 'L':
                Tile('L', x, y)
            elif level[y][x] == 'A':
                Tile('A', x, y)
            elif level[y][x] == 'J':
                Tile('J', x, y)
            elif level[y][x] == 't':
                Tile('t', x, y)
            elif level[y][x] == 'D':
                Tile('D', x, y)
            elif level[y][x] == 'U':
                Tile('U', x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x + 1, y + 1


def choose_random_empty_coords(level):
    empty = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                empty.append((y, x))
    y, x = choice(empty)
    level[y][x] = '1'
    return y, x


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def update(self, x, y):
        self.dx -= x
        self.dy -= y

    def return_d(self):
        return self.dx, self.dy


if __name__ == '__main__':
    start_screen()
    pygame.display.set_caption('Mario')
    level = load_level('1.txt')

    running = True
    to_move_up, to_move_down, to_move_right, to_move_left = False, False, False, False
    player, level_w, level_h = generate_level(level)
    camera = Camera()
    Artefact('1', *choose_random_empty_coords(level))
    surf = pygame.Surface((level_w * tile_width, level_h * tile_height))
    all_sprites.draw(surf)
    step = 5
    while running:
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                '''Движение происходит, если плитка, в которую хочет перейти персонаж, не является стеной, и если
                    персонаж не выходит за рамки уровня.'''
                if event.key == pygame.K_s:
                    to_move_down = True
                if event.key == pygame.K_w:
                    to_move_up = True
                if event.key == pygame.K_d:
                    to_move_right = True
                if event.key == pygame.K_a:
                    to_move_left = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    to_move_down = False
                elif event.key == pygame.K_w:
                    to_move_up = False
                elif event.key == pygame.K_d:
                    to_move_right = False
                elif event.key == pygame.K_a:
                    to_move_left = False
            if to_move_down:
                dy += step
            elif to_move_up:
                dy -= step
            elif to_move_right:
                dx += step
            elif to_move_left:
                dx -= step
        screen.fill('black')
        moved_player, moved_x, moved_y = generate_level(level)
        camera.update(dx, dy)
        ds = camera.return_d()
        artefacts_group.draw(surf)
        screen.blit(surf, ds)
        player_group.draw(screen)
        pygame.display.flip()
