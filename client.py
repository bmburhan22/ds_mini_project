import pygame
from network import Network

pygame.font.init()

# Set window size (default, can be resized)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)  # Enable resizing
pygame.display.set_caption("Rock Paper Scissors")

# Colors and fonts
BG_COLOR = (10, 10, 25)
ACCENT_COLOR = (0, 255, 200)
WAIT_COLOR = (180, 180, 180)
LOCKED_COLOR = (100, 100, 100)
MOVE_COLOR = (203, 229, 255)
font_large = pygame.font.SysFont("Segoe UI", 60, bold=True)
font_medium = pygame.font.SysFont("Segoe UI", 36)
font_small = pygame.font.SysFont("Segoe UI", 24)

class EmojiButton:
    def __init__(self, label, emoji, x, y):
        self.label = label
        self.emoji = emoji
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont("Segoe UI Emoji", 60)
        self.text = self.font.render(emoji, True, (255, 255, 255))

        # Adjust button size to fit content
        self.rect = self.text.get_rect(center=(x, y))

    def draw(self, win):
        pygame.draw.rect(win, (30, 30, 60), self.rect.inflate(30, 30), border_radius=12)  # Simplified border radius
        pygame.draw.rect(win, ACCENT_COLOR, self.rect.inflate(30, 30), 3, border_radius=12)  # Simplified border
        win.blit(self.text, self.rect)

    def click(self, pos):
        return self.rect.collidepoint(pos)


def draw_text_with_shadow(win, text, font, color, x, y):
    # Draw text with shadow effect
    shadow = font.render(text, True, (0, 0, 0))
    win.blit(shadow, (x + 2, y + 2))
    text_surface = font.render(text, True, color)
    win.blit(text_surface, (x, y))


def re_draw_window(win, game, player, result=None):
    win.fill(BG_COLOR)

    # Result section (centered)
    if result:
        color = (0, 200, 0) if "Win" in result else (200, 0, 0) if "Lose" in result else (255, 255, 0)
        draw_text_with_shadow(win, result, font_large, color, win.get_width() // 2 - 150, win.get_height() // 2 - 100)
        draw_text_with_shadow(win, "Click to Play Again!", font_medium, ACCENT_COLOR, win.get_width() // 2 - 180, win.get_height() // 2 + 40)

    # Waiting for connection
    elif not game.connected():
        text = font_medium.render("Waiting for both players to connect...", True, WAIT_COLOR)
        win.blit(text, (win.get_width() // 2 - text.get_width() // 2, win.get_height() // 2 - text.get_height() // 2))

    else:
        # Show player moves (centered)
        win.blit(font_medium.render("Your Move", True, ACCENT_COLOR), (win.get_width() // 4 - 70, win.get_height() // 3))
        win.blit(font_medium.render("Opponent's", True, ACCENT_COLOR), (win.get_width() * 3 // 4 - 90, win.get_height() // 3))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)

        if game.both_went():
            text1 = font_medium.render(move1, True, MOVE_COLOR)
            text2 = font_medium.render(move2, True, MOVE_COLOR)
        else:
            text1 = font_medium.render(
                move1 if game.p1_went and player == 0 else "Locked in" if game.p1_went else "Waiting...", True, LOCKED_COLOR
            )
            text2 = font_medium.render(
                move2 if game.p2_went and player == 1 else "Locked in" if game.p2_went else "Waiting...", True, LOCKED_COLOR
            )

        # Define text positioning for "Your Move" and "Opponent's" aligned horizontally
        text1_x = win.get_width() // 4 - text1.get_width() // 2  # X position for "Your Move"
        text2_x = win.get_width() * 3 // 4 - text2.get_width() // 2  # X position for "Opponent's"
        text_y = win.get_height() // 2 - 50  # Adjust Y position for both texts

        # Center the text horizontally and place them in the same row vertically
        win.blit(text1, (text1_x, text_y))  # Positioning "Your Move"
        win.blit(text2, (text2_x, text_y))  # Positioning "Opponent's"

        # Draw buttons in the center of the screen (vertically and horizontally)
        button_width = 200  # Width of each button
        button_height = 100  # Height of each button
        spacing = 30  # Space between buttons

        # Calculate starting Y position to center the buttons vertically below the text
        total_button_height = button_height + spacing  # Total height needed for buttons with spacing
        start_y = text_y + 80  # Adjust to position buttons below the text (you can modify this value as needed)

        # Calculate starting X position to center the buttons horizontally
        start_x = (win.get_width() - (button_width * 3 + spacing * 2)) // 2  # Center buttons horizontally

        for idx, button in enumerate(buttons):
            button.x = start_x + (button_width + spacing) * idx  # Calculate X position
            button.y = start_y  # Y position is adjusted to place the buttons below the text
            button.rect.center = (button.x + button_width // 2, button.y + button_height // 2)  # Update the button's rect position
            button.draw(win)  # Draw each button


    pygame.display.update()


# Button setup: Create buttons for Rock, Paper, Scissors
buttons = [
    EmojiButton("Rock", "🪨", 0, 0),
    EmojiButton("Scissors", "✂️", 0, 0),
    EmojiButton("Paper", "📄", 0, 0)
]

def main():
    run = True
    clock = pygame.time.Clock()
    network = Network()
    player = int(network.get_player())
    print("You are player number:", player)

    result = None
    waiting_for_restart = False

    while run:
        clock.tick(60)

        if not waiting_for_restart:
            try:
                game = network.send("get")
            except:
                print("Server error - could not retrieve game.")
                run = False
                break

            # Check if both players have chosen their move
            if game.both_went():
                re_draw_window(window, game, player)
                pygame.time.delay(1000)

                try:
                    game = network.send("reset")
                except:
                    print("Server error - could not reset game.")
                    run = False
                    break

                # Determine result of the game
                if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
                    result = "You Win!"
                elif game.winner() == -1:
                    result = "Draw!"
                else:
                    result = "You Lose!"

                waiting_for_restart = True

        re_draw_window(window, game, player, result)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONUP:
                if waiting_for_restart:
                    result = None
                    waiting_for_restart = False
                    try:
                        game = network.send("get")
                    except:
                        run = False
                else:
                    pos = pygame.mouse.get_pos()
                    for button in buttons:
                        if button.click(pos) and game.connected():
                            # Send the move to the server if the player hasn't made a move yet
                            if player == 0 and not game.p1_went:
                                network.send(button.label)
                            elif player == 1 and not game.p2_went:
                                network.send(button.label)


main()
