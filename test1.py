from pyray import *
from raylib import *
import math
import random

WIDTH, HEIGHT = 1440, 900

init_window(WIDTH, HEIGHT, 'pyray')

class Player:
    def __init__(self, x, y, w, h, color):
        self.pos = Vector2(x, y)
        self.dir = Vector2(0, 0)
        self.speed = 500
        self.w = w
        self.h = h
        self.color = color
        self.angle = 0.0

    def draw(self):
        DrawRectangleV(self.pos, Vector2(self.w, self.h), self.color)
        
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
        DrawRectangleV(self.pos, Vector2(self.w, self.h), self.color)
        
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
                
class Bullet:
    def __init__(self, x, y, r, color):
        self.pos = Vector2(x, y)
        self.r = r
        self.color = color
        self.speed = 1000
        self.vel = Vector2(0, 0)
        self.isShoot = False
    
    def draw(self):
        DrawCircleV(self.pos, self.r, self.color)

    def update(self, dt):
        # Convert mouse to world coordinates so shooting aims where the cursor is in the world
        mouse_screen = GetMousePosition()
        mouse_world = GetScreenToWorld2D(mouse_screen, camera)

        # On mouse press, spawn/reset bullet at player's center and compute a fixed velocity
        if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
            # place bullet at player's center (adjust if player.pos represents top-left or center)
            self.pos.x = player.pos.x + player.w * 0.5
            self.pos.y = player.pos.y + player.h * 0.5

            dx = mouse_world.x - self.pos.x
            dy = mouse_world.y - self.pos.y
            dist = math.hypot(dx, dy)
            if dist != 0:
                nx = dx / dist
                ny = dy / dist
            else:
                nx, ny = 1.0, 0.0

            self.vel.x = nx * self.speed
            self.vel.y = ny * self.speed
            self.isShoot = True

        # Move along the fixed velocity — direction NOT recomputed each frame
        if self.isShoot:
            self.pos.x += self.vel.x * dt
            self.pos.y += self.vel.y * dt

            # Optional: stop bullet when it goes far off-screen (simple lifetime)
            if (abs(self.pos.x - camera.target.x) > WIDTH * 2) or (abs(self.pos.y - camera.target.y) > HEIGHT * 2):
                self.isShoot = False
                self.vel = Vector2(0, 0)

player = Player(0, 0, 50, 50, WHITE)
bullet = Bullet(player.pos.x + player.w / 2, player.pos.y + player.h / 2, 5.0, WHITE)
walls = [
    Wall(100, 100, 50, 200, WHITE),
    Wall(150, 100, 400, 50, WHITE)
]
collision = Collision(player, walls)

camera = Camera2D()
camera.zoom = 1 
camera.offset = Vector2(WIDTH / 2, HEIGHT / 2)

timer = Timer(1, True, True, bullet.draw())

SetTargetFPS(45)

while not window_should_close():
    # Update
    dt = get_frame_time()
    player.update(dt)
    collision.update()
    bullet.update(dt)
    
    # Camera
    camera.target = player.pos
    camera.offset = Vector2(WIDTH / 2, HEIGHT / 2)

    # Drawing
    begin_drawing()
    clear_background(BLACK)
    begin_mode_2d(camera)
    bullet.draw()
    for wall in walls:
        wall.draw()
    player.draw()
    end_mode_2d()
    end_drawing()
    
close_window()