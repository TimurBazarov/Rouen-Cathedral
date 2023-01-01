import pygame
import sys
import os
from random import choice


FPS = 50
pygame.init()
size = WIDTH, HEIGHT = 550, 550
screen = pygame.display.set_mode(size)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ['Перемещение героя',
                  '',
                  'Камера']

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
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
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = os.path.join('data', filename)
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
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'empty':
            super().__init__(tiles_group, all_sprites)
        else:
            super().__init__(tiles_group, walls_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


player = None

all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    all_sprites.empty()
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
    return new_player, x, y


def find_player(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                return y, x


class Camera:
    def __init__(self, level_num):
        if level_num == 1:
            self.dx = -320
            self.dy = -320
        else:
            pass
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, x, y):
        self.dx -= x
        self.dy -= y

    def return_d(self):
        return self.dx, self.dy


if __name__ == '__main__':
    start_screen()
    screen.fill('black')
    pygame.display.set_caption('Game')
    level_num = choice(range(1, 6))
    level_size = choice(['small', 'large'])
    level = load_level(f'{level_size}/level{level_num}.txt')

    camera = Camera(level_num)
    player, level_x, level_y = generate_level(level)
    all_sprites.draw(screen)
    pygame.display.flip()

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

    to_move_up, to_move_down, to_move_right, to_move_left = False, False, False, False
    running = True
    step = 5
    while running:
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
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
        for sprite in tiles_group:
            camera.apply(sprite)
        all_sprites.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
