'''交换框'''
import pygame
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.sprite import Sprite, Group
from ..game_type import *
from .entity import ToolPositionRect
from .wall import Wall, WallMap


class SwapBox(Sprite, ToolPositionRect):
    def __init__(self, size: PointT, color: pygame.Color, position: pygame.Vector2 | PointT, group: Sequence[Group] = ()) -> None:
        super().__init__(group)
        self.size = size  # 尺寸
        self.color = pygame.Color(color)  # 颜色
        self.color.a = 100  # 设置不透明度
        self.image = Surface((self.size)).convert_alpha()
        self.image.fill(self.color)
        self.position = pygame.Vector2(position)  # 位置
        self.rect = Rect((0, 0), self.size)  # 矩形
        self.set_rect_by_position()

        # 记录被我切割到的wall
        # 用于第二个切割
        self.rect_in_self: list[Wall] = []  # 包含的矩形,这些矩形是共用对象

    def move(self, d_xy: tuple[int, int]) -> None:
        self.rect.move_ip(d_xy)

    def _cut_rect_by_rects(self, wall_rect: Rect, clipped_rect: Rect) -> tuple[dict[str, Rect], str]:
        '''
        根据矩形切割矩形

        :return: 切割成的矩阵, 用于拿到新加入的rect的key
        :rtype: tuple[dict[str, pygame.rect.Rect], str]
        '''
        x = y = None  # 切割线的位置
        top_or_bottom = ''  # swap_box内的矩形的上下位置
        left_or_right = ''  # swap_box内的矩形的左右位置
        rects: dict[str, Rect] = {}  # 记录方位对应的矩形
        if wall_rect.right != clipped_rect.right:  # 相交矩形在wall左侧
            x = clipped_rect.right
            left_or_right = 'right'
        elif wall_rect.left != clipped_rect.left:  # 相交矩形在wall右侧
            x = clipped_rect.left
            left_or_right = 'left'
        if wall_rect.bottom != clipped_rect.bottom:  # 相交矩形在wall左上侧
            y = clipped_rect.bottom
            top_or_bottom = 'top'
        elif wall_rect.top != clipped_rect.top:  # 相交矩形在wall左下侧
            y = clipped_rect.top
            top_or_bottom = 'bottom'
        if x is None and y is None:
            raise ValueError("x is None and y is None")
        if y is None:
            rects = {
                '_left': Rect(wall_rect.left, wall_rect.top, x - wall_rect.left, wall_rect.height),
                '_right': Rect(x, wall_rect.top, wall_rect.right - x, wall_rect.height),
            }
        elif x is None:
            rects = {
                'top_': Rect(wall_rect.left, wall_rect.top, wall_rect.width, y - wall_rect.top),
                'bottom_': Rect(wall_rect.left, y, wall_rect.width, wall_rect.bottom - y),
            }
        else:
            rects = {
                'top_left': Rect(wall_rect.left, wall_rect.top, x - wall_rect.left, y - wall_rect.top),
                'top_right': Rect(x, wall_rect.top, wall_rect.right - x, y - wall_rect.top),
                'bottom_left': Rect(wall_rect.left, y, x - wall_rect.left, wall_rect.bottom - y),
                'bottom_right': Rect(x, y, wall_rect.right - x, wall_rect.bottom - y),
            }

        return rects, '_'.join((top_or_bottom, left_or_right))

    def cut_rects(self, wall_group: Sequence[Wall]) -> WallMap:
        '''给出切割后的rect

        :param wall_group: 可以迭代拿到需要的Wall的结构
        :type wall_group: Sequence[Wall]

        :return: 一个字典,将每一个Wall映射到它被割出的rect
        :rtype: dict[Wall, list[pygame.rect.Rect]]
        '''
        rect_map: WallMap = {}
        for wall in wall_group:
            wall_rect = wall.rect
            if not self.rect.colliderect(wall_rect):  # 没有相交
                rect_map[wall] = [wall_rect]
            elif self.rect.contains(wall_rect):  # 包含在内的
                rect_map[wall] = [wall_rect]
                self.rect_in_self.append(wall_rect)
            else:  # 相交
                clipped_rect = self.rect.clip(wall_rect)  # 相交的矩形
                # 拿到切割后的数据
                rects, key = self._cut_rect_by_rects(wall_rect, clipped_rect)
                # 设置wall_对应的[rect]
                rect_map[wall] = list(rects.values())
                # 添加自己包含的rect
                self.rect_in_self.append(rects[key])
        return rect_map

    def cut_rects_second(self, wall_group: Sequence[Wall], rect_map: WallMap, other_box_rects: list[Rect]) -> None:
        '''二次切割

        在切过的基础上再切一次

        :param wall_group: 可以迭代拿到需要的Wall的结构
        :type wall_group: Sequence[Wall]

        :param rect_map: 第一次切得的Wall映射到[pygame.rect.Rect]的映射
        :type rect_map: dict[Wall, list[pygame.rect.Rect]]

        :param other_box_rects: 第一次切割的SwapBox储存的包含在内的矩形
        :type other_box_rects: Sequence[Wall]
        '''
        for wall in wall_group:
            mapped_rect_list = rect_map[wall].copy()  # 这里要复制一份用来迭代
            for mapped_rect in mapped_rect_list:
                if self.rect.contains(mapped_rect):  # 包含在内的
                    self.rect_in_self.append(mapped_rect)
                elif self.rect.colliderect(mapped_rect):  # 相交
                    clipped_rect = self.rect.clip(mapped_rect)  # 相交的矩形
                    # 拿到切割后的数据
                    rects, key = self._cut_rect_by_rects(
                        mapped_rect, clipped_rect)
                    # 修改WallSys的映射
                    rect_map[wall].remove(mapped_rect)
                    rect_map[wall].extend(rects.values())
                    # 添加自己包含的rect
                    if mapped_rect in other_box_rects:  # 已经在前一个SwapBox里了,要复制
                        self.rect_in_self.append(rects[key].copy())
                    else:
                        self.rect_in_self.append(rects[key])
                    if mapped_rect in other_box_rects:
                        # 修改前一个SwapBox的包含矩形
                        other_box_rects.remove(mapped_rect)
                        rect_map[wall].extend(rects.values())

                # 不相交
        #     if not self.rect.colliderect(wall_rect):  # 没有相交
        #         rect_map[wall] = [wall_rect]
        #     elif self.rect.contains(wall_rect):  # 包含在内的
        #         rect_map[wall] = [wall_rect]
        #         self.rect_in_self.append(wall_rect)
        #     else:  # 相交
        #         clipped_rect = self.rect.clip(wall_rect)  # 相交的矩形
        #         # 添加矩形
        #         self._cut_rect_by_rects(rect_map, wall, clipped_rect)
        # return rect_map


class SwapBoxSys:
    def __init__(self) -> None:
        self.swap_boxs = Group()
        self.red_box = SwapBox(
            (Wall.SIZE * 2, Wall.SIZE * 2), (237, 28, 36), (100, 100), self.swap_boxs)
        self.blue_box = SwapBox(
            (Wall.SIZE * 2, Wall.SIZE * 2), (0, 162, 232), (200, 200), self.swap_boxs)
        self.clicked_box: SwapBox | None = None  # 正在挪动的 SwapBox

    def do_when_mouse_down(self, pos: PointT) -> None:
        '''控制一个SwapBox'''
        swap_box: SwapBox
        for swap_box in self.swap_boxs:
            if (swap_box.rect).collidepoint(pos):
                self.clicked_box = swap_box
                return

    def do_when_mouse_up(self) -> None:
        '''取消控制SwapBox'''
        self.clicked_box = None

    def swap_space(self, swap_box_a: SwapBox, swap_box_b: SwapBox) -> None:
        '''互换空间

        "与游戏同名的函数"
        将两个SwapBox中矩形的位置改变来实现互换

        '''

    def cut_wall_rects(self, wall_group: Sequence[Wall]) -> WallMap:
        '''将Wall进行切割

        :param wall_group: 可以迭代拿到需要的Wall的结构
        :type wall_group: Sequence[Wall]

        :return: 一个字典,将每一个Wall映射到它被割出的rect
        :rtype: dict[Wall, list[pygame.rect.Rect]]
        '''
        # 第一次切割
        rect_cut = self.red_box.cut_rects(wall_group)
        # 第二次切割
        self.blue_box.cut_rects_second(
            wall_group, rect_cut, self.red_box.rect_in_self)
        # 互换碰撞
        self.swap_space(self.red_box, self.blue_box)
        return rect_cut

    def update(self, update_cut_rects):
        d_xy = pygame.mouse.get_rel()
        if self.clicked_box and pygame.mouse.get_pressed()[0]:
            self.clicked_box.move(d_xy)
            # 更新切割后的矩形
            update_cut_rects()

    def draw(self, surf: Surface) -> None:
        self.swap_boxs.draw(surf)

    def swap_view(self, surface) -> None:
        '''交换两框的可见内容'''
        ...
