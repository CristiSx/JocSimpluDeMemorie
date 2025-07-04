import pygame
import requests
from io import BytesIO
import random
import time
from threading import Timer

class MemoryImage:
    def __init__(self, image_name, id, rect=None):
        self.id = id  # ID unic pentru fiecare imagine
        self.image_name = image_name  # Numele imaginii (fără extensie)
        self.url = image_name  # URL-ul imaginii complet
        self.image = self.load_image_from_url(self.url)  # Încarcă imaginea
        self.rect = rect  # Rectangular care va reprezenta locația imaginii pe ecran
        self.revealed = False  # Inițial imaginea nu este revelată

    def load_image_from_url(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = pygame.image.load(img_data)
                img = pygame.transform.scale(img, (128, 128))  # Setează dimensiunea imaginii
                return img
            else:
                print(f"Error loading image from {url}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def display(self, surface):
        if self.image:  # Verificăm dacă imaginea este validă
            if self.revealed:
                surface.blit(self.image, self.rect)  # Afișează imaginea pe ecran
            else:
                pygame.draw.rect(surface, (255, 255, 255), (self.rect.x, self.rect.y, 128, 128))  # Desenează un dreptunghi alb dacă imaginea nu este revelată
        else:
            print(f"Image {self.image_name} is invalid.")

    def reveal(self):
        self.revealed = True  # Setează imaginea ca fiind vizibilă

    def hide(self):
        self.revealed = False  # Ascunde imaginea


class MemoryGame:
    def __init__(self, rows, columns, sound_enabled=True, music_enabled=True):
        self.rows = rows
        self.columns = columns
        self.memory_images = []
        self.hidden_images = []
        self.selection1 = None
        self.selection2 = None
        self.waiting = False
        self.time_waited = 0
        self.wait_time = 1000  # 1 secundă de așteptare
        self.score = 100
        self.total_clicks = 0
        self.min_clicks = rows * columns

        # Setări pentru muzică și sunet
        self.sound_enabled = sound_enabled
        self.music_enabled = music_enabled

        if self.music_enabled:
            pygame.mixer.music.load("miaw miaw miaw song sad lyrics video visual.mp3")
            pygame.mixer.music.play(-1)

        self.correct_sound = (
            pygame.mixer.Sound("correct_sound.mp3") if self.sound_enabled else None
        )
        self.wrong_sound = (
            pygame.mixer.Sound("correct_sound.mp3") if self.sound_enabled else None
        )

        self.left_margin = (840 - ((128 + 10) * self.columns)) // 2
        self.top_margin = (640 - ((128 + 10) * self.rows)) // 2

    def display_loading_screen(self, screen):
        """Afișează un ecran de încărcare."""
        screen.fill((0, 0, 0))  # Fundal negru
        font = pygame.font.Font(None, 36)
        text = font.render("Se încarcă imagini...", True, (255, 255, 255))
        text_rect = text.get_rect(center=(840 // 2, 640 // 2))  # Centrat pe ecran
        screen.blit(text, text_rect)
        pygame.display.update()

    def fetch_images(self, num_images, screen):
        """Încarcă imaginile și afișează un ecran de încărcare."""
        image_urls = []
        while len(image_urls) < num_images:  # Continuăm să încercăm până avem suficiente imagini
            try:
                response = requests.get("https://api.thecatapi.com/v1/images/search")
                if response.status_code == 200:
                    image_data = response.json()[0]
                    image_urls.append(image_data["url"])
                else:
                    print("Failed to fetch image. Retrying...")
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
            self.display_loading_screen(screen)  # Actualizăm ecranul de încărcare
            time.sleep(0.5)  # Pauză scurtă între încercări

        self.setup_game(image_urls)

    def setup_game(self, image_urls):
        memory_pictures = image_urls + image_urls  # Creăm 2 copii ale aceleași imagini
        random.shuffle(memory_pictures)

        for i, image_url in enumerate(memory_pictures):
            x = self.left_margin + ((128 + 10) * (i % self.columns))
            y = self.top_margin + ((128 + 10) * (i // self.columns))
            rect = pygame.Rect(x, y, 128, 128)
            memory_image = MemoryImage(image_url, i, rect)
            self.memory_images.append(memory_image)
            self.hidden_images.append(False)

    def handle_click(self, event_pos):
        if self.waiting:  # Dacă suntem în perioada de așteptare, nu permitem un nou click
            return

        for item in self.memory_images:
            if item.rect.collidepoint(event_pos) and not item.revealed:
                if self.selection1 is None:  # Dacă nu am selectat încă o imagine
                    self.selection1 = item
                    item.reveal()
                elif self.selection2 is None:  # Dacă am selectat deja o imagine
                    self.selection2 = item
                    item.reveal()
                    self.waiting = True  # Începem perioada de așteptare
                    self.start_time = pygame.time.get_ticks()
    def check_for_match(self):
        if self.selection1 and self.selection2:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            if elapsed_time >= self.wait_time:  # Dacă a trecut 1 secundă
                self.total_clicks += 1  # Incrementăm numărul de încercări
                if self.selection1.image_name == self.selection2.image_name:
                    self.score += 10
                    if self.correct_sound:
                        self.correct_sound.play()
                    self.selection1, self.selection2 = None, None
                    self.waiting = False
                else:
                    if self.wrong_sound:
                        self.wrong_sound.play()
                    self.selection1.hide()
                    self.selection2.hide()
                    self.selection1, self.selection2 = None, None
                    self.waiting = False

    def calculate_final_score(self):
        if self.total_clicks <= self.min_clicks:
            self.score = 100
        else:
            penalty = (self.total_clicks - self.min_clicks)
            self.score = max(0, 100 - penalty)

    def check_win(self):
        return all(image.revealed for image in self.memory_images)

    def start_timer(self, time_limit, on_timeout):
        """Pornește un timer pentru joc."""
        self.timer_end_time = pygame.time.get_ticks() + time_limit * 1000
        self.on_timeout = on_timeout

    def update_timer(self):
        """Actualizează timer-ul și verifică dacă timpul a expirat."""
        if pygame.time.get_ticks() >= self.timer_end_time:
            self.on_timeout()

    def display_timer(self, surface):
        """Afișează timpul rămas pe ecran."""
        remaining_time = max(0, (self.timer_end_time - pygame.time.get_ticks()) // 1000)
        font = pygame.font.Font(None, 36)
        timer_text = font.render(f"Timp rămas: {remaining_time} secunde", True, (255, 255, 255))
        surface.blit(timer_text, (10, 10))

    def display_score(self, screen):
        """Afișează scorul în colțul din dreapta sus."""
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Scor: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (screen.get_width() - 150, 10))
