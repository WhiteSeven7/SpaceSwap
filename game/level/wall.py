'''不可穿过的障碍物'''
import csv
import random
from random import randint
import pygame
from pygame.sprite import Sprite, Group
from ..game_type import *
from ..setting import *


class Wall(Sprite):
    SIZE = 66

    @staticmethod
    def random_color() -> tuple[int, int, int]:
        color = [randint(0, 150), randint(50, 200), randint(100, 255)]
        random.shuffle(color)
        return tuple(color)

    def __init__(self, num: int, pos_g: PointT, center_pos: pygame.Vector2, *, groups: Group | Sequence = ()) -> None:
        super().__init__(groups)
        self.num = num
        self.x_g, self.y_g = pos_g
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = center_pos

        self.color = self.random_color()

    def draw(self, surf: pygame.Surface):
        if DEBUG['show_rect']:
            pygame.draw.rect(surf, self.color, self.rect)
        else:
            pygame.draw.rect(surf, (120, 120, 120), self.rect)


WallMap = dict[Wall, list[pygame.Rect]]


class WallSys:
    x = Wall.SIZE * 2
    y = Wall.SIZE * 2

    def get_center_by_pos_g(self, xy_or_x: PointT | int | float, y: int | float = 0):
        '''给定格子的x,y获取格子的中心位置'''
        if isinstance(xy_or_x, tuple):
            x, y = xy_or_x
        else:
            x = xy_or_x
        return pygame.Vector2(self.x + Wall.SIZE * x, self.y + Wall.SIZE * y)

    def get_walls_from_csv(self, csv_path: str) -> Group:
        group = Group()
        with open(csv_path, mode='r', newline='') as file:
            for y, line in enumerate(csv.reader(file)):
                for x, c in enumerate(line):
                    num = int(c)  # 每一个数字
                    if num == 0:
                        continue
                    Wall(num, (x, y), self.get_center_by_pos_g(x, y), groups=group)
        return group

    def __init__(self, wall_csv_path: str) -> None:
        self.walls: Group = self.get_walls_from_csv(wall_csv_path)
        self.cut_rects: WallMap = {}

    def __iter__(self):
        return iter(self.walls)

    def draw(self, surf: pygame.Surface):
        wall: Wall
        for wall in self.walls:
            wall.draw(surf)
        if DEBUG['show_rect']:
            for rect_set in self.cut_rects.values():
                for rect in rect_set:
                    pygame.draw.rect(surf, 'purple', rect, 1)


if __name__ == '__main__':
    '''测试'''
    WallSys('res_ss/level/wall_maps/1.csv')
