'''玩家'''
import pygame

from ..game_type import *
from ..setting import *
from .entity import Entity


class Player(Entity):
    jump = -500
    speed = 300

    def __init__(self, home_position) -> None:
        self.home_position = home_position
        super().__init__(self.home_position)
        self.image = pygame.Surface((40, 40))
        self.image.fill('white')
        pygame.draw.rect(self.image, '#B5E61D', (5, 5, 10, 10))
        pygame.draw.rect(self.image, '#B5E61D', (25, 5, 10, 10))
        pygame.draw.line(self.image, '#99D9EA', (8, 22), (20, 32), 5)
        pygame.draw.line(self.image, '#99D9EA', (32, 22), (20, 32), 5)
        self.rect = self.image.get_rect(center=self.position)

    def do_when_press_jump(self) -> bool:
        '''
        当jump键按着时

        :return: 是否跳起
        :rtype: bool
        '''
        if self.is_on_floor:
            self.velocity.y = self.jump
            self.is_on_floor = False
            return True
        return False

    def do_when_move_key_state(self, left_pressed: bool, right_pressed: bool) -> None:
        '''根据移动键状态行动'''
        self.velocity.x = (right_pressed - left_pressed) * self.speed

    def init(self):
        self.position = pygame.Vector2(self.home_position)
        self.set_rect_by_position()
        self.velocity = pygame.Vector2(0, 0)

    def update(self, keys: Sequence[bool], delta_time: Number, collision_group: Sequence[pygame.Rect]):
        # 控制
        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:  # 空格跳跃
            self.do_when_press_jump()
        self.do_when_move_key_state(  # 左右移动
            keys[pygame.K_LEFT] or keys[pygame.K_a], keys[pygame.K_RIGHT] or keys[pygame.K_d])
        # 位移
        self.move_and_collide(delta_time, collision_group)
        # 在脱离屏幕时回到初始点
        if self.rect.top > WINDOWS_SIZE[1] or self.rect.right < 0 or self.rect.left > WINDOWS_SIZE[0]:
            self.init()

    def draw(self, surface: pygame.Surface):
        super().draw(surface, 'blue')
