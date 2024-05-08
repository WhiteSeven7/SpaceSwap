'''关卡'''
import pygame
from ..setting import *
from ..scene import Scene, PopUp
from .wall import WallSys
from .swap_box import SwapBoxSys
from .player import Player


class LevelMenu(PopUp):
    def __init__(self) -> None:
        pass


class Level(Scene):
    '''关卡类'''

    def __init__(self) -> None:
        self.wall_sys = WallSys('res_ss/level/wall_maps/1.csv')
        self.player = Player(self.wall_sys.get_center_by_pos_g((1, 3)))
        self.swap_box_sys = SwapBoxSys()

        self.pause = False  # 暂停

        # 更新切割后的矩形
        self.update_cut_rects()

    def run(self, surface: pygame.Surface, clock: pygame.time.Clock) -> None:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.swap_box_sys.do_when_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.swap_box_sys.do_when_mouse_up()
        keys = pygame.key.get_pressed()
        self.swap_box_sys.update(self.update_cut_rects)
        self.player.run(
            keys, 1 / FPS, [rect for rect_list in self.wall_sys.cut_rects for rect in rect_list])

        surface.fill('black')  # 画背景
        # self.swap_box_sys.swap_view(surface)  # 交换
        self.wall_sys.draw(surface)  # 画墙
        self.swap_box_sys.swap_view(surface)  # 交换

        self.wall_sys.bebug_draw(surface)  # 交换后再画轮廓线
        self.swap_box_sys.draw(surface)  # 画交换盒
        self.player.draw(surface)  # 画玩家

    def update_cut_rects(self) -> None:
        '''更新切割后的矩形'''
        self.wall_sys.cut_rects.update(
            self.swap_box_sys.cut_wall_rects(self.wall_sys))
