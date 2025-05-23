import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Game constants
WIDTH = 800
HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_BLUE = (0, 191, 255)
NEON_RED = (255, 50, 50)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (147, 0, 211)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Human vs AI Pong")

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.hover_color = tuple(min(c + 50, 255) for c in color)
        self.font = pygame.font.Font(None, 36)
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color

        # Draw button glow
        for i in range(3):
            glow_size = (3 - i) * 2
            glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
            alpha = 100 - i * 30
            s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=10)
            surface.blit(s, glow_rect)

        # Draw main button
        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        # Draw text
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Paddle:
    def __init__(self, x, color, ai_difficulty=None):
        self.x = x
        self.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.color = color
        self.speed = 8
        self.score = 0
        self.ai_difficulty = ai_difficulty

        # AI attributes based on difficulty
        if ai_difficulty == "easy":
            self.reaction_delay = 30
            self.prediction_error = 50
            self.speed_factor = 0.6
        elif ai_difficulty == "medium":
            self.reaction_delay = 20
            self.prediction_error = 30
            self.speed_factor = 0.8
        elif ai_difficulty == "hard":
            self.reaction_delay = 10
            self.prediction_error = 15
            self.speed_factor = 1.0

    def move(self, up=True):
        speed = self.speed * (self.speed_factor if hasattr(self, 'speed_factor') else 1)
        if up and self.y > 0:
            self.y -= speed
        elif not up and self.y < HEIGHT - self.height:
            self.y += speed

    def ai_move(self, ball):
        if not self.ai_difficulty:
            return

        if ball.speed_x > 0:  # Only move if ball is coming towards AI
            # Add randomness based on difficulty
            prediction_error = random.randint(-self.prediction_error, self.prediction_error)
            target_y = ball.y + prediction_error

            # Add delay based on difficulty
            if abs(self.y + PADDLE_HEIGHT/2 - target_y) > self.reaction_delay:
                if self.y + PADDLE_HEIGHT/2 < target_y:
                    self.move(up=False)
                elif self.y + PADDLE_HEIGHT/2 > target_y:
                    self.move(up=True)

    def draw(self):
        # Draw paddle glow
        for i in range(3):
            glow_size = (3 - i) * 2
            s = pygame.Surface((self.width + glow_size * 2, self.height + glow_size * 2), pygame.SRCALPHA)
            alpha = 100 - i * 30
            pygame.draw.rect(s, (*self.color, alpha), s.get_rect())
            screen.blit(s, (self.x - glow_size, self.y - glow_size))

        # Draw main paddle
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self):
        self.reset()
        self.trail = []
        self.trail_length = 10

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_x = random.choice([-4, 4])
        self.speed_y = random.randint(-3, 3)

    def move(self):
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        self.x += self.speed_x
        self.y += self.speed_y

        if self.y <= 0 or self.y >= HEIGHT - BALL_SIZE:
            self.speed_y *= -1

    def draw(self):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / self.trail_length))
            s = pygame.Surface((BALL_SIZE, BALL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 255, 255, alpha), s.get_rect())
            screen.blit(s, pos)

        # Draw ball with rainbow effect
        time_color = pygame.time.get_ticks() // 50  # Changes color over time
        rainbow_color = (
            abs(math.sin(time_color * 0.1)) * 255,  # Red
            abs(math.sin(time_color * 0.1 + 2)) * 255,  # Green
            abs(math.sin(time_color * 0.1 + 4)) * 255   # Blue
        )

        # Draw ball glow
        for i in range(3):
            glow_size = (3 - i) * 2
            s = pygame.Surface((BALL_SIZE + glow_size * 2, BALL_SIZE + glow_size * 2), pygame.SRCALPHA)
            alpha = 100 - i * 30
            pygame.draw.rect(s, (*rainbow_color, alpha), s.get_rect())
            screen.blit(s, (self.x - glow_size, self.y - glow_size))

        # Draw main ball
        pygame.draw.rect(screen, rainbow_color, (self.x, self.y, BALL_SIZE, BALL_SIZE))

class Game:
    def __init__(self, difficulty=None):
        self.state = "menu" if difficulty is None else "game"
        self.difficulty = difficulty
        self.setup_menu_buttons()
        self.setup_game()

    def setup_menu_buttons(self):
        button_width = 200
        button_height = 50
        center_x = WIDTH // 2 - button_width // 2

        if self.state == "menu":
            self.play_button = Button(center_x, 250, button_width, button_height, "PLAY", NEON_GREEN)
        elif self.state == "difficulty":
            self.easy_button = Button(center_x, 150, button_width, button_height, "EASY", NEON_GREEN)
            self.medium_button = Button(center_x, 280, button_width, button_height, "MEDIUM", NEON_BLUE)
            self.hard_button = Button(center_x, 410, button_width, button_height, "HARD", NEON_RED)

    def setup_game(self):
        if self.state == "game":
            self.player = Paddle(50, NEON_BLUE)
            self.ai = Paddle(WIDTH - 65, NEON_RED, self.difficulty)
            self.ball = Ball()
            self.game_font = pygame.font.Font(None, 74)
            self.game_active = True
            self.winner = None

    def handle_collision(self):
        if not hasattr(self, 'ball'):
            return

        # Ball collision with paddles
        if (self.ball.x <= self.player.x + PADDLE_WIDTH and
            self.ball.y + BALL_SIZE >= self.player.y and
            self.ball.y <= self.player.y + PADDLE_HEIGHT and
            self.ball.x >= self.player.x):
            if self.ball.speed_x < 0:
                self.ball.speed_x *= -1
                relative_y = (self.player.y + PADDLE_HEIGHT/2) - (self.ball.y + BALL_SIZE/2)
                self.ball.speed_y = -relative_y * 0.1

        if (self.ball.x + BALL_SIZE >= self.ai.x and
            self.ball.y + BALL_SIZE >= self.ai.y and
            self.ball.y <= self.ai.y + PADDLE_HEIGHT and
            self.ball.x <= self.ai.x + PADDLE_WIDTH):
            if self.ball.speed_x > 0:
                self.ball.speed_x *= -1
                relative_y = (self.ai.y + PADDLE_HEIGHT/2) - (self.ball.y + BALL_SIZE/2)
                self.ball.speed_y = -relative_y * 0.1

    def update(self):
        if self.state == "game" and self.game_active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player.move(up=True)
            if keys[pygame.K_DOWN]:
                self.player.move(up=False)

            self.ball.move()
            self.ai.ai_move(self.ball)
            self.handle_collision()

            # Score points
            if self.ball.x <= 0:
                self.ai.score += 1
                self.ball.reset()
            elif self.ball.x >= WIDTH:
                self.player.score += 1
                self.ball.reset()

            # Check for winner
            if self.player.score >= 5:
                self.game_active = False
                self.winner = "PLAYER"
            elif self.ai.score >= 5:
                self.game_active = False
                self.winner = "AI"

    def draw_menu(self):
        screen.fill(BLACK)

        # Draw main title
        title_font = pygame.font.Font(None, 100)
        title_text = title_font.render("Human vs AI", True, NEON_PURPLE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 80))
        screen.blit(title_text, title_rect)

        # Draw subtitle
        subtitle_font = pygame.font.Font(None, 74)
        subtitle_text = subtitle_font.render("PONG", True, NEON_BLUE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, 150))
        screen.blit(subtitle_text, subtitle_rect)

        # Draw instructions
        instruction_font = pygame.font.Font(None, 28)
        instructions = [
            "How to Play:",
            "- Use UP and DOWN arrow keys to move your paddle",
            "- First to score 5 points wins",
            "- Press R to restart after game over"
        ]

        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, WHITE)
            rect = text.get_rect(center=(WIDTH//2, HEIGHT - 150 + i * 30))
            screen.blit(text, rect)

        # Draw buttons
        self.play_button.draw(screen)

    def draw_difficulty(self):
        screen.fill(BLACK)

        # Draw difficulty selection title
        diff_title_font = pygame.font.Font(None, 74)
        diff_title = diff_title_font.render("Select Difficulty", True, NEON_PURPLE)
        diff_title_rect = diff_title.get_rect(center=(WIDTH//2, 80))
        screen.blit(diff_title, diff_title_rect)

        # Draw buttons only, no descriptions
        button_y_positions = [150, 280, 410]  # Increased spacing between buttons
        for button, y_pos in zip([self.easy_button, self.medium_button, self.hard_button], button_y_positions):
            button.rect.y = y_pos  # Update button position
            button.draw(screen)

    def draw_game(self):
        screen.fill(BLACK)

        # Draw center line
        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, (255, 255, 255, 100), (WIDTH//2 - 5, y, 10, 10))

        self.player.draw()
        self.ai.draw()
        self.ball.draw()

        # Draw scores with glow
        for i in range(3):
            offset = i * 2
            alpha = 255 - i * 50
            player_score = self.game_font.render(str(self.player.score), True, (*NEON_BLUE, alpha))
            ai_score = self.game_font.render(str(self.ai.score), True, (*NEON_RED, alpha))
            screen.blit(player_score, (WIDTH//4 - offset, 20))
            screen.blit(ai_score, (3*WIDTH//4 - offset, 20))

        if not self.game_active:
            winner_color = NEON_BLUE if self.winner == "PLAYER" else NEON_RED
            winner_text = self.game_font.render(f"{self.winner} WINS!", True, winner_color)
            restart_text = pygame.font.Font(None, 36).render("Press R to restart", True, WHITE)
            screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "difficulty":
            self.draw_difficulty()
        else:
            self.draw_game()

def main():
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.state == "game" and not game.game_active:
                    game = Game(game.difficulty)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                if game.state == "menu":
                    if game.play_button.handle_event(event):
                        game.state = "difficulty"
                        game.setup_menu_buttons()
                elif game.state == "difficulty":
                    if game.easy_button.handle_event(event):
                        game = Game("easy")
                    elif game.medium_button.handle_event(event):
                        game = Game("medium")
                    elif game.hard_button.handle_event(event):
                        game = Game("hard")

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
