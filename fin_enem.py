from random import randint
import pygame
import sys
import os
from random import choice
from pygame import K_s, K_w, K_a, K_d, K_SPACE, K_f
from copy import copy, deepcopy
from math import ceil

FPS = 50
pygame.init()
size = WIDTH, HEIGHT = 550, 550
font = pygame.font.Font(None, 30)
font_stats = pygame.font.Font(None, 20)
font_dead = pygame.font.Font(None, 28)
screen = pygame.display.set_mode(size)
full_artefacts_list = ['1', '電', '買', '車', '红', '無', '東', '馬', '風', '愛', '時', '鳥', '島', '語', '頭', '魚']

player = None

all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
artefacts_group = pygame.sprite.Group()


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
    'void': load_image('void.png'),
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
player_images = {1: load_image('cherkash1.png'),
                 2: load_image('cherkash1_right.png'),
                 3: load_image('cherkash1_left.png'),
                 4: load_image('cherkash1_up.png')}
artefacts_images = {
    '1': load_image('artefacts/apple.png'),
    '電': load_image('artefacts/floppa.png'),
    '買': load_image('artefacts/cucumber.png'),
    '車': load_image('artefacts/edwardshorizon.png'),
    '红': load_image('artefacts/kozinaks.png'),
    '無': load_image('artefacts/gluegun.png'),
    '東': load_image('artefacts/ibanez2550.png'),
    '馬': load_image('artefacts/krotovuha.png'),
    '風': load_image('artefacts/lays.png'),
    '愛': load_image('artefacts/metalzone.png'),
    '時': load_image('artefacts/oneboob.png'),
    '鳥': load_image('artefacts/onion.png'),
    '島': load_image('artefacts/eye.png'),
    '語': load_image('artefacts/mushroom.png'),
    '頭': load_image('artefacts/virus.png'),
    '魚': load_image('artefacts/heart.png')
}

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'void':
            super().__init__(tiles_group, walls_group, all_sprites)
            num = randint(1, 100)
            self.image = tile_images['void']
        else:
            super().__init__(tiles_group, all_sprites)
            self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_images[1]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        #  от углеводов (ch) зависит сколько выстрелов может сделать игрок
        #  Жиры () - ресурс. при неполном здоровье можно восстановить хп, буквально съев свой жир
        #  ЖУ (Жиры Углеводы) можно получить за подбираемые предметы или за убийство врагов
        self.max_health = 100
        self.health = 100
        self.fats = 20
        self.ch = 100  # carbohydrates
        # Статы
        self.speed = 5
        self.luck = 0  # Можно повысить или понизить артефактами
        self.step = 5
        self.gun = None

    def will_collide(self, walls_group, action):
        if action is None:
            return
        if action == 'up':
            self.rect.y -= step
            result = any(list(map(lambda sprite: pygame.sprite.collide_mask(self, sprite), walls_group)))
            if result:
                self.rect.y += step
                return True
            self.rect.y += step
            return False
        elif action == 'down':
            self.rect.y += step
            result = any(list(map(lambda sprite: pygame.sprite.collide_mask(self, sprite), walls_group)))
            if result:
                self.rect.y -= step
                return True
            self.rect.y -= step
            return False
        elif action == 'right':
            self.rect.x += step
            result = any(list(map(lambda sprite: pygame.sprite.collide_mask(self, sprite), walls_group)))
            if result:
                self.rect.x -= step
                return True
            self.rect.x -= step
            return False
        elif action == 'left':
            self.rect.x -= step
            result = any(list(map(lambda sprite: pygame.sprite.collide_mask(self, sprite), walls_group)))
            if result:
                self.rect.x += step
                return True
            self.rect.x += step
            return False

    def check_health_is_max(self):
        if self.health > self.max_health:
            self.ch += self.health - self.max_health
            self.health = self.max_health

    def increase_health(self, value):
        self.health += value
        self.check_health_is_max()

    def collides_with_artefact(self):
        return pygame.sprite.spritecollideany(self, artefacts_group)

    def show_stats(self):
        global additional_lifes
        text = [f'Здоровье: {self.health if self.health > 0 else 0}',
                f'Макс. здоровье: {self.max_health}',
                f'Жиры: {self.fats}',
                f'Углеводы: {self.ch}',
                f'Удача: {self.luck}',
                f'Скорость: {self.step}',
                f'Оружие: {self.gun}',
                f'Дополнительные жизни: {additional_lifes}']
        text_coord = 350
        for line in text:
            string_rendered = font_stats.render(line, True, pygame.Color('white'))
            rect = string_rendered.get_rect()
            text_coord += 10
            rect.top = text_coord
            rect.x = 10
            text_coord += rect.height
            screen.blit(string_rendered, rect)

    def is_dead(self):
        global additional_lifes
        if self.health > 0:
            return False
        if additional_lifes > 0:
            self.health = 100
            self.ch = self.ch // 2
            self.fats = self.fats // 2
            additional_lifes -= 1
            return False
        return True

    def eat_fats(self):
        value = min(self.max_health - self.health, self.fats)
        self.health += value
        self.fats -= value


class Artefact(pygame.sprite.Sprite):
    def __init__(self, artefact_type, pos_x, pos_y):
        super().__init__(artefacts_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = artefacts_images[artefact_type]
        self.rect = self.image.get_rect().move(pos_x * tile_width + 15, pos_y * tile_height + 15)

    def delete_artifact(self):
        level[self.pos_y][self.pos_x] = '.'

    def activate(self, player):
        pass


class Apple(Artefact):
    def activate(self, player):
        player.increase_health(-15)
        player.ch += 50


class Floppa(Artefact):
    def activate(self, player):
        global additional_lifes
        additional_lifes += 1


class Cucumber(Artefact):
    def activate(self, player):
        player.max_health += 10
        player.step += 1


class Edwards(Artefact):
    def activate(self, player):
        player.step = ceil(player.step * 0.8)


class Kozinaks(Artefact):
    def activate(self, player):
        player.step += 1
        player.ch += 200
        player.fats += 25


class Gluegun(Artefact):
    def activate(self, player):
        player.ch += 100
        player.fats += 50


class Ibanez(Artefact):
    def activate(self, player):
        player.ch += 150
        player.step += 2
        player.increase_health(10)


class Krotovuha(Artefact):
    def activate(self, player):
        player.fats += 40
        player.step = ceil(1.2 * player.step)


class Lays(Artefact):
    def activate(self, player):
        player.fats += 60


class MetalZone(Artefact):
    def activate(self, player):
        player.step += 2
        player.max_health += 50


class Oneboob(Artefact):
    def activate(self, player):
        player.ch += 200
        player.fats += 15
        player.luck += 1
        player.increase_health(-10)


class Onion(Artefact):
    def activate(self, player):
        player.step += 2
        player.max_health += 10


class Eye(Artefact):
    def activate(self, player):
        player.luck += 1
        player.increase_health(30)


class Mushroom(Artefact):
    def activate(self, player):
        global additional_lifes
        additional_lifes += 1
        player.ch += 50


class Virus(Artefact):
    def activate(self, player):
        player.step += round(0.2 * player.step)
        player.fats += 45


class Heart(Artefact):
    def activate(self, player):
        player.health = player.max_health


def choose_random_empty_coords(level):
    empty = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                empty.append((y, x))
    y, x = choice(empty)
    level[y][x] = choice(full_artefacts_list)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, pix):
        if level[pos_y][pos_x] != '#':
            if enem_gen:
                if level_path[pos_y][pos_x][0] != 'E' and level[pos_y][pos_x] != '@':
                    self.pix = pix
                    self.pos_x = pos_x
                    self.pos_y = pos_y
                    self.last_x = pos_x
                    self.last_y = pos_y
                    super().__init__(enemy_group, all_sprites, tiles_group)
                    self.image = load_image(pix)
                    self.rect = self.image.get_rect().move(
                        tile_width * self.pos_x, tile_height * self.pos_y)
                    level_path[self.pos_y][self.pos_x] = 'E' + pix
            else:
                self.pix = pix
                self.pos_x = pos_x
                self.pos_y = pos_y
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
        self.pathArr = [[-1 if x == '#' or x[0] == 'E' else 0 for x in y] for y in level_path]
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
        self.t += self.k * a * 50 / 1000
        if self.forw == 'x':
            self.rect.x = self.t + tile_width * self.last_x + camera.dx
        if self.forw == 'y':
            self.rect.y = self.t + tile_height * self.last_y + camera.dy

    def udt(self):
        level_path[self.pos_y][self.pos_x] = 'E' + self.pix
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x + camera.dx, tile_height * self.pos_y + camera.dy)

    def last(self, x, y):
        self.last_x = x
        self.last_y = y


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
                Apple('1', x, y)
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
            elif level[y][x] == '電':
                Tile('empty', x, y)
                Floppa('電', x, y)
            elif level[y][x] == '買':
                Tile('empty', x, y)
                Cucumber('買', x, y)
            elif level[y][x] == '車':
                Tile('empty', x, y)
                Edwards('車', x, y)
            elif level[y][x] == '红':
                Tile('empty', x, y)
                Kozinaks('红', x, y)
            elif level[y][x] == '無':
                Tile('empty', x, y)
                Gluegun('無', x, y)
            elif level[y][x] == '東':
                Tile('empty', x, y)
                Ibanez('東', x, y)
            elif level[y][x] == '馬':
                Tile('empty', x, y)
                Krotovuha('馬', x, y)
            elif level[y][x] == '風':
                Tile('empty', x, y)
                Lays('風', x, y)
            elif level[y][x] == '愛':
                Tile('empty', x, y)
                MetalZone('愛', x, y)
            elif level[y][x] == '時':
                Tile('empty', x, y)
                Oneboob('時', x, y)
            elif level[y][x] == '鳥':
                Tile('empty', x, y)
                Onion('鳥', x, y)
            elif level[y][x] == '島':
                Tile('empty', x, y)
                Eye('島', x, y)
            elif level[y][x] == '語':
                Tile('empty', x, y)
                Mushroom('語', x, y)
            elif level[y][x] == '頭':
                Tile('empty', x, y)
                Virus('頭', x, y)
            elif level[y][x] == '魚':
                Tile('empty', x, y)
                Heart('魚', x, y)

            # if level_path[y][x][0] == 'E':
            #     a = level_path[y][x]
            #     Enemy(x, y, a[1:])
    return new_player, x, y


def find_player(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                return y * 50 + 5, x * 50 + 15


def make_void():
    for _ in range(1000):
        screen.set_at((randint(0, 649), randint(0, 649)), 'white')


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
    #  Блок, отвечающий за rogue-like смену комнаты
    #  ----------
    level_num = choice(range(1, 6))
    level_size = choice(['small', 'large'])
    level = load_level(f'{level_size}/level{level_num}.txt')
    level_path = deepcopy(level)
    camera = Camera(level_num)
    for i in range(5):
        choose_random_empty_coords(level)
    player, level_x, level_y = generate_level(level, player=1)
    pl_y, pl_x = find_player(level)
    all_sprites.draw(screen)
    comand_list = []
    po = []
    #  ----------
    pygame.display.flip()
    enem_gen = True
    while len(enemy_group) != 3:
        Enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), 'enemy.png')
    # while len(enemy_group) != 2:
    #     Enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), 'enemy.png')
    # while len(enemy_group) != 4:
    #     Enemy(randint(1, len(level) - 1), randint(1, len(level) - 1), 'enemy2.png')
    enem_gen = False
    MYEVENTTYPE = pygame.USEREVENT + 1
    PATHEVENTTYPE = pygame.USEREVENT + 2
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, MYEVENTTYPE])
    to_move_up, to_move_down, to_move_right, to_move_left = False, False, False, False
    running = True
    additional_lifes = 0
    moves_dict = {K_s: to_move_down, K_w: to_move_up, K_d: to_move_right, K_a: to_move_left}
    to_move_flag = False
    see = False
    ssav = False
    level_cleared = False
    is_dead = False

    pygame.time.set_timer(MYEVENTTYPE, 1000 // FPS)  # FPS
    pygame.time.set_timer(PATHEVENTTYPE, 1000)

    artifact_inventory = []  # ИНВЕНТАРЬ АРТЕФАКТОВ ОЧЕНЬ ВАЖНО!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    while running:
        step = player.step
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
                    camera = Camera(level_num)
                    player, level_x, level_y = generate_level(level, player=1)
                    continue
                if event.key == K_SPACE:
                    received_artefact = player.collides_with_artefact()
                    if received_artefact:
                        received_artefact.activate(player)
                        artifact_inventory.append(received_artefact)
                        received_artefact.delete_artifact()
                if event.key == K_f:
                    player.eat_fats()
            if event.type == pygame.KEYUP:
                player.image = player_images[1]
                moves_dict[event.key] = False
            if event.type == MYEVENTTYPE:
                to_move_flag = True
            if event.type == PATHEVENTTYPE:
                see = True
        if to_move_flag:
            if moves_dict[K_s]:
                action = 'down'
                dy += step
            elif moves_dict[K_w]:
                player.image = player_images[4]
                action = 'up'
                dy -= step
            elif moves_dict[K_d]:
                player.image = player_images[2]
                action = 'right'
                dx += step
            elif moves_dict[K_a]:
                player.image = player_images[3]
                action = 'left'
                dx -= step
        if not player.will_collide(walls_group, action) and not is_dead:
            screen.fill('black')
            make_void()
            moved_player, moved_x, moved_y = generate_level(level)
            camera.update(dx, dy)
            ds = camera.return_d()
            for sprite in tiles_group:
                camera.apply(sprite)
            for sprite in artefacts_group:
                camera.apply(sprite)
            for obj in enemy_group:
                print(obj.last_x, obj.last_y)
                print(obj.pos_x, obj.pos_y)
                obj.rect.x = tile_width * obj.last_x + camera.dx
                obj.rect.y = tile_height * obj.last_y + camera.dy
            pl_x += dx
            pl_y += dy
            if see:
                tx = 0
                ty = 0
                for enemy in enemy_group:
                    enemy.udt()
                    crdy = int(pl_y / 50)
                    crdx = int(pl_x / 50)
                    for i in level_path:
                        print(i)
                    if po:
                        level_path[enemy.last_y][enemy.last_x] = '.'
                    ch = enemy.path_find(crdy, crdx)
                    enemy.last(enemy.pos_x, enemy.pos_y)
                    if ch:
                        comande = enemy.printPath(ch, crdx, crdy)
                        comands = comande[0]
                        po = True
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
                    else:
                        po = False
            see = False
            to_move_flag = False
            if po:
                for z in enemy_group:
                    z.walk()
        all_sprites.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)

        if player.is_dead():
            player_group.empty()
            camera = None
            string_rendered = font_dead.render('Вы мертвы! Чтобы начать новую игру, перезапуститесь',
                                               True, pygame.Color('white'))
            rect = string_rendered.get_rect()
            screen.blit(string_rendered, rect)
            artifact_inventory = []
            is_dead = True
        player.show_stats()
        pygame.display.flip()
