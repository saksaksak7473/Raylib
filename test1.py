from pyray import *
from raylib import *
import math

WIDTH, HEIGHT = 2560, 1600

init_window(WIDTH, HEIGHT, 'pyray')

class Player:
    def __init__(self, x, y, w, h, color):
        self.pos = Vector2(x, y)
        self.dir = Vector2(0, 0)
        self.speed = 250
        self.w = w
        self.h = h
        self.color = color
        self.angle = 0.0

    def draw(self):
        DrawRectangleV(self.pos, Vector2(self.w, self.h), self.color)
        
    def update(self, dt):
        boost = 1
        self.dir.x = int(IsKeyDown(KEY_D)) - int(IsKeyDown(KEY_A))
        self.dir.y = int(IsKeyDown(KEY_S)) - int(IsKeyDown(KEY_W))
        if IsKeyDown(KEY_LEFT_SHIFT): boost = 2
        
        self.pos.x += self.dir.x * self.speed * boost * dt
        self.pos.y += self.dir.y * self.speed * boost * dt
        
class Wall:
    def __init__(self, x, y, w, h, color):
        self.pos = Vector2(x, y)
        self.w = w
        self.h = h
        self.color = color
    
    def draw(self):
        DrawRectangleV(self.pos, Vector2(self.w, self.h), self.color)
        
class Collision:
    def __init__(self, player, walls, bullets):
        self.player = player
        self.walls = walls
        self.bullets = bullets
    
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
                        
            for bullet in self.bullets:
                bullet_rec = Rectangle(bullet.pos.x - bullet.r, bullet.pos.y - bullet.r, bullet.r * 2, bullet.r * 2)
                if check_collision_recs(bullet_rec, wall_rec):
                    self.bullets.remove(bullet)
        
class Timer:
    def __init__(self, duration: int, autostart = False, repeat = False):
        self.duration = duration
        self.active = False
        self.repeat = repeat
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
            if self.active and GetTime() - self.start >= self.duration:
                self.deactivate()
                
class Bullet:
    def __init__(self, pos, velocity):
        self.pos = pos
        self.r = 10
        self.color = WHITE
        self.vel = velocity
    
    def draw(self):
        DrawCircleV(self.pos, self.r, self.color)

    def update(self, dt):
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt
            
player = Player(0, 0, 100, 100, WHITE)
bullets = []
shoot_timer = Timer(0.25)
walls = [
    Wall(100, 100, 100,400, WHITE),
    Wall(200, 100, 1000, 100, WHITE)
]
collision = Collision(player, walls, bullets)

camera = Camera2D()
camera.zoom = 1 
camera.offset = Vector2(WIDTH / 2, HEIGHT / 2)

set_target_fps(45)

while not window_should_close():
    # Update
    dt = get_frame_time()

    if IsKeyPressed(KEY_F11):
        toggle_fullscreen()

    player.update(dt)
    collision.update()
    shoot_timer.update()

    if IsMouseButtonDown(MOUSE_BUTTON_LEFT) and not shoot_timer.active:
        shoot_timer.activate()

        mouse_world = GetScreenToWorld2D(GetMousePosition(), camera)
        bullet_pos = Vector2(player.pos.x + player.w * 0.5, player.pos.y + player.h * 0.5)
        dx = mouse_world.x - bullet_pos.x
        dy = mouse_world.y - bullet_pos.y
        distance = math.hypot(dx, dy)

        if distance != 0:
            bullet_velocity = Vector2(dx / distance * 1000, dy / distance * 1000)
            bullets.append(Bullet(bullet_pos, bullet_velocity))

    for bullet in bullets:
        bullet.update(dt)
    
    # Camera
    camera.offset = Vector2(get_screen_width() / 2, get_screen_height() / 2)
    player_center = Vector2(player.pos.x + player.w / 2, player.pos.y + player.h / 2)
    current_target = player_center

    if IsMouseButtonDown(MOUSE_BUTTON_RIGHT):
        mouse = GetScreenToWorld2D(GetMousePosition(), camera)
        current_target = Vector2(
            (player_center.x + mouse.x) / 2,
            (player_center.y + mouse.y) / 2
        )

    smooth = min(1.0, 5.0 * dt)
    camera.target.x += (current_target.x - camera.target.x) * smooth
    camera.target.y += (current_target.y - camera.target.y) * smooth

    # Drawing
    begin_drawing()
    clear_background(BLACK)
    begin_mode_2d(camera)
    for bullet in bullets:
        bullet.draw()
    for wall in walls:
        wall.draw()
    player.draw()
    end_mode_2d()
    draw_text(
        f"FPS: {get_fps()}",
        20,
        20,
        50,
        GREEN
    )
    end_drawing()
    
close_window()