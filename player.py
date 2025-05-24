import pygame

class Player:
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, screen, images, x, y, gravity, jump_strength):
        self.screen = screen
        self.images = images
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.x = x
        self.y = y
        self.gravity = gravity
        self.jump_strength = jump_strength
        self.velocity = 0
        self.tick_count = 0
        self.rotation_angle = 0
        self.height_at_jump = y

        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.JUMP_STRENGTH_CONST = jump_strength
        self.GRAVITY_CONST = gravity

    def jump(self):
        self.velocity = -self.jump_strength
        self.tick_count = 0
        self.rotation_angle = self.MAX_ROTATION
        self.height_at_jump = self.y

    def move(self):
        self.tick_count += 1
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.centery = int(self.y)

        if self.velocity < 0 or self.y < self.height_at_jump + 50:
            if self.rotation_angle < self.MAX_ROTATION:
                self.rotation_angle = self.MAX_ROTATION
        else:
            if self.rotation_angle > -90:
                self.rotation_angle -= self.ROTATION_VELOCITY

        if self.rotation_angle < -90:
            self.rotation_angle = -90

    def draw(self, screen):
        self.image_index = (self.tick_count // self.ANIMATION_TIME) % len(self.images)
        self.image = self.images[self.image_index]

        if self.rotation_angle <= -80:
            self.image = self.images[1]

        rotated_image = pygame.transform.rotate(self.image, self.rotation_angle)
        rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rect.topleft)

    def get_mask(self):
        rotated_image = pygame.transform.rotate(self.image, self.rotation_angle)
        return pygame.mask.from_surface(rotated_image)
