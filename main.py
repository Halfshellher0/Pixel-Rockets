import pygame
import os
import math
import random

# Global Variables
window_Width, window_Height = 2000, 1000
#window_Width, window_Height = 2560, 1440 #Full Screen
fps = 144
window = pygame.display.set_mode((window_Width, window_Height))
pygame.display.set_caption("Pixel Rockets")
baseDir = os.path.dirname(__file__)
screen_Wrapping = False
take_Off_Frames_Max = 100 # How many frames to pause collision detection after take off.

# Physics Variables
rocket_Rotation_Speed = 0.7
rocket_Weight = 1000 #kg
rocket_Thrust1_Force = 1 #N
rocket_Thrust2_Force = 2 #N
distance_Coordinates = 1 #m (one pixel in game coordinates = 1m)
time_Conversion = 1 #ticks per second (one iteration of the game loop = one second in the physics simulation)
asteroid_Weight = 100000 #kg
crash_Speed_Threshold = 0.2

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

asteroid_Images = [pygame.image.load(os.path.join(baseDir, 'Assets', 'Asteroid1.png'))]

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
        self.img = None        
        if color == 'red':
            self.img = red_Rocket_Images[0]
        elif color == 'blue':
            self.img = blue_Rocket_Images[0]
        self.rect = self.img.get_rect

        # Initialize rockets with fixed parameters.
        self.velocityX = 0
        self.velocityY = 0
        self.mass = rocket_Weight        
        self.thrust = 0
        self.landed = False
        self.take_Off_Frames = 0

    def increase_Thrust(self):
        if self.thrust == 0:
            if self.landed:
                self.landed = False
                self.take_Off_Frames = take_Off_Frames_Max
            self.thrust += 1
        elif self.thrust == 1:
            self.thrust += 1

    def decrease_Thrust(self):
        if self.thrust > 0:
            self.thrust -= 1
        
        
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Asteroid:
    def __init__(self, angle, position):
        # Variable Init parameters
        self.angle = angle
        self.position = position

        # Initialize rockets with fixed parameters.
        self.velocityX = 0
        self.velocityY = 0
        self.mass = asteroid_Weight
        self.img = asteroid_Images[0]
        self.rect = self.img.get_rect

    def collide(self, rocket):
        # Check that the rocket has not very recently taken off before collision check.
        if rocket.take_Off_Frames == 0:
            rocket_mask = rocket.get_mask()
            asteroid_mask = pygame.mask.from_surface(self.img)

            offset = (self.rect.x - rocket.rect.x, self.rect.y - rocket.rect.y)

            if rocket_mask.overlap(asteroid_mask, offset):
                # Rocket is in contact with the asteroid.
                # Ensure that the rocket is landing on its base
                angle_Asteroid = calculate_Angle(rocket, self)
                opposite_Angle = 0
                if angle_Asteroid >= 180:
                    opposite_Angle = angle_Asteroid - 180
                else:
                    opposite_Angle = angle_Asteroid + 180
                max_Angle = (opposite_Angle + 90) % 360
                min_Angle = (opposite_Angle - 90) % 360       

                # Check whether the rocket is landing in the correct orientation.
                if check_Angle(rocket.angle % 360, max_Angle, min_Angle):
                    # Calculate relative velocity between objects.
                    relative_Velocity = math.sqrt((self.velocityX - rocket.velocityX) ** 2 + (self.velocityY - rocket.velocityY) ** 2)      
                    if relative_Velocity < crash_Speed_Threshold:
                        # Rocket landed slowly enough to land.
                        rocket.thrust = 0
                        rocket.velocityX = 0
                        rocket.velocityY = 0
                        rocket.landed = True
                    else:
                        # Rocket crash landed on asteroid.     
                        rockets.pop(rockets.index(rocket))
                else:
                        # Rocket crash landed on asteroid.     
                        rockets.pop(rockets.index(rocket))            
            
            

# Calculate an angle between a rocket and a destination object.    
def calculate_Angle(rocket, object):
    diffX = object.position[0] - rocket.position[0]
    diffY = object.position[1] - rocket.position[1]
    angle = math.degrees(math.atan(diffX / diffY))

    # Determine the quadrant where the destination object lies, and add an offset to it.
    if diffX <= 0 and diffY <= 0:
        pass
    elif diffX <= 0 and diffY > 0:        
        angle += 180
    elif diffX > 0 and diffY >= 0:
        angle += 180
    elif diffX > 0 and diffY < 0:
        angle += 360
    
    return angle

# Function that checks whether an angle is within a given range (inclusive of range boundaries)
def check_Angle(angle, max_Angle, min_Angle):
    if angle == max_Angle or angle == min_Angle:
        return True
    elif min_Angle > max_Angle:
        # overlap is occuring
        if angle > min_Angle or angle < max_Angle:
           return True
        else:
            return False
    else:
        if angle > min_Angle and angle < max_Angle:
            return True
        else:
            return False


# Dynamic Game Data
rockets = []
asteroids = []

def handle_rocket_movement(keys_pressed, rocket):
    if rocket.landed == False:
        if keys_pressed [pygame.K_LEFT]: # LEFT
            rocket.angle += rocket_Rotation_Speed
        if keys_pressed [pygame.K_RIGHT]: # RIGHT
            rocket.angle -= rocket_Rotation_Speed    

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
        

# Rotate an object about its center point and draw it on the screen.
def blit_rotate(image, pos, angle, object):
    imgSizeX, imgSizeY = image.get_size()
    image_rect = image.get_rect(topleft = (pos[0] - imgSizeX / 2, pos[1] - imgSizeY / 2))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    object.img = rotated_image
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    object.rect = rotated_image_rect

    # rotate and blit the image
    window.blit(rotated_image, rotated_image_rect)

    # draw rectangle around the image
    #pygame.draw.rect(window, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)

def generate_Asteroids(number):
    for i in range(number):
        ranX = random.randrange(1,window_Width)
        ranY = random.randrange(1,window_Height)
        ranAngle = random.randrange(1,361)
        asteroids.append(Asteroid(ranAngle, (ranX, ranY)))

# Draw Functions
def draw_window():
    window.fill(black)
    draw_asteroids()
    draw_rockets()
    pygame.display.update()

def draw_rockets():
    for rocket in rockets:
        if rocket.color == 'blue':
            blit_rotate(blue_Rocket_Images[rocket.thrust], rocket.position, rocket.angle, rocket)
        elif rocket.color == 'red':
            blit_rotate(red_Rocket_Images[rocket.thrust], rocket.position, rocket.angle, rocket)
        
        # Debug
        # Draw a circle on the rockets real position point
        # pygame.draw.circle(window, green, rocket.position, 2)

def draw_asteroids():
    for asteroid in asteroids:
        blit_rotate(asteroid_Images[0], asteroid.position, asteroid.angle, asteroid)
        
        # Debug
        # Draw a circle on the rockets real position point
        #pygame.draw.circle(window, green, asteroid.position, 2)

def main():
    rockets.append(Rocket(0, (700.0, 400.0), 'red'))
    generate_Asteroids(1)

    # Debug
    for asteroid in asteroids:
        print(calculate_Angle(rockets[0], asteroid))

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
                if len(rockets) > 0:
                    if event.key == pygame.K_UP:
                        rockets[0].increase_Thrust()
                    if event.key == pygame.K_DOWN:
                        rockets[0].decrease_Thrust()

        if len(rockets) > 0:
            keys_pressed = pygame.key.get_pressed()
            handle_rocket_movement(keys_pressed, rockets[0])
        
        draw_window()

        # Check for collisions
        for asteroid in asteroids:
            for rocket in rockets:
                asteroid.collide(rocket)

        # Update things that are counting frames
        for rocket in rockets:
            if rocket.take_Off_Frames > 0:
                rocket.take_Off_Frames -= 1


if __name__ == "__main__":
    main()