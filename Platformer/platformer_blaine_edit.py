import threading, time, os, queue, readchar

# Viewport and world size
VIEW_W = 80
VIEW_H = 20
WORLD_W = 300
WORLD_H = VIEW_H

# Physics
GRAVITY = 10.0
MOVE_SPEED = 16.0
JUMP_V = 10.0
FRAME = 1.0 / 30.0

# Input queue and state
inq = queue.Queue()
last_left = 0.0
last_right = 0.0
HOLD_TIMEOUT = 0.18

SOLID = '█'

def input_reader(q):
    while True:
        k = readchar.readkey()
        q.put(k)
        if k == 'q':
            break

# Build an empty world
def make_world():
    world = [[' ' for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    # ground
    for x in range(WORLD_W):
        if x % 30 == 29:
            # make a gap sometimes
            continue
        world[WORLD_H - 1][x] = SOLID
    # platforms pattern
    for x in range(10, WORLD_W - 10, 12):
        h = WORLD_H - 3 - ((x // 12) % 4)
        for px in range(x, min(x + 8, WORLD_W)):
            world[h][px] = SOLID
    # taller pillars
    for x in range(60, 80, 6):
        for y in range(WORLD_H - 2, WORLD_H - 6, -1):
            if 0 <= y < WORLD_H and 0 <= x < WORLD_W:
                world[y][x] = SOLID
    return world

world = make_world()

def tile_at(tx, ty):
    if tx < 0 or tx >= WORLD_W or ty < 0 or ty >= WORLD_H:
        return SOLID
    return world[ty][tx]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Player state
px = 5.0
py = WORLD_H - 2.0
vx = 0.0
vy = 0.0

running = True

# Start input thread
t = threading.Thread(target=input_reader, args=(inq,), daemon=True)
t.start()

def handle_input(now):
    global last_left, last_right, vx, vy, px, py, running
    while not inq.empty():
        k = inq.get_nowait()
        if k == 'a':
            last_left = now
        elif k == 'd':
            last_right = now
        elif k == 'w' or k == ' ':
            if on_ground(px, py):
                vy = -JUMP_V
        elif k == 'q':
            running = False
    left_active = (now - last_left) < HOLD_TIMEOUT
    right_active = (now - last_right) < HOLD_TIMEOUT
    if left_active and not right_active:
        vx = -MOVE_SPEED
    elif right_active and not left_active:
        vx = MOVE_SPEED
    else:
        vx = 0.0

def on_ground(x, y):
    foot_y = int(y + 1)
    return tile_at(int(x), foot_y) == SOLID

def move_physics(dt):
    global px, py, vx, vy
    # horizontal movement: check collisions against player's occupied tiles (top and body)
    new_x = px + vx * dt
    top_tile = int(py)
    body_tile = int(py + 0.9)
    if tile_at(int(new_x), top_tile) == SOLID or tile_at(int(new_x), body_tile) == SOLID:
        pass
    else:
        px = new_x
    # gravity and vertical movement
    vy += GRAVITY * dt
    new_y = py + vy * dt
    if vy > 0:
        foot = int(new_y + 1)
        if tile_at(int(px), foot) == SOLID:
            py = foot - 1.0
            vy = 0.0
        else:
            py = new_y
    elif vy < 0:
        head = int(new_y)
        if tile_at(int(px), head) == SOLID:
            vy = 0.0
            py = head + 1.0
        else:
            py = new_y
    if py > WORLD_H - 1.0:
        py = WORLD_H - 1.0
        vy = 0.0
    if py < 0.0:
        py = 0.0
        vy = 0.0

def render():
    cam_x = int(px) - VIEW_W // 3
    cam_x = max(0, min(cam_x, WORLD_W - VIEW_W))
    out_lines = []
    for row in range(VIEW_H):
        line_chars = []
        wy = row
        for col in range(VIEW_W):
            wx = cam_x + col
            ch = tile_at(wx, wy)
            line_chars.append(ch)
        out_lines.append(''.join(line_chars))
    px_screen = int(px) - cam_x
    py_screen = int(py)
    if 0 <= py_screen < VIEW_H and 0 <= px_screen < VIEW_W:
        line = list(out_lines[py_screen])
        line[px_screen] = '@'
        out_lines[py_screen] = ''.join(line)
    clear_screen()
    print(' ' + '=' * (VIEW_W - 2))
    for ln in out_lines:
        print('|' + ln[:VIEW_W - 2] + '|')
    print(' ' + '=' * (VIEW_W - 2))
    print('Controls: a d to move, w or space to jump, q to quit')

# Main loop
last = time.time()
try:
    while running:
        now = time.time()
        dt = now - last
        if dt < FRAME:
            time.sleep(FRAME - dt)
            now = time.time()
            dt = now - last
        last = now
        handle_input(now)
        move_physics(dt)
        render()
except KeyboardInterrupt:
    pass
finally:
    running = False
