import pygame
import os
import math

# Global Variables
window_Width, window_Height = 2000, 1000
#window_Width, window_Height = 2560, 1440 #Full Screen
fps = 144
window = pygame.display.set_mode((window_Width, window_Height))
pygame.display.set_caption("Pixel Rockets")
baseDir = os.path.dirname(__file__)
screen_Wrapping = False

# Physics Variables
rocket_Rotation_Speed = 0.4
rocket_Weight = 1000 #kg
rocket_Thrust1_Force = 1 #N
rocket_Thrust2_Force = 2 #N
distance_Coordinates = 1 #m (one pixel in game coordinates = 1m)
time_Conversion = 1 #ticks per second (one iteration of the game loop = one second in the physics simulation)

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
green = (0, 255, 0)

# Game Classes
class Rocket:
    def __init__(self, angle, position, color):
        # Variable Init parameters
        self.angle = angle
        self.position = position
        self.color = color

        # Initialize rockets with fixed parameters.
        self.velocityX = 0
        self.velocityY = 0
        self.mass = rocket_Weight        
        self.thrust = 0
        

# Dynamic Game Data
rockets = []

def handle_rocket_movement(keys_pressed, rocket):
    if keys_pressed [pygame.K_LEFT]: # LEFT
        rocket.angle += rocket_Rotation_Speed
    if keys_pressed [pygame.K_RIGHT]: # RIGHT
        rocket.angle -= rocket_Rotation_Speed

    print(rocket.angle)

    # Set acceleration to zero, unless there is active thrust.
    accelerationX, accelerationY = 0, 0

    # If the rocket's thrusters are active.
    if rocket.thrust > 0:
        rocket_Propulsion_Force = 0
        if rocket.thrust == 1:
            rocket_Propulsion_Force = rocket_Thrust1_Force
        elif rocket.thrust == 2:
            rocket_Propulsion_Force = rocket_Thrust2_Force
        
        # Calculate acceleration magnitude
        acceleration = rocket_Propulsion_Force / rocket.mass #m/s^2
        
        # Break down acceleration into X and Y
        angle = rocket.angle #* -1 # angle is flipped for trig calcs
        accelerationX = math.sin(math.radians(angle)) * acceleration
        accelerationY = math.cos(math.radians(angle)) * acceleration

    # Adjust rocket velocity (for one game tick)
    rocket.velocityX = (rocket.velocityX - accelerationX) / time_Conversion
    rocket.velocityY = (rocket.velocityY - accelerationY) / time_Conversion

    # Adjust the position of the rocket based on the velocity.
    rocket.position = (rocket.position[0] + (rocket.velocityX / distance_Coordinates), rocket.position[1] + (rocket.velocityY / distance_Coordinates))

    # Simple Screen Wrapping
    if screen_Wrapping:
        if rocket.position[0] < 0:
            rocket.position = (rocket.position[0] + window_Width, rocket.position[1])
        elif rocket.position[0] > window_Width:
            rocket.position = (rocket.position[0] - window_Width, rocket.position[1])

        if rocket.position[1] < 0:
            rocket.position = (rocket.position[0], rocket.position[1] + window_Height)
        elif rocket.position[1] > window_Height:
            rocket.position = (rocket.position[0], rocket.position[1] - window_Height)
        

def blit_rotate(image, pos, angle):
    imgSizeX, imgSizeY = image.get_size()
    image_rect = image.get_rect(topleft = (pos[0] - imgSizeX / 2, pos[1] - imgSizeY / 2))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    window.blit(rotated_image, rotated_image_rect)

    # draw rectangle around the image
    # pygame.draw.rect(window, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)


# Draw Functions
def draw_window():
    window.fill(black)
    draw_rockets()
    pygame.display.update()

def draw_rockets():
    for rocket in rockets:
        if rocket.color == 'blue':
            blit_rotate(blue_Rocket_Images[rocket.thrust], rocket.position, rocket.angle)
            # window.blit(pygame.transform.rotate(
            #     blue_Rocket_Images[rocket.thrust], rocket.angle), 
            #     rocket.position)

        elif rocket.color == 'red':
            blit_rotate(red_Rocket_Images[rocket.thrust], rocket.position, rocket.angle)
            # window.blit(pygame.transform.rotate(
            #     red_Rocket_Images[rocket.thrust], rocket.angle), 
            #     rocket.position)
        
        # Debug
        # Draw a circle on the rockets real position point
        pygame.draw.circle(window, green, rocket.position, 2)

def main():
    rockets.append(Rocket(0, (300.0, 300.0), 'red'))
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
                if event.key == pygame.K_UP:                    
                    # Adjust thrust level
                    if rockets[0].thrust < 2:
                        rockets[0].thrust += 1
                if event.key == pygame.K_DOWN:
                    # Adjust thrust level
                    if rockets[0].thrust > 0:
                        rockets[0].thrust -= 1

        keys_pressed = pygame.key.get_pressed()
        handle_rocket_movement(keys_pressed, rockets[0])

        draw_window()

if __name__ == "__main__":
    main()