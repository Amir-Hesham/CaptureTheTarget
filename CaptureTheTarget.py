"""
=============================================================================
CaptureTheTarget is AI-Driven Network Pathfinder & Cyber Attack Simulation.
=======
A Python desktop application that visualizes BFS and A* pathfinding algorithms
on a randomly generated network of nodes (simulating a computer network).
=============================================================================
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import math
import random
import heapq
import time
import threading
# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# Color palette
BG_COLOR        = "#030b14"
PANEL_COLOR     = "#060f1a"
BORDER_COLOR    = "#0f2d4a"
ACCENT_CYAN     = "#00ffe5"
ACCENT_RED      = "#ff3c6e"
ACCENT_ORANGE   = "#f5a623"
NODE_FILL       = "#040f1e"
NODE_BORDER     = "#1a5a8a"
TEXT_COLOR      = "#c8e8ff"
DIM_COLOR       = "#3a6080"
SUCCESS_COLOR   = "#00ff88"

# Node radius on canvas
NODE_RADIUS = 20

# Available device types to assign to nodes
DEVICE_TYPES = ["ROUTER", "FIREWALL", "SERVER", "WORKSTATION",
                "SWITCH", "DATABASE", "IOT", "GATEWAY"]

# Unicode icons to draw inside each node representing its device type
DEVICE_ICONS = {
    "ROUTER":      "⬡",
    "FIREWALL":    "⊠",
    "SERVER":      "▣",
    "WORKSTATION": "◫",
    "SWITCH":      "⬢",
    "DATABASE":    "⬤",
    "IOT":         "◈",
    "GATEWAY":     "◉",
}

# Network size presets
PRESETS = {
    "Small Office (8 nodes)":    8,
    "Enterprise Network (14 nodes)": 14,
    "Data Center (20 nodes)":    20,
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def euclidean(a, b):
    """
    Parameters:
        a, b : dict — node dictionaries containing 'x' and 'y' canvas coordinates.
    """
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)

def heuristic(nodes, a_id, b_id):
    """
    Parameters:
        nodes  : list of node dicts
        a_id   : int — index of the source node
        b_id   : int — index of the destination node
    """
    return euclidean(nodes[a_id], nodes[b_id])

# =============================================================================
# GRAPH ALGORITHMS
# =============================================================================

def bfs(nodes, edges, start, end, visited_cb=None):
    """
    Parameters:
        nodes      : list of node dicts
        edges      : list of edge dicts, each with keys 'a', 'b', 'weight'
        start      : int — index of the starting node
        end        : int — index of the target node
        visited_cb : invoked each time a new node is dequeued (used to animate the canvas).
    Returns:
        dict with keys:
            'path'    : list of node indices from start to end (or None)
            'visited' : int — total number of nodes explored
    """
    # Build an adjacency list from the edge list for O(1) neighbor lookup
    adj = build_adjacency(nodes, edges)

    # Each entry is a list of node indices leading to the current node.
    queue = [[start]]

    # Track visited nodes to avoid revisiting
    visited = set([start])

    while queue:
        # Dequeue the oldest path (FIFO)
        path = queue.pop(0)
        current = path[-1]          # The last node in the path is the current one

        # Fire the animation callback so the UI can highlight this node
        if visited_cb:
            visited_cb(current)

        # Goal check: if we reached the target, return the result
        if current == end:
            return {"path": path, "visited": len(visited)}

        # Expand neighbors in the adjacency list
        for neighbor_id, _weight in adj[current]:
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                # Append a new path that extends to this neighbor
                queue.append(path + [neighbor_id])

    # If the queue is exhausted without reaching the target, no path exists
    return {"path": None, "visited": len(visited)}

def astar(nodes, edges, start, end, visited_cb=None):

    adj = build_adjacency(nodes, edges)

    # Open set implemented as a min-heap.
    # Each entry: (f_score, g_score, node_id, path_so_far)
    h0 = heuristic(nodes, start, end)
    open_heap = [(h0, 0, start, [start])]

    # g_score[node] tracks the cost from start to that node
    g_score = {start: 0}

    # Closed set: nodes whose optimal cost has been finalized
    closed = set()

    while open_heap:
        # Pop the node with the lowest f score
        f, g, current, path = heapq.heappop(open_heap)

        # Skip if already processed
        if current in closed:
            continue

        closed.add(current)

        # Fire animation callback
        if visited_cb:
            visited_cb(current)

        # Goal reached
        if current == end:
            return {"path": path, "visited": len(closed)}

        # Expand neighbors
        for neighbor_id, weight in adj[current]:
            if neighbor_id in closed:
                continue

            # Tentative g score through the current node
            tentative_g = g + weight

            # Only proceed if this is a better route to the neighbor
            if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                g_score[neighbor_id] = tentative_g
                h = heuristic(nodes, neighbor_id, end)
                new_f = tentative_g + h * 30
                heapq.heappush(open_heap, (new_f, tentative_g, neighbor_id, path + [neighbor_id]))

    # No path found
    return {"path": None, "visited": len(closed)}


def build_adjacency(nodes, edges):
    """
    Returns:
        dict mapping node_id → list of (neighbor_id, weight) tuples.
    """
    adj = {i: [] for i in range(len(nodes))}
    for e in edges:
        adj[e["a"]].append((e["b"], e["weight"]))
        adj[e["b"]].append((e["a"], e["weight"]))
    return adj

# =============================================================================
# NETWORK GENERATION
# =============================================================================

def generate_network(preset_name, canvas_width, canvas_height):
    """
    Randomly generate a connected network of nodes and edges.
    Nodes are placed in a rough circular arrangement.

    Each node is then connected to its 2 or 3 nearest neighbors.

    Parameters:
        preset_name   : str — key from PRESETS dict
        canvas_width  : int — width of the drawing canvas in pixels
        canvas_height : int — height of the drawing canvas in pixels
    Returns:
        tuple (nodes, edges) where:
            nodes : list of dicts with keys:
                        id, x, y, type, label, security
            edges : list of dicts with keys:
                        a (index), b (index), weight (int)
    """
    n = PRESETS[preset_name]
    nodes = []
    edges = []
    padding = 80
    cx, cy = canvas_width / 2, (canvas_height - 40) / 2
    radius = min(canvas_width, canvas_height) * 0.30

    # Place nodes in a circlies
    for i in range(n):
        angle = (i / n) * math.pi * 2 + random.uniform(-0.2, 0.2)
        r = radius + random.uniform(-radius * 0.1, radius * 0.1)
        x = cx + math.cos(angle) * r + random.uniform(-30, 30)
        y = cy + math.sin(angle) * r + random.uniform(-30, 30)

        # Clamp to canvas bounds so nodes don't go off-screen
        x = max(padding, min(canvas_width - padding, x))
        y = max(padding, min(canvas_height - padding - 40, y))

        nodes.append({
            "id":       i,
            "x":        x,
            "y":        y,
            "type":     random.choice(DEVICE_TYPES),
            "label":    f"NODE-{i:02d}",
            "security": random.randint(1, 5),
        })

    # Connect each node to its 2–3 nearest neighbors
    for i in range(n):
        # Compute distances from node i to all others
        distances = sorted(
            [(euclidean(nodes[i], nodes[j]), j) for j in range(n) if j != i]
        )
        connections = random.randint(2, 3)
        for k in range(min(connections, len(distances))):
            d, j = distances[k]
            # Avoid duplicate edges (undirected graph)
            already = any(
                (e["a"] == i and e["b"] == j) or (e["a"] == j and e["b"] == i)
                for e in edges
            )
            if not already:
                weight = max(1, int(d / 30))  # Edge weight proportional to distance
                edges.append({"a": i, "b": j, "weight": weight})

    return nodes, edges

# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================

class NetHunterApp:
    """
    The main GUI application for the NetHunter pathfinder.

    Manages:
        - The Tkinter window layout (left panel, canvas, right panel)
        - Network generation and canvas rendering
        - Running BFS / A* algorithms
        - Displaying simulation results and a scrollable log
    """

    def __init__(self, root):
        """
        Initialize the application window and all UI widgets.
        """
        self.root = root
        self.root.title("CaptureTheTarget — Network Pathfinder")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("1200x720")
        self.root.minsize(900, 600)

        self.nodes = []          # List of node dicts
        self.edges = []          # List of edge dicts
        self.start_node = 0      # Index of the start node
        self.end_node   = 1      # Index of the target node
        self.animating  = False  # True while a simulation is running

        # Sets tracking which nodes/edges are highlighted during animation
        self.visited_nodes = set()   # Nodes explored by the current algo
        self.path_nodes    = set()   # Nodes on the final path
        self.path_edges    = set()   # Edges on the final path

        # For "Compare Both" mode — separate sets per algorithm
        self.visited_bfs   = set()
        self.visited_astar = set()
        self.path_bfs      = set()
        self.path_astar    = set()

        self.sim_results   = {}      # Stores result dicts from each algorithm
        self.selected_algo = "bfs"   # Currently selected algorithm
        self.start_time    = time.time()

        # ── Build the UI ── 
        self._build_layout()
        self._build_left_panel()
        self._build_canvas()
        self._build_right_panel()

        self.root.after(100, self._init_network)

    # =========================================================================
    # LAYOUT CONSTRUCTION
    # =========================================================================

    def _build_layout(self):
        """
        Create the top-level three-column grid:
            [ Left Panel | Canvas | Right Panel ]
        """
        self.root.columnconfigure(0, weight=0, minsize=240)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=0, minsize=260)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)

        # ── Header bar ─ 
        header = tk.Frame(self.root, bg="#040e1a", height=55)
        header.grid(row=0, column=0, columnspan=3, sticky="ew")
        header.grid_propagate(False)

        tk.Label(
            header, text="CaptureThe", font=("Courier", 16, "bold"),
            bg="#040e1a", fg=ACCENT_CYAN
        ).pack(side="left", padx=(20, 0), pady=10)

        tk.Label(
            header, text="Target", font=("Courier", 16, "bold"),
            bg="#040e1a", fg=ACCENT_RED
        ).pack(side="left")

        tk.Label(
            header,
            text="  AI-Driven Network Pathfinder  |  Cyber Attack Simulation",
            font=("Courier", 8), bg="#040e1a", fg=DIM_COLOR
        ).pack(side="left", pady=10)

        self.badge_label = tk.Label(
            header, text="● SIMULATION ACTIVE",
            font=("Courier", 8), bg="#040e1a", fg=ACCENT_ORANGE
        )
        self.badge_label.pack(side="right", padx=20)
        self._blink_badge()

    def _blink_badge(self):
        current = self.badge_label.cget("fg")
        new_color = ACCENT_ORANGE if current == BG_COLOR else BG_COLOR
        self.badge_label.config(fg=new_color)
        self.root.after(800, self._blink_badge)

    def _build_left_panel(self):
        # Outer frame
        left = tk.Frame(self.root, bg=PANEL_COLOR, width=240)
        left.grid(row=1, column=0, sticky="nsew")
        left.grid_propagate(False)

        # ── Panel title ── 
        tk.Label(
            left, text="⚙  CONFIGURATION",
            font=("Courier", 8, "bold"), bg=PANEL_COLOR, fg=DIM_COLOR,
            anchor="w"
        ).pack(fill="x", padx=14, pady=(12, 6))
        ttk.Separator(left, orient="horizontal").pack(fill="x")

        # ── Network Preset ── 
        tk.Label(
            left, text="NETWORK PRESET",
            font=("Courier", 7), bg=PANEL_COLOR, fg=DIM_COLOR, anchor="w"
        ).pack(fill="x", padx=14, pady=(10, 2))

        self.preset_var = tk.StringVar(value="Enterprise Network (14 nodes)")
        preset_cb = ttk.Combobox(
            left, textvariable=self.preset_var,
            values=list(PRESETS.keys()), state="readonly", font=("Courier", 8)
        )
        preset_cb.pack(fill="x", padx=14)

        tk.Button(
            left, text="↺  REGENERATE NETWORK",
            font=("Courier", 8), bg="#073040", fg=DIM_COLOR,
            activebackground="#0a4060", relief="flat", cursor="hand2",
            command=self._regen_network
        ).pack(fill="x", padx=14, pady=(4, 8))
        ttk.Separator(left, orient="horizontal").pack(fill="x")

        # ── Node Selection ── 
        tk.Label(
            left, text="SELECT NODES",
            font=("Courier", 7), bg=PANEL_COLOR, fg=DIM_COLOR, anchor="w"
        ).pack(fill="x", padx=14, pady=(10, 4))

        # Start node row
        row_start = tk.Frame(left, bg=PANEL_COLOR)
        row_start.pack(fill="x", padx=14, pady=2)
        tk.Label(
            row_start, text=" START ", font=("Courier", 7),
            bg="#0a3a1a", fg=SUCCESS_COLOR, relief="flat"
        ).pack(side="left")
        self.start_var = tk.StringVar()
        self.start_cb  = ttk.Combobox(
            row_start, textvariable=self.start_var,
            state="readonly", font=("Courier", 8), width=10
        )
        self.start_cb.pack(side="right", expand=True, fill="x")
        self.start_cb.bind("<<ComboboxSelected>>", self._on_start_change)

        # Target node row
        row_end = tk.Frame(left, bg=PANEL_COLOR)
        row_end.pack(fill="x", padx=14, pady=2)
        tk.Label(
            row_end, text="TARGET", font=("Courier", 7),
            bg="#3a0a0a", fg=ACCENT_RED, relief="flat"
        ).pack(side="left")
        self.end_var = tk.StringVar()
        self.end_cb  = ttk.Combobox(
            row_end, textvariable=self.end_var,
            state="readonly", font=("Courier", 8), width=10
        )
        self.end_cb.pack(side="right", expand=True, fill="x")
        self.end_cb.bind("<<ComboboxSelected>>", self._on_end_change)

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=6)

        # ── Algorithm Cards ── 
        tk.Label(
            left, text="ALGORITHM",
            font=("Courier", 7), bg=PANEL_COLOR, fg=DIM_COLOR, anchor="w"
        ).pack(fill="x", padx=14, pady=(0, 4))

        # Each algorithm card is a clickable frame
        self._add_algo_card(left, "bfs",  "BFS",
            "Breadth-First Search. Explores all\nneighbors layer by layer. Guarantees\nshortest hop count.")
        self._add_algo_card(left, "astar","A* SEARCH",
            "Informed search with heuristic cost.\nSmarter & faster by prioritizing\npromising paths.")
        self._add_algo_card(left, "both", "COMPARE BOTH",
            "Run BFS and A* simultaneously\nand compare efficiency, path,\nand nodes explored.")

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        # ── Action Buttons ── 
        self.run_btn = tk.Button(
            left, text="▶  RUN SIMULATION",
            font=("Courier", 9, "bold"), bg=ACCENT_CYAN, fg="black",
            activebackground="#00ccb8", relief="flat", cursor="hand2",
            command=self._run_simulation
        )
        self.run_btn.pack(fill="x", padx=14, pady=(0, 4))

        tk.Button(
            left, text="■  RESET",
            font=("Courier", 8), bg=PANEL_COLOR, fg=DIM_COLOR,
            activebackground="#0a1e30", relief="flat", cursor="hand2",
            command=self._reset_sim
        ).pack(fill="x", padx=14)

    def _add_algo_card(self, parent, algo_id, title, description):
        """
        Create a clickable algorithm selection card in the left panel.
        Parameters:
            parent      : tk widget — container to place the card in
            algo_id     : str — algorithm identifier ('bfs', 'astar', 'both')
            title       : str — display name shown in the card header
            description : str — short description text
        """
        # Each card is stored so we can toggle its highlight on selection
        if not hasattr(self, "_algo_cards"):
            self._algo_cards = {}

        frame = tk.Frame(
            parent, bg=PANEL_COLOR,
            highlightbackground=BORDER_COLOR, highlightthickness=1,
            cursor="hand2"
        )
        frame.pack(fill="x", padx=14, pady=2)

        title_lbl = tk.Label(
            frame, text=title, font=("Courier", 8, "bold"),
            bg=PANEL_COLOR, fg=ACCENT_CYAN, anchor="w"
        )
        title_lbl.pack(fill="x", padx=8, pady=(6, 2))

        desc_lbl = tk.Label(
            frame, text=description, font=("Courier", 7),
            bg=PANEL_COLOR, fg=DIM_COLOR, anchor="w", justify="left"
        )
        desc_lbl.pack(fill="x", padx=8, pady=(0, 6))

        # Bind click on every widget inside the card
        for widget in [frame, title_lbl, desc_lbl]:
            widget.bind("<Button-1>", lambda e, aid=algo_id: self._select_algo(aid))

        self._algo_cards[algo_id] = frame

        # Mark BFS as selected by default
        if algo_id == "bfs":
            frame.config(
                highlightbackground=ACCENT_CYAN,
                bg="#001a2a"
            )
            title_lbl.config(bg="#001a2a")
            desc_lbl.config(bg="#001a2a")

    def _select_algo(self, algo_id):
        self.selected_algo = algo_id

        # Update visual highlight on each card
        for aid, frame in self._algo_cards.items():
            is_active = (aid == algo_id)
            frame.config(
                highlightbackground=ACCENT_CYAN if is_active else BORDER_COLOR,
                bg="#001a2a" if is_active else PANEL_COLOR
            )
            for child in frame.winfo_children():
                child.config(bg="#001a2a" if is_active else PANEL_COLOR)

        self._reset_sim()

    def _build_canvas(self):
        """
        Create the central canvas area where the network is drawn.
        Also adds a status bar at the bottom showing live stats.
        """
        canvas_frame = tk.Frame(self.root, bg=BG_COLOR)
        canvas_frame.grid(row=1, column=1, sticky="nsew")
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame, bg=BG_COLOR,
            highlightthickness=0, cursor="crosshair"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Bind mouse events for interaction
        self.canvas.bind("<Motion>",   self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Status bar at the bottom of the canvas
        status_frame = tk.Frame(canvas_frame, bg="#040d17", height=26)
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.grid_propagate(False)

        self.stat_nodes  = self._stat_label(status_frame, "NODES")
        self.stat_edges  = self._stat_label(status_frame, "EDGES")
        self.stat_algo   = self._stat_label(status_frame, "ALGO")
        self.stat_status = self._stat_label(status_frame, "STATUS")

        # Hover tooltip
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.withdraw()
        self.tooltip.overrideredirect(True)
        self.tooltip.configure(bg="#040d17")
        self.tooltip_label = tk.Label(
            self.tooltip, font=("Courier", 8),
            bg="#040d17", fg=TEXT_COLOR,
            padx=8, pady=4,
            relief="solid", bd=1
        )
        self.tooltip_label.pack()

    def _stat_label(self, parent, key):
        """
        Helper that creates a KEY: VALUE label pair for the status bar.
        Parameters:
            parent : tk widget
            key    : str — label prefix (e.g. "NODES")
        Returns:
            tk.Label — the value label (so callers can update it later).
        """
        frame = tk.Frame(parent, bg="#040d17")
        frame.pack(side="left", padx=12)
        tk.Label(
            frame, text=key + ": ",
            font=("Courier", 7), bg="#040d17", fg=DIM_COLOR
        ).pack(side="left")
        val_lbl = tk.Label(
            frame, text="—",
            font=("Courier", 7, "bold"), bg="#040d17", fg=ACCENT_CYAN
        )
        val_lbl.pack(side="left")
        return val_lbl

    def _build_right_panel(self):
        
        right = tk.Frame(self.root, bg=PANEL_COLOR, width=260)
        right.grid(row=1, column=2, sticky="nsew")
        right.grid_propagate(False)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Panel title
        tk.Label(
            right, text="📡  SYSTEM LOG",
            font=("Courier", 8, "bold"), bg=PANEL_COLOR, fg=DIM_COLOR, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        # ── Tab buttons ── 
        tab_frame = tk.Frame(right, bg=PANEL_COLOR)
        tab_frame.grid(row=0, column=0, sticky="ew", pady=(40, 0))

        self.tab_log_btn = tk.Button(
            tab_frame, text="LOG", font=("Courier", 8),
            bg=PANEL_COLOR, fg=ACCENT_CYAN, relief="flat",
            activebackground=PANEL_COLOR, cursor="hand2",
            command=lambda: self._switch_tab("log")
        )
        self.tab_log_btn.pack(side="left", expand=True, fill="x")

        self.tab_res_btn = tk.Button(
            tab_frame, text="RESULTS", font=("Courier", 8),
            bg=PANEL_COLOR, fg=DIM_COLOR, relief="flat",
            activebackground=PANEL_COLOR, cursor="hand2",
            command=lambda: self._switch_tab("results")
        )
        self.tab_res_btn.pack(side="left", expand=True, fill="x")

        ttk.Separator(right, orient="horizontal").grid(row=0, column=0, sticky="ew", pady=(66, 0))

        # ── Log area ─ 
        self.log_frame = tk.Frame(right, bg=PANEL_COLOR)
        self.log_frame.grid(row=1, column=0, sticky="nsew")
        self.log_frame.rowconfigure(0, weight=1)
        self.log_frame.columnconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            self.log_frame, font=("Courier", 8),
            bg=PANEL_COLOR, fg=TEXT_COLOR,
            relief="flat", state="disabled",
            wrap="word", padx=8, pady=6
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")

        # Colors for different log message
        self.log_text.tag_config("info",    foreground=TEXT_COLOR)
        self.log_text.tag_config("success", foreground=SUCCESS_COLOR)
        self.log_text.tag_config("warn",    foreground=ACCENT_ORANGE)
        self.log_text.tag_config("error",   foreground=ACCENT_RED)
        self.log_text.tag_config("algo",    foreground=ACCENT_CYAN)
        self.log_text.tag_config("time",    foreground=DIM_COLOR)

        # ── Results area ── 
        self.results_frame = tk.Frame(right, bg=PANEL_COLOR)
        self.results_frame.grid(row=1, column=0, sticky="nsew")
        self.results_frame.grid_remove()

        self.results_text = scrolledtext.ScrolledText(
            self.results_frame, font=("Courier", 8),
            bg=PANEL_COLOR, fg=TEXT_COLOR,
            relief="flat", state="disabled",
            wrap="word", padx=8, pady=6
        )
        self.results_text.pack(fill="both", expand=True)
        self.results_text.tag_config("title",   foreground=ACCENT_CYAN,   font=("Courier", 9, "bold"))
        self.results_text.tag_config("label",   foreground=DIM_COLOR)
        self.results_text.tag_config("value",   foreground=ACCENT_CYAN,   font=("Courier", 9, "bold"))
        self.results_text.tag_config("success", foreground=SUCCESS_COLOR)
        self.results_text.tag_config("warn",    foreground=ACCENT_ORANGE)
        self.results_text.tag_config("path",    foreground=TEXT_COLOR)

        # ── Legend ── 
        legend_frame = tk.Frame(right, bg=PANEL_COLOR)
        legend_frame.grid(row=2, column=0, sticky="ew")
        ttk.Separator(right, orient="horizontal").grid(row=2, column=0, sticky="ew")

        items = [
            (SUCCESS_COLOR, "Start"),
            (ACCENT_RED,    "Target"),
            (ACCENT_CYAN,   "Visited (BFS)"),
            (ACCENT_ORANGE, "Path / A*"),
        ]
        for color, label in items:
            item = tk.Frame(legend_frame, bg=PANEL_COLOR)
            item.pack(side="left", padx=6, pady=6)
            tk.Canvas(
                item, width=10, height=10,
                bg=PANEL_COLOR, highlightthickness=0
            ).pack(side="left")
            dot = tk.Canvas(
                item, width=10, height=10,
                bg=PANEL_COLOR, highlightthickness=0
            )
            dot.pack(side="left")
            dot.create_oval(1, 1, 9, 9, fill=color, outline="")
            tk.Label(
                item, text=label, font=("Courier", 6),
                bg=PANEL_COLOR, fg=DIM_COLOR
            ).pack(side="left")

    # =========================================================================
    # NETWORK INITIALIZATION & REGENERATION
    # =========================================================================

    def _init_network(self):
        self.canvas.update_idletasks() 
        self._regen_network()

    def _regen_network(self):
        """
        Generate a fresh random network and redraw the canvas.
        """
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10:   # Window not ready yet
            self.root.after(100, self._regen_network)
            return

        self.nodes, self.edges = generate_network(self.preset_var.get(), w, h)
        self.start_node = 0
        self.end_node   = len(self.nodes) - 1
        self._clear_sim_state()
        self._update_selects()
        self._update_status_bar()
        self._log("Network regenerated.", "info")
        self._log(f"Topology: {len(self.nodes)} nodes, {len(self.edges)} edges.", "info")
        self._draw_network()

    def _update_selects(self):
        """Repopulate the Start / Target comboboxes with the current node list."""
        labels = [nd["label"] for nd in self.nodes]
        self.start_cb["values"] = labels
        self.end_cb["values"]   = labels
        self.start_var.set(labels[self.start_node])
        self.end_var.set(labels[self.end_node])

    def _on_start_change(self, event):
        """Called when the user selects a new start node from the combobox."""
        self.start_node = self.start_cb.current()
        self._reset_sim()

    def _on_end_change(self, event):
        """Called when the user selects a new target node from the combobox."""
        self.end_node = self.end_cb.current()
        self._reset_sim()

    def _update_status_bar(self):
        """Update the bottom status bar labels with current network/algo info."""
        self.stat_nodes.config(text=str(len(self.nodes)))
        self.stat_edges.config(text=str(len(self.edges)))
        self.stat_algo.config(text=self.selected_algo.upper())

    # =========================================================================
    # CANVAS DRAWING
    # =========================================================================

    def _draw_network(self):
        """
        Redraw the entire network on the canvas.
        Draws:
            1. Background dot grid
            2. All edges
            3. All nodes
            4. Node labels and security-level indicators
        """
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        # Background grid — subtle dots
        for gx in range(0, w, 40):
            for gy in range(0, h, 40):
                self.canvas.create_oval(
                    gx-1, gy-1, gx+1, gy+1,
                    fill="#0a1f33", outline=""
                )

        # ── Draw edges ─ 
        for e in self.edges:
            a = self.nodes[e["a"]]
            b = self.nodes[e["b"]]
            key1 = f"{e['a']}-{e['b']}"
            key2 = f"{e['b']}-{e['a']}"

            # Determine edge color based on which set it belongs to
            in_bfs   = key1 in self.path_bfs   or key2 in self.path_bfs
            in_astar = key1 in self.path_astar  or key2 in self.path_astar
            in_path  = key1 in self.path_edges  or key2 in self.path_edges

            if self.selected_algo == "both":
                if in_bfs and in_astar:
                    color, width = "#ffffff", 3
                elif in_bfs:
                    color, width = ACCENT_CYAN, 2
                elif in_astar:
                    color, width = ACCENT_ORANGE, 2
                else:
                    color, width = BORDER_COLOR, 1
            else:
                if in_path:
                    color, width = ACCENT_ORANGE, 3
                elif e["a"] in self.visited_nodes or e["b"] in self.visited_nodes:
                    color, width = "#0a3a5a", 1.5
                else:
                    color, width = BORDER_COLOR, 1

            self.canvas.create_line(
                a["x"], a["y"], b["x"], b["y"],
                fill=color, width=width
            )

            # Edge weight label at the midpoint
            mx, my = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2
            self.canvas.create_text(
                mx + 4, my - 6,
                text=str(e["weight"]),
                font=("Courier", 7), fill="#1a4060"
            )

        # ── Draw nodes ── 
        for i, nd in enumerate(self.nodes):
            is_start   = (i == self.start_node)
            is_end     = (i == self.end_node)
            is_visited = i in self.visited_nodes
            is_path    = i in self.path_nodes
            in_bfs     = i in self.visited_bfs
            in_astar   = i in self.visited_astar

            # Choose fill/stroke colors based on node state
            if is_start:
                fill, stroke, text_color = "#001a08", SUCCESS_COLOR, SUCCESS_COLOR
            elif is_end:
                fill, stroke, text_color = "#1a0008", ACCENT_RED, ACCENT_RED
            elif is_path:
                fill, stroke, text_color = "#1a0f00", ACCENT_ORANGE, ACCENT_ORANGE
            elif self.selected_algo == "both":
                if in_bfs and in_astar:
                    fill, stroke, text_color = "#001522", ACCENT_CYAN, ACCENT_CYAN
                elif in_bfs:
                    fill, stroke, text_color = "#001522", ACCENT_CYAN, ACCENT_CYAN
                elif in_astar:
                    fill, stroke, text_color = "#1a0e00", ACCENT_ORANGE, ACCENT_ORANGE
                else:
                    fill, stroke, text_color = NODE_FILL, NODE_BORDER, DIM_COLOR
            elif is_visited:
                fill, stroke, text_color = "#001522", ACCENT_CYAN, ACCENT_CYAN
            else:
                fill, stroke, text_color = NODE_FILL, NODE_BORDER, DIM_COLOR

            r = NODE_RADIUS
            x, y = nd["x"], nd["y"]

            # Draw the circular node body
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=fill, outline=stroke,
                width=2.5 if is_start or is_end else 1.5
            )

            # Device type icon inside the node
            icon = DEVICE_ICONS.get(nd["type"], "◇")
            self.canvas.create_text(
                x, y - 3, text=icon,
                font=("Courier", 10), fill=text_color
            )

            # Node ID label below the node circle
            self.canvas.create_text(
                x, y + r + 10, text=nd["label"],
                font=("Courier", 7), fill=stroke
            )

            # Security level dots
            dot_colors = {1: SUCCESS_COLOR, 2: ACCENT_ORANGE, 3: ACCENT_ORANGE,
                        4: ACCENT_RED,    5: ACCENT_RED}
            dot_color  = dot_colors.get(nd["security"], ACCENT_RED)
            sec = nd["security"]
            for s in range(sec):
                dx = x - (sec - 1) * 5 + s * 10
                self.canvas.create_oval(
                    dx - 2, y + 14, dx + 2, y + 18,
                    fill=dot_color, outline=""
                )

    # =========================================================================
    # MOUSE INTERACTION
    # =========================================================================

    def _on_mouse_move(self, event):
        """
        Show a tooltip when the cursor hovers over a node.
        Parameters:
            event : tk.Event with .x and .y canvas-relative coordinates.
        """
        hit = self._node_at(event.x, event.y)
        if hit is not None:
            nd = self.nodes[hit]
            sec_dots = "●" * nd["security"] + "○" * (5 - nd["security"])
            self.tooltip_label.config(
                text=f"{nd['label']}\nType: {nd['type']}\nSecurity: {sec_dots}"
            )
            self.tooltip.deiconify()
            self.tooltip.geometry(
                f"+{event.x_root + 14}+{event.y_root - 10}"
            )
        else:
            self.tooltip.withdraw()

    def _on_canvas_click(self, event):
        """
        Left-click sets the start node.
        Shift+Left-click sets the target node.
        Parameters:
            event : tk.Event
        """
        hit = self._node_at(event.x, event.y)
        if hit is not None:
            if event.state & 0x0001:   # Shift key is held
                self.end_node = hit
                self.end_var.set(self.nodes[hit]["label"])
                self._log(f"Target → {self.nodes[hit]['label']} ({self.nodes[hit]['type']})", "warn")
            else:
                self.start_node = hit
                self.start_var.set(self.nodes[hit]["label"])
                self._log(f"Start → {self.nodes[hit]['label']} ({self.nodes[hit]['type']})", "warn")
            self._reset_sim()

    def _node_at(self, mx, my):
        """
        Return the index of the node under position (mx, my), or None.
        Parameters:
            mx, my : float — mouse coordinates relative to the canvas.
        """
        for i, nd in enumerate(self.nodes):
            if euclidean({"x": mx, "y": my}, nd) < NODE_RADIUS + 4:
                return i
        return None

    # =========================================================================
    # SIMULATION CONTROL
    # =========================================================================

    def _run_simulation(self):
        """
        Entry point for running a simulation.
        Validates inputs, then dispatches a background thread so the
        algorithm can update the canvas without freezing the UI.
        """
        if self.animating:
            return

        if self.start_node == self.end_node:
            self._log("ERROR: Start and Target nodes must be different.", "error")
            return

        self._clear_sim_state()
        self.animating = True
        self.run_btn.config(state="disabled")
        self.stat_status.config(text="RUNNING")

        self._log("━" * 28, "info")
        self._log("Initiating attack simulation...", "warn")
        self._log(
            f"Origin: {self.nodes[self.start_node]['label']}  →  "
            f"Target: {self.nodes[self.end_node]['label']}",
            "warn"
        )

        # Run the simulation in a thread so it doesn't block Tkinter
        thread = threading.Thread(target=self._simulation_worker, daemon=True)
        thread.start()

    def _simulation_worker(self):
        """
        Background thread that runs the selected algorithm(s).
        """
        start  = self.start_node
        end    = self.end_node
        delay  = 0.1

        def visited_cb(node_id):
            self.visited_nodes.add(node_id)
            self.root.after(0, self._draw_network)
            time.sleep(delay)

        def visited_bfs_cb(node_id):
            self.visited_bfs.add(node_id)
            self.root.after(0, self._draw_network)
            time.sleep(delay)

        def visited_astar_cb(node_id):
            self.visited_astar.add(node_id)
            self.root.after(0, self._draw_network)
            time.sleep(delay)

        if self.selected_algo == "bfs":
            self._log("Running BFS algorithm...", "algo")
            t0  = time.time()
            res = bfs(self.nodes, self.edges, start, end, visited_cb)
            elapsed = int((time.time() - t0) * 1000)
            self.sim_results["bfs"] = res
            self._finish_single(res, "BFS", elapsed)

        elif self.selected_algo == "astar":
            self._log("Running A* algorithm...", "algo")
            t0  = time.time()
            res = astar(self.nodes, self.edges, start, end, visited_cb)
            elapsed = int((time.time() - t0) * 1000)
            self.sim_results["astar"] = res
            self._finish_single(res, "A*", elapsed)

        else:
            self._log("Running BFS algorithm...", "algo")
            t0      = time.time()
            res_bfs = bfs(self.nodes, self.edges, start, end, visited_bfs_cb)
            self.sim_results["bfs"] = {**res_bfs, "time": int((time.time()-t0)*1000)}

            self._log("Running A* algorithm...", "algo")
            t0       = time.time()
            res_ast  = astar(self.nodes, self.edges, start, end, visited_astar_cb)
            self.sim_results["astar"] = {**res_ast, "time": int((time.time()-t0)*1000)}

            self._finish_compare()

        self._highlight_paths()
        self.root.after(0, self._draw_network)
        self.root.after(0, self._render_results)
        self.root.after(0, lambda: self.stat_status.config(text="DONE"))
        self.root.after(0, lambda: self.run_btn.config(state="normal"))
        self._log("Simulation complete.", "success")
        self.animating = False

    def _finish_single(self, res, name, elapsed):
        if res["path"]:
            self._log(f"{name} PATH FOUND! Hops: {len(res['path'])-1}", "success")
            self._log(f"Nodes explored: {res['visited']} | Time: {elapsed}ms", "success")
        else:
            self._log(f"{name}: No path found between selected nodes!", "error")

    def _finish_compare(self):
        b = self.sim_results.get("bfs")
        a = self.sim_results.get("astar")
        if b and b["path"]:
            self._log(
                f"BFS: {len(b['path'])-1} hops, {b['visited']} explored, {b['time']}ms",
                "success"
            )
        if a and a["path"]:
            self._log(
                f"A*: {len(a['path'])-1} hops, {a['visited']} explored, {a['time']}ms",
                "success"
            )

    def _highlight_paths(self):
        b = self.sim_results.get("bfs")
        a = self.sim_results.get("astar")

        def add_path(path, path_node_set, path_edge_set):
            if not path:
                return
            for n in path:
                path_node_set.add(n)
                self.path_nodes.add(n)
            for i in range(len(path) - 1):
                key = f"{path[i]}-{path[i+1]}"
                path_edge_set.add(key)
                self.path_edges.add(key)

        if self.selected_algo == "bfs" and b:
            add_path(b["path"], self.path_nodes, self.path_edges)
        elif self.selected_algo == "astar" and a:
            add_path(a["path"], self.path_nodes, self.path_edges)
        elif self.selected_algo == "both":
            if b:
                add_path(b["path"], self.path_bfs, self.path_edges)
            if a:
                add_path(a["path"], self.path_astar, self.path_edges)

    # =========================================================================
    # RESULTS RENDERING
    # =========================================================================

    def _render_results(self):
        """
        Write formatted simulation results to the RESULTS tab.
        """
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")

        b = self.sim_results.get("bfs")
        a = self.sim_results.get("astar")

        if self.selected_algo == "both" and b and a:
            winner = "BFS" if (b["visited"] <= a["visited"]) else "A*"
            self.results_text.insert("end", f"⚡ WINNER: {winner} (fewer nodes explored)\n\n", "warn")

            # BFS stats
            self.results_text.insert("end", "── BFS ─────────────────\n", "title")
            self._result_row("Path Hops",     str(len(b["path"])-1) if b["path"] else "N/A")
            self._result_row("Nodes Explored", str(b["visited"]))
            if b["path"]:
                path_str = " → ".join(self.nodes[n]["label"] for n in b["path"])
                self.results_text.insert("end", f"\n{path_str}\n\n", "path")

            # A* stats
            self.results_text.insert("end", "── A* ──────────────────\n", "title")
            self._result_row("Path Hops",     str(len(a["path"])-1) if a["path"] else "N/A")
            self._result_row("Nodes Explored", str(a["visited"]))
            if a["path"]:
                path_str = " → ".join(self.nodes[n]["label"] for n in a["path"])
                self.results_text.insert("end", f"\n{path_str}\n\n", "path")

            if b["visited"] > 0:
                savings = (1 - a["visited"] / b["visited"]) * 100
                self.results_text.insert(
                    "end",
                    f"A* explored {savings:.0f}% fewer nodes than BFS.\n",
                    "success"
                )

        elif b or a:
            # Single algorithm result
            r    = b or a
            name = "BFS" if b else "A*"
            self.results_text.insert("end", f"── {name} RESULT ──────────\n", "title")
            self._result_row("Algorithm", name)
            self._result_row("Status",    "PATH FOUND" if r["path"] else "NO PATH")
            if r["path"]:
                self._result_row("Hops",           str(len(r["path"]) - 1))
                self._result_row("Nodes Explored", str(r["visited"]))
                path_str = " → ".join(self.nodes[n]["label"] for n in r["path"])
                self.results_text.insert("end", f"\n{path_str}\n", "path")
        else:
            self.results_text.insert("end", "Run a simulation to see results.\n", "label")

        self.results_text.config(state="disabled")

    def _result_row(self, label, value):
        """
        Write a single label: value row in the results area.
        """
        self.results_text.insert("end", f"{label:<18}", "label")
        self.results_text.insert("end", f"{value}\n", "value")

    # =========================================================================
    # LOG HELPERS
    # =========================================================================

    def _log(self, message, msg_type="info"):
        """
        Append a timestamped message to the system log.
        Parameters:
            message  : str — the log message text
            msg_type : str — one of 'info', 'success', 'warn', 'error', 'algo'
        """
        elapsed = time.time() - self.start_time
        mm = int(elapsed // 60)
        ss = int(elapsed % 60)
        timestamp = f"{mm:02d}:{ss:02d}"

        def _insert():
            self.log_text.config(state="normal")
            self.log_text.insert("end", f"{timestamp}  ", "time")
            self.log_text.insert("end", f"{message}\n", msg_type)
            self.log_text.see("end")      # Auto-scroll to the latest entry
            self.log_text.config(state="disabled")

        # Always update the log on the main thread (thread-safe)
        self.root.after(0, _insert)

    # =========================================================================
    # TAB SWITCHING
    # =========================================================================

    def _switch_tab(self, tab):
        """
        Switch between the LOG and RESULTS tabs in the right panel.
        """
        if tab == "log":
            self.log_frame.grid()
            self.results_frame.grid_remove()
            self.tab_log_btn.config(fg=ACCENT_CYAN)
            self.tab_res_btn.config(fg=DIM_COLOR)
        else:
            self.results_frame.grid()
            self.log_frame.grid_remove()
            self.tab_res_btn.config(fg=ACCENT_CYAN)
            self.tab_log_btn.config(fg=DIM_COLOR)

    # =========================================================================
    # SIMULATION STATE MANAGEMENT
    # =========================================================================

    def _clear_sim_state(self):
        """
        Clear all sets that track visited/path nodes/edges.
        """
        self.visited_nodes.clear()
        self.path_nodes.clear()
        self.path_edges.clear()
        self.visited_bfs.clear()
        self.visited_astar.clear()
        self.path_bfs.clear()
        self.path_astar.clear()
        self.sim_results = {}

    def _reset_sim(self):
        """
        Reset the simulation state and redraw a clean network.
        Called when the user changes nodes or switches algorithms.
        """
        self._clear_sim_state()
        self.stat_status.config(text="READY")
        self._log("Simulation reset.", "info")
        self._draw_network()

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app  = NetHunterApp(root)

    # Initial log messages
    app._log("System initialized.", "info")
    app._log("Network topology loaded.", "info")
    app._log("Click node = Set START  |  Shift+Click = Set TARGET", "warn")

    root.mainloop()