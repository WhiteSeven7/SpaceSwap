'''游戏窗口数据Game(Windows)'''
import pygame
from .setting import *
from .scene import Scene
from .level import Level


class Windows:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOWS_SIZE)
        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            if pygame.event.get(pygame.QUIT):
                pygame.quit()
                break
            self.update()
            pygame.display.flip()
            self.clock.tick(FPS)

    def update(self):
        ...


class Game(Windows):
    def __init__(self) -> None:
        super().__init__()
        pygame.display.set_caption("Space Swap")  # 窗口名
        self.scene: Scene = Level()

    def update(self):
        # pygame.display.get_surface().fill("#FAF9DE")
        self.scene.run(self.screen, self.clock)


if __name__ == '__main__':
    Game().run()
