from pyray import *
from raylib import *

init_window(1440, 900, 'pyray')

class Player:
    def __init__(self, x, y, w, h, color):
        self.pos = Vector2(x, y)
        self.dir = Vector2(1, 0)
        self.speed = 1000
        self.w = w
        self.h = h
        self.color = color 

    def draw(self):
        draw_rectangle_v(self.pos, Vector2(self.w, self.h), self.color)
        
    def update(self):
        dt = get_frame_time()
        
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
        
player = Player(0, 0, 50, 50, WHITE)
walls = [
    Wall(100, 100, 50, 200, WHITE),
    Wall(150, 100, 400, 50, WHITE)
]
    
while not window_should_close():
    begin_drawing()
    # Update
    player.update()
    
    # Drawing
    clear_background(BLACK)
    for wall in walls:
        wall.draw()
    player.draw()
    
    end_drawing()
    
close_window()