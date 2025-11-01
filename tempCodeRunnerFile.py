import pygame
import sys
print("it is running")
print(sys.executable)
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test Window")
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 128, 255))
    pygame.display.flip()

pygame.quit()