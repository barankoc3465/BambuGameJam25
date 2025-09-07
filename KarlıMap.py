import pygame
import sys
import random

# ----- Sabitler ve Başlangıç Ayarları -----
# Ekran boyutları
WIDTH, HEIGHT = 800, 600
# Ekran adı
TITLE = "İki Kutu - Kar Macerası"
# FPS
FPS = 60

# Renkler
COLORS = {
    "SKY": (135, 206, 235),     # Açık Mavi
    "SNOW": (255, 255, 255),    # Beyaz
    "BLUE": (30, 144, 255),     # Mavi
    "RED": (220, 20, 60),       # Kırmızı
    "BLACK": (0, 0, 0),         # Siyah
    "GREEN": (50, 205, 50),     # Yeşil
    "YELLOW": (255, 215, 0),    # Sarı
    "PURPLE": (138, 43, 226),   # Mor
    "ORANGE": (255, 140, 0)     # Turuncu
}

# Oyun ayarları
PLAYER_SPEED = 10
ENEMY_TYPES = {
    "chaser": {"color": COLORS["RED"], "speed": 3},
    "zigzag": {"color": COLORS["PURPLE"], "speed": 4},
    "dropper": {"color": COLORS["ORANGE"], "speed": 10},
}
HEAT_DECAY_RATE = 0.08
HEAT_GAIN_RATE = 0.3
MAX_HEAT = 100
WIN_SCORE = 3000

# ----- Sınıflar -----
class Player:
    def __init__(self, x, y, size, color, controls):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.controls = controls

    def update(self, keys):
        # Yön tuşlarına göre hareketi ayarla
        if self.controls == "wasd":
            if keys[pygame.K_a]:
                self.rect.x -= PLAYER_SPEED
            if keys[pygame.K_d]:
                self.rect.x += PLAYER_SPEED
            if keys[pygame.K_w]:
                self.rect.y -= PLAYER_SPEED
            if keys[pygame.K_s]:
                self.rect.y += PLAYER_SPEED
        elif self.controls == "arrows":
            if keys[pygame.K_LEFT]:
                self.rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                self.rect.x += PLAYER_SPEED
            if keys[pygame.K_UP]:
                self.rect.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                self.rect.y += PLAYER_SPEED
        
        # Sınır kontrolü
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Enemy:
    def __init__(self, x, y, size, enemy_type):
        self.rect = pygame.Rect(x, y, size, size)
        self.type = enemy_type
        self.color = ENEMY_TYPES[enemy_type]["color"]
        self.speed = ENEMY_TYPES[enemy_type]["speed"]
        self.dir = 1 # Zigzag düşman için yön

    def update(self, player_rects):
        if self.type == "chaser":
            target = player_rects[0] # İlk oyuncuyu hedef al
            dx = target.centerx - self.rect.centerx
            dy = target.centery - self.rect.centery
            
            if abs(dx) > self.speed:
                self.rect.x += self.speed if dx > 0 else -self.speed
            if abs(dy) > self.speed:
                self.rect.y += self.speed if dy > 0 else -self.speed

        elif self.type == "zigzag":
            self.rect.x += self.speed * self.dir
            time_factor = pygame.time.get_ticks() / 500.0
            self.rect.y = 200 + int(30 * pygame.math.Vector2(1, 0).rotate(time_factor * 180).y)
            
            if self.rect.right >= WIDTH or self.rect.left <= 0:
                self.dir *= -1
                self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

        elif self.type == "dropper":
            self.rect.y += self.speed
            if self.rect.top > HEIGHT:
                self.rect.x = random.randint(0, WIDTH - self.rect.width)
                self.rect.y = -40

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# ----- Fonksiyonlar -----
def draw_centered_text(font, screen, text_list, y_offset_start, line_height):
    """Verilen metinleri ekranın ortasında dikey olarak sıralar ve çizer."""
    screen_width, screen_height = screen.get_size()
    for i, (text, color) in enumerate(text_list):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(centerx=screen_width // 2)
        text_rect.centery = screen_height // 2 + y_offset_start + i * line_height
        screen.blit(text_surface, text_rect)

def reset_game():
    """Tüm oyun değişkenlerini başlangıç durumuna döndürür."""
    global players, enemies, heat, score, game_over, win, snowflakes
    
    # Oyuncu pozisyonlarını sıfırla
    players[0].rect.topleft = (100, 500)
    players[1].rect.topleft = (200, 500)
    
    # Oyun değişkenlerini sıfırla
    heat = MAX_HEAT
    score = 0
    game_over = False
    win = False
    
    # Kar tanelerini sıfırla
    snowflakes = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(50)]
    
    # Düşmanları sıfırla
    enemies = [
        Enemy(600, 500, 40, "chaser"),
        Enemy(0, 200, 40, "zigzag"),
        Enemy(random.randint(0, WIDTH-40), 0, 40, "dropper")
    ]

# ----- Pygame Başlangıcı -----
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)

# Oyuncu ve düşman nesneleri
players = [
    Player(100, 500, 40, COLORS["BLUE"], "wasd"),
    Player(200, 500, 40, COLORS["BLUE"], "arrows")
]

# Oyun değişkenleri
heat = MAX_HEAT
game_over = False
win = False
score = 0

# Nesneleri başlat
reset_game()

# ----- Ana Oyun Döngüsü -----
running = True
frame_count = 0

while running:
    frame_count += 1
    
    # Olay yönetimi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if (game_over or win) and event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_ESCAPE:
                running = False
    
    if not game_over and not win:
        keys = pygame.key.get_pressed()
        
        # Oyuncuları ve düşmanları güncelle
        for player in players:
            player.update(keys)
        
        for enemy in enemies:
            # Düşmanları güncellerken oyuncu dikdörtgenlerini gönder
            enemy.update([p.rect for p in players])
        
        # Isı yönetimi
        heat -= HEAT_DECAY_RATE
        if players[0].rect.colliderect(players[1].rect):
            heat = min(MAX_HEAT, heat + HEAT_GAIN_RATE)
        
        # Skor artışı
        if frame_count % 10 == 0:
            score += 1
        
        # Oyun bitiş ve kazanma koşulları
        if score >= WIN_SCORE:
            win = True
        
        if heat <= 0:
            game_over = True
        
        for player in players:
            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    game_over = True
                    break
            if game_over:
                break
    
    # Her şeyi çiz
    screen.fill(COLORS["SKY"])
    pygame.draw.rect(screen, COLORS["SNOW"], (0, HEIGHT-50, WIDTH, 50))
    
    # Kar tanelerini güncelle ve çiz
    for flake in snowflakes:
        flake[1] += 2
        flake[0] += random.uniform(-0.5, 0.5)
        if flake[1] > HEIGHT:
            flake[0] = random.randint(0, WIDTH)
            flake[1] = 0
        pygame.draw.circle(screen, COLORS["SNOW"], (int(flake[0]), int(flake[1])), 3)

    if not game_over and not win:
        for player in players:
            player.draw(screen)
        
        if players[0].rect.colliderect(players[1].rect.inflate(20, 20)):
            pygame.draw.circle(screen, COLORS["YELLOW"], players[0].rect.center, 30, 3)
            pygame.draw.circle(screen, COLORS["YELLOW"], players[1].rect.center, 30, 3)
        
        for enemy in enemies:
            enemy.draw(screen)
        
        # Skor ve ısı barını çiz
        heat_color = COLORS["RED"] if heat < 30 else COLORS["YELLOW"] if heat < 60 else COLORS["GREEN"]
        
        # Skor yerine yıldızları çiz
        star_count = score // 20
        for i in range(star_count):
            star_x = 20 + i * 25
            star_y = 20
            pygame.draw.circle(screen, COLORS["YELLOW"], (star_x, star_y), 10)
        
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH - bar_width - 10
        bar_y = 10
        
        pygame.draw.rect(screen, COLORS["BLACK"], (bar_x-2, bar_y-2, bar_width+4, bar_height+4))
        pygame.draw.rect(screen, COLORS["RED"], (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, heat_color, (bar_x, bar_y, int(bar_width * (heat/MAX_HEAT)), bar_height))
        
    elif game_over:
        draw_centered_text(font, screen, 
            [("Game Over", COLORS["RED"]),
             (f"Toplam Skor: {score}", COLORS["BLACK"]),
             ("Yeniden Başlamak İçin 'R' Tuşuna Basınız", COLORS["BLACK"])], 
            -50, 50)
        
    elif win:
        draw_centered_text(font, screen,
            [("Kazandınız!!!", COLORS["GREEN"]),
             (f"Toplam Skorunuz: {score}!!!", COLORS["BLACK"]),
             ("Yeniden Başlamak İçin 'R' Tuşuna Basınız", COLORS["BLACK"])], 
            -50, 50)
    
    pygame.display.flip()
    clock.tick(FPS)
    
# Temizleme
pygame.quit()
sys.exit()
