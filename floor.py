import pygame

class Floor:
    def __init__(self, screen, image_path, y):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.y = y
        self.x1 = 0
        self.x2 = self.image.get_width()
        self.scroll_speed = 2
        self.stopped = False

    def draw(self):
        self.screen.blit(self.image, (self.x1, self.y))
        self.screen.blit(self.image, (self.x2, self.y))
        if not self.stopped:
            self.x1 -= self.scroll_speed
            self.x2 -= self.scroll_speed
            if self.x1 + self.image.get_width() < 0:
                self.x1 = self.x2 + self.image.get_width()
            if self.x2 + self.image.get_width() < 0:
                self.x2 = self.x1 + self.image.get_width()

    def stop(self):
        self.stopped = True

    def reset(self):
        self.x1 = 0
        self.x2 = self.image.get_width()
        self.stopped = False
