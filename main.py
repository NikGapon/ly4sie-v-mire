import pygame
import requests
import sys
import os

import random
import math

from common.distance import lonlat_distance
from common.geocoder import geocode as reverse_geocode
from common.business import find_business

# Подобранные констатны для поведения карты.
LAT_STEP = 0.008  # Шаги при движении карты по широте и долготе
LON_STEP = 0.02
coord_to_geo_x = 0.0000428  # Пропорции пиксельных и географических координат.
coord_to_geo_y = 0.0000428


all_sprites = pygame.sprite.Group()



def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image: ', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image



def ll(x, y):
    return "{0},{1}".format(x, y)


def ck(x, y, ad):
    if x == 0 and y == 0:
        find_business()
    reverse_geocode(ad)
    lonlat_distance(x, y)
# Параметры отображения карты:
# координаты, масштаб, найденные объекты и т.д.


class MapParams(object):
    # Параметры по умолчанию.
    def __init__(self):
        self.lat = 55.729738  # Координаты центра карты на старте.
        self.lon = 37.664777
        self.zoom = 15  # Масштаб карты на старте.
        self.type = "map"  # Тип карты на старте.
        self.r_lat, self.r_lon = random.randint(-90.000, 90.000), random.randint(-180.000, 180.000)
        # self.r_lat, self.r_lon = self.lat, self.lon
        print(self.r_lat, self.r_lon)
        self.search_result = None  # Найденный объект для отображения на карте.
        self.use_postal_code = False

    # Преобразование координат в параметр ll
    def ll(self):
        return ll(self.lon, self.lat)

    def rylat(self):
        return self.r_lat, self.r_lon

    def proverka(self):
        if int(self.lon) == self.r_lon and int(self.lat) == self.r_lat:
            print(self.lat)
            print(self.r_lat)
            return True

    # Обновление параметров карты по нажатой клавише.
    def update(self, event):
        if event.key == pygame.K_LEFT:
            if LON_STEP * 2**(15 - self.zoom) <= 180 and LON_STEP * 2**(15 - self.zoom) >= -180:
                self.lon -= LON_STEP * 2**(15 - self.zoom)
        if event.key == pygame.K_RIGHT:
            if LON_STEP * 2 ** (15 - self.zoom) <= 180 and LON_STEP * 2 ** (15 - self.zoom) >= -180:
                self.lon += LON_STEP * 2**(15 - self.zoom)
        if event.key == pygame.K_UP:
            if LAT_STEP * 2**(15 - self.zoom) <= 90 and LAT_STEP * 2**(15 - self.zoom) >= -90:
                self.lat += LAT_STEP * 2**(15 - self.zoom)
        if event.key == pygame.K_DOWN:
            if LAT_STEP * 2 ** (15 - self.zoom) <= 90 and LAT_STEP * 2 ** (15 - self.zoom) >= -90:
                self.lat -= LAT_STEP * 2**(15 - self.zoom)

    # Преобразование экранных координат в географические.
    def screen_to_geo(self, pos):
        dy = 225 - pos[1]
        dx = pos[0] - 300
        lx = self.lon + dx * coord_to_geo_x * math.pow(2, 15 - self.zoom)
        ly = self.lat + dy * coord_to_geo_y * math.cos(math.radians(self.lat)) * math.pow(2, 15 - self.zoom)
        return lx, ly

    def retyrn_kord(self):
        return self.lat, self.lon
    # еще несколько функций


# Создание карты с соответствующими параметрами.
def load_map(mp):
    response = None
    try:
        map_request = "http://static-maps.yandex.ru/1.x/?ll={}&z={}&l={}".format(mp.ll(), mp.zoom, mp.type)
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            #sys.exit(1)

    except:
        print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
        #sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    return map_file



def main():
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))


    # Заводим объект, в котором будем хранить все параметры отрисовки карты.
    mp = MapParams()

    win = pygame.sprite.Sprite()
    win.image = load_image("win.png")
    win.rect = win.image.get_rect()
    all_sprites.add(win)
    win.rect.x = 4000
    win.rect.y = -4000

    # blue


    pd_cs = pygame.sprite.Sprite()
    pd_cs.image = load_image("p.d c.s.png")
    pd_cs.rect = pd_cs.image.get_rect()
    all_sprites.add(pd_cs)
    pd_cs.rect.x = 284
    pd_cs.rect.y = 410

    pl_cs = pygame.sprite.Sprite()
    pl_cs.image = load_image("p.l c.s.png")
    pl_cs.rect = pl_cs.image.get_rect()
    all_sprites.add(pl_cs)
    pl_cs.rect.x = 0
    pl_cs.rect.y = 209

    pr_cs = pygame.sprite.Sprite()
    pr_cs.image = load_image("p.r c.s.png")
    pr_cs.rect = pd_cs.image.get_rect()
    all_sprites.add(pr_cs)
    pr_cs.rect.x = 560
    pr_cs.rect.y = 209

    pu_cs = pygame.sprite.Sprite()
    pu_cs.image = load_image("p.u c.s.png")
    pu_cs.rect = pu_cs.image.get_rect()
    all_sprites.add(pu_cs)
    pu_cs.rect.x = 284
    pu_cs.rect.y = 0



    # red


    pd_ck = pygame.sprite.Sprite()
    pd_ck.image = load_image("p.d c.k.png")
    pd_ck.rect = pd_ck.image.get_rect()
    all_sprites.add(pd_ck)
    pd_ck.rect.x = 4000
    pd_ck.rect.y = -4000

    pl_ck = pygame.sprite.Sprite()
    pl_ck.image = load_image("p.l c.k.png")
    pl_ck.rect = pl_ck.image.get_rect()
    all_sprites.add(pl_ck)
    pl_ck.rect.x = 4000
    pl_ck.rect.y = -4000

    pr_ck = pygame.sprite.Sprite()
    pr_ck.image = load_image("p.r c.k.png")
    pr_ck.rect = pd_ck.image.get_rect()
    all_sprites.add(pr_ck)
    pr_ck.rect.x = 4000
    pr_ck.rect.y = -4000

    pu_ck = pygame.sprite.Sprite()
    pu_ck.image = load_image("p.u c.k.png")
    pu_ck.rect = pu_ck.image.get_rect()
    all_sprites.add(pu_ck)
    pu_ck.rect.x = 4000
    pu_ck.rect.y = -4000

    proverks_ret = 30
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:  # Выход из программы
            break
        elif event.type == pygame.KEYUP:  # Обрабатываем различные нажатые клавиши.
            mp.update(event)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                mp.type = 'sat,skl'
            elif event.key == pygame.K_F6:
                mp.type = 'sat'
            elif event.key == pygame.K_F7:
                mp.type = 'map'

            if event.key == pygame.K_PAGEUP and mp.zoom < 19 and mp.zoom > 0:
                mp.zoom += 1

            elif event.key == pygame.K_PAGEDOWN and mp.zoom < 19 and mp.zoom > 0:
                mp.zoom -= 1

            elif event.key == pygame.K_SPACE:
                print(mp.rylat())
                print(mp.retyrn_kord())

                # print(mp.zoom)
                if mp.zoom >= 14:
                    if proverks_ret > 0:
                        if mp.retyrn_kord()[0] > mp.rylat()[0]:
                            pd_ck.rect.x = 284
                            pd_ck.rect.y = 410
                        else:
                            pd_ck.rect.x = 4000
                            pd_ck.rect.y = -4000

                        if mp.retyrn_kord()[0] < mp.rylat()[0]:
                            pu_ck.rect.x = 284
                            pu_ck.rect.y = 0
                        else:
                            pu_ck.rect.x = 4000
                            pu_ck.rect.y = -4000



                        if mp.retyrn_kord()[1] < mp.rylat()[0]:
                            pl_ck.rect.x = 0
                            pl_ck.rect.y = 209
                        else:
                            pl_ck.rect.x = 4000
                            pl_ck.rect.y = -4000

                        if mp.retyrn_kord()[1] > mp.rylat()[0]:
                            pr_ck.rect.x = 560
                            pr_ck.rect.y = 209
                        else:
                            pr_ck.rect.x = 4000
                            pr_ck.rect.y = -4000
                    proverks_ret -= 1
            # другие eventы


        # Загружаем карту, используя текущие параметры.

        if mp.zoom <= 14:
        #    if mp.retyrn_kord()[0] > mp.rylat()[0]:
        #       pd_ck.rect.x = 284
        #        pd_ck.rect.y = 410
        #    else:
        #        pd_ck.rect.x = 4000
        #        pd_ck.rect.y = -4000
        #
        #    if mp.retyrn_kord()[0] < mp.rylat()[0]:
        #        pu_ck.rect.x = 284
        #        pu_ck.rect.y = 0
        #    else:
        #        pu_ck.rect.x = 4000
        #        pu_ck.rect.y = -4000
        #
        #    if mp.retyrn_kord()[1] < mp.rylat()[0]:
        #        pl_ck.rect.x = 0
        #        pl_ck.rect.y = 209
        #    else:
        #        pl_ck.rect.x = 4000
        #        pl_ck.rect.y = -4000
        #
        #    if mp.retyrn_kord()[1] > mp.rylat()[0]:
        #        pr_ck.rect.x = 560
        #       pr_ck.rect.y = 209
        #    else:
        #        pr_ck.rect.x = 4000
        #        pr_ck.rect.y = -4000

        #else:

            pd_ck.rect.x = 4000
            pd_ck.rect.y = -4000


            pl_ck.rect.x = 4000
            pl_ck.rect.y = -4000


            pr_ck.rect.x = 4000
            pr_ck.rect.y = -4000


            pu_ck.rect.x = 4000
            pu_ck.rect.y = -4000

        map_file = load_map(mp)

        #print(mp.retyrn_kord())
        # Рисуем картинку, загружаемую из только что созданного файла.
        screen.blit(pygame.image.load(map_file), (0, 0))
        all_sprites.draw(screen)
        # Переключаем экран и ждем закрытия окна.
        pygame.display.flip()
        if mp.proverka():
            win.rect.x = 150
            win.rect.y = 100
            print('Победа после обеда')

            all_sprites.draw(screen)
            pygame.display.flip()
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:  # Выход из программы
                    break
            break
    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)


if __name__ == "__main__":
    main()
