'''笔记，记录新的知识'''
import csv
import pygame

# 如何写csv：newline=''
def a():
    with open('res_ss/level/wall_maps/2.csv', 'w', newline='') as d:
        csv_writer = csv.writer(d)
        csv_writer.writerows([
            [1,2,3,4],
            [4,5,6,7],
            [9,9,9,9],
        ])

def b():
    try:
        # pygame.Vector2 不可哈希
        m = {pygame.Vector2(1,1): 1}
    except TypeError as e:
        print(e)

def c():
    rect = pygame.Rect(0, 0, 100, 100)
    print(rect)

    rect.centerx = 250

    print(rect)


c()