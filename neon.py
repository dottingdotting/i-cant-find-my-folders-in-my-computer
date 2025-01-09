import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids Shooter - Retry on Game Over")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.SysFont("arial", 48)

# Helper functions
def rotate_image(image, angle):
    """Rotate an image and keep its center."""
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image

def calculate_angle(origin, target):
    """Calculate the angle between two points."""
    dx, dy = target[0] - origin[0], target[1] - origin[1]
    return math.degrees(math.atan2(dy, dx))

# Title Screen Function
def title_screen():
    """Display the title screen."""
    screen.fill(BLACK)
    title_text = title_font.render("ASTEROIDS SHOOTER", True, WHITE)
    instructions_text = font.render("Press ENTER to Play", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    # Wait for the player to press ENTER
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

# Game Over Screen
def game_over_screen():
    """Display the game over screen."""
    screen.fill(BLACK)
    game_over_text = title_font.render("GAME OVER", True, RED)
    retry_text = font.render("Press ENTER to Retry or ESC to Quit", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
    screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    # Wait for the player to make a choice
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Retry
                    waiting = False
                    return True
                if event.key == pygame.K_ESCAPE:  # Quit
                    pygame.quit()
                    exit()
    return False

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(0, 0), (40, 10), (0, 20)])
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.angle = 0
        self.speed = 5
        self.velocity = pygame.math.Vector2(0, 0)
        self.lives = 3

    def update(self):
        # Rotate towards the mouse
        mouse_pos = pygame.mouse.get_pos()
        self.angle = calculate_angle(self.rect.center, mouse_pos)
        self.image = rotate_image(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Move the player with WASD keys
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0
        if keys[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys[pygame.K_s]:
            self.velocity.y = self.speed
        if keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_d]:
            self.velocity.x = self.speed

        # Update position and apply screen wrapping
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        self.rect.x %= WIDTH
        self.rect.y %= HEIGHT

# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((10, 5), pygame.SRCALPHA)
        pygame.draw.rect(self.image, WHITE, (0, 0, 10, 5))
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = 10

    def update(self):
        self.rect.x += self.speed * math.cos(math.radians(self.angle))
        self.rect.y += self.speed * math.sin(math.radians(self.angle))

        # Remove the bullet if it goes off-screen
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()

# Asteroid Class
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed, color, parent_size=None):
        super().__init__()
        self.size = size
        self.original_size = parent_size if parent_size else size
        self.color = color
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = random.uniform(-speed, speed)
        self.speed_y = random.uniform(-speed, speed)
        self.split_time = time.time()  # Track when this asteroid was split

    def update(self):
        # Asteroid movement
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Screen wrap
        self.rect.x %= WIDTH
        self.rect.y %= HEIGHT

        # Grow back to the original size if 10 seconds have passed since splitting
        if self.size < self.original_size and time.time() - self.split_time >= 5:
            self.size = self.original_size
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
            self.rect = self.image.get_rect(center=self.rect.center)

    def split(self):
        """Split the asteroid into two smaller ones."""
        if self.size > 20:  # Minimum size for splitting
            new_size = self.size // 2
            speed = abs(self.speed_x) + 1  # Increase speed for smaller asteroids
            return [
                Asteroid(self.rect.centerx, self.rect.centery, new_size, speed, self.color, self.size),
                Asteroid(self.rect.centerx, self.rect.centery, new_size, speed, self.color, self.size)
            ]
        return []

# Main Game Function
def main_game():
    # Sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()

    # Player instance
    player = Player()
    all_sprites.add(player)

    # Level counter
    level = 1

    def random_color():
        """Generate a random color."""
        return random.choice([
            (255, 0, 0),   # Red
            (0, 255, 0),   # Green
            (0, 0, 255),   # Blue
            (255, 255, 0), # Yellow
            (255, 0, 255), # Magenta
            (0, 255, 255)  # Cyan
        ])

    def spawn_asteroids(level):
        """Spawn asteroids with random colors for the level."""
        for _ in range(level * 3):  # Spawn asteroids
            size = random.choice([40, 60])
            speed = 2
            color = random_color()
            asteroid = Asteroid(random.randint(0, WIDTH), random.randint(0, HEIGHT), size, speed, color)
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

    spawn_asteroids(level)

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Shoot bullets
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bullet = Bullet(player.rect.centerx, player.rect.centery, player.angle)
                all_sprites.add(bullet)
                bullets.add(bullet)

        # Update
        all_sprites.update()

        # Check for collisions between bullets and asteroids
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, asteroids, True)
            for hit in hits:
                bullet.kill()
                smaller_asteroids = hit.split()
                for asteroid in smaller_asteroids:
                    all_sprites.add(asteroid)
                    asteroids.add(asteroid)

        # Check for collisions between player and asteroids
        player_hits = pygame.sprite.spritecollide(player, asteroids, False)
        if player_hits:
            player.lives -= 1
            for asteroid in player_hits:
                asteroid.kill()
            if player.lives <= 0:
                running = False

        # Check if all asteroids are destroyed
        if len(asteroids) == 0:
            level += 1
            spawn_asteroids(level)

        # Draw everything
        screen.fill(BLACK)  # Clear the screen
        all_sprites.draw(screen)

        # Draw lives and level
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(lives_text, (10, 10))
        screen.blit(level_text, (WIDTH - 120, 10))

        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    return game_over_screen()

# Main Execution
title_screen()
while True:
    if not main_game():
        break