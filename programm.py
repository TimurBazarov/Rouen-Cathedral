import pygame
import os
import sys


FPS, WIDTH, HEIGHT = 50, 640, 640
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
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
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

tile_width = tile_height = 32
tile_size = tile_width, tile_height


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.image = pygame.transform.scale(self.image, tile_size)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.mask = pygame.mask.from_surface(player_image)
        self.image = player_image
        self.image = pygame.transform.scale(self.image, tile_size)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('.', x, y)
            elif level[y][x] == '@':
                Tile('.', x, y)
                new_player = Player(x, y)
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
    return new_player, x, y


def find_hero(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                return y, x


if __name__ == '__main__':
    start_screen()
    pygame.display.set_caption('Mario')
    level = load_level('1.txt')

    running = True
    player, level_x, level_y = generate_level(load_level('1.txt'))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                '''Движение происходит, если плитка, в которую хочет перейти персонаж, не является стеной, и если
                    персонаж не выходит за рамки уровня.'''
                y, x = find_hero(level)
                if event.key == pygame.K_s:
                    if y + 1 not in range(len(level)):
                        continue
                    if level[y + 1][x] not in wall_tiles:
                        level[y][x], level[y + 1][x] = level[y + 1][x], level[y][x]
                if event.key == pygame.K_w:
                    if y - 1 not in range(len(level)):
                        continue
                    if level[y - 1][x] not in wall_tiles:
                        level[y][x], level[y - 1][x] = level[y - 1][x], level[y][x]
                if event.key == pygame.K_d:
                    if x + 1 not in range(len(level)):
                        continue
                    if level[y][x + 1] not in wall_tiles:
                        level[y][x], level[y][x + 1] = level[y][x + 1], level[y][x]
                if event.key == pygame.K_a:
                    if x - 1 not in range(len(level)):
                        continue
                    if level[y][x - 1] not in wall_tiles:
                        level[y][x], level[y][x - 1] = level[y][x - 1], level[y][x]
        generate_level(level)
        all_sprites.draw(screen)
        pygame.display.flip()
