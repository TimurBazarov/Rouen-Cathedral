import time
from random import randint
import pygame
import sys
import os
from random import choice
from pygame import K_s, K_w, K_a, K_d
from copy import deepcopy
import csv


FPS = 50
pygame.init()
size = WIDTH, HEIGHT = 550, 550
font = pygame.font.Font(None, 30)
font_stats = pygame.font.Font(None, 20)
font_dead = pygame.font.Font(None, 28)
screen = pygame.display.set_mode(size)

player = None

all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
artefacts_group = pygame.sprite.Group()
with open('enemys.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    enem_stat = [i for i in list(reader)[1:]]
with open('renemys.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    renem_stat = [i for i in list(reader)[1:]]


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

    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
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
    player_group.empty()
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
    'empty': load_image('Tile_12.png'),
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
player_image = load_image('mario.png')
artefacts_images = {
    '1': load_image('artefact1.png')
}
void_images = dict()
count = 1
for i in range(1, 11):
    for i1 in range(1, 11):
        void_images[count] = load_image(f'void{i}{i1}.png')
        count += 1

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'void':
            super().__init__(tiles_group, walls_group, all_sprites)
            num = randint(1, 100)
            self.image = void_images[num]
        else:
            super().__init__(tiles_group, all_sprites)
            self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        #  от углеводов (ch) зависит сколько выстрелов может сделать игрок
        #  Жиры () - ресурс. при неполном здоровье можно восстановить хп, буквально съев свой жир
        #  ЖУ (Жиры Углеводы) можно получить за подбираемые предметы или за убийство врагов
        self.health = 100
        self.fats = 20
        self.ch = 100  # carbohydrates
        # Статы
        self.speed = 5
        self.luck = 0  # Можно повысить или понизить артефактами
        self.gun = None

    def will_collide(self, walls_group, action):
        if action is None:
            return
        if action == 'up':
            self.rect.y -= step
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect.y += step
                return True
            self.rect.y += step
            return False
        elif action == 'down':
            self.rect.y += step
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect.y -= step
                return True
            self.rect.y -= step
            return False
        elif action == 'right':
            self.rect.x += step
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect.x -= step
                return True
            self.rect.x -= step
            return False
        elif action == 'left':
            self.rect.x -= step
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect.x += step
                return True
            self.rect.x += step
            return False

    def show_stats(self):
        text = [f'Здоровье: {self.health}',
                f'Жиры: {self.fats}',
                f'Углеводы: {self.ch}',
                f'Удача: {self.luck}',
                f'Оружие: {self.gun}']
        text_coord = 350
        for line in text:
            string_rendered = font_stats.render(line, True, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

    def is_dead(self):
        if self.health > 0:
            return False
        return True


class Artefact(pygame.sprite.Sprite):
    def __init__(self, artefact_type, pos_x, pos_y):
        super().__init__(artefacts_group, all_sprites)
        self.image = artefacts_images[artefact_type]
        self.rect = self.image.get_rect().move(pos_x * tile_width + 15, pos_y * tile_height + 15)


def choose_random_empty_coords(level):
    empty = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                empty.append((y, x))
    y, x = choice(empty)
    level[y][x] = '1'

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, pix, v, hp, dmg):
        if level[pos_y][pos_x] != '#':
            if level_path[pos_y][pos_x][0] != 'E' and level[pos_y][pos_x] != '@':
                self.end_walk = False
                self.hp = hp
                self.t = 0
                self.dmg = dmg
                self.pix = pix
                self.pos_x = pos_x
                self.v = v
                self.clock = pygame.time.Clock()
                self.forw = '0'
                self.k = 0
                self.pos_y = pos_y
                self.timer = time.time()
                self.last_x = pos_x
                self.last_y = pos_y
                super().__init__(enemy_group, all_sprites, tiles_group)
                self.image = load_image(pix)
                self.rect = self.image.get_rect().move(
                    tile_width * self.pos_x, tile_height * self.pos_y)
                level_path[self.pos_y][self.pos_x] = 'E' + pix

    def path_find(self, finPoint1, finPoint2):
        a = find_player(level)
        finPoint = (finPoint1, finPoint2)
        stPoint = (self.pos_y, self.pos_x)
        self.pathArr = [[-1 if x == '#' or x[0] == 'E' else 0 for x in y] for y in level]
        self.pathArr[stPoint[0]][stPoint[1]] = 1
        self.pathArr[finPoint[0]][finPoint[1]] = 0
        if level_path[finPoint[0]][finPoint[1]][0] == 'E':
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

    def start(self, forw, k):
        self.clock = pygame.time.Clock()
        self.forw = forw
        self.k = k
        self.t = 0

    def walk(self):
        a = self.clock.tick()
        self.t += self.k * a * self.v / 1000
        if self.forw == 'x':
            self.rect.x = self.t + tile_width * self.last_x + camera.dx
        if self.forw == 'y':
            self.rect.y = self.t + tile_height * self.last_y + camera.dy

    def udt(self):
        level_path[enemy.last_y][enemy.last_x] = '.'
        level_path[self.pos_y][self.pos_x] = 'E' + self.pix
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x + camera.dx, tile_height * self.pos_y + camera.dy)

    def last(self, x, y):
        self.last_x = x
        self.last_y = y

class Range_enemy(Enemy):
    def __init__(self, pos_x, pos_y, pix, v, hp, dmg, range, b_speed, b_pix):
        if level[pos_y][pos_x] != '#':
            if level_path[pos_y][pos_x][0] != 'E' and level[pos_y][pos_x] != '@':
                super().__init__(pos_x, pos_y, pix, v, hp, dmg)
                self.end_walk = False
                self.b_speed = b_speed
                self.b_pix = b_pix
                self.pix = pix
                self.hp = hp
                self.dmg = dmg
                self.range = range
                self.pos_x = pos_x
                self.clock = pygame.time.Clock()
                self.forw = '0'
                self.k = 0
                self.t = 0
                self.v = v
                self.pos_y = pos_y
                self.timer = time.time()
                self.last_x = pos_x
                self.last_y = pos_y
                self.image = load_image(pix)
                self.rect = self.image.get_rect().move(
                    tile_width * self.pos_x, tile_height * self.pos_y)
                level_path[self.pos_y][self.pos_x] = 'E' + pix



def generate_level(level, player=None):
    all_sprites.empty()
    walls_group.empty()
    tiles_group.empty()
    # enemy_group.empty()
    artefacts_group.empty()
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('void', x, y)
            elif level[y][x] == '1':
                Tile('empty', x, y)
                Artefact('1', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                if player is not None:
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
            # if level_path[y][x][0] == 'E':
            #     a = level_path[y][x]
            #     Enemy(x, y, a[1:])
    return new_player, x, y


def find_player(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                return y * 50 + 5, x * 50 + 15


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
        obj.rect.x -= dx
        obj.rect.y -= dy

    def update(self, x, y):
        self.dx -= x
        self.dy -= y

    def return_d(self):
        return self.dx, self.dy


if __name__ == '__main__':
    start_screen()
    screen.fill('black')
    pygame.display.set_caption('Game')
    #  Блок, отвечающий за rogue-like смену комнаты
    #  ----------
    level_num = choice(range(1, 6))
    level_size = choice(['small', 'large'])
    level = load_level(f'{level_size}/level{level_num}.txt')
    level_path = deepcopy(level)
    camera = Camera(level_num)
    choose_random_empty_coords(level)
    player, level_x, level_y = generate_level(level, player=1)
    pl_y, pl_x = find_player(level)
    all_sprites.draw(screen)
    comand_list = []
    #  ----------
    pygame.display.flip()
    all_en = randint(5, 8)
    m_en = randint(4, all_en - 1)
    while len(enemy_group) != m_en:
        enem_sta = enem_stat[randint(0, len(enem_stat) - 1)]
        Enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), enem_sta[0], int(enem_sta[1]),
              int(enem_sta[2]), int(enem_sta[3]))
    while len(enemy_group) != all_en:
        enem_sta = renem_stat[randint(0, len(enem_stat) - 1)]
        Range_enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), enem_sta[0], int(enem_sta[1]),
              int(enem_sta[2]), int(enem_sta[3]), int(enem_sta[4]), int(enem_sta[5]), enem_sta[6])
    MYEVENTTYPE = pygame.USEREVENT + 1
    PATHEVENTTYPE = pygame.USEREVENT + 2
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, MYEVENTTYPE])
    to_move_up, to_move_down, to_move_right, to_move_left = False, False, False, False
    running = True
    step = 5
    moves_dict = {K_s: to_move_down, K_w: to_move_up, K_d: to_move_right, K_a: to_move_left}
    to_move_flag = False
    see = False
    ssav = False
    level_cleared = True

    pygame.time.set_timer(MYEVENTTYPE, 1000 // FPS)  # FPS
    pygame.time.set_timer(PATHEVENTTYPE, 1000)

    artifact_inventory = []  # ИНВЕНТАРЬ АРТЕФАКТОВ ОЧЕНЬ ВАЖНО!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for enemy in enemy_group:
        crdy = int(pl_y / 50)
        crdx = int(pl_x / 50)
        ch = enemy.path_find(crdy, crdx)
        if ch:
            enemy.udt()
        for i in level_path:
            print(i)
        enemy.last(enemy.pos_x, enemy.pos_y)
        if ch:
            while True:
                enemy.timer = time.time()
                enemy.pos_x = enemy.last_x
                enemy.pos_y = enemy.last_y
                comande = enemy.printPath(ch, crdx, crdy)
                comands = comande[randint(0, len(comande) - 1)]
                enemy.end_walk = False
                if comands == 'left':
                    enemy.pos_x -= 1
                    enemy.start('x', -1)
                if comands == 'right':
                    enemy.pos_x += 1
                    enemy.start('x', 1)
                if comands == 'down':
                    enemy.pos_y += 1
                    enemy.start('y', 1)
                if comands == 'up':
                    enemy.pos_y -= 1
                    enemy.start('y', -1)
                if level[enemy.pos_y][enemy.pos_x] != '#':
                    break
        else:
            enemy.start('0', 0)
            enemy.end_walk = True
    while running:
        if len(enemy_group) == 0:  # Если уровень зачищен
            level_cleared = True
        action = None
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                '''Движение происходит, если плитка, в которую хочет перейти персонаж, не является стеной, и если
                    персонаж не выходит за рамки уровня.'''
                moves_dict[event.key] = True
                if event.key == pygame.K_e and level_cleared:
                    level_num = choice(range(1, 6))
                    level_size = choice(['small', 'large'])
                    level = load_level(f'{level_size}/level{level_num}.txt')
                    level_path = deepcopy(level)
                    camera = Camera(level_num)
                    player, level_x, level_y = generate_level(level, player=1)
                    enemy_group.empty()
                    all_en = randint(5, 8)
                    m_en = randint(4, all_en - 1)
                    while len(enemy_group) != m_en:
                        enem_sta = enem_stat[randint(0, len(enem_stat) - 1)]
                        Enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), enem_sta[0], int(enem_sta[1]),
                              int(enem_sta[2]), int(enem_sta[3]))
                    while len(enemy_group) != all_en:
                        enem_sta = renem_stat[randint(0, len(enem_stat) - 1)]
                        Range_enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), enem_sta[0],
                                    int(enem_sta[1]),
                                    int(enem_sta[2]), int(enem_sta[3]), int(enem_sta[4]), int(enem_sta[5]), enem_sta[6])
                    continue
            if event.type == pygame.KEYUP:
                moves_dict[event.key] = False
            if event.type == MYEVENTTYPE:
                to_move_flag = True
            if event.type == PATHEVENTTYPE:
                see = True
        if not to_move_flag:
            continue
        if moves_dict[K_s]:
            action = 'down'
            dy += step
        elif moves_dict[K_w]:
            action = 'up'
            dy -= step
        elif moves_dict[K_d]:
            action = 'right'
            dx += step
        elif moves_dict[K_a]:
            action = 'left'
            dx -= step
        if not player.will_collide(walls_group, action):
            screen.fill('black')
            camera.update(dx, dy)
            ds = camera.return_d()
            for sprite in tiles_group:
                camera.apply(sprite)
            for sprite in artefacts_group:
                camera.apply(sprite)
            for obj in enemy_group:
                obj.rect.x = tile_width * obj.last_x + camera.dx
                obj.rect.y = tile_height * obj.last_y + camera.dy
            pl_x += dx
            pl_y += dy
            for enemy in enemy_group:
                if abs(enemy.t) >= 48:
                    crdy = int(pl_y / 50)
                    crdx = int(pl_x / 50)
                    ch = enemy.path_find(crdy, crdx)
                    if ch:
                        enemy.udt()
                    for i in level_path:
                        print(i)
                    enemy.last(enemy.pos_x, enemy.pos_y)
                    if ch:
                        while True:
                            enemy.timer = time.time()
                            enemy.pos_x = enemy.last_x
                            enemy.pos_y = enemy.last_y
                            comande = enemy.printPath(ch, crdx, crdy)
                            comands = comande[randint(0, len(comande) - 1)]
                            enemy.end_walk = False
                            if comands == 'left':
                                enemy.pos_x -= 1
                                enemy.start('x', -1)
                            if comands == 'right':
                                enemy.pos_x += 1
                                enemy.start('x', 1)
                            if comands == 'down':
                                enemy.pos_y += 1
                                enemy.start('y', 1)
                            if comands == 'up':
                                enemy.pos_y -= 1
                                enemy.start('y', -1)
                            if level[enemy.pos_y][enemy.pos_x] != '#':
                                break
                    else:
                        enemy.start('0', 0)
                        enemy.end_walk = True
                else:
                    if time.time() - enemy.timer >= 50 / enemy.v:
                        crdy = int(pl_y / 50)
                        crdx = int(pl_x / 50)
                        ch = enemy.path_find(crdy, crdx)
                        if ch:
                            enemy.udt()
                        for i in level_path:
                            print(i)
                        enemy.last(enemy.pos_x, enemy.pos_y)
                        if ch:
                            while True:
                                enemy.timer = time.time()
                                enemy.pos_x = enemy.last_x
                                enemy.pos_y = enemy.last_y
                                comande = enemy.printPath(ch, crdx, crdy)
                                comands = comande[randint(0, len(comande) - 1)]
                                enemy.end_walk = False
                                if comands == 'left':
                                    enemy.pos_x -= 1
                                    enemy.start('x', -1)
                                if comands == 'right':
                                    enemy.pos_x += 1
                                    enemy.start('x', 1)
                                if comands == 'down':
                                    enemy.pos_y += 1
                                    enemy.start('y', 1)
                                if comands == 'up':
                                    enemy.pos_y -= 1
                                    enemy.start('y', -1)
                                if level[enemy.pos_y][enemy.pos_x] != '#':
                                    break
                        else:
                            enemy.start('0', 0)
                            enemy.end_walk = True
            see = False
            to_move_flag = False
            for ens in enemy_group:
                if ens.end_walk:
                    level_path = deepcopy(level)
                    ens.start('0', 0)
                    ens.pos_x = ens.last_x
                    ens.pos_t = ens.last_y
                    level_path[ens.pos_y][ens.pos_x] = 'E' + ens.pix
                    ens.rect = ens.image.get_rect().move(
                        tile_width * ens.pos_x + camera.dx, tile_height * ens.pos_y + camera.dy)
            for z in enemy_group:
                z.walk()
        all_sprites.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)

        if player.is_dead():
            player_group.empty()
            string_rendered = font_dead.render('Вы мертвы! Чтобы начать новую игру, перезапуститесь',
                                                True, pygame.Color('white'))
            rect = string_rendered.get_rect()
            screen.blit(string_rendered, rect)
            artifact_inventory = []
        player.show_stats()

        pygame.display.flip()