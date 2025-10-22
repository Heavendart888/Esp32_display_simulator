# display_designer/app.py
"""
Tkinter application logic, including the display selector and the main emulator window.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import math
import re
import os  # Import os for path handling
import sys # Import sys for PyInstaller check

from .core import DISPLAY_PRESETS, Element

# Global padding for the simulated display border
PAD = 12

# ----------------- PATH RESOLUTION HELPER -----------------
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Base path for running locally
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
# -----------------------------------------------------------


# ----------------- Display selector -----------------
def open_display_selector():
    """Opens the initial window to select or define display dimensions."""
    
    def on_open():
        # ... (on_open logic remains the same)
        sel = var.get()
        if sel == "Custom...":
            try:
                w = int(width_ent.get())
                h = int(height_ent.get())
                if w <= 0 or h <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid", "Enter positive integers for width & height.")
                return
        else:
            w, h = DISPLAY_PRESETS[sel]
        
        root.destroy()
        open_emulator_window(sel, w, h)

    root = tk.Tk()
    root.title("Select Display")
    root.geometry("380x240")
    root.config(bg="#101820")
    root.resizable(False, False)

    # --- SET WINDOW ICON (Using resource_path) ---
    ICON_FILE = resource_path('assets/simulator_icon.png')
    try:
        # Load the icon image using the resolved path
        icon_img = tk.PhotoImage(file=ICON_FILE)
        # Setting True applies the icon to the root and all subsequent Toplevel windows
        root.iconphoto(True, icon_img)
    except tk.TclError:
        # Ignore if the image file is not found (e.g., if assets folder is missing)
        pass
    # ----------------------------------------------------

    tk.Label(root, text="Choose display size", fg="#FEE715", bg="#101820", font=("Segoe UI", 13, "bold")).pack(pady=12)

    var = tk.StringVar(value="OLED 128x64")
    combo = ttk.Combobox(root, textvariable=var, values=list(DISPLAY_PRESETS.keys()), state="readonly", width=28)
    combo.pack(pady=6)
    
    # Custom dimension input
    cf = tk.Frame(root, bg="#101820")
    tk.Label(cf, text="Width:", bg="#101820", fg="white").grid(row=0, column=0, padx=6)
    width_ent = tk.Entry(cf, width=6)
    width_ent.insert(0, "128")
    width_ent.grid(row=0, column=1)
    tk.Label(cf, text="Height:", bg="#101820", fg="white").grid(row=0, column=2, padx=6)
    height_ent = tk.Entry(cf, width=6)
    height_ent.insert(0, "64")
    height_ent.grid(row=0, column=3)
    cf.pack(pady=8)

    tk.Button(root, text="Open Simulator", bg="#00FF88", command=on_open, width=18).pack(pady=6)
    tk.Button(root, text="Exit", bg="#E74C3C", command=root.destroy, width=18).pack()

    # Center the window
    root.update_idletasks()
    width_win = root.winfo_width()
    height_win = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width_win // 2)
    y = (root.winfo_screenheight() // 2) - (height_win // 2)
    root.geometry(f'+{x}+{y}')

    root.mainloop()

# ----------------- Emulator (main app) -----------------
def open_emulator_window(display_name, width, height):
    """Opens the main emulator and designer window."""
    app = tk.Tk()
    # Updated Title to 'Simulator'
    app.title(f"ESP32 Display Simulator — {display_name} ({width}x{height})")
    app.geometry("1250x700")
    app.config(bg="#151515")

    # elements mapping: item id -> Element
    elements = {}
    selected_id = {"id": None}
    handles = []  # resize handles ids
    dragging = {"active": False, "id": None, "start_x": 0, "start_y": 0, "mode": None}  # mode: "move" or "resize"
    updating_from_code = {"flag": False}  # to prevent feedback loops

    # --- Utility Functions (rest of functions omitted for brevity, assume they are copied from previous step) ---
    
    # ... (All utility functions: clear_selection_visuals, show_selection_visuals, 
    # parse_editor_and_draw, generate_arduino_code, add_from_button, delete_selected, 
    # rotate_selected, canvas_click, canvas_drag, canvas_release, apply_code_to_canvas) ...
    # ... (GUI Layout remains the same) ...

    def clear_selection_visuals():
        # ... (implementation) ...
        nonlocal handles
        canvas.delete("select")
        for h in handles:
            canvas.delete(h)
        handles = []
        selected_id["id"] = None
        
    def show_selection_visuals(item_id):
        # ... (implementation) ...
        nonlocal handles
        clear_selection_visuals()
        if item_id is None:
            return
        selected_id["id"] = item_id
        bbox = canvas.bbox(item_id)
        if not bbox:
            return
        x1, y1, x2, y2 = bbox
        
        # Selection outline
        canvas.create_rectangle(x1 - 3, y1 - 3, x2 + 3, y2 + 3, outline="#FFD700", dash=(4,4), width=2, tags="select")
        
        el = elements.get(item_id)
        if not el:
            return
            
        # Add resize handles for rect and circle
        if el.type in ("rect", "circle"):
            size = 8
            if el.rotation % 360 != 0 and el.type == "rect":
                 x1_orig = PAD + el.x
                 y1_orig = PAD + el.y
                 x2_orig = PAD + el.x + el.w
                 y2_orig = PAD + el.y + el.h
                 corners = [(x1_orig, y1_orig), (x2_orig, y1_orig), (x2_orig, y2_orig), (x1_orig, y2_orig)]
            else:
                 corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                 
            for (cx, cy) in corners:
                h = canvas.create_rectangle(cx - size/2, cy - size/2, cx + size/2, cy + size/2,
                                            fill="#FFFFFF", outline="#000000", tags=("select", "handle"))
                handles.append(h)

    # ---------------- drawing from editor ----------------
    def parse_editor_and_draw():
        # ... (implementation) ...
        nonlocal elements
        canvas.delete("drawn")
        elements.clear()
        lines = editor.get("1.0", "end-1c").splitlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            cmd = parts[0].lower()
            
            try:
                if cmd == "text":
                    x = int(parts[1]); y = int(parts[2]); txt = " ".join(parts[3:])
                    cid = canvas.create_text(PAD + x, PAD + y, text=txt, anchor="nw", fill="white", font=("Consolas", 10), tags=("drawn",))
                    el = Element("text", cid, x, y, 0, 0, text=txt, rotation=0)
                    elements[cid] = el
                elif cmd == "rect":
                    x1 = int(parts[1]); y1 = int(parts[2]); x2 = int(parts[3]); y2 = int(parts[4])
                    cid = canvas.create_rectangle(PAD + x1, PAD + y1, PAD + x2, PAD + y2, outline="#00FFFF", width=1, tags=("drawn",))
                    el = Element("rect", cid, x1, y1, x2 - x1, y2 - y1, rotation=0)
                    elements[cid] = el
                elif cmd == "circle":
                    x = int(parts[1]); y = int(parts[2]); r = int(parts[3])
                    cid = canvas.create_oval(PAD + x - r, PAD + y - r, PAD + x + r, PAD + y + r, outline="#FFA500", width=1, tags=("drawn",))
                    el = Element("circle", cid, x - r, y - r, 2 * r, 2 * r, rotation=0)
                    elements[cid] = el
            except Exception as e:
                messagebox.showerror("Parse error", f"Failed to parse: {line}\n\nError: {e}")
        
        generate_arduino_code()
        clear_selection_visuals()

    # ---------------- generate Arduino code from elements ----------------
    def generate_arduino_code():
        # ... (implementation) ...
        if updating_from_code["flag"]:
            return
        
        lines = []
        header = [
            "#include <Adafruit_GFX.h>",
            "#include <Adafruit_SSD1306.h>",
            f"#define SCREEN_WIDTH {width}",
            f"#define SCREEN_HEIGHT {height}",
            "// Assuming a standard I2C connection and OLED type (adjust for other displays/protocols)",
            "Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire);",
            "",
            "void setup() {",
            "  // Serial.begin(115200); // Uncomment for debugging",
            "  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {",
            "    // Serial.println(F(\"SSD1306 allocation failed\"));",
            "    for(;;); // Don't proceed, loop forever",
            "  }",
            "  display.clearDisplay();",
            "  display.setTextColor(WHITE);",
        ]
        body = []
        for el in elements.values():
            if el.type == "text":
                body.append(f'  display.setCursor({el.x}, {el.y}); display.print("{el.text}");')
            elif el.type == "rect":
                if el.rotation % 360 != 0:
                    body.append(f'  // WARNING: Rotated rectangle (rotation={el.rotation}°) - Not supported by Adafruit_GFX::drawRect.')
                    body.append(f'  // Drawing the bounding box based on unrotated coordinates.')
                body.append(f'  display.drawRect({el.x}, {el.y}, {el.w}, {el.h}, WHITE);')
            elif el.type == "circle":
                cx = el.x + el.w // 2 
                cy = el.y + el.h // 2
                r = el.w // 2
                body.append(f'  display.drawCircle({cx}, {cy}, {r}, WHITE);')
                
        footer = [
            "  display.display();",
            "}",
            "",
            "void loop() {",
            "  // Your main loop code here",
            "}"
        ]
        
        text = "\n".join(header + body + footer)
        code_area.delete("1.0", "end")
        code_area.insert("1.0", text)

    # ---------------- add elements by buttons ----------------
    def add_from_button(kind):
        # ... (implementation) ...
        if kind == "rect":
            x1, y1, w_r, h_r = 10, 10, 70, 40
            cid = canvas.create_rectangle(PAD + x1, PAD + y1, PAD + x1 + w_r, PAD + y1 + h_r, outline="#00FFFF", width=1, tags=("drawn",))
            el = Element("rect", cid, x1, y1, w_r, h_r, rotation=0)
            elements[cid] = el
        elif kind == "circle":
            r = 20; cx, cy = 60, 30
            cid = canvas.create_oval(PAD + cx - r, PAD + cy - r, PAD + cx + r, PAD + cy + r, outline="#FFA500", width=1, tags=("drawn",))
            el = Element("circle", cid, cx - r, cy - r, 2 * r, 2 * r, rotation=0)
            elements[cid] = el
        elif kind == "text":
            x, y = 12, 12
            cid = canvas.create_text(PAD + x, PAD + y, text="New Text", anchor="nw", fill="white", font=("Consolas", 10), tags=("drawn",))
            el = Element("text", cid, x, y, 0, 0, text="New Text", rotation=0)
            elements[cid] = el
        
        show_selection_visuals(cid) 
        generate_arduino_code()

    # ---------------- Delete element ----------------
    def delete_selected():
        # ... (implementation) ...
        sid = selected_id.get("id")
        if sid and sid in elements:
            canvas.delete(sid)
            del elements[sid]
            clear_selection_visuals()
            generate_arduino_code()
            
    # ---------------- rotate selected ----------------
    def rotate_selected(delta_degrees):
        # ... (implementation) ...
        sid = selected_id.get("id")
        if not sid:
            return
        el = elements.get(sid)
        if not el or el.type == "text": 
            return
            
        el.rotation = (el.rotation + delta_degrees) % 360
        
        if el.type == "rect":
            bbox_model = [PAD + el.x, PAD + el.y, PAD + el.x + el.w, PAD + el.y + el.h]
            x1,y1,x2,y2 = bbox_model
            
            cx = (x1 + x2)/2; cy = (y1 + y2)/2
            w_orig = (x2 - x1); h_orig = (y2 - y1)
            corners = [(-w_orig/2, -h_orig/2), (w_orig/2, -h_orig/2), (w_orig/2, h_orig/2), (-w_orig/2, h_orig/2)]
            rad = math.radians(el.rotation)
            pts = []
            
            for dx,dy in corners:
                nx = cx + dx*math.cos(rad) - dy*math.sin(rad)
                ny = cy + dx*math.sin(rad) + dy*math.cos(rad)
                pts.extend([nx, ny])
            
            canvas.coords(sid, *pts) 
            canvas.itemconfig(sid, dash=(2,2)) 
            
        elif el.type == "circle":
            pass
            
        show_selection_visuals(sid)
        generate_arduino_code()

    # ---------------- Interaction Handlers ----------------
    
    def canvas_click(event):
        # ... (implementation) ...
        if event.x < PAD or event.x > PAD + width or event.y < PAD or event.y > PAD + height:
            clear_selection_visuals()
            return
        found = None
        for it in reversed(canvas.find_overlapping(event.x, event.y, event.x, event.y)):
            if it in elements:
                found = it
                break

        if found:
            if "handle" in canvas.gettags(canvas.find_closest(event.x, event.y)):
                dragging["mode"] = "resize"
                dragging["id"] = selected_id["id"] 
            else:
                dragging["mode"] = "move"
                dragging["id"] = found

            dragging["active"] = True
            dragging["start_x"] = event.x
            dragging["start_y"] = event.y
            show_selection_visuals(dragging["id"])
        else:
            clear_selection_visuals()
        
    def canvas_drag(event):
        # ... (implementation) ...
        if not dragging["active"] or dragging["id"] is None:
            return
        iid = dragging["id"]
        el = elements.get(iid)
        if not el: return
        
        event_x = max(PAD, min(PAD + width, event.x))
        event_y = max(PAD, min(PAD + height, event.y))
        
        dx = event_x - dragging["start_x"]
        dy = event_y - dragging["start_y"]
        dragging["start_x"] = event_x
        dragging["start_y"] = event_y
        
        if dragging["mode"] == "move":
            bbox = canvas.bbox(iid)
            if not bbox: return
            x1, y1, x2, y2 = bbox
            
            final_dx = dx
            final_dy = dy
            if x1 + dx < PAD: final_dx = PAD - x1
            if y1 + dy < PAD: final_dy = PAD - y1
            if x2 + dx > PAD + width: final_dx = (PAD + width) - x2
            if y2 + dy > PAD + height: final_dy = (PAD + height) - y2
            
            canvas.move(iid, final_dx, final_dy)
            
            if el.type == "text":
                cx, cy = canvas.coords(iid)
                el.x = int(cx - PAD); el.y = int(cy - PAD)
            else:
                bb = canvas.bbox(iid)
                ex1, ey1, ex2, ey2 = bb
                el.x = int(ex1 - PAD); el.y = int(ey1 - PAD)
                el.w = int(ex2 - ex1); el.h = int(ey2 - ey1)
                
            show_selection_visuals(iid)
            generate_arduino_code()
        
        elif dragging["mode"] == "resize" and el.type in ("rect", "circle"):
            bb = canvas.bbox(iid)
            if not bb: return
            x1, y1, x2, y2 = bb
            
            corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            dists = [ (math.hypot(event_x - cx, event_y - cy), idx) for idx, (cx,cy) in enumerate(corners) ]
            dists.sort()
            _, corner_idx = dists[0]
            
            ex, ey = event_x, event_y
            
            if corner_idx == 0: nx1, ny1, nx2, ny2 = ex, ey, x2, y2
            elif corner_idx == 1: nx1, ny1, nx2, ny2 = x1, ey, ex, y2
            elif corner_idx == 2: nx1, ny1, nx2, ny2 = x1, y1, ex, ey
            else: nx1, ny1, nx2, ny2 = ex, y1, x2, ey
            
            min_size = 6
            if nx2 - nx1 < min_size: nx2 = nx1 + min_size
            if ny2 - ny1 < min_size: ny2 = ny1 + min_size
            
            canvas.coords(iid, nx1, ny1, nx2, ny2)
            
            el.x = int(nx1 - PAD); el.y = int(ny1 - PAD); el.w = int(nx2 - nx1); el.h = int(ny2 - ny1)
            show_selection_visuals(iid)
            generate_arduino_code()


    def canvas_release(event):
        # ... (implementation) ...
        dragging["active"] = False
        dragging["id"] = None
        dragging["mode"] = None
        
    # ---------------- parse generated Arduino code and apply to canvas ----------------
    def apply_code_to_canvas():
        # ... (implementation) ...
        text = code_area.get("1.0", "end-1c")
        updating_from_code["flag"] = True
        
        for iid in list(elements.keys()):
            canvas.delete(iid)
        elements.clear()
        clear_selection_visuals()
        
        # Rectangles
        rect_patterns = [r"drawRect\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)", r"fillRect\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)"]
        for pat in rect_patterns:
            for m in re.finditer(pat, text):
                x, y, w_rect, h_rect = map(int, m.groups())
                cid = canvas.create_rectangle(PAD + x, PAD + y, PAD + x + w_rect, PAD + y + h_rect, outline="#00FFFF", width=1, tags=("drawn",))
                elements[cid] = Element("rect", cid, x, y, w_rect, h_rect, rotation=0)

        # Circles
        circ_patterns = [r"drawCircle\((\d+),\s*(\d+),\s*(\d+)", r"fillCircle\((\d+),\s*(\d+),\s*(\d+)"]
        for pat in circ_patterns:
            for m in re.finditer(pat, text):
                cx, cy, r = map(int, m.groups())
                cid = canvas.create_oval(PAD + cx - r, PAD + cy - r, PAD + cx + r, PAD + cy + r, outline="#FFA500", width=1, tags=("drawn",))
                elements[cid] = Element("circle", cid, cx - r, cy - r, 2 * r, 2 * r, rotation=0)
                
        # Text (setCursor/print style)
        cursor_prints = re.findall(r"setCursor\((\d+),\s*(\d+)\);\s*display\.print\(\"([^\"]*)\"\)", text)
        for x,y,s in cursor_prints:
            x,y = int(x), int(y)
            cid = canvas.create_text(PAD + x, PAD + y, text=s, anchor="nw", fill="white", font=("Consolas", 10), tags=("drawn",))
            elements[cid] = Element("text", cid, x, y, 0, 0, text=s, rotation=0)

        updating_from_code["flag"] = False
        generate_arduino_code()
        clear_selection_visuals()
        
    # --- GUI Layout ---

    # Left Panel: Editor, Controls, Code
    left = tk.Frame(app, bg="#1E1E1E", width=420)
    left.pack(side="left", fill="y", expand=False)

    tk.Label(left, text="Editor (commands)", bg="#2b2b2b", fg="#FEE715", font=("Consolas", 12, "bold")).pack(fill="x")
    editor = tk.Text(left, bg="#111111", fg="#dcdcdc", insertbackground="white", font=("Consolas", 11), height=10)
    editor.pack(fill="x", padx=8, pady=6)
    editor.insert("1.0", "text 8 8 Hello Simulator\nrect 10 25 80 45\ncircle 100 30 15\n")
    
    # Run button (draw from editor)
    run_btn = tk.Button(left, text="▶ Run Editor Commands", bg="#0E639C", fg="white", font=("Segoe UI", 10, "bold"), command=parse_editor_and_draw)
    run_btn.pack(pady=4)

    # Controls: add elements
    ctl_frame = tk.Frame(left, bg="#1E1E1E")
    ctl_frame.pack(fill="x", padx=8, pady=6)
    tk.Button(ctl_frame, text="Add Rect", command=lambda: add_from_button("rect")).pack(side="left", padx=2)
    tk.Button(ctl_frame, text="Add Circle", command=lambda: add_from_button("circle")).pack(side="left", padx=2)
    tk.Button(ctl_frame, text="Add Text", command=lambda: add_from_button("text")).pack(side="left", padx=2)
    tk.Button(ctl_frame, text="Delete Selected", command=delete_selected).pack(side="left", padx=2, fill="x", expand=True)

    # Generated Arduino code area
    tk.Label(left, text="Generated Arduino Code (Adafruit GFX)", bg="#2b2b2b", fg="#FEE715", font=("Consolas", 12, "bold")).pack(fill="x", pady=(8,0))
    code_area = tk.Text(left, bg="#0b0b0b", fg="#bfbfbf", insertbackground="white", font=("Consolas", 10), height=18)
    code_area.pack(fill="both", expand=True, padx=8, pady=6)

    apply_code_btn = tk.Button(left, text="Apply Code → Canvas (Heuristic Parse)", bg="#F0A500", fg="black", command=apply_code_to_canvas)
    apply_code_btn.pack(pady=4)

    # Right Panel: Canvas Area
    right = tk.Frame(app, bg="#0a0a0a")
    right.pack(side="right", fill="both", expand=True)
    tk.Label(right, text=f"Simulated Display ({width}x{height})", bg="#0a0a0a", fg="#FEE715", font=("Consolas", 12, "bold")).pack(fill="x")

    canvas_w = width + PAD * 2
    canvas_h = height + PAD * 2
    canvas = tk.Canvas(right, width=canvas_w, height=canvas_h, bg="#222222", highlightthickness=0)
    canvas.pack(padx=20, pady=12)

    # Display Border
    canvas.create_rectangle(PAD, PAD, PAD + width, PAD + height, outline="#00FF00", width=2, tags="display_border")

    # --- Wire Events ---
    canvas.bind("<Button-1>", canvas_click)
    canvas.bind("<B1-Motion>", canvas_drag)
    canvas.bind("<ButtonRelease-1>", canvas_release)
    app.bind("<Delete>", lambda e: delete_selected())
    app.bind("<BackSpace>", lambda e: delete_selected())
    # Rotate with arrow keys for demonstration
    app.bind("<Left>", lambda e: rotate_selected(-15))
    app.bind("<Right>", lambda e: rotate_selected(15))
    
    # Initial setup
    parse_editor_and_draw() # Draw initial elements
    
    app.mainloop()