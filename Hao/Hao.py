import cv2
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as msg
from PIL import Image, ImageTk
import os

# ===================== MODEL =====================
class ImageModel:
    def __init__(self):
        self.original_img = None
        self.current_img = None
        self.img_path = ""

        self.brightness = 0
        self.contrast = 1.0
        self.zoom = 1.0
        self.blur = 0  # must be odd or 0

        self.undo_stack = []
        self.redo_stack = []

    def snapshot(self):
        return {
            "img": self.current_img.copy(),
            "base": self.original_img.copy(),
            "brightness": self.brightness,
            "contrast": self.contrast,
            "zoom": self.zoom,
            "blur": self.blur
        }

    def restore(self, s):
        self.current_img = s["img"]
        self.original_img = s["base"]
        self.brightness = s["brightness"]
        self.contrast = s["contrast"]
        self.zoom = s["zoom"]
        self.blur = s["blur"]

    def push_undo(self):
        if self.current_img is not None and self.original_img is not None:
            self.undo_stack.append(self.snapshot())
            self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return False
        self.redo_stack.append(self.snapshot())
        self.restore(self.undo_stack.pop())
        return True

    def redo(self):
        if not self.redo_stack:
            return False
        self.undo_stack.append(self.snapshot())
        self.restore(self.redo_stack.pop())
        return True

    def open_image(self, path):
        self.img_path = path
        self.original_img = cv2.imread(path)
        self.current_img = self.original_img.copy()

        self.brightness = 0
        self.contrast = 1.0
        self.zoom = 1.0
        self.blur = 0

        self.undo_stack.clear()
        self.redo_stack.clear()

    def apply_all(self):
        if self.original_img is None:
            return

        img = self.original_img.copy()

        if self.blur > 0:
            k = self.blur if self.blur % 2 == 1 else self.blur + 1
            img = cv2.GaussianBlur(img, (k, k), 0)

        img = cv2.convertScaleAbs(
            img,
            alpha=float(self.contrast),
            beta=int(self.brightness)
        )
        self.current_img = img

    # ---------- effects ----------
    def grayscale(self):
        self.push_undo()
        g = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        self.current_img = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        self.original_img = self.current_img.copy()

    def edge(self):
        self.push_undo()
        e = cv2.Canny(self.current_img, 100, 200)
        self.current_img = cv2.cvtColor(e, cv2.COLOR_GRAY2BGR)
        self.original_img = self.current_img.copy()

    def rotate(self, angle):
        self.push_undo()
        if angle == 90:
            self.current_img = cv2.rotate(self.current_img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            self.current_img = cv2.rotate(self.current_img, cv2.ROTATE_180)
        elif angle == 270:
            self.current_img = cv2.rotate(self.current_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.original_img = self.current_img.copy()

    def flip_h(self):
        self.push_undo()
        self.current_img = cv2.flip(self.current_img, 1)
        self.original_img = self.current_img.copy()

    def flip_v(self):
        self.push_undo()
        self.current_img = cv2.flip(self.current_img, 0)
        self.original_img = self.current_img.copy()


# ===================== VIEW =====================
class ImageView:
    def __init__(self, root):
        self.canvas_img = None

        self.canvas = tk.Canvas(root, bg="#444", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, expand=True, fill="both")

        self.status = tk.Label(
            root, text="No image loaded",
            bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def show(self, img, zoom):
        if img is None:
            return

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        w, h = pil.size
        pil = pil.resize((int(w * zoom), int(h * zoom)), Image.LANCZOS)

        self.canvas_img = ImageTk.PhotoImage(pil)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_img)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def update_status(self, model):
        if model.current_img is None:
            self.status.config(text="No image loaded")
        else:
            h, w = model.current_img.shape[:2]
            name = os.path.basename(model.img_path)
            self.status.config(text=f"{name} | {w} × {h}")


# ===================== CONTROLLER =====================
class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.model = ImageModel()

        self.build_menu()
        self.build_toolbar()
        self.view = ImageView(root)

    # ---------- MENU ----------
    def build_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Open", command=self.open_image)
        file.add_command(label="Save", command=self.save)
        file.add_command(label="Save As", command=self.save_as)
        file.add_separator()
        file.add_command(label="Exit", command=self.root.quit)

        edit = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit)
        edit.add_command(label="Undo", command=self.undo)
        edit.add_command(label="Redo", command=self.redo)

    # ---------- TOOLBAR ----------
    def build_toolbar(self):
        bar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        bar.pack(side=tk.TOP, fill=tk.X)

        effects = tk.LabelFrame(bar, text="Effects")
        effects.pack(side=tk.LEFT, padx=6, pady=4)

        tk.Button(effects, text="Grayscale", command=self.grayscale).pack(side=tk.LEFT, padx=3)
        tk.Button(effects, text="Edge", command=self.edge).pack(side=tk.LEFT, padx=3)

        adjust = tk.LabelFrame(bar, text="Adjustments")
        adjust.pack(side=tk.LEFT, padx=6, pady=4)

        self.brightness = tk.Scale(
            adjust, from_=-100, to=100,
            orient=tk.HORIZONTAL, label="Brightness",
            length=140, command=self.on_brightness
        )
        self.brightness.pack(side=tk.LEFT, padx=4)

        self.contrast = tk.Scale(
            adjust, from_=0.5, to=2.0,
            resolution=0.05, orient=tk.HORIZONTAL,
            label="Contrast", length=140,
            command=self.on_contrast
        )
        self.contrast.set(1.0)
        self.contrast.pack(side=tk.LEFT, padx=4)

        self.blur = tk.Scale(
            adjust, from_=0, to=25,
            orient=tk.HORIZONTAL, label="Blur",
            length=140, command=self.on_blur
        )
        self.blur.pack(side=tk.LEFT, padx=4)

        self.zoom = tk.Scale(
            adjust, from_=0.2, to=3.0,
            resolution=0.05, orient=tk.HORIZONTAL,
            label="Zoom", length=140,
            command=self.on_zoom
        )
        self.zoom.set(1.0)
        self.zoom.pack(side=tk.LEFT, padx=4)

        transform = tk.LabelFrame(bar, text="Transform")
        transform.pack(side=tk.LEFT, padx=6, pady=4)

        tk.Button(transform, text="90°", command=lambda: self.rotate(90)).pack(side=tk.LEFT, padx=3)
        tk.Button(transform, text="180°", command=lambda: self.rotate(180)).pack(side=tk.LEFT, padx=3)
        tk.Button(transform, text="270°", command=lambda: self.rotate(270)).pack(side=tk.LEFT, padx=3)
        tk.Button(transform, text="Flip H", command=self.flip_h).pack(side=tk.LEFT, padx=3)
        tk.Button(transform, text="Flip V", command=self.flip_v).pack(side=tk.LEFT, padx=3)

    # ---------- CORE ----------
    def refresh(self):
        self.view.show(self.model.current_img, self.model.zoom)
        self.view.update_status(self.model)

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")]
        )
        if path:
            self.model.open_image(path)
            self.brightness.set(0)
            self.contrast.set(1.0)
            self.zoom.set(1.0)
            self.blur.set(0)
            self.refresh()

    def save(self):
        if self.model.current_img is not None:
            cv2.imwrite(self.model.img_path, self.model.current_img)

    def save_as(self):
        if self.model.current_img is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if path:
            cv2.imwrite(path, self.model.current_img)
            self.model.img_path = path

    def undo(self):
        self.model.undo()
        self.sync()
        self.refresh()

    def redo(self):
        self.model.redo()
        self.sync()
        self.refresh()

    def sync(self):
        self.brightness.set(self.model.brightness)
        self.contrast.set(self.model.contrast)
        self.zoom.set(self.model.zoom)
        self.blur.set(self.model.blur)

    # ---------- ACTIONS ----------
    def grayscale(self):
        self.model.grayscale()
        self.refresh()

    def edge(self):
        self.model.edge()
        self.refresh()

    def rotate(self, a):
        self.model.rotate(a)
        self.refresh()

    def flip_h(self):
        self.model.flip_h()
        self.refresh()

    def flip_v(self):
        self.model.flip_v()
        self.refresh()

    def on_brightness(self, v):
        self.model.brightness = int(float(v))
        self.model.apply_all()
        self.refresh()

    def on_contrast(self, v):
        self.model.contrast = float(v)
        self.model.apply_all()
        self.refresh()

    def on_blur(self, v):
        self.model.push_undo()
        self.model.blur = int(v)
        self.model.apply_all()
        self.refresh()

    def on_zoom(self, v):
        self.model.zoom = float(v)
        self.refresh()


# ===================== RUN =====================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Assignment 3")
    root.geometry("1100x650")
    ImageEditorApp(root)
    root.mainloop()
