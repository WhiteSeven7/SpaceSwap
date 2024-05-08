'''实体'''
import pygame
from pygame.sprite import Sprite, Group
from ..game_type import *
from ..setting import *
from .wall import Wall


class ToolPositionRect:
    def set_rect_by_position(self) -> None:
        '''根据 position 改变 rect, 用于 positon 改变时'''
        self.rect.center = self.position

    def set_position_by_rect(self) -> None:
        '''根据 rect 改变 position, 用于 rect 改变时'''
        self.position.update(self.rect.center)


class Entity(Sprite, ToolPositionRect):
    gravity = 980

    def __init__(self, position: pygame.Vector2 | PointT, groups: Group | Sequence = ()) -> None:
        super().__init__(groups)
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0, 0)
        self.is_on_floor = False
        # self.rect = pygame.Rect(0, 0, 100, 100)

    # def get_rect(self, position: pygame.Vector2) -> pygame.Rect:
    #     rect = self.rect.copy()
    #     rect.center = position
    #     return rect

    def move_and_collide_x(self, delta_time: Number, collision_group: Sequence[Wall]) -> None:
        '''x轴方向的移动位置和碰撞体'''
        self.position.x += self.velocity.x * delta_time
        self.set_rect_by_position()
        # 检测碰撞
        for wall in collision_group:
            if self.rect.colliderect(wall):
                # 根据速度重设rect
                if self.velocity.x > 0:
                    self.rect.right = wall.left
                    self.velocity.x = 0
                elif self.velocity.x < 0:
                    self.rect.left = wall.right
                    self.velocity.x = 0
        # 更新玩家位置
        self.set_position_by_rect()

    def move_and_collide_y(self, delta_time: Number, collision_group: Sequence[Wall]) -> None:
        '''y轴方向的移动位置和碰撞体'''
        self.position.y += self.velocity.y * delta_time
        self.set_rect_by_position()
        # 检测碰撞
        for wall in collision_group:
            if self.rect.colliderect(wall):
                if self.velocity.y > 0:
                    self.rect.bottom = wall.top
                    self.velocity.y = 0
                    # 朝下碰撞,设为触地
                    self.is_on_floor = True
                elif self.velocity.y < 0:
                    self.rect.top = wall.bottom
                    self.velocity.y = 0
        # 更新玩家位置
        self.set_position_by_rect()

    def move_and_collide(self, delta_time: Number, collision_group: Sequence[pygame.Rect]) -> bool:
        '''
        移动与碰撞

        :return: 是否发生移动
        :rtype: bool
        '''
        # 当前位置位于墙里面时无法移动
        for rect in collision_group:
            if self.rect.colliderect(rect):
                self.is_on_floor = True
                self.velocity.update(0, 0)
                return False
        # 新的速度
        self.velocity.y += self.gravity * delta_time

        # 在哥哥分量上进行移动和碰撞
        self.move_and_collide_y(delta_time, collision_group)
        self.move_and_collide_x(delta_time, collision_group)

        return True

    def draw(self, surface: pygame.Surface, debug_color):
        surface.blit(self.image, self.rect)
        if DEBUG['show_rect']:
            # 蓝色框
            pygame.draw.rect(surface, debug_color, self.rect, 1)
