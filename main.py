import pygame
import sys
import time
from memory_game_classes import MemoryGame

# Inițializăm pygame
pygame.init()

# Setăm dimensiunile ecranului
screen_width = 840
screen_height = 640
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jocul de Memorie cu Pisici")

# Listă globală pentru scoruri
player_scores = []


def select_difficulty(screen):
    font = pygame.font.Font(None, 36)
    instructions = font.render("Selectează dificultatea: 1 - Easy, 2 - Medium, 3 - Hard", True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(instructions, (screen_width // 2 - instructions.get_width() // 2, screen_height // 2 - 50))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 120  # Easy: 2 minute
                elif event.key == pygame.K_2:
                    return 90   # Medium: 1:30 minute
                elif event.key == pygame.K_3:
                    return 60   # Hard: 1 minut


def get_player_name(screen):
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 20, 300, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((0, 0, 0))
        instructions = font.render("Introduceți numele jucătorului și apăsați Enter:", True, (255, 255, 255))
        screen.blit(instructions, (screen_width // 2 - instructions.get_width() // 2, screen_height // 2 - 100))

        txt_surface = font.render(text, True, color)
        width = max(300, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()


def display_top_scores(screen, scores):
    font = pygame.font.Font(None, 36)
    screen.fill((0, 0, 0))

    header = font.render("Ultimii 5 jucători (ordine descrescătoare a scorului):", True, (255, 255, 255))
    screen.blit(header, (screen_width // 2 - header.get_width() // 2, 50))

    for i, (name, score) in enumerate(scores):
        text = font.render(f"{i + 1}. {name}: {score} puncte", True, (255, 255, 255))
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, 100 + i * 40))

    pygame.display.update()
    time.sleep(5)  # Afișează lista timp de 5 secunde


def display_end_screen(screen, message, player_name, score):
    font = pygame.font.Font(None, 36)
    screen.fill((0, 0, 0))

    # Mesaj de final
    end_message = font.render(message, True, (255, 255, 255))
    screen.blit(end_message, (screen_width // 2 - end_message.get_width() // 2, screen_height // 2 - 100))

    # Scorul final
    score_message = font.render(f"Scor final: {score} puncte", True, (255, 255, 255))
    screen.blit(score_message, (screen_width // 2 - score_message.get_width() // 2, screen_height // 2 - 50))

    # Butoanele Quit și Replay
    button_width, button_height = 200, 50
    button_margin = 20
    quit_button = pygame.Rect(screen_width // 2 - button_width - button_margin, screen_height // 2 + 50, button_width, button_height)
    replay_button = pygame.Rect(screen_width // 2 + button_margin, screen_height // 2 + 50, button_width, button_height)

    pygame.draw.rect(screen, (255, 0, 0), quit_button)  # Buton roșu pentru Quit
    pygame.draw.rect(screen, (0, 255, 0), replay_button)  # Buton verde pentru Replay

    quit_text = font.render("Quit", True, (255, 255, 255))
    replay_text = font.render("Replay", True, (255, 255, 255))

    screen.blit(quit_text, (quit_button.x + (button_width - quit_text.get_width()) // 2, quit_button.y + (button_height - quit_text.get_height()) // 2))
    screen.blit(replay_text, (replay_button.x + (button_width - replay_text.get_width()) // 2, replay_button.y + (button_height - replay_text.get_height()) // 2))

    pygame.display.update()

    return quit_button, replay_button


def main():
    global player_scores

    # Obține numele jucătorului
    player_name = get_player_name(screen)

    # Alegem dificultatea
    time_limit = select_difficulty(screen)

    # Inițializăm jocul
    game = MemoryGame(rows=4, columns=4, sound_enabled=True, music_enabled=True)

    # Pre-fetching imagini de la API (cu ecran de loading)
    game.fetch_images(8, screen)

    # Începem timer-ul
    start_time = time.time()

    # Loop-ul principal al jocului
    running = True
    while running:
        elapsed_time = time.time() - start_time

        # Verificăm dacă timpul a expirat
        if elapsed_time >= time_limit:
            game.score = 0  # Setăm scorul la 0 când timpul a expirat
            print("Timpul a expirat! Scorul este 0.")
            screen.fill((0, 0, 0))  # Curățăm ecranul

            # Afișăm mesajul de expirare a timpului și scorul final
            font = pygame.font.Font(None, 36)
            timer_text = font.render("Timpul a expirat!", True, (255, 255, 255))
            score_text = font.render(f"Scor final: {game.score}", True, (255, 255, 255))

            screen.blit(timer_text, (screen_width // 2 - timer_text.get_width() // 2, screen_height // 2 - 50))
            screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2))

            pygame.display.update()
            time.sleep(3)  # Pauză pentru a afișa mesajul
            running = False
            continue

        screen.fill((0, 0, 0))  # Setează fundalul la negru

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

        # Verificăm pentru potriviri
        game.check_for_match()

        # Verificăm dacă s-a câștigat jocul
        if game.check_win():
            game.calculate_final_score()
            print(f"Felicitări! Ai câștigat cu {game.score} puncte!")
            running = False

        # Afișăm imaginile pe ecran
        for image in game.memory_images:
            image.display(screen)

        game.calculate_final_score()
        game.display_score(screen)

        # Afișăm timpul rămas pe ecran
        remaining_time = max(0, int(time_limit - elapsed_time))
        font = pygame.font.Font(None, 36)
        timer_text = font.render(f"Timp rămas: {remaining_time} secunde", True, (255, 255, 255))
        screen.blit(timer_text, (10, 10))

        pygame.display.update()

    # Salvăm scorul jucătorului în lista globală
    player_scores.append((player_name, game.score))
    player_scores = sorted(player_scores, key=lambda x: x[1], reverse=True)[:5]

    # Afișăm scorurile top 5
    display_top_scores(screen, player_scores)

    # Afișăm ecranul final
    quit_button, replay_button = display_end_screen(screen, "Jocul s-a terminat!", player_name, game.score)

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif replay_button.collidepoint(event.pos):
                    waiting_for_input = False  # Ieșim din bucla de așteptare și rejucăm


if __name__ == "__main__":
    main()
