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
        self.rect_in_self: list[Wall] = []

    def move(self, d_xy: tuple[int, int]) -> None:
        self.rect.move_ip(d_xy)

    def _cut_rect_by_rects(self, rect_map: WallMap, wall: Wall, clipped_rect: Rect) -> None:
        '''根据矩形切割矩形'''
        wall_rect = wall.rect
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
        # 添加自己包含的rect
        self.rect_in_self.append(
            rects['_'.join((top_or_bottom, left_or_right))])
        # 设置wall_对应的[rect]
        rect_map[wall] = list(rects.values())

    def cut_rects(self, wall_group: Sequence[Wall]) -> WallMap:
        '''给出切割后的rect'''
        rect_map: WallMap = {}
        for wall in wall_group:
            wall_rect = wall.rect
            # 排除没有相交和包含在内的
            if not self.rect.colliderect(wall_rect):
                rect_map[wall] = [wall_rect]
            elif self.rect.contains(wall_rect):
                rect_map[wall] = [wall_rect]
                self.rect_in_self.append(wall_rect)
                continue
            else:
                clipped_rect = self.rect.clip(wall_rect)  # 相交的矩形
                # 添加矩形
                self._cut_rect_by_rects(rect_map, wall, clipped_rect)
        return rect_map

    def cut_rects_second(self, wall_group: Sequence[Wall]):
        '''在切过的基础上再切一次'''
        rect_map = {}
        for wall_rect in wall_group:
            # 排除没有相交和包含在内的
            if not self.rect.colliderect(wall_rect) or self.rect.contains(wall_rect):
                continue
            clipped_rect = self.rect.clip(wall_rect)  # 相交的矩形
            # 添加矩形
            if wall_rect.right != clipped_rect.right:  # 相交矩形在wall左侧
                x = clipped_rect.right
                if wall_rect.bottom != clipped_rect.bottom:  # 相交矩形在wall左上侧
                    ...
                elif wall_rect.bottom != clipped_rect.bottom:  # 相交矩形在wall左下侧
                    ...
                else:  # 相交矩形在wall纯左侧
                    # 右半部分矩形
                    rect_right = pygame.Rect(
                        x, wall_rect.top, wall_rect.right - x, wall_rect.height)
                    rect_map[wall_rect] = {clipped_rect, rect_right}
            elif wall_rect.left != clipped_rect.left:  # 相交矩形在wall右侧
                x = clipped_rect.right
                # 左半部分矩形
                rect_left = wall_rect.copy()
                rect_left.width = x - wall_rect.left
                # 右半部分矩形
                rect_right = wall_rect.copy()
                rect_right.left = x
                rect_right.width = wall_rect.right - x
            elif wall_rect.right != clipped_rect.right:  # 相交矩形在wall上侧  #确定只切一个
                ...


class SwapBoxSys:
    def __init__(self) -> None:
        self.swap_boxs = Group()
        self.red_box = SwapBox(
            (Wall.SIZE * 2, Wall.SIZE * 2), (237, 28, 36), (100, 100), self.swap_boxs)
        # self.blue_box = SwapBox(
        #     (Wall.SIZE * 2, Wall.SIZE * 2), (0, 162, 232), (200, 200), self.swap_boxs)
        self.clicked_box: SwapBox | None = None  # 正在挪动的 SwapBox

    def do_when_mouse_down(self) -> None:
        ...

    def cut_wall_rects(self, wall_group: Sequence[Wall]) -> WallMap:
        return self.red_box.cut_rects(wall_group)

    def update(self, update_cut_rects):
        d_xy = pygame.mouse.get_rel()
        if pygame.mouse.get_pressed()[0]:
            self.red_box.move(d_xy)
            # 更新切割后的矩形
            update_cut_rects()

    def draw(self, surf: Surface) -> None:
        self.swap_boxs.draw(surf)
