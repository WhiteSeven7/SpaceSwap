import pygame
from pygame.event import Event as PgEvent



event_index = pygame.USEREVENT


def UserEvent(data: dict) -> PgEvent:
    global event_index
    event_index += 1
    return PgEvent(event_index, data)
