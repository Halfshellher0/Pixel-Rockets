import pygame
import os
import math
import random
import neat

# Global Variables
window_Width, window_Height = 2000, 1000
#window_Width, window_Height = 2560, 1440 #Full Screen
fps = 144
window = pygame.display.set_mode((window_Width, window_Height))
pygame.display.set_caption("Pixel Rockets")
baseDir = os.path.dirname(__file__)
screen_Wrapping = False
take_Off_Frames_Max = 100 # How many frames to pause collision detection after take off.
max_Simulation_Seconds = 15
max_Simulation_Frames = 2000
elapsed_Frames = 0
generation_Count = 0
starting_X, starting_Y = window_Width // 2, window_Height // 2


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
        self.bonus_Fitness = 2000

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

    def get_Angle_Of_Travel(self):
        if self.velocityX == 0 and self.velocityY == 0:
            return 0
        elif self.velocityX <=0 and self.velocityY <=0:
            return math.degrees(math.atan(self.velocityX / self.velocityY))
        elif self.velocityX <=0 and self.velocityY > 0:
            return math.degrees(math.atan(self.velocityX / self.velocityY)) + 180
        elif self.velocityX > 0 and self.velocityY > 0:
            return math.degrees(math.atan(self.velocityX / self.velocityY)) + 180
        else:
            return math.degrees(math.atan(self.velocityX / self.velocityY)) + 360

    def get_Speed(self):
        return math.sqrt((self.velocityX) ** 2 + (self.velocityY) ** 2)

    def get_Thrust(self):
        if self.thrust == 0:
            return 0
        elif self.thrust == 1:
            return rocket_Thrust1_Force
        else:
            return rocket_Thrust2_Force
        
        
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
                rocket_Angle = rocket.angle % 360
                travelling_Angle = rocket.get_Angle_Of_Travel()
                opposite_Angle = 0
                if angle_Asteroid >= 180:
                    opposite_Angle = angle_Asteroid - 180
                else:
                    opposite_Angle = angle_Asteroid + 180
                max_Angle = (opposite_Angle + 60) % 360
                min_Angle = (opposite_Angle - 60) % 360
                max_Angle_Travelling = (angle_Asteroid + 60) % 360
                min_Angle_Travelling = (angle_Asteroid - 60) % 360


                # Calculate relative velocity between objects.
                relative_Velocity = math.sqrt((self.velocityX - rocket.velocityX) ** 2 + (self.velocityY - rocket.velocityY) ** 2)    

                # Check whether the rocket is landing in the correct orientation.
                if check_Angle(rocket_Angle, max_Angle, min_Angle) and check_Angle(travelling_Angle, max_Angle_Travelling, min_Angle_Travelling):                      
                    if relative_Velocity < crash_Speed_Threshold:
                        # Rocket landed slowly enough to land.
                        global elapsed_Frames
                        rocket.thrust = 0
                        rocket.velocityX = 0
                        rocket.velocityY = 0
                        rocket.landed = True
                        x = rockets.index(rocket)  
                        ge[x].fitness = (max_Simulation_Frames - elapsed_Frames) + 14001 + rocket.bonus_Fitness
                        rockets.pop(x)
                        nets.pop(x)
                        ge.pop(x)   
                    else:
                        # Rocket crash landed on asteroid in the correct orientation.
                        # Rocket loses fitness for crashing at a faster speed. 
                        angle_Diff = abs(calculate_Angle_Difference(rocket_Angle, angle_Asteroid))
                        fitness_Points = angle_Diff * 11.11111 # will add up to 2000 fitness points for an angle that was very close to being correct.
                        x = rockets.index(rocket)
                        lost_Fitness = (relative_Velocity - crash_Speed_Threshold) * 1000
                        if lost_Fitness > 2000:
                            lost_Fitness = 2000
                        ge[x].fitness = (10001 - lost_Fitness) + rocket.bonus_Fitness + fitness_Points
                        rockets.pop(x)
                        nets.pop(x)
                        ge.pop(x)
                else:
                    # Rocket crash landed on asteroid, for not being in the correct orientation

                    # Check how close the rocket was to landing in the correct orientation
                    angle_Diff = abs(calculate_Angle_Difference(rocket_Angle, angle_Asteroid))
                    fitness_Points = angle_Diff * 11.11111 # will add up to 2000 fitness points for an angle that was very close to being correct.
                    x = rockets.index(rocket)  
                    ge[x].fitness = 4001 + fitness_Points + rocket.bonus_Fitness
                    rockets.pop(x)
                    nets.pop(x)
                    ge.pop(x)        
            
            

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

# Calculate a distance between a rocket and a destination object.    
def calculate_Distance(rocket, object):
    diffX = object.position[0] - rocket.position[0]
    diffY = object.position[1] - rocket.position[1]

    return math.sqrt((diffX) ** 2 + (diffY) ** 2)   

# Calculate difference between two angles
def calculate_Angle_Difference(angle1, angle2):
    if angle1 == angle2:
        return 0
    elif angle2 > angle1:
        diff1 = angle2 - angle1
        diff2 = ((angle1 + 360) - angle2) * -1
        if abs(diff1) >= abs(diff2):
            return diff2
        else:
            return diff1
    else:
        #angle1 > angle2
        diff1 = angle2 - angle1
        diff2 = (angle2 + 360) - angle1
        if abs(diff1) >= abs(diff2):
            return diff2
        else:
            return diff1


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
nets = []
ge = []

def handle_rocket_movement(rocket):

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

        if len(rockets) > 0:
            blit_rotate(blue_Rocket_Images[rockets[0].thrust], rockets[0].position, rockets[0].angle, rockets[0])
        
        # Debug
        # Draw a circle on the rockets real position point
        # pygame.draw.circle(window, green, rocket.position, 2)

def draw_asteroids():
    for asteroid in asteroids:
        blit_rotate(asteroid_Images[0], asteroid.position, asteroid.angle, asteroid)
        
        # Debug
        # Draw a circle on the rockets real position point
        #pygame.draw.circle(window, green, asteroid.position, 2)

def eval_Genomes(genomes, config):
    global elapsed_Frames    
    global generation_Count
    elapsed_Frames = 0
    print (generation_Count)
    if generation_Count % 100 == 0:
        if len(asteroids) > 0:
            asteroids.clear()
        generate_Asteroids(1)

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        if len(rockets) == 0:
            rockets.append(Rocket(0, (starting_X, starting_Y), 'blue'))     
        else:
            rockets.append(Rocket(0, (starting_X, starting_Y), 'red'))      
        genome.fitness = 0
        ge.append(genome)
  
    

    clock = pygame.time.Clock()
    run = True
    while run:
        # Main game loop.
        clock.tick()

        # Check any events that are present.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()

                # if len(rockets) > 0:
                #     if event.key == pygame.K_UP:
                #         rockets[0].increase_Thrust()
                #     if event.key == pygame.K_DOWN:
                #         rockets[0].decrease_Thrust()

        # if len(rockets) > 0:
        #     keys_pressed = pygame.key.get_pressed()
        #     handle_rocket_movement(keys_pressed, rockets[0])

        # Determine what each rocket is doing
        for x, rocket in enumerate(rockets):
            rocket_Facing_Angle = rocket.angle % 360            
            rocket_Traveling_Angle = rocket.get_Angle_Of_Travel()
            asteroid_Angle = calculate_Angle(rocket, asteroids[0])
            opposite_Asteroid_Angle = (asteroid_Angle + 180) % 360

            # Calculate Input neuron values
            input1 = calculate_Angle_Difference(rocket_Facing_Angle, asteroid_Angle)
            input2 = calculate_Angle_Difference(rocket_Facing_Angle, opposite_Asteroid_Angle)
            input3 = calculate_Angle_Difference(rocket_Traveling_Angle, asteroid_Angle)
            input4 = calculate_Angle_Difference(rocket_Traveling_Angle, opposite_Asteroid_Angle)
            input5 = calculate_Distance(rocket, asteroids[0])
            input6 = rocket.get_Speed()
            input7 = rocket.get_Thrust()

            #Debug
            if x == 0:
                i = 0
                pass

            output = nets[x].activate((input1, input2, input3, input4, input5, input6, input7))
            
            if output[0] < 0.5 and output[1] < 0.5:
                pass
            elif output[0] < output[1]:
                rocket.angle += rocket_Rotation_Speed
                if rocket.bonus_Fitness > 0:
                    rocket.bonus_Fitness -= 1
            else:
                rocket.angle -= rocket_Rotation_Speed
                if rocket.bonus_Fitness > 0:
                    rocket.bonus_Fitness -= 1
            # if output[0] < -0.999:
            #     # Rotate Rocket Left
            #     rocket.angle += rocket_Rotation_Speed
            # elif output[0] > 0.999:
            #     # Rotate Rocket Right
            #     rocket.angle -= rocket_Rotation_Speed

            if output[2] > output[3]:
                rocket.increase_Thrust()
            else:
                rocket.decrease_Thrust()

            # if rocket.thrust > 0:
            #     if output[1] > 0.95:
            #         rocket.increase_Thrust()
            # else:
            #     if output[1] < 0.98:
            #         rocket.decrease_Thrust()
            #     elif output[1] > 0.99:
            #         rocket.increase_Thrust()

            handle_rocket_movement(rocket)
        
        
        draw_window()

        # Check for collisions
        for asteroid in asteroids:
            for rocket in rockets:
                asteroid.collide(rocket)

        # Update things that are counting frames
        for rocket in rockets:
            if rocket.take_Off_Frames > 0:
                rocket.take_Off_Frames -= 1

        elapsed_Frames += 1
        
        # End of the simulation if time has elapsed or there is no rockets remaining.
        if elapsed_Frames >= max_Simulation_Frames or len(rockets) == 0:
            # The simulation has run for its maximum allowed time.
            run = False

            # Assign fitness for any rockets that did not touch the asteroid
            for rocket in rockets:
                x = rockets.index(rocket)
                if rocket.position[0] == starting_X and rocket.position[1] == starting_Y:
                    #Rocket did not move from its starting position, award it 0 fitness.
                    ge[x].fitness = 0
                else:
                    # Rocket did not come into contact with an asteroid, fitness is a function of how close it came, and how little it rotated.
                    # Possible fitness values: 0 - 4000
                    distance = calculate_Distance(rocket, asteroids[0])
                    if distance > 6000:
                        ge[x].fitness = rocket.bonus_Fitness
                    else:
                        ge[x].fitness = (2000 - distance / 3) + rocket.bonus_Fitness
                rockets.pop(x)
                nets.pop(x)
                ge.pop(x) 

    generation_Count += 1
    rockets.clear()
    #asteroids.clear()
    nets.clear()
    ge.clear()        



def run(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    # Report some details about the population to the console.
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(eval_Genomes, 100000)

if __name__ == "__main__":
    config_path = os.path.join(baseDir, "neat.config")
    run(config_path)