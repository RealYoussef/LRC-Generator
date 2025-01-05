import pygame
import sys
import time
import os

os.environ["SDL_VIDEODRIVER"] = "windib"

def animated_splash(duration=5):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(BASE_DIR, "Logo5.png")

    pygame.init()
    screen = pygame.display.set_mode((700, 600))
    pygame.display.set_caption("Loading...")
    clock = pygame.time.Clock()

    logo = pygame.image.load(logo_path)
    logo = pygame.transform.scale(logo, (500, 500))

    gradient_direction = 1
    alpha = 128
    start_time = time.time()

    while time.time() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill((0, 0, 0))
        alpha += gradient_direction * 1
        if alpha >= 255:
            gradient_direction = -1
        elif alpha <= 128:
            gradient_direction = 1

        overlay = logo.copy()
        overlay.set_alpha(alpha)
        screen.blit(overlay, ((700 - 500) // 2, (600 - 500) // 2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    animated_splash()
