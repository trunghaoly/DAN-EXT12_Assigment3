import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
from PIL import Image, ImageTk, ImageDraw

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
        self.is_modified = False

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
        img = cv2.imread(path)
        if img is None:
            raise ValueError("Cannot read image file")
        
        self.img_path = path
        self.original_img = img
        self.brightness = 0
        self.contrast = 1.0
        self.scale = 1.0
        self.blur = 0
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.apply_all()
        self.is_modified = False

    def apply_all(self):
        if self.original_img is None: return
        img = self.original_img.copy()

        if self.scale != 1.0:
            img = cv2.resize(img, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_LINEAR)

        if self.blur > 0:
            k = int(self.blur)
            k = k if k % 2 == 1 else k + 1
            img = cv2.GaussianBlur(img, (k, k), 0)

        img = cv2.convertScaleAbs(img, alpha=self.contrast, beta=self.brightness)
        self.current_img = img
        self.is_modified = True

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

class ScrollableImageCanvas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        
        self.h_scroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.current_tk_image = None

    def update_image(self, cv_img):
        if cv_img is None:
            self.canvas.delete("all")
            return

        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        
        self.current_tk_image = ImageTk.PhotoImage(pil)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.current_tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Assignment 3")
        self.geometry("1100x750")
        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)

        self.model = ImageModel()
        self.menu_icons = {}
        self.load_menu_icons()
        self.slider_labels = {} 

        self.build_native_menu()
        self.build_status_bar()
        self.build_controls()
        
        self.image_area = ScrollableImageCanvas(self, fg_color="#1a1a1a", corner_radius=0)
        self.image_area.pack(side="top", fill="both", expand=True)

        self.bind("<Configure>", self.on_resize)

    def load_menu_icons(self):
        icon_names = ["open", "save", "save_as", "undo", "redo", "close"]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "icons") 

        for name in icon_names:
            path = os.path.join(icon_path, f"{name}.png")
            if os.path.exists(path):
                img = Image.open(path)
            else:
                img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                d.rectangle([2,2,18,18], fill="white")
            
            img = img.resize((18, 18), Image.Resampling.LANCZOS)
            if img.mode != 'RGBA': img = img.convert('RGBA')
            r, g, b, a = img.split()
            white_bg = Image.new('RGB', img.size, (255, 255, 255))
            img = Image.merge('RGBA', (*white_bg.split(), a))
            self.menu_icons[name] = ImageTk.PhotoImage(img)

    def build_native_menu(self):
        menu_theme = {"bg": "#2b2b2b", "fg": "white", "activebackground": "#555", "activeforeground": "white", "tearoff": 0, "bd": 0}
        menubar = tk.Menu(self) 
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, **menu_theme)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label=" Open", image=self.menu_icons["open"], compound="left", command=self.open_image)
        file_menu.add_command(label=" Save", image=self.menu_icons["save"], compound="left", command=self.save)
        file_menu.add_command(label=" Save As", image=self.menu_icons["save_as"], compound="left", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label=" Exit", image=self.menu_icons["close"], compound="left", command=self.confirm_exit)

        edit_menu = tk.Menu(menubar, **menu_theme)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label=" Undo", image=self.menu_icons["undo"], compound="left", command=self.undo)
        edit_menu.add_command(label=" Redo", image=self.menu_icons["redo"], compound="left", command=self.redo)

    def build_status_bar(self):
        self.status_frame = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color="#222222")
        self.status_frame.pack(side="bottom", fill="x")
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready", text_color="gray", font=("Arial", 11), anchor="w")
        self.status_label.pack(side="left", padx=10, pady=2)

    def build_controls(self):
        control_frame = ctk.CTkFrame(self, fg_color=("#E0E0E0", "#2B2B2B"), height=160, corner_radius=15)
        control_frame.pack(side="bottom", fill="x", padx=20, pady=10) 

        col1 = ctk.CTkFrame(control_frame, fg_color="transparent")
        col1.pack(side="left", fill="y", padx=20, pady=20)
        ctk.CTkLabel(col1, text="EFFECTS", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        ctk.CTkButton(col1, text="Grayscale", width=100, command=self.grayscale).pack(pady=5)
        ctk.CTkButton(col1, text="Edge Detect", width=100, command=self.edge).pack(pady=5)

        col2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=20, pady=10)
        ctk.CTkLabel(col2, text="ADJUSTMENTS", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))

        def make_slider(parent, name, f, t, default_val, cmd_drag, cmd_rel, show_reset=True):
            sub = ctk.CTkFrame(parent, fg_color="transparent")
            sub.pack(fill="x", pady=2)
            
            lbl_text = f"{name}: {default_val}"
            lbl = ctk.CTkLabel(sub, text=lbl_text, width=110, anchor="w", font=("Arial", 11))
            lbl.pack(side="left")
            self.slider_labels[name] = lbl

            def on_drag_wrapper(val):
                if name == "Blur" or name == "Brightness": display_val = int(val)
                else: display_val = f"{val:.2f}"
                
                self.slider_labels[name].configure(text=f"{name}: {display_val}")
                cmd_drag(val)

            def reset_action():
                slider.set(default_val)
                on_drag_wrapper(default_val) 
                cmd_rel(None)

            if show_reset:
                btn_reset = ctk.CTkButton(sub, text="⟲", width=25, height=20, 
                                          fg_color="transparent", border_width=1, border_color="gray",
                                          text_color=("black", "white"), font=("Arial", 10, "bold"),
                                          command=reset_action)
                btn_reset.pack(side="left", padx=(0, 5))
            else:
                ctk.CTkFrame(sub, width=25, height=20, fg_color="transparent").pack(side="left", padx=(0, 5))

            slider = ctk.CTkSlider(sub, from_=f, to=t, height=18)
            slider.set(default_val)
            slider.pack(side="left", fill="x", expand=True, padx=5)
            
            slider.configure(command=on_drag_wrapper)
            slider.bind("<ButtonRelease-1>", cmd_rel)
            return slider

        self.s_br = make_slider(col2, "Brightness", -100, 100, 0, self.on_br_change, self.on_release, show_reset=True)
        self.s_ct = make_slider(col2, "Contrast", 0.5, 2.0, 1.0, self.on_ct_change, self.on_release, show_reset=True)
        self.s_bl = make_slider(col2, "Blur", 0, 20, 0, self.on_bl_change, self.on_release, show_reset=True)
        self.s_sz = make_slider(col2, "Resize", 0.1, 3.0, 1.0, self.on_sz_change, self.on_release, show_reset=True)

        col3 = ctk.CTkFrame(control_frame, fg_color="transparent")
        col3.pack(side="right", fill="y", padx=20, pady=20)
        ctk.CTkLabel(col3, text="TRANSFORM", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        row = ctk.CTkFrame(col3, fg_color="transparent")
        row.pack(pady=5)
        ctk.CTkButton(row, text="90°", width=60, command=lambda: self.rotate(90)).pack(side="left", padx=2)
        ctk.CTkButton(row, text="Flip H", width=60, command=self.flip_h).pack(side="left", padx=2)
        ctk.CTkButton(row, text="Flip V", width=60, command=self.flip_v).pack(side="left", padx=2)

    def refresh(self):
        if self.model.current_img is None: return
        self.image_area.update_image(self.model.current_img)
        h, w = self.model.current_img.shape[:2]
        
        mod_mark = "*" if self.model.is_modified else ""
        file_name = os.path.basename(self.model.img_path) if self.model.img_path else "Untitled"
        
        self.status_label.configure(text=f"File: {file_name}{mod_mark}  |  Resolution: {w} x {h} px  |  Zoom: {self.model.scale:.1f}x")
        self.title(f"Assignment 3 - {file_name}{mod_mark}")

    def sync_sliders(self):
        self.s_br.set(self.model.brightness)
        self.s_ct.set(self.model.contrast)
        self.s_bl.set(self.model.blur)
        self.s_sz.set(self.model.scale)
        
        self.slider_labels["Brightness"].configure(text=f"Brightness: {self.model.brightness}")
        self.slider_labels["Contrast"].configure(text=f"Contrast: {self.model.contrast:.2f}")
        self.slider_labels["Blur"].configure(text=f"Blur: {self.model.blur}")
        self.slider_labels["Resize"].configure(text=f"Resize: {self.model.scale:.2f}")

    def on_resize(self, event):
        pass
    
    def confirm_exit(self):
        if self.model.is_modified and self.model.current_img is not None:
            answer = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before exiting?")
            if answer is True:
                if self.save(): self.quit()
            elif answer is False:
                self.quit()
        else:
            if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
                self.quit()

    def open_image(self):
        if self.model.is_modified and self.model.current_img is not None:
             answer = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Save before opening new image?")
             if answer is True:
                 if not self.save(): return 
             elif answer is None:
                 return

        p = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.bmp")])
        if p:
            try:
                self.model.open_image(p)
                self.sync_sliders()
                self.refresh()
            except ValueError:
                messagebox.showerror("Error", "Could not load image. The file might be corrupted or unsupported.")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    
    def save(self):
        if self.model.current_img is None:
            messagebox.showwarning("Warning", "No image loaded to save!")
            return False

        if self.model.img_path:
            try:
                cv2.imwrite(self.model.img_path, self.model.current_img)
                self.model.is_modified = False
                self.refresh()
                messagebox.showinfo("Success", "Image saved successfully!")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}")
                return False
        else:
            return self.save_as()
            
    def save_as(self):
        if self.model.current_img is None:
            messagebox.showwarning("Warning", "No image loaded to save!")
            return False
            
        p = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")])
        if p:
            try:
                cv2.imwrite(p, self.model.current_img)
                self.model.img_path = p
                self.model.is_modified = False
                self.refresh()
                messagebox.showinfo("Success", "Image saved successfully!")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}")
                return False
        return False

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
    def on_br_change(self, v): self.model.brightness = int(v); self.model.apply_all(); self.refresh()
    def on_ct_change(self, v): self.model.contrast = float(v); self.model.apply_all(); self.refresh()
    def on_bl_change(self, v): self.model.blur = int(v); self.model.apply_all(); self.refresh()
    def on_sz_change(self, v): self.model.scale = float(v); self.model.apply_all(); self.refresh()

if __name__ == "__main__":
    app = App()
    app.mainloop()