from pyray import *
from raylib import *
import math
import random

WIDTH, HEIGHT = 2560, 1600

init_window(WIDTH, HEIGHT, 'pyray')

class Player:
    def __init__(self, x, y, w, h, color):
        self.hp = 100
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
        
class Enemy:
    def __init__(self):
        self.type = {
            "Fast": [50, 50, 750, 50, GREEN], # enemy_type = [w, h, speed, hp, color]
            "Slow": [150, 150, 100, 500, RED],
            "Normal": [100, 100, 200, 100, BLUE]
        }
        
        self.current_type = random.choice(["Fast", "Slow", "Normal"])
        self.current_enemy = self.type[self.current_type]

        enemy_width = self.current_enemy[0]
        enemy_height = self.current_enemy[1]
        edge = random.choice(["top", "right", "bottom", "left"])
        if edge == "top":
            self.current_pos = Vector2(random.uniform(0, WIDTH - enemy_width) + player.pos.x, - player.pos.y - enemy_height)
        elif edge == "right":
            self.current_pos = Vector2(WIDTH + player.pos.x, random.uniform(0, HEIGHT - enemy_height) + player.pos.y)
        elif edge == "bottom":
            self.current_pos = Vector2(random.uniform(0, WIDTH - enemy_width) + player.pos.x, HEIGHT + player.pos.y)
        else:
            self.current_pos = Vector2(- player.pos.x - enemy_width, random.uniform(0, HEIGHT - enemy_height) + player.pos.y)
    
    def draw(self):
        DrawRectangleV(self.current_pos, Vector2(self.current_enemy[0], self.current_enemy[1]), self.current_enemy[4])
        draw_text(
            f"HP: {self.current_enemy[3]}",
            int(self.current_pos.x),
            int(self.current_pos.y - 25),
            20,
            WHITE
        )
        
    def update(self, dt):
        center_self = Vector2(self.current_pos.x + self.current_enemy[0] / 2, self.current_pos.y + self.current_enemy[1] / 2)
        target = Vector2(player.pos.x + player.w / 2, player.pos.y + player.h / 2)
        dx = target.x - center_self.x
        dy = target.y - center_self.y
        distance = math.hypot(dx, dy)

        direction_x = dx / distance
        direction_y = dy / distance
        
        speed = self.current_enemy[2]
        self.current_pos.x += direction_x * speed * dt
        self.current_pos.y += direction_y * speed * dt
     
class Wall:
    def __init__(self, x, y, w, h, color):
        self.pos = Vector2(x, y)
        self.w = w
        self.h = h
        self.color = color
    
    def draw(self):
        DrawRectangleV(self.pos, Vector2(self.w, self.h), self.color)
        
class Collision:
    def __init__(self, player, walls, bullets, enemies):
        self.player = player
        self.walls = walls
        self.bullets = bullets
        self.enemies = enemies
    
    def update(self):
        player_rec = Rectangle(self.player.pos.x, self.player.pos.y, self.player.w, self.player.h)

        for enemy in self.enemies.copy():
            enemy_rec = Rectangle(
                enemy.current_pos.x,
                enemy.current_pos.y,
                enemy.current_enemy[0],
                enemy.current_enemy[1]
            )
            if check_collision_recs(enemy_rec, player_rec):
                self.player.hp -= 10
                self.enemies.remove(enemy)

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

            for enemy in self.enemies:
                enemy_rec = Rectangle(
                    enemy.current_pos.x,
                    enemy.current_pos.y,
                    enemy.current_enemy[0],
                    enemy.current_enemy[1]
                )
                if check_collision_recs(enemy_rec, wall_rec): # The same as Player collide Walls
                    if min(enemy_rec.x + enemy_rec.width, wall_rec.x + wall_rec.width) - max(enemy_rec.x, wall_rec.x) < min(enemy_rec.y + enemy_rec.height, wall_rec.y + wall_rec.height) - max(enemy_rec.y, wall_rec.y):
                        if enemy.current_pos.x < wall.pos.x:
                            enemy.current_pos.x = wall.pos.x - enemy.current_enemy[0]
                        else:
                            enemy.current_pos.x = wall.pos.x + wall.w
                    else:
                        if enemy.current_pos.y < wall.pos.y:
                            enemy.current_pos.y = wall.pos.y - enemy.current_enemy[1]
                        else:
                            enemy.current_pos.y = wall.pos.y + wall.h
                        
            for bullet in self.bullets.copy():
                bullet_rec = Rectangle(bullet.pos.x - bullet.r, bullet.pos.y - bullet.r, bullet.r * 2, bullet.r * 2)
                if check_collision_recs(bullet_rec, wall_rec):
                    self.bullets.remove(bullet)

        for bullet in self.bullets.copy():
            bullet_rec = Rectangle(
                bullet.pos.x - bullet.r,
                bullet.pos.y - bullet.r,
                bullet.r * 2,
                bullet.r * 2
            )
            for enemy in self.enemies.copy():
                enemy_rec = Rectangle(
                    enemy.current_pos.x,
                    enemy.current_pos.y,
                    enemy.current_enemy[0],
                    enemy.current_enemy[1]
                )
                if check_collision_recs(bullet_rec, enemy_rec):
                    if bullet in self.bullets:
                        enemy.current_enemy[3] -= 50
                        self.bullets.remove(bullet)
                    if enemy.current_enemy[3] <= 0:
                        self.enemies.remove(enemy)
                    break
        
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
        self.active = False
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

enemies = []
enemy_spawn_timer = Timer(random.uniform(0.5, 1))

bullets = []
shoot_timer = Timer(0.15)

walls = [
    Wall(random.randint(-10000, 10000), random.randint(-10000, 10000), random.randint(100, 2000), random.randint(100, 2000), WHITE) for _ in range(1, 100)
]
collision = Collision(player, walls, bullets, enemies)

camera = Camera2D()
camera.zoom = 1
zoom_rate = 0.01
camera.offset = Vector2(WIDTH / 2, HEIGHT / 2)

set_target_fps(45)

game_over = False

while not window_should_close():
    # Update
    dt = get_frame_time()
    
    # GAME OVER
    if game_over:
        begin_drawing()
        clear_background(BLACK)

        title = "GAME OVER"
        title_size = 100
        title_x = int((get_screen_width() - measure_text(title, title_size)) / 2)
        title_y = int(get_screen_height() / 2 - title_size)
        draw_text(title, title_x, title_y, title_size, RED)

        prompt = "Press ESC to quit"
        prompt_size = 30
        prompt_x = int((get_screen_width() - measure_text(prompt, prompt_size)) / 2)
        prompt_y = title_y + title_size + 30
        draw_text(prompt, prompt_x, prompt_y, prompt_size, WHITE)
        end_drawing()

        if IsKeyPressed(KEY_ESCAPE):
            break
        continue # RESTART THE FRAME INSTEAD OF CONTINUE DOWNWARD.

    if IsKeyPressed(KEY_F11):
        toggle_fullscreen()

    player.update(dt)
    for bullet in bullets:
        bullet.update(dt)
    for enemy in enemies:
        enemy.update(dt)
    collision.update()
    if player.hp <= 0:
        game_over = True
    shoot_timer.update()
    enemy_spawn_timer.update()

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
        
    # Enemies
    if not enemy_spawn_timer.active:
        enemy_spawn_timer.activate()
        if len(enemies) < 10:
            enemies.append(Enemy())
    
    # Camera
    camera.offset = Vector2(get_screen_width() / 2, get_screen_height() / 2)
    player_center = Vector2(player.pos.x + player.w / 2, player.pos.y + player.h / 2)
    current_target = player_center
    
    if IsKeyDown(KEY_E):
        camera.zoom = min(1.2, camera.zoom + zoom_rate) # zoom in
    elif IsKeyDown(KEY_Q):
        camera.zoom = max(0.7, camera.zoom - zoom_rate) # zoom out

    if IsMouseButtonDown(MOUSE_BUTTON_RIGHT):
        mouse = GetScreenToWorld2D(GetMousePosition(), camera)
        current_target = Vector2(
            (player_center.x + mouse.x) / 2,
            (player_center.y + mouse.y) / 2
        )

    smooth = 2.5 * dt
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
    for enemy in enemies:
        enemy.draw()
    player.draw()
    end_mode_2d()
    
    draw_text(f"FPS: {get_fps()}", 20, 20, 20, GREEN)
    draw_text(f"player HP: {player.hp}", 20, 50, 20, GREEN)
    draw_text(f"Enemies Count: {len(enemies)}", 20, 90, 20, GREEN)
    end_drawing()
close_window()