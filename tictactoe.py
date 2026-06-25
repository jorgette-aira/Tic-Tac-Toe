import tkinter as tk
from tkinter import messagebox
import random
import json
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Main Game Window
root = tk.Tk()
root.title("PIXEL TIC-TAC-TOE")
root.geometry("480x700") 

# --- RETRO PIXEL COLOR PALETTE ---
BG_COLOR = "#0C4926"       # Matrix Green
BUTTON_COLOR = "#0F502B"   # Lighter Game Boy Green
TEXT_COLOR = "#C1FFC1"     # Bright Green Text
ACTIVE_BG = "#306230"      # Mid-tone Green for hover states

root.config(bg=BG_COLOR)

# --- LOAD CUSTOM IMAGE ASSETS ---
IMAGE_PATH_X = resource_path(os.path.join("assets", "X.png")) 
IMAGE_PATH_O = resource_path(os.path.join("assets", "O.png")) 
IMAGE_PATH_SCORE = resource_path(os.path.join("assets", "scoreboard.png")) 
IMAGE_PATH_TITLE = resource_path(os.path.join("assets", "header.png"))

if os.path.exists(IMAGE_PATH_X):
    x_image = tk.PhotoImage(file=IMAGE_PATH_X)
else:
    print(f"Warning: Could not find '{IMAGE_PATH_X}'. Falling back to text.")
    x_image = None

if os.path.exists(IMAGE_PATH_O):
    o_image = tk.PhotoImage(file=IMAGE_PATH_O)
else:
    print(f"Warning: Could not find '{IMAGE_PATH_O}'. Falling back to text.")
    o_image = None

if os.path.exists(IMAGE_PATH_SCORE):
    score_bg_image = tk.PhotoImage(file=IMAGE_PATH_SCORE)
else:
    print(f"Warning: Could not find '{IMAGE_PATH_SCORE}'.")
    score_bg_image = None

if os.path.exists(IMAGE_PATH_TITLE):
    title_banner_image = tk.PhotoImage(file=IMAGE_PATH_TITLE)
else:
    print(f"Warning: Could not find '{IMAGE_PATH_TITLE}'.")
    title_banner_image = None

# --- LOAD PIXEL DIGIT IMAGES (0-9) ---
num_images = {}
for i in range(10):
    num_path = resource_path(os.path.join("assets", f"{i}.png"))
    if os.path.exists(num_path):
        num_images[str(i)] = tk.PhotoImage(file=num_path)
    else:
        num_images[str(i)] = None

current_player = "X"
board = [[None for _ in range(3)] for _ in range(3)]

# --- SCOREBOARD TRACKING ---
player_score = 0
ai_score = 0

# --- LIVE ADAPTIVE Q-LEARNING BRAIN ---
Q_TABLE_FILE = "live_q_table.json"
q_table = {}
game_history = []  

ALPHA = 0.6   
GAMMA = 0.95  

if os.path.exists(Q_TABLE_FILE):
    with open(Q_TABLE_FILE, "r") as f:
        q_table = json.load(f)

def get_board_state_from_matrix(matrix):
    return "".join(["-" if x == "" else x for row in matrix for x in row])

def get_board_state():
    state = ""
    for r in range(3):
        for c in range(3):
            val = board[r][c]["text"] if board[r][c] else ""
            state += val if val != "" else "-"
    return state

def get_q_value(state, action):
    action_str = f"{action[0]},{action[1]}"
    return q_table.get(state, {}).get(action_str, 0.0)

def set_q_value(state, action, value):
    action_str = f"{action[0]},{action[1]}"
    if state not in q_table:
        q_table[state] = {}
    q_table[state][action_str] = value

def save_q_table():
    with open(Q_TABLE_FILE, "w") as f:
        json.dump(q_table, f)

def update_brain_live(history, reward):
    for state, action in reversed(history):
        old_q = get_q_value(state, action)
        new_q = old_q + ALPHA * (reward - old_q)
        set_q_value(state, action, new_q)
        reward *= GAMMA

# --- SIMULATED STRATEGIC BOOTCAMP ---
def check_v_win(b, p):
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] == p: return True
        if b[0][i] == b[1][i] == b[2][i] == p: return True
    if b[0][0] == b[1][1] == b[2][2] == p: return True
    if b[0][2] == b[1][1] == b[2][0] == p: return True
    return False

def get_strategic_move(b, player, opponent):
    moves = [(r, c) for r in range(3) for c in range(3) if b[r][c] == ""]
    for r, c in moves:
        b[r][c] = opponent
        if check_v_win(b, opponent):
            b[r][c] = ""
            return (r, c)
        b[r][c] = ""
    if (1, 1) in moves:
        return (1, 1)
    corners = [m for m in moves if m in [(0,0), (0,2), (2,0), (2,2)]]
    if corners:
        return random.choice(corners)
    return random.choice(moves) if moves else None

def run_advanced_bootcamp(episodes=10000): 
    for _ in range(episodes):
        v_board = [["" for _ in range(3)] for _ in range(3)]
        turn = "X"  
        history = []
        strategy_profile = random.choice(["defensive", "aggressive", "random"])

        while True:
            state = get_board_state_from_matrix(v_board)
            moves = [(r, c) for r in range(3) for c in range(3) if v_board[r][c] == ""]
            if not moves: break
            
            if turn == "X":
                if strategy_profile == "random" or random.random() < 0.1:
                    action = random.choice(moves)
                else:
                    action = get_strategic_move(v_board, "X", "O")
            else:
                best_score = float('-inf')
                action = random.choice(moves)
                for m in moves:
                    score = get_q_value(state, m)
                    if score > best_score:
                        best_score = score
                        action = m
                history.append((state, action))

            v_board[action[0]][action[1]] = turn
            
            if check_v_win(v_board, "O"):
                update_brain_live(history, 12)
                break
            elif check_v_win(v_board, "X"):
                update_brain_live(history, -15) 
                break
            elif not [(r, c) for r in range(3) for c in range(3) if v_board[r][c] == ""]:
                update_brain_live(history, 3)
                break
                
            turn = "X" if turn == "O" else "O"

run_advanced_bootcamp(10000)
save_q_table()

# --- VALIDATION LOGIC ---
def check_winner(player):
    b = [[board[r][c]["text"] if board[r][c] else "" for c in range(3)] for r in range(3)]
    return check_v_win(b, player)

def is_board_full():
    for r in range(3):
        for c in range(3):
            if board[r][c] and board[r][c]["text"] == "":
                return False
    return True

def reset_game():
    global current_player, game_history
    current_player = "X"
    game_history = []
    for row in range(3):
        for col in range(3):
            board[row][col].config(text="", image="", bg=BUTTON_COLOR, state="normal")

# --- GAME ACTIONS ---
def ai_move():
    state = get_board_state()
    moves = [(r, c) for r in range(3) for c in range(3) if board[r][c]["text"] == ""]
    
    if not moves: return

    best_score = float('-inf')
    best_move = random.choice(moves)
    for m in moves:
        score = get_q_value(state, m)
        if score > best_score:
            best_score = score
            best_move = m

    game_history.append((state, best_move))
    
    r, c = best_move
    board[r][c]["text"] = "O" 
    
    if o_image:
        board[r][c].config(image=o_image)
    else:
        board[r][c].config(text="O", fg=TEXT_COLOR) 
    
    if check_winner("O"):
        global ai_score
        ai_score += 1
        update_score_display()
        messagebox.showinfo("GAME OVER", "CPU WINS!")
        update_brain_live(game_history, 12)
        save_q_table()
        reset_game()
        return
    elif is_board_full():
        messagebox.showinfo("GAME OVER", "DRAW GAME!")
        update_brain_live(game_history, 3)
        save_q_table()
        reset_game()
        return

def on_click(row, col):
    global current_player
    btn = board[row][col]

    if btn["text"] == "" and current_player == "X":
        btn["text"] = "X" 
        
        if x_image:
            btn.config(image=x_image)
        else:
            btn.config(text="X", fg=TEXT_COLOR)

        if check_winner("X"):
            global player_score
            player_score += 1
            update_score_display()
            messagebox.showinfo("GAME OVER", "YOU WIN!")
            update_brain_live(game_history, -15)
            save_q_table()
            reset_game()
            return
        
        if is_board_full():
            messagebox.showinfo("GAME OVER", "DRAW GAME!")
            update_brain_live(game_history, 3)
            save_q_table()
            reset_game()
            return
        
        root.after(200, ai_move)

# --- RETRO UI WINDOW SETUP ---

# Title Container Banner
if title_banner_image:
    title_label = tk.Label(root, image=title_banner_image, bg=BG_COLOR)
    title_label.pack(pady=(25, 15))
else:
    title_label = tk.Label(root, text="TIC-TAC-TOE", font=("Courier New", 26, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
    title_label.pack(pady=(25, 15))

# Scoreboard Row container 
score_frame = tk.Frame(root, bg=BG_COLOR)
score_frame.pack(pady=(0, 20))

if score_bg_image:
    # X display module
    score_container_x = tk.Label(score_frame, image=score_bg_image, bg=BG_COLOR)
    score_container_x.pack(side="left", padx=12)
    
    # Text design indicator prefix
    plr_prefix = tk.Label(score_container_x, text="YOU:", font=("Courier New", 19, "bold"), bg="#22b14c", fg=TEXT_COLOR)
    plr_prefix.place(relx=0.40, rely=0.5, anchor="center")
    
    # Graphic container slot that renders your pixel numbers
    plr_num_label = tk.Label(score_container_x, bg="#22b14c")
    plr_num_label.place(relx=0.65, rely=0.5, anchor="center")

    # O display module
    score_container_o = tk.Label(score_frame, image=score_bg_image, bg=BG_COLOR)
    score_container_o.pack(side="left", padx=12)
    
    cpu_prefix = tk.Label(score_container_o, text="AI:", font=("Courier New", 19, "bold"), bg="#22b14c", fg=TEXT_COLOR)
    cpu_prefix.place(relx=0.40, rely=0.5, anchor="center")
    
    cpu_num_label = tk.Label(score_container_o, bg="#22b14c")
    cpu_num_label.place(relx=0.65, rely=0.5, anchor="center")

    # Dynamic lookup engine function to load image vs text fallback string
    def update_score_display():
        # Update Player X
        p_score_str = str(player_score)[-1] # Grabs single digit
        if num_images.get(p_score_str):
            plr_num_label.config(image=num_images[p_score_str], text="")
        else:
            plr_num_label.config(text=p_score_str, font=("Courier New", 13, "bold"), fg=TEXT_COLOR)
            
        # Update CPU O
        c_score_str = str(ai_score)[-1]
        if num_images.get(c_score_str):
            cpu_num_label.config(image=num_images[c_score_str], text="")
        else:
            cpu_num_label.config(text=c_score_str, font=("Courier New", 13, "bold"), fg=TEXT_COLOR)

else:
    score_label = tk.Label(score_frame, text="YOU: 0  |  AI: 0", font=("Courier New", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
    score_label.pack()
    
    def update_score_display():
        score_label.config(text=f"YOU: {player_score}  |  AI: {ai_score}")

# Initialize score graphic display positions
update_score_display()

# Main Grid Block Environment
grid_frame = tk.Frame(root, bg=BG_COLOR, bd=6, relief="ridge")
grid_frame.pack()

for row in range(3):
    for col in range(3):
        btn_frame = tk.Frame(grid_frame, width=110, height=110, bg=BG_COLOR)
        btn_frame.grid_propagate(False) 
        btn_frame.grid(row=row, column=col, padx=6, pady=6)

        btn = tk.Button(
            btn_frame, 
            text="", 
            font=("Courier New", 28, "bold"),
            bg=BUTTON_COLOR, 
            activebackground=ACTIVE_BG,
            activeforeground=TEXT_COLOR,
            bd=5,               
            relief="raised"     
        )
        btn.place(x=0, y=0, width=110, height=110)
        btn.config(command=lambda r=row, c=col: on_click(r, c))
        board[row][col] = btn

root.mainloop()