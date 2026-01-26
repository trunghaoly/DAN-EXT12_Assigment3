import cv2
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as msg
from PIL import Image, ImageTk
import os

class ImageModel:
    def __init__(self):
        self.original_img = None
        self.current_img = None
        self.img_path = ""
        self.brightness = 0
        self.contrast = 1.0
        self.scale = 1.0
        self.blur = 0
        self.undo_stack = []
        self.redo_stack = []

    def snapshot(self):
        return {
            "base": self.original_img.copy() if self.original_img is not None else None,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "scale": self.scale,
            "blur": self.blur
        }

    def restore(self, s):
        if s["base"] is None: return
        self.original_img = s["base"]
        self.brightness = s["brightness"]
        self.contrast = s["contrast"]
        self.scale = s["scale"]
        self.blur = s["blur"]
        self.apply_all()

    def push_undo(self):
        if self.original_img is not None:
            self.undo_stack.append(self.snapshot())
            self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack: return False
        self.redo_stack.append(self.snapshot())
        self.restore(self.undo_stack.pop())
        return True

    def redo(self):
        if not self.redo_stack: return False
        self.undo_stack.append(self.snapshot())
        self.restore(self.redo_stack.pop())
        return True

    def open_image(self, path):
        self.img_path = path
        self.original_img = cv2.imread(path)
        self.brightness = 0
        self.contrast = 1.0
        self.scale = 1.0
        self.blur = 0
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.apply_all()

    def apply_all(self):
        if self.original_img is None: return
        img = self.original_img.copy()

        if self.scale != 1.0:
            img = cv2.resize(img, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_LINEAR)

        if self.blur > 0:
            k = self.blur if self.blur % 2 == 1 else self.blur + 1
            img = cv2.GaussianBlur(img, (k, k), 0)

        img = cv2.convertScaleAbs(img, alpha=self.contrast, beta=self.brightness)
        self.current_img = img

    def grayscale(self):
        self.push_undo()
        g = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        self.original_img = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        self.apply_all()

    def edge(self):
        self.push_undo()
        e = cv2.Canny(self.original_img, 100, 200)
        self.original_img = cv2.cvtColor(e, cv2.COLOR_GRAY2BGR)
        self.apply_all()

    def rotate(self, angle):
        self.push_undo()
        if angle == 90: self.original_img = cv2.rotate(self.original_img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180: self.original_img = cv2.rotate(self.original_img, cv2.ROTATE_180)
        elif angle == 270: self.original_img = cv2.rotate(self.original_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.apply_all()

    def flip_h(self):
        self.push_undo()
        self.original_img = cv2.flip(self.original_img, 1)
        self.apply_all()

    def flip_v(self):
        self.push_undo()
        self.original_img = cv2.flip(self.original_img, 0)
        self.apply_all()


class ImageView:
    def __init__(self, root):
        self.canvas_img = None
        self.canvas_frame = tk.Frame(root, bg="#333")
        self.canvas_frame.pack(side=tk.TOP, expand=True, fill="both")

        self.canvas = tk.Canvas(self.canvas_frame, bg="#333", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, expand=True, fill="both")

        self.status = tk.Label(root, text="No image loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#ccc")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def show(self, img):
        if img is None:
            self.canvas.delete("all")
            return
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        self.canvas_img = ImageTk.PhotoImage(pil)
        
        self.canvas.delete("all")
        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()
        if c_w < 10: c_w = 800 
        if c_h < 10: c_h = 600
        
        self.canvas.create_image(c_w//2, c_h//2, anchor="center", image=self.canvas_img)

    def update_status(self, model):
        if model.current_img is None:
            self.status.config(text="No image loaded")
        else:
            h, w = model.current_img.shape[:2]
            name = os.path.basename(model.img_path) if model.img_path else "Untitled"
            self.status.config(text=f"{name} | {w}x{h} | Zoom: {model.scale:.1f}x")


class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.model = ImageModel()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_dir = os.path.join(base_dir, "icon")
        self.icons = {} 

        self.preload_icons()
        self.build_menu()
        self.build_toolbar()
        
        self.view = ImageView(root)
        self.root.bind("<Configure>", lambda e: self.refresh() if self.model.current_img is not None else None)

    def preload_icons(self):
        icon_files = {
            "open": "open.png",
            "save": "save.png",
            "save_as": "save_as.png",
            "close": "close.png",
            "undo": "undo.png",
            "redo": "redo.png"
        }
        
        for key, filename in icon_files.items():
            path = os.path.join(self.icon_dir, filename)
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path).resize((20, 20), Image.Resampling.LANCZOS)
                    self.icons[key] = ImageTk.PhotoImage(pil_img)
                except Exception:
                    pass

    def build_menu(self):
        menu_conf = {
            "bg": "#2b2b2b",
            "fg": "white",
            "activebackground": "#555",
            "activeforeground": "white",
            "tearoff": 0
        }

        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, **menu_conf)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label=" Open", image=self.icons.get("open"), compound=tk.LEFT, command=self.open_image)
        file_menu.add_command(label=" Save", image=self.icons.get("save"), compound=tk.LEFT, command=self.save)
        file_menu.add_command(label=" Save As", image=self.icons.get("save_as"), compound=tk.LEFT, command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label=" Exit", image=self.icons.get("close"), compound=tk.LEFT, command=self.root.quit)

        edit_menu = tk.Menu(menu_bar, **menu_conf)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        edit_menu.add_command(label=" Undo", image=self.icons.get("undo"), compound=tk.LEFT, command=self.undo)
        edit_menu.add_command(label=" Redo", image=self.icons.get("redo"), compound=tk.LEFT, command=self.redo)

    def build_toolbar(self):
        bar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        bar.pack(side=tk.TOP, fill=tk.X)

        effects = tk.LabelFrame(bar, text="Effects")
        effects.pack(side=tk.LEFT, padx=6)
        tk.Button(effects, text="Grayscale", command=self.grayscale).pack(side=tk.LEFT, padx=3)
        tk.Button(effects, text="Edge", command=self.edge).pack(side=tk.LEFT, padx=3)

        adjust = tk.LabelFrame(bar, text="Adjustments")
        adjust.pack(side=tk.LEFT, padx=6)

        def create_scale(parent, lbl, from_, to_, res, var_setter, release_setter):
            s = tk.Scale(parent, from_=from_, to=to_, resolution=res, orient=tk.HORIZONTAL, label=lbl, length=120)
            s.pack(side=tk.LEFT)
            s.bind("<B1-Motion>", var_setter)
            s.bind("<ButtonRelease-1>", release_setter)
            return s

        self.scale_br = create_scale(adjust, "Brightness", -100, 100, 1, self.on_brightness_change, self.on_release)
        self.scale_ct = create_scale(adjust, "Contrast", 0.5, 2.0, 0.05, self.on_contrast_change, self.on_release)
        self.scale_ct.set(1.0)
        self.scale_bl = create_scale(adjust, "Blur", 0, 25, 1, self.on_blur_change, self.on_release)
        self.scale_sz = create_scale(adjust, "Resize", 0.2, 3.0, 0.1, self.on_resize_change, self.on_release)
        self.scale_sz.set(1.0)

        transform = tk.LabelFrame(bar, text="Transform")
        transform.pack(side=tk.LEFT, padx=6)
        tk.Button(transform, text="90°", command=lambda: self.rotate(90)).pack(side=tk.LEFT, padx=2)
        tk.Button(transform, text="Flip H", command=self.flip_h).pack(side=tk.LEFT, padx=2)
        tk.Button(transform, text="Flip V", command=self.flip_v).pack(side=tk.LEFT, padx=2)

    def refresh(self):
        self.view.show(self.model.current_img)
        self.view.update_status(self.model)

    def sync_sliders(self):
        self.scale_br.set(self.model.brightness)
        self.scale_ct.set(self.model.contrast)
        self.scale_bl.set(self.model.blur)
        self.scale_sz.set(self.model.scale)

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if path:
            self.model.open_image(path)
            self.sync_sliders()
            self.refresh()

    def save(self):
        if self.model.current_img is not None:
            if self.model.img_path:
                cv2.imwrite(self.model.img_path, self.model.current_img)
                msg.showinfo("Success", "Image saved!")
            else: self.save_as()

    def save_as(self):
        if self.model.current_img is None: return
        path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if path:
            cv2.imwrite(path, self.model.current_img)
            if not self.model.img_path: self.model.img_path = path
            self.refresh()

    def undo(self):
        if self.model.undo(): self.sync_sliders(); self.refresh()

    def redo(self):
        if self.model.redo(): self.sync_sliders(); self.refresh()

    def grayscale(self): self.model.grayscale(); self.refresh()
    def edge(self): self.model.edge(); self.refresh()
    def rotate(self, a): self.model.rotate(a); self.refresh()
    def flip_h(self): self.model.flip_h(); self.refresh()
    def flip_v(self): self.model.flip_v(); self.refresh()

    def on_release(self, e): self.model.push_undo()

    def on_brightness_change(self, e): 
        self.model.brightness = int(self.scale_br.get())
        self.model.apply_all(); self.refresh()
    def on_contrast_change(self, e): 
        self.model.contrast = float(self.scale_ct.get())
        self.model.apply_all(); self.refresh()
    def on_blur_change(self, e): 
        self.model.blur = int(self.scale_bl.get())
        self.model.apply_all(); self.refresh()
    def on_resize_change(self, e): 
        self.model.scale = float(self.scale_sz.get())
        self.model.apply_all(); self.refresh()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Assignment 3")
    root.geometry("1100x700")
    root.configure(bg="#333") 
    ImageEditorApp(root)
    root.mainloop()