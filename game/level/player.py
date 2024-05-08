'''玩家'''
import pygame
from ..game_type import *
from ..setting import *
from .entity import Entity


class Player(Entity):
    jump = -600
    speed = 300

    def __init__(self, position) -> None:
        super().__init__(position)
        self.image = pygame.Surface((46, 46))
        self.image.fill('white')
        pygame.draw.rect(self.image, '#B5E61D', (5, 15, 20, 30))
        pygame.draw.line(self.image, '#99D9EA', (42, 15), (6, 40), 5)
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

    def do_when_move_key_state(self, left_pressed: bool, right_pressed: bool) -> None:
        '''根据移动键状态行动'''
        self.velocity.x = (right_pressed - left_pressed) * self.speed

    def run(self, keys: list[bool], delta_time: Number, collision_group: Sequence[pygame.Rect]):
        # 控制
        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:  # 空格跳跃
            self.do_when_press_jump()
        self.do_when_move_key_state(  # 左右移动
            keys[pygame.K_LEFT] or keys[pygame.K_a], keys[pygame.K_RIGHT] or keys[pygame.K_d])
        # 位移
        self.move_and_collide(delta_time, collision_group)

    def draw(self, surface: pygame.Surface):
        super().draw(surface, 'blue')
