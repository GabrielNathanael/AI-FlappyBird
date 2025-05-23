import pygame

class Score:
    def __init__(self, screen, number_paths):
        self.screen = screen
        self.digits = [pygame.image.load(p).convert_alpha() for p in number_paths]

    def draw(self, score):
        digits = list(str(score))
        total_width = sum(self.digits[int(d)].get_width() for d in digits)
        x = (self.screen.get_width() - total_width) // 2
        for d in digits:
            img = self.digits[int(d)]
            self.screen.blit(img, (x, 50))
            x += img.get_width()
