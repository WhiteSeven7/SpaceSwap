from itertools import product
import pygame
from pygame.rect import Rect

x_num = 10
y_num = 10
SIZE = 50

group = [Rect(x * SIZE, y * SIZE, SIZE, SIZE) for x in range(x_num) for y in range(y_num)]

a = pygame.Rect(-60, -5, 2 * SIZE, 2 * SIZE)

for _ in range(1000):
    p = False
    for rect in group:
        A = a.colliderect(rect)
        B = a.contains(rect)
        if A and not B:
            p = True
            C = a.clip(rect)
            print(f'{rect=}, {A=}, {B=}, {C=}')
            a.move_ip(1, 0)
    if p:
        print("+++++++++++++++++++++++++++")
