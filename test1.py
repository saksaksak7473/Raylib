from pyray import *
from raylib import *
import time
import random

WIDTH, HEIGHT = 1440, 900

init_window(WIDTH, HEIGHT, 'pyray')

class Player:
    def __init__(self, x, y, w, h, color = WHITE):
        self.pos = Vector2(x, y)
        self.dir = Vector2(0, 0)
        self.speed = 500
        self.w = w
        self.h = h
        self.color = color
        
    def RandColor(self):
        self.color = random.choice([WHITE, PURPLE, BLUE, RED, PINK, ORANGE, GREEN])

    def draw(self):
        draw_rectangle_v(self.pos, Vector2(self.w, self.h), self.color)
        
    def update(self, dt):
        
        self.dir.x = int(IsKeyDown(KEY_D)) - int(IsKeyDown(KEY_A))
        self.dir.y = int(IsKeyDown(KEY_S)) - int(IsKeyDown(KEY_W))
        
        self.pos.x += self.dir.x * self.speed * dt
        self.pos.y += self.dir.y * self.speed * dt
        
class Wall:
    def __init__(self, x, y, w, h, color):
        self.pos = Vector2(x, y)
        self.w = w
        self.h = h
        self.color = color
    
    def draw(self):
        draw_rectangle_v(self.pos, Vector2(self.w, self.h), self.color)
        
class Collision:
    def __init__(self, player, walls):
        self.player = player
        self.walls = walls
    
    def update(self):
        player_rec = Rectangle(self.player.pos.x, self.player.pos.y, self.player.w, self.player.h)
        for wall in self.walls:
            wall_rec = Rectangle(wall.pos.x, wall.pos.y, wall.w, wall.h)
            if check_collision_recs(player_rec, wall_rec):
                if min(self.player.pos.x + self.player.w, wall.pos.x + wall.w) - max(self.player.pos.x, wall.pos.x) < min(self.player.pos.y + self.player.h, wall.pos.y + wall.h,) - max(self.player.pos.y, wall.pos.y): # Hit from left or right
                    self.player.dir.x = 0
                    if self.player.pos.x < wall.pos.x: # hit from the left
                        self.player.pos.x = wall.pos.x - self.player.w
                    else: # hit from the right
                        self.player.pos.x = wall.pos.x + wall.w
                else: # hit from the top or bottom
                    self.player.dir.y = 0
                    if self.player.pos.y < wall.pos.y: # hit from the top
                        self.player.pos.y = wall.pos.y - self.player.h
                    else: # hit from the bottom
                        self.player.pos.y = wall.pos.y + wall.h
                        
                rand_color.update()
        
class Timer:
    def __init__(self, duration: int, autostart = False, repeat = False, function = None):
        self.duration = duration
        self.active = False
        self.repeat = repeat
        self.function = function
        self.start = 0
        
        if autostart:
            self.activate()
            
    def activate(self):
        self.active = True
        self.start = GetTime()
        
    def deactivate(self):
        self.active = 0
        self.start = 0
        
        if self.repeat:
            self.activate()
        
    def update(self):
        if self.active:
            if GetTime() - self.start >= self.duration:
                self.function()
                self.deactivate()

player = Player(0, 0, 50, 50)
walls = [
    Wall(100, 100, 50, 200, WHITE),
    Wall(150, 100, 400, 50, WHITE)
]
collision = Collision(player, walls)

camera = Camera2D()
camera.zoom = 1 
camera.offset = Vector2(WIDTH / 2 - player.w, HEIGHT / 2 - player.h)

rand_color = Timer(0.3, True, True, player.RandColor)

SetTargetFPS(45)

while not window_should_close():
    # Update
    dt = get_frame_time()
    player.update(dt)
    collision.update()
    
    # Camera
    camera.target = player.pos
    camera.offset = Vector2(WIDTH / 2 - player.w, HEIGHT / 2 - player.h)

    # Drawing
    begin_drawing()
    clear_background(BLACK)
    begin_mode_2d(camera)
    for wall in walls:
        wall.draw()
    player.draw()
    end_mode_2d()
    end_drawing()
    
close_window()