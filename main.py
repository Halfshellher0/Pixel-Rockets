import pygame
import os

# Global Variables
window_Width, window_Height = 900, 500
window_Width, window_Height = 2560, 1440 #Full Screen
fps = 144
window = pygame.display.set_mode((window_Width, window_Height))
pygame.display.set_caption("Pixel Rockets")
baseDir = os.path.dirname(__file__)

# Game Image Assets
# rocket_Images[0] = no thrust,
# rocket_Images[1] = low thrust, 
# rocket_Images[2] = high thrust
blue_Rocket_Images = [pygame.image.load(os.path.join(baseDir, 'Assets', 'Blue Rocket.png')),
    pygame.image.load(os.path.join(baseDir, 'Assets', 'Blue Rocket_Small Flame.png')),
    pygame.image.load(os.path.join(baseDir, 'Assets', 'Blue Rocket_Big Flame.png'))]

red_Rocket_Images = [pygame.image.load(os.path.join(baseDir, 'Assets', 'Red Rocket.png')),
    pygame.image.load(os.path.join(baseDir, 'Assets', 'Red Rocket_Small Flame.png')),
    pygame.image.load(os.path.join(baseDir, 'Assets', 'Red Rocket_Big Flame.png'))]

# Game Colors
white = (255, 255, 255)
black = (0, 0, 0)

def draw_window():
    window.fill(black)
    draw_rockets()
    pygame.display.update()

def draw_rockets():
    window.blit(blue_Rocket_Images[1], (200, 200))


def main():
    print(os.path.join(baseDir, 'Assets', 'Blue Rocket.png'))
    

    clock = pygame.time.Clock()
    run = True
    while run:
        # Main game loop.
        clock.tick(fps)      
        # Check any events that are present.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()

        draw_window()

if __name__ == "__main__":
    main()