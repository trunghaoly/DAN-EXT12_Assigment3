import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as msg
from PIL import Image, ImageTk
from tkinter import filedialog
import os

original_img = None
current_img = None
img_path = ""

root = tk.Tk()
root.title("Assigment 3")
root.geometry("1000x600")

brightness = 0
contrast = 1.0
undo_stack = []
redo_stack = []

def show_image(cv_img):
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    frame_w = image_frame.winfo_width()
    frame_h = image_frame.winfo_height()
    if frame_w < 10 or frame_h < 10:
        frame_w, frame_h = 800, 500

    img_w, img_h = img.size

    scale = min(frame_w / img_w, frame_h / img_h, 1)

    new_size = (int(img_w * scale), int(img_h * scale))
    img = img.resize(new_size, Image.LANCZOS)
    imgtk = ImageTk.PhotoImage(img)
    image_label.config(image=imgtk)
    image_label.image = imgtk

def update_status():
    global current_img, img_path

    if current_img is None:
        status_bar.config(text="No image loaded")
    else:
        h, w = current_img.shape[:2]

        if img_path:
            filename = os.path.basename(img_path)
        else:
            filename = "Untitled"

        status_bar.config(text=f"{filename} | {w} × {h}")

def open():
    global original_img, current_img, img_path
    img_path = filedialog.askopenfilename(
    filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")]
)
    if img_path:
        original_img = cv2.imread(img_path)
        current_img = original_img.copy()
        show_image(current_img)
        update_status()

def save():
    global current_img, img_path
    if current_img is None:
        msg.showwarning("Warning", "No image to save")
        return

    if img_path == "":
        save_as()
    else:
        cv2.imwrite(img_path, current_img)
        msg.showinfo("Saved", "Image saved successfully")

def save_as():
    global current_img
    if current_img is None:
        msg.showwarning("Warning", "No image to save")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[
            ("JPEG", "*.jpg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp")
        ]
    )

    if path:
        cv2.imwrite(path, current_img)
        msg.showinfo("Saved", f"Image saved to:\n{path}")

def push_undo():
    global undo_stack, redo_stack, current_img
    if current_img is not None:
        undo_stack.append(current_img.copy())
        redo_stack.clear()

def undo():
    global current_img, undo_stack, redo_stack
    if undo_stack:
        redo_stack.append(current_img.copy())
        current_img = undo_stack.pop()
        show_image(current_img)
        update_status()
    else:
        msg.showinfo("Undo", "Nothing to undo")

def redo():
    global current_img, undo_stack, redo_stack
    if redo_stack:
        undo_stack.append(current_img.copy())
        current_img = redo_stack.pop()
        show_image(current_img)
        update_status()
    else:
        msg.showinfo("Redo", "Nothing to redo")


def grayscale():
    global current_img
    if current_img is not None:
        push_undo()
        gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
        current_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        show_image(current_img)
        update_status()

def blur():
    global current_img
    if current_img is not None:
        push_undo()
        current_img = cv2.GaussianBlur(current_img, (9, 9), 0)
        show_image(current_img)
        update_status()

def edge():
    global current_img
    if current_img is not None:
        push_undo()
        current_img = cv2.Canny(current_img, 100, 200)
        show_image(current_img)
        update_status()

def bright_up():
    global current_img, brightness, contrast, original_img
    if current_img is not None: 
        push_undo()
        brightness += 10
        current_img = cv2.convertScaleAbs(original_img, alpha=contrast, beta=brightness)
        show_image(current_img)
        update_status()

def bright_down():
    global current_img, brightness, contrast, original_img
    if current_img is not None:
        push_undo() 
        brightness -= 10
        current_img = cv2.convertScaleAbs(original_img, alpha=contrast, beta=brightness)
        show_image(current_img)
        update_status()

def bright():
    global current_img, brightness, contrast, original_img
    if current_img is not None:
        push_undo() 
        brightness = 10
        current_img = cv2.convertScaleAbs(original_img, alpha=contrast, beta=brightness)
        show_image(current_img)
        update_status()

def cons_up():
    global current_img, brightness, contrast, original_img
    if current_img is not None:
        push_undo() 
        contrast += 0.1
        current_img = cv2.convertScaleAbs(original_img, alpha=contrast, beta=brightness)
        show_image(current_img)
        update_status()

def cons_down():
    global current_img, brightness, contrast, original_img
    if current_img is not None:
        push_undo() 
        contrast -= 0.1
        current_img = cv2.convertScaleAbs(original_img, alpha=contrast, beta=brightness)
        show_image(current_img)
        update_status()

def cons():
    global current_img, brightness, contrast, original_img
    if current_img is not None:
        push_undo() 
        contrast = 1.0
        current_img = cv2.convertScaleAbs(original_img, alpha=contrast, beta=brightness)
        show_image(current_img)
        update_status()

def rotation():
    global current_img
    if current_img is not None:
        push_undo() 
        current_img = cv2.rotate(current_img, cv2.ROTATE_90_CLOCKWISE)
        show_image(current_img)
        update_status()

def flip():
    global current_img
    if current_img is not None:
        push_undo()
        current_img = cv2.flip(current_img, 1)
        show_image(current_img)
        update_status()

def resize():
    global current_img
    if current_img is not None:
        push_undo()
        current_img = cv2.resize(current_img, None, fx=0.5, fy=0.5)
        show_image(current_img)
        update_status()

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar,tearoff=0)
menu_bar.add_cascade(label="File",menu=file_menu)
file_menu.add_command(label="Open",command=open)
file_menu.add_command(label="Save",command=save)
file_menu.add_command(label="Save As",command=save_as)
file_menu.add_separator()
file_menu.add_command(label="Exit",command=root.quit)

edit_menu = tk.Menu(menu_bar,tearoff=0)
menu_bar.add_cascade(label="Edit",menu=edit_menu)
edit_menu.add_command(label="Undo",command=undo)
edit_menu.add_command(label="Redo",command=redo)


toolbar = tk.Frame(root, bd=1, relief=tk.RAISED)

but_grayscale = tk.Button(toolbar,text="Grayscale Conversion",command=grayscale).pack(side=tk.LEFT,padx=2,pady=2)

but_blur = tk.Button(toolbar,text="Blur Effect",command=blur).pack(side=tk.LEFT,padx=2,pady=2)

but_edge = tk.Button(toolbar,text="Edge Detection",command=edge).pack(side=tk.LEFT,padx=2,pady=2)

but_brightness = tk.Button(toolbar,text="Brightness",command=bright).pack(side=tk.LEFT,padx=2,pady=2)

but_brightness = tk.Button(toolbar,text="+",command=bright_up).pack(side=tk.LEFT,padx=2,pady=2)

but_brightness = tk.Button(toolbar,text="-",command=bright_down).pack(side=tk.LEFT,padx=2,pady=2)

but_contrast = tk.Button(toolbar,text="Contrast",command=cons).pack(side=tk.LEFT,padx=2,pady=2)

but_contrast = tk.Button(toolbar,text="+",command=cons_up).pack(side=tk.LEFT,padx=2,pady=2)

but_contrast = tk.Button(toolbar,text="-",command=cons_down).pack(side=tk.LEFT,padx=2,pady=2)

but_rotation = tk.Button(toolbar,text="Image Rotationn",command=rotation).pack(side=tk.LEFT,padx=2,pady=2)

but_flip = tk.Button(toolbar,text="Image Flip",command=flip).pack(side=tk.LEFT,padx=2,pady=2)

but_resize = tk.Button(toolbar,text="Resize/Scale",command=resize).pack(side=tk.LEFT,padx=2,pady=2)

toolbar.pack(side=tk.TOP, fill=tk.X)

image_frame = tk.Frame(root, bg="#444")
image_frame.pack(side="top", expand=True, fill="both")
image_label = tk.Label(
    image_frame,
    text="No image loaded",
    fg="white",
    bg="#444",
    font=("Arial", 14)
)
image_label.pack(expand=True)

status_bar = tk.Label(
    root,
    text="No image loaded",
    bd=1,
    relief=tk.SUNKEN,
    anchor=tk.W
)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()