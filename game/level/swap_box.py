'''交换框'''
import pygame
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.sprite import Sprite, Group
from pygame.math import Vector2
from pygame.color import Color
from ..game_type import *
from ..setting import *
from .entity import ToolPositionRect
from .wall import Wall


class SwapBox(Sprite, ToolPositionRect):
    def __init__(self, size: PointT, color: Color | tuple[int, int, int], position: Vector2 | PointT, group: Sequence[Group] = ()) -> None:
        super().__init__(group)
        self.size = size  # 尺寸
        self.color = Color(color)  # 颜色
        self.color.a = 100  # 设置不透明度
        self.image = Surface((self.size)).convert_alpha()
        self.image.fill(self.color)
        self.position = Vector2(position)  # 位置
        self.rect = Rect((0, 0), self.size)  # 矩形
        self.set_rect_by_position()

        # 记录包含的矩形, 用于第二个切割, 这些矩形是共用对象, 不需要保存到下一帧
        self.rect_in_self: list[Rect] = []
        # 记录覆盖的图层的内容, 不需要保存到下一帧
        self.frozen_surface = pygame.Surface(self.size)
        # 记录需要在交汇区相对与自身的矩形
        self.collision_rect_relative: Rect | None = None

    def move(self, d_xy: tuple[int, int]) -> None:
        '''移动'''
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
            left_or_right = 'left'
        elif wall_rect.left != clipped_rect.left:  # 相交矩形在wall右侧
            x = clipped_rect.left
            left_or_right = 'right'
        if wall_rect.bottom != clipped_rect.bottom:  # 相交矩形在wall左上侧
            y = clipped_rect.bottom
            top_or_bottom = 'top'
        elif wall_rect.top != clipped_rect.top:  # 相交矩形在wall左下侧
            y = clipped_rect.top
            top_or_bottom = 'bottom'
        if x is None and y is None:
            raise ValueError("x is None and y is None")
        elif y is None:
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

    def cut_rects(self, wall_group: Sequence[Wall]) -> dict[Wall, list[pygame.Rect]]:
        '''给出切割后的rect

        :param wall_group: 可以迭代拿到需要的Wall的结构
        :type wall_group: Sequence[Wall]

        :return: 一个字典,将每一个Wall映射到它被割出的rect
        :rtype: dict[Wall, list[pygame.rect.Rect]]
        '''
        self.rect_in_self = []  # 清空上一帧的遗留
        rect_map: dict[Wall, list[pygame.Rect]] = {}
        for wall in wall_group:
            wall_rect = wall.rect
            if not self.rect.colliderect(wall_rect):  # 没有相交
                rect_map[wall] = [wall_rect.copy()]  # 用拷贝防止Wall的rect被移动
            elif self.rect.contains(wall_rect):  # 包含在内的
                rect_copy = wall_rect.copy()  # 用拷贝防止Wall的rect被移动
                rect_map[wall] = [rect_copy]
                self.rect_in_self.append(rect_copy)
            else:  # 相交
                clipped_rect = self.rect.clip(wall_rect)  # 相交的矩形
                # 拿到切割后的数据
                rects, key = self._cut_rect_by_rects(wall_rect, clipped_rect)
                # 设置wall_对应的[rect]
                rect_map[wall] = list(rects.values())
                # 添加自己包含的rect
                self.rect_in_self.append(rects[key])
        return rect_map

    def cut_rects_second(self, wall_group: Sequence[Wall], rect_map: dict[Wall, list[pygame.Rect]], other_box_rects: list[Rect]) -> None:
        '''二次切割

        在切过的基础上再切一次

        :param wall_group: 可以迭代拿到需要的Wall的结构
        :type wall_group: Sequence[Wall]

        :param rect_map: 第一次切得的Wall映射到[pygame.rect.Rect]的映射
        :type rect_map: dict[Wall, list[pygame.rect.Rect]]

        :param other_box_rects: 第一次切割的SwapBox储存的包含在内的矩形
        :type other_box_rects: Sequence[Wall]
        '''
        self.rect_in_self = []  # 清空上一帧的遗留
        for wall in wall_group:
            mapped_rect_list = rect_map[wall].copy()  # 这里要复制一份用来迭代
            for mapped_rect in mapped_rect_list:
                if self.rect.contains(mapped_rect):  # 包含在内的
                    if mapped_rect in other_box_rects:  # 已经在前一个SwapBox里,要复制
                        self.rect_in_self.append(mapped_rect.copy())
                    else:
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
                        rect_copy = rects[key].copy()
                        self.rect_in_self.append(rect_copy)
                        rect_map[wall].append(rect_copy)
                    else:
                        self.rect_in_self.append(rects[key])
                    if mapped_rect in other_box_rects:
                        # 修改前一个SwapBox的包含矩形
                        other_box_rects.remove(mapped_rect)
                        other_box_rects.extend(rects.values())

    def freeze_surface(self, surface: Surface) -> None:
        '''把surface上的内容画到frozen_surface上'''
        self.frozen_surface.blit(surface, (0, 0), self.rect)

    def set_collision_rect(self, clipped_rect: Rect | None) -> None:
        '''根据相交矩形得到相对的相交矩形'''
        if clipped_rect is None:
            self.collision_rect_relative = None
        else:
            self.collision_rect_relative = clipped_rect.move(
                -Vector2(self.rect.topleft))

    def update(self):
        '''如果出界, 就贴边'''
        # x方向
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WINDOWS_SIZE[0]:
            self.rect.right = WINDOWS_SIZE[0]
        # y方向
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > WINDOWS_SIZE[1]:
            self.rect.bottom = WINDOWS_SIZE[1]

    def draw_in_clipped(self, surface: Surface, clipped_rect: Rect | PointT, rect_of_other: Rect | None) -> None:
        '''把自己将换到重叠区域的矩形绘制到指定位置'''
        self.frozen_surface.set_alpha(50)
        surface.blit(self.frozen_surface, clipped_rect, rect_of_other)
        self.frozen_surface.set_alpha(255)


class SwapBoxSys:
    def __init__(self) -> None:
        self.swap_boxs = Group()
        self.red_box = SwapBox(
            (Wall.SIZE * 2, Wall.SIZE * 2), (237, 28, 36), (200, 200), self.swap_boxs)
        self.blue_box = SwapBox(
            (Wall.SIZE * 2, Wall.SIZE * 2), (0, 162, 232), (450, 450), self.swap_boxs)
        self.clicked_box: SwapBox | None = None  # 正在挪动的 SwapBox

        self.clipped_surface = Surface(self.red_box.size)   # 记录SwapBox相交的图像
        self.clipped_rect: Rect | None = None   # 两个SwapBox相交的矩形

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

    @staticmethod
    def swap_space(swap_box_a: SwapBox, swap_box_b: SwapBox) -> None:
        '''互换空间

        "与游戏同名的函数"
        将两个SwapBox中矩形的位置改变来实现互换

        '''
        # a中移动到b
        a_to_b = Vector2(swap_box_b.rect.topleft) - \
            Vector2(swap_box_a.rect.topleft)
        for rect_in_a in swap_box_a.rect_in_self:
            rect_in_a.move_ip(a_to_b)
        # b中移动到a
        b_to_a = -a_to_b
        for rect_in_b in swap_box_b.rect_in_self:
            rect_in_b.move_ip(b_to_a)

    def cut_wall_rects(self, wall_group: Sequence[Wall]) -> dict[Wall, list[pygame.Rect]]:
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

        # 设置相交矩形
        clipped_rect = self.red_box.rect.clip(self.blue_box.rect)
        self.clipped_rect = clipped_rect if clipped_rect else None
        # 设置各自的相对相交矩形
        swap_box: SwapBox
        for swap_box in self.swap_boxs:
            swap_box.set_collision_rect(self.clipped_rect)

        return rect_cut

    def update(self, update_cut_rects):
        '''
        1. 如果有SwapBox位置变了, 切割矩形
        2. SwapBox.update()
        '''
        d_xy = pygame.mouse.get_rel()
        if self.clicked_box and pygame.mouse.get_pressed()[0]:
            self.clicked_box.move(d_xy)
            # 更新切割后的矩形
            update_cut_rects()
        swap_box: SwapBox
        for swap_box in self.swap_boxs:
            swap_box.update()

    def record_surface(self, surface: Surface) -> None:
        '''在其他对象绘制前记录好位置, 用于接下来交换'''
        if self.clipped_rect:
            self.clipped_surface.blit(
                surface, (0, 0), self.clipped_rect)  # 记录相交区域

    def swap_view_simple(self, surface: Surface) -> None:
        '''简单交换两框的可见内容, 不考虑重叠的部分'''
        swap_box: SwapBox
        for swap_box in self.swap_boxs:
            swap_box.freeze_surface(surface)  # 记录各自的屏幕画面
        surface.blit(self.red_box.frozen_surface, self.blue_box.rect)  # 交换屏幕画面
        surface.blit(self.blue_box.frozen_surface, self.red_box.rect)  # 交换屏幕画面
        # surface.blit(surface, self.red_box.rect, )
        # surface.blit(self.frozen_surface, (0, 0))

    def swap_view(self, surface: Surface) -> None:
        '''交换两框的可见内容'''
        self.swap_view_simple(surface)
        if self.clipped_rect:
            # 恢复相交区域之前的情况
            surface.blit(self.clipped_surface, self.clipped_rect,
                         ((0, 0), self.clipped_rect.size))
            # 将相交区域的两个来源绘制上去
            self.red_box.draw_in_clipped(
                surface, self.clipped_rect, self.blue_box.collision_rect_relative)
            self.blue_box.draw_in_clipped(
                surface, self.clipped_rect, self.red_box.collision_rect_relative)
            # surface.blit(surface, self.red_box.rect, )
            # surface.blit(self.frozen_surface, (0, 0))

    def draw(self, surface: Surface) -> None:
        self.swap_boxs.draw(surface)
        # swap_box: SwapBox
        # for swap_box in self.swap_boxs:
        #     for rect in swap_box.rect_in_self:
        #         pygame.draw.rect(surface, swap_box.color, rect)
