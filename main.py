import pygame
import sys
import os
import math
if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Перетаскивание')
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    pygame.mouse.set_visible(False)
    x2 = -100
    y2 = -100
    wea_list = []
    k = 0


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


    class Weapon:
        def __init__(self, name, pix, pix_bul, max_range, fire_rate, v):
            self.name = name
            self.pix_bul = pix_bul
            self.max_range = max_range
            self.fire_rate = fire_rate
            self.pix = pix
            self.v = v

        def show(self):
            ima = load_image(self.pix)
            screen.blit(ima, (0, 550))

        def piu(self):
            xx = abs(x1 - x2)
            yy = abs(y1 - y2)
            self.a = math.atan(yy / xx)
            self.angle = (180 * self.a) / math.pi
            self.vx = math.cos(self.a) * self.v * (x2 - x1) / abs(x1 - x2)
            self.vy = math.sin(self.a) * self.v * (y2 - y1) / abs(y1 - y2)
            return Bullet(self.max_range, self.vx, self.vy, self.pix_bul, self.angle, x1, y1)


    class Bullet:
        def __init__(self, max, vx, vy, pix, angle, x0, y0):
            self.clock = pygame.time.Clock()
            self.max = max
            self.x0 = x0
            self.y0 = y0
            self.xd = x0
            self.yd = y0
            self.vx = vx
            self.vy = vy
            if x2 > x1 and y2 > y1:
                self.ima = pygame.transform.rotate(load_image(pix), -angle - 90)
            if x2 > x1 and y2 < y1:
                self.ima = pygame.transform.rotate(load_image(pix), angle - 90)
            if x2 < x1 and y2 > y1:
                self.ima = pygame.transform.rotate(load_image(pix), angle + 90)
            if x2 < x1 and y2 < y1:
                self.ima = pygame.transform.rotate(load_image(pix), -angle + 90)

        def fly(self):
            t = self.clock.tick() / 1000
            self.xd += self.vx * t
            self.yd += self.vy * t
            screen.blit(self.ima, (self.xd, self.yd))
            ddx = abs(self.xd - self.x0)
            ddy = abs(self.yd - self.y0)
            if ddx ** 2 + ddy ** 2 >= self.max ** 2:
                self.vy = 0
                self.vx = 0
                self.xd = -10000
                self.yd = -10000
                return True



    game = True
    image1 = load_image("creature.png", colorkey=-1)
    x1 = (800 - 83) / 2
    y1 = (600 - 101) / 2
    image = load_image("cur.png")
    pist = Weapon('pistol', 'gun.jpg', 'piu.png', 900, 1, 500)
    wea_list.append(pist)
    push = False
    reload = True
    bull_list = []
    while game:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    push = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    push = False
            if event.type == pygame.QUIT:
                game = False
            if event.type == pygame.MOUSEMOTION:
                x2, y2 = event.pos
            if keys[pygame.K_LEFT]:
                x1 -= 10
            if keys[pygame.K_RIGHT]:
                x1 += 10
            if keys[pygame.K_DOWN]:
                y1 += 10
            if keys[pygame.K_UP]:
                y1 -= 10
        screen.fill((255, 255, 255))
        wea_list[k].show()
        screen.blit(image1, (x1, y1))
        if push and reload:
            bull_list.append(wea_list[k].piu())
            reload = False
            clock = pygame.time.Clock()
            t = 0
        if not reload:
            t += clock.tick() / 1000
            if t >= wea_list[k].fire_rate:
                reload = True
        if bull_list:
            for i in bull_list:
                if i.fly():
                    del i
        if x2 > 0 and x2 < 800:
            if y2 > 0 and y2 < 600:
                screen.blit(image, (x2 - 25, y2 - 25))
        pygame.display.flip()
    pygame.quit()
