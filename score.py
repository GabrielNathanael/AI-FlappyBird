import pygame

class Score:
    def __init__(self, screen, number_paths):
        self.screen = screen
        self.numbers = [pygame.image.load(path).convert_alpha() for path in number_paths]

    def draw(self, score):
        score_str = str(score)
        total_width = 0
        digits = []

        # Hitung total lebar semua digit agar score bisa ditampilkan rata tengah
        for digit_char in score_str:
            digit = int(digit_char)
            digits.append(self.numbers[digit])
            total_width += self.numbers[digit].get_width()

        x = (self.screen.get_width() - total_width) // 2
        y = 50  # posisi vertikal score

        for digit_image in digits:
            self.screen.blit(digit_image, (x, y))
            x += digit_image.get_width()
