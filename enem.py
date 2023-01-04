from random import randint
import pygame
import sys
import os
from random import choice
from pygame import K_s, K_w, K_a, K_d

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


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, pix):
        if level[pos_y][pos_x] == '.' or level[pos_y][pos_x] == 'E' + pix:
            self.pos_x = pos_x
            self.pos_y = pos_y
            super().__init__(enemy_group, all_sprites, tiles_group)
            self.image = load_image(pix)
            self.rect = self.image.get_rect().move(
                tile_width * self.pos_x, tile_height * self.pos_y)
            level[self.pos_y][self.pos_x] = 'E' + pix

    def path_find(self, finPoint1, finPoint2):
        a = find_player(level)
        finPoint = (finPoint1, finPoint2)
        stPoint = (self.pos_y, self.pos_x)
        self.pathArr = [[0 if x == '.' else -1 for x in y] for y in level_path]
        self.pathArr[stPoint[0]][stPoint[1]] = 1
        self.pathArr[finPoint[0]][finPoint[1]] = 0
        if level[finPoint[0]][finPoint[1]][0] == 'E':
            return False
        weight = 1
        for i in range(400):
            weight += 1
            for y in range(len(level)):
                for x in range(len(level)):
                    if self.pathArr[y][x] == (weight - 1):
                        if y >= 0 and self.pathArr[y - 1][x] == 0:
                            self.pathArr[y - 1][x] = weight
                        if y < len(level) and self.pathArr[y + 1][x] == 0:
                            self.pathArr[y + 1][x] = weight
                        if x >= 0 and self.pathArr[y][x - 1] == 0:
                            self.pathArr[y][x - 1] = weight
                        if x < len(level) and self.pathArr[y][x + 1] == 0:
                            self.pathArr[y][x + 1] = weight
                        if (abs(y - finPoint[0]) + abs(x - finPoint[1])) == 1:
                            self.pathArr[finPoint[0]][finPoint[1]] = weight
                            return self.pathArr
        return False


    def printPath(self, pathArr, finPoint1, finPoint2):
        y = finPoint2
        x = finPoint1
        weight = pathArr[y][x]
        result = list(range(weight))
        while weight:
            weight -= 1
            if y > 0 and pathArr[y - 1][x] == weight:
                y -= 1
                result[weight] = 'down'
            elif y < (len(pathArr) - 1) and pathArr[y + 1][x] == weight:
                result[weight] = 'up'
                y += 1
            elif x > 0 and pathArr[y][x - 1] == weight:
                result[weight] = 'right'
                x -= 1
            elif x < (len(pathArr[y]) - 1) and pathArr[y][x + 1] == weight:
                result[weight] = 'left'
                x += 1
        return result[1:]


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
enemy_group = pygame.sprite.Group()


def generate_level(level):
    all_sprites.empty()
    walls_group.empty()
    tiles_group.empty()
    enemy_group.empty()
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
            elif level[y][x][0] == 'E':
                a = level[y][x][1:]
                Tile('empty', x, y)
                Enemy(x, y, a)
    return new_player, x, y


def find_player(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                return y * 50, x * 50


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
    level = load_level(f'small/level3.txt')
    level_path = level.copy()
    pl_y, pl_x = find_player(level)

    camera = Camera(level_num)
    player, level_x, level_y = generate_level(level)
    all_sprites.draw(screen)
    pygame.display.flip()
    while len(enemy_group) != 2:
        Enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), 'enemy.png')
    while len(enemy_group) != 4:
        Enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), 'enemy2.png')
    MYEVENTTYPE = pygame.USEREVENT + 1
    PATHEVENTTYPE = pygame.USEREVENT + 2
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, MYEVENTTYPE, PATHEVENTTYPE])

    to_move_up, to_move_down, to_move_right, to_move_left = False, False, False, False
    running = True
    step = 10
    moves_up_dict = {K_s: to_move_down, K_w: to_move_up, K_d: to_move_right, K_a: to_move_left}
    to_move_flag = False
    see = False

    pygame.time.set_timer(MYEVENTTYPE, 1000 // FPS)
    pygame.time.set_timer(PATHEVENTTYPE, 1000)
    while running:
        dy, dx = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                '''Движение происходит, если плитка, в которую хочет перейти персонаж, не является стеной, и если
                    персонаж не выходит за рамки уровня.'''
                moves_up_dict[event.key] = True
            if event.type == pygame.KEYUP:
                moves_up_dict[event.key] = False
            if event.type == MYEVENTTYPE:
                to_move_flag = True
            if event.type == PATHEVENTTYPE:
                see = True
        if moves_up_dict[K_s]:
            dy += step
        elif moves_up_dict[K_w]:
            dy -= step
        elif moves_up_dict[K_d]:
            dx += step
        elif moves_up_dict[K_a]:
            dx -= step
        if to_move_flag:
            screen.fill('black')
            moved_player, moved_x, moved_y = generate_level(level)
            camera.update(dx, dy)
            ds = camera.return_d()
            for sprite in tiles_group:
                camera.apply(sprite)
            pl_x += dx
            pl_y += dy
            if see:
                for enemy in enemy_group:
                    crdy = pl_y // 50
                    crdx = pl_x // 50
                    ch = enemy.path_find(crdy, crdx)
                    if ch:
                        comands = enemy.printPath(ch, crdx, crdy)[0]
                        sav = level[enemy.pos_y][enemy.pos_x]
                        level[enemy.pos_y][enemy.pos_x] = '.'
                        if comands == 'left':
                            enemy.pos_x -= 1
                        if comands == 'right':
                            enemy.pos_x += 1
                        if comands == 'down':
                            enemy.pos_y += 1
                        if comands == 'up':
                            enemy.pos_y -= 1
                        level[enemy.pos_y][enemy.pos_x] = sav

            see = False
            all_sprites.draw(screen)
            player_group.draw(screen)
            to_move_flag = False
        pygame.display.flip()
