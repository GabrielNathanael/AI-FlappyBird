import pygame

class Player:
    MAX_ROTATION = 25 # Rotasi maksimal ke atas
    ROTATION_VELOCITY = 20 # Kecepatan rotasi
    ANIMATION_TIME = 5 # Berapa frame untuk setiap animasi flap

    def __init__(self, screen, images, x, y, gravity, jump_strength):
        self.screen = screen
        self.images = images # list gambar (up, mid, down)
        self.image_index = 0
        self.image = self.images[self.image_index] # Gambar yang sedang aktif
        self.x = x
        self.y = y
        self.gravity = gravity
        self.jump_strength = jump_strength
        self.velocity = 0
        self.tick_count = 0 # Untuk fisika dan animasi
        self.rotation_angle = 0 # Sudut rotasi actual
        self.height_at_jump = y # Tinggi saat terakhir melompat (untuk rotasi)

        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.JUMP_STRENGTH_CONST = jump_strength
        self.GRAVITY_CONST = gravity

    def jump(self):
        self.velocity = -self.jump_strength
        self.tick_count = 0 # Reset tick_count saat melompat
        self.rotation_angle = self.MAX_ROTATION # Langsung miring ke atas saat jump
        self.height_at_jump = self.y # Simpan tinggi saat melompat

    def move(self):
        self.tick_count += 1

        # Fisika Dasar
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.centery = int(self.y)

        # Logika Rotasi (lebih smooth)
        if self.velocity < 0 or self.y < self.height_at_jump + 50: # Saat naik atau baru saja melompat
            if self.rotation_angle < self.MAX_ROTATION:
                self.rotation_angle = self.MAX_ROTATION # Miring ke atas
        else: # Saat jatuh
            if self.rotation_angle > -90:
                self.rotation_angle -= self.ROTATION_VELOCITY # Menukik ke bawah

        # Batasi rotasi agar tidak menukik terlalu parah di awal jatuh
        if self.rotation_angle < -90:
            self.rotation_angle = -90

    def draw(self, screen):
        # Logika animasi flapping
        self.image_index = (self.tick_count // self.ANIMATION_TIME) % len(self.images)
        self.image = self.images[self.image_index]

        # Menjaga burung tidak terlalu "terbalik" saat jatuh bebas di bawah
        # Gunakan gambar mid-flap jika menukik terlalu tajam
        if self.rotation_angle <= -80:
            self.image = self.images[1] # Pakai gambar mid-flap saat menukik tajam

        # Rotasi gambar burung
        rotated_image = pygame.transform.rotate(self.image, self.rotation_angle)
        
        # Hitung posisi rect setelah rotasi agar draw dan mask akurat
        # Get_rect(center=...) akan memastikan pusat gambar tetap di self.rect.center
        rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rect.topleft)

    def get_mask(self):
        """Mengembalikan mask dari gambar yang telah dirotasi untuk akurasi kolisi visual."""
        # Penting: mask harus diambil dari gambar yang dirotasi agar akurat dengan visualnya
        rotated_image = pygame.transform.rotate(self.image, self.rotation_angle)
        return pygame.mask.from_surface(rotated_image)