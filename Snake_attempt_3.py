"""import tkinter
import random
 
COLS = 25
ROWS = 25
TILE_SIZE = 20
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE
SPEEDS = {1: 150, 2: 100, 3: 60}  # milliseconds per step: slow, normal, fast
SPEED_NAMES = {1: "Slow", 2: "Normal", 3: "Fast"}
 
 
class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
 
    def same(self, other):
        return self.x == other.x and self.y == other.y
 
    def randomize(self):
        self.x = random.randint(0, COLS - 1)
        self.y = random.randint(0, ROWS - 1)
 
 
class Snake:
    def __init__(self, x, y, color, name):
        self.body = [Tile(x, y)]  # body[0] is the head
        self.dx = 0
        self.dy = 0
        self.score = 0
        self.color = color
        self.name = name
 
 
# ---------- window ----------
window = tkinter.Tk()
window.title("Snake - Bomb Run")
window.resizable(False, False)
 
left = tkinter.Frame(window)
left.pack(side="left", padx=10, pady=10)
right = tkinter.Frame(window)
right.pack(side="right", padx=10, pady=10, anchor="n")
 
score_label = tkinter.Label(left, text="", font="Arial 12")
score_label.pack(anchor="w")
canvas = tkinter.Canvas(left, bg="white", width=WIDTH, height=HEIGHT,
                        borderwidth=0, highlightthickness=0)
canvas.pack()
hint_label = tkinter.Label(left, text="Press START to play.", font="Arial 10")
hint_label.pack(anchor="w")
 
# ---------- settings panel ----------
tkinter.Label(right, text="Game features", font="Arial 14 bold").pack(anchor="w", pady=(0, 10))
 
tkinter.Label(right, text="Players").pack(anchor="w")
players_var = tkinter.StringVar(value="1 player")
tkinter.OptionMenu(right, players_var, "1 player", "2 players").pack(anchor="w", pady=(0, 10))
 
tkinter.Label(right, text="Bombs").pack(anchor="w")
bombs_scale = tkinter.Scale(right, from_=0, to=10, orient="horizontal")
bombs_scale.set(1)
bombs_scale.pack(anchor="w", pady=(0, 10))
 
tkinter.Label(right, text="Apples").pack(anchor="w")
apples_scale = tkinter.Scale(right, from_=1, to=10, orient="horizontal")
apples_scale.set(1)
apples_scale.pack(anchor="w", pady=(0, 10))
 
tkinter.Label(right, text="Speed (1 slow, 2 normal, 3 fast)").pack(anchor="w")
speed_scale = tkinter.Scale(right, from_=1, to=3, orient="horizontal")
speed_scale.set(2)
speed_scale.pack(anchor="w", pady=(0, 10))
 
# ---------- game state ----------
snakes = []
foods = []
bombs = []
game_over = False
started = False
message = ""
h_score = 0
loop_id = None
 
 
def start_game():
    global snakes, foods, bombs, game_over, started, message, loop_id
    if loop_id is not None:
        window.after_cancel(loop_id)
 
    snakes = [Snake(5, 5, "green", "Player 1")]
    if players_var.get() == "2 players":
        snakes.append(Snake(19, 19, "royal blue", "Player 2"))
 
    foods = []
    for _ in range(apples_scale.get()):
        t = Tile(0, 0)
        t.randomize()
        foods.append(t)
    bombs = []
    for _ in range(bombs_scale.get()):
        t = Tile(0, 0)
        t.randomize()
        bombs.append(t)
 
    game_over = False
    started = True
    message = ""
    if len(snakes) == 2:
        hint_label.config(text="Player 1: arrow keys. Player 2: W A S D.")
    else:
        hint_label.config(text="Move with the arrow keys.")
    canvas.focus_set()  # so the sliders don't take the arrow keys
    loop()
 
 
start_button = tkinter.Button(right, text="START", font="Arial 12", command=start_game)
start_button.pack(anchor="w", pady=10)
 
# key -> (snake index, dx, dy)
KEYS = {
    "Up": (0, 0, -1), "Down": (0, 0, 1), "Left": (0, -1, 0), "Right": (0, 1, 0),
    "w": (1, 0, -1), "s": (1, 0, 1), "a": (1, -1, 0), "d": (1, 1, 0),
}
 
 
def change_direction(e):
    if not started or game_over:
        return
    key = e.keysym.lower() if len(e.keysym) == 1 else e.keysym
    if key not in KEYS:
        return
    index, dx, dy = KEYS[key]
    if index >= len(snakes):
        return
    s = snakes[index]
    # don't allow turning straight back into yourself
    if dx != 0 and dx == -s.dx:
        return
    if dy != 0 and dy == -s.dy:
        return
    s.dx = dx
    s.dy = dy
 
 
def move():
    global game_over
    dead = []
    for i, s in enumerate(snakes):
        if s.dx == 0 and s.dy == 0:
            continue
        head = Tile(s.body[0].x + s.dx, s.body[0].y + s.dy)
 
        # walls
        if head.x < 0 or head.x >= COLS or head.y < 0 or head.y >= ROWS:
            dead.append(i)
            continue
        # snake bodies (own and the other player's)
        if any(head.same(t) for o in snakes for t in o.body):
            dead.append(i)
            continue
 
        s.body.insert(0, head)
 
        eaten = next((f for f in foods if f.same(head)), None)
        hit = next((b for b in bombs if b.same(head)), None)
        if eaten:
            eaten.randomize()
            s.score += 1  # keep the tail, so the snake grows
        else:
            s.body.pop()
            if hit:
                if len(s.body) > 1:
                    s.body.pop()
                    s.score -= 1
                    hit.randomize()
                else:
                    dead.append(i)
 
    # bombs sometimes jump to a new spot
    for b in bombs:
        if random.randint(1, 50) == 1:
            b.randomize()
 
    if dead:
        finish(dead)
 
 
def finish(dead):
    global game_over, message, h_score
    game_over = True
    if len(snakes) == 1:
        message = f"Game over: {snakes[0].score}"
    elif len(dead) == 2:
        message = "Draw!"
    else:
        message = f"{snakes[1 - dead[0]].name} wins!"
    h_score = max(h_score, max(s.score for s in snakes))
    hint_label.config(text="Change the features on the right and press START to play again.")
 
 
def draw_tile(t, color):
    x = t.x * TILE_SIZE
    y = t.y * TILE_SIZE
    canvas.create_rectangle(x, y, x + TILE_SIZE, y + TILE_SIZE, fill=color, outline=color)
 
 
def draw():
    canvas.delete("all")
    if not started:
        canvas.create_text(WIDTH / 2, HEIGHT / 2, font="Arial 20", text="Press START")
        return
 
    for f in foods:
        draw_tile(f, "red")
    for b in bombs:
        draw_tile(b, "black")
    for s in snakes:
        for t in s.body:
            draw_tile(t, s.color)
 
    text = f"Player 1: {snakes[0].score}"
    if len(snakes) == 2:
        text += f"    Player 2: {snakes[1].score}"
    text += f"    High score: {h_score}"
    score_label.config(text=text)
 
    if game_over:
        canvas.create_text(WIDTH / 2, HEIGHT / 2, font="Arial 24", text=message, fill="black")
 
 
def loop():
    global loop_id
    move()
    draw()
    if not game_over:
        loop_id = window.after(SPEEDS[speed_scale.get()], loop)
    else:
        loop_id = None
 
 
window.bind("<KeyPress>", change_direction)
draw()
window.mainloop()"""