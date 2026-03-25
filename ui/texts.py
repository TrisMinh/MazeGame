APP_TITLE = "🌀 Maze Pathfinding — DFS · BFS · A*"

ALGORITHM_ORDER = ["DFS", "BFS", "A*"]

BUTTON_LABELS = {
    "DFS": "Run DFS",
    "BFS": "Run BFS",
    "A*": "Run A*",
    "PLAY": "Play Now",
    "COMPARE": "Compare All",
    "CLEAR": "Clear Path",
    "RESET": "New Maze",
    "TABLE": "Show Table",
}

BUTTON_ICONS = {
    "DFS": "",
    "BFS": "",
    "A*": "",
    "PLAY": "",
    "COMPARE": "",
    "CLEAR": "",
    "RESET": "",
    "TABLE": "",
}

STATUS_MESSAGES = {
    "initial": "Chọn thuật toán và nhấn nút để bắt đầu!",
    "new_maze": "Maze mới! Chọn thuật toán để bắt đầu.",
    "running": "🔍 {algo} đang tìm đường...",
    "game_started": "🎮 Game mode: Dùng WASD hoặc phím mũi tên để đi từ S tới G.",
    "game_blocked": "🎮 Game mode đang chạy. Hãy về đích hoặc nhấn [New Maze] để chơi lại.",
    "game_win": "🏁 Victory! Steps={steps} | Path dung={correct_steps} | Shortest={shortest_steps} | Hieu qua={efficiency:.1f}%",
    "compare_done": "✅ So sánh hoàn tất! Nhấn [Show Table] để xem bảng.",
    "clear_paths": "✅ Đã xóa các đường chạy (paths).",
    "algo_done": "✅ {algo} xong! Path={path_length} | Nodes={nodes_explored} | {time_ms:.3f}ms | [Show Table] để so sánh",
    "algo_failed": "❌ {algo}: Không tìm được đường đi!",
}

BOTTOM_HINT = "[1] DFS  [2] BFS  [3] A*  [C] Compare All  [R] New Maze  [ESC] Đóng bảng"

LEGEND_ITEMS = [
    ("Start", "start"),
    ("Goal", "goal"),
    ("Player", "player"),
    ("My trace", "player_trace"),
    ("My correct path", "player_correct"),
    ("DFS path", "dfs_path"),
    ("BFS path", "bfs_path"),
    ("A* path", "astar_path"),
]

STATS_PANEL_TEXT = {
    "title": "📊 Kết quả & Phân tích",
    "empty_hint": "Chọn thuật toán và nhấn nút để chạy.",
    "comparison_title": "🏆 So sánh",
    "explanations_title": "💡 Giải thích thuật toán",
    "fastest": "⚡ Nhanh nhất",
    "shortest": "📏 Đường ngắn",
    "efficient": "🧠 Ít node nhất",
    "path_length": "Path length",
    "nodes_explored": "Nodes explored",
    "time": "Time",
    "steps_suffix": "bước",
    "not_found": "Không tìm được",
}

ALGO_EXPLANATIONS = {
    "DFS": [
        "DFS – Depth First Search",
        "─" * 26,
        "• Đi sâu nhất có thể theo",
        "  một hướng trước.",
        "• Dùng STACK (vào sau ra trước).",
        "• Không đảm bảo đường ngắn nhất.",
        "• Tốt khi maze rất sâu hoặc",
        "  khi chỉ cần tìm 1 đường.",
    ],
    "BFS": [
        "BFS – Breadth First Search",
        "─" * 26,
        "• Khám phá tất cả node cùng",
        "  khoảng cách trước.",
        "• Dùng QUEUE (vào trước ra trước).",
        "• ĐẢM BẢO đường ngắn nhất",
        "  (đếm theo số bước).",
        "• Tốn nhiều RAM hơn DFS.",
    ],
    "A*": [
        "A* – A-Star Search",
        "─" * 26,
        "• Kết hợp BFS + Heuristic.",
        "• f(n)=g(n)+h(n)",
        "  g: chi phí đã đi thực tế",
        "  h: ước lượng Manhattan đến goal",
        "• Ưu tiên node 'có vẻ gần goal'.",
        "• Nhanh nhất & tối ưu nhất.",
    ],
}

COMPARE_TABLE_TEXT = {
    "title": "Bảng So Sánh Thuật Toán",
    "close_hint": "Nhấn ESC hoặc click bên ngoài để đóng",
    "empty": "Chưa có kết quả. Hãy chạy ít nhất 1 thuật toán!",
    "headers": ["Thuật toán", "Path length", "Nodes explored", "Time (ms)"],
    "path_section": "Path Length (bước)",
    "node_section": "Nodes Explored",
    "time_section": "Time (ms)",
    "fastest": "Nhanh nhất",
    "shortest": "Đường ngắn",
    "efficient": "Ít node nhất",
    "steps_suffix": "bước",
    "not_available": "N/A",
    "no_data": "(Chưa có dữ liệu)",
}

CONSOLE_TEXT = {
    "line": "═" * 65,
    "subline": "─" * 65,
    "title": "  MAZE PATHFINDING — KẾT QUẢ SO SÁNH",
    "header": f"{'Thuật toán':<12} {'Path Length':>12} {'Nodes Explored':>16} {'Time (ms)':>12}",
    "not_found_tag": "(Không tìm được)",
    "fastest": "Nhanh nhất   : {algo}",
    "shortest": "Đường ngắn  : {algo}",
    "explanation_title": "  GIẢI THÍCH THUẬT TOÁN",
}

CONSOLE_EXPLANATIONS = {
    "DFS": """
  DFS (Depth First Search):
    Luôn đi sâu trước rồi mới quay lui.
    Dùng STACK.
    Không đảm bảo đường ngắn nhất.
""",
    "BFS": """
  BFS (Breadth First Search):
    Khám phá theo từng lớp.
    Dùng QUEUE.
    Luôn tìm được đường ngắn nhất theo số bước.
""",
    "A*": """
  A* (A-Star Search):
    Dùng f(n) = g(n) + h(n)
    g(n): chi phí đã đi
    h(n): heuristic Manhattan đến goal
    Thường nhanh hơn BFS và vẫn tối ưu.
""",
}