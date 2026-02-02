"""
Main application class for image editor GUI.

Provides a complete graphical interface for image processing with controls
for effects, adjustments, transformations, and file operations.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
from PIL import Image, ImageTk, ImageDraw
from image_model import ImageModel
from scrollable_canvas import ScrollableImageCanvas


# Set application theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """
    Main application window for image editor.
    
    Manages UI layout, user interactions, file operations, and coordinates
    between the model and view components.
    """
    
    def __init__(self):
        """Initialize main application window."""
        super().__init__()

        # Set window properties
        self.title("Assignment 3")
        self.geometry("1100x750")
        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)

        # Initialize model
        self.model = ImageModel()
        
        # UI state
        self.menu_icons = {}
        self.load_menu_icons()
        self.slider_labels = {} 

        # Build UI components
        self.build_native_menu()
        self.build_status_bar()
        self.build_controls()
        
        # Add image display area
        self.image_area = ScrollableImageCanvas(self, fg_color="#1a1a1a", corner_radius=0)
        self.image_area.pack(side="top", fill="both", expand=True)

        # Bind resize event
        self.bind("<Configure>", self.on_resize)

    def load_menu_icons(self):
        """Load or create menu icons from files."""
        # Icon names to load
        icon_names = ["open", "save", "save_as", "undo", "redo", "close"]
        
        # Get icons directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "icons") 

        # Load or create each icon
        for name in icon_names:
            path = os.path.join(icon_path, f"{name}.png")
            
            # Load from file if exists, otherwise create placeholder
            if os.path.exists(path):
                img = Image.open(path)
            else:
                # Create blank white rectangle as placeholder
                img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                d.rectangle([2,2,18,18], fill="white")
            
            # Resize icon to 18x18 pixels
            img = img.resize((18, 18), Image.Resampling.LANCZOS)
            
            # Ensure RGBA format
            if img.mode != 'RGBA': 
                img = img.convert('RGBA')
            
            # Extract alpha channel
            r, g, b, a = img.split()
            
            # Create white background
            white_bg = Image.new('RGB', img.size, (255, 255, 255))
            
            # Combine with alpha for proper display
            img = Image.merge('RGBA', (*white_bg.split(), a))
            
            # Convert to PhotoImage
            self.menu_icons[name] = ImageTk.PhotoImage(img)

    def build_native_menu(self):
        """Build native menu bar with File and Edit menus."""
        # Menu styling
        menu_theme = {
            "bg": "#2b2b2b", 
            "fg": "white", 
            "activebackground": "#555", 
            "activeforeground": "white", 
            "tearoff": 0, 
            "bd": 0
        }
        
        # Create menu bar
        menubar = tk.Menu(self) 
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, **menu_theme)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label=" Open", image=self.menu_icons["open"], compound="left", command=self.open_image)
        file_menu.add_command(label=" Save", image=self.menu_icons["save"], compound="left", command=self.save)
        file_menu.add_command(label=" Save As", image=self.menu_icons["save_as"], compound="left", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label=" Exit", image=self.menu_icons["close"], compound="left", command=self.confirm_exit)

        # Edit menu
        edit_menu = tk.Menu(menubar, **menu_theme)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label=" Undo", image=self.menu_icons["undo"], compound="left", command=self.undo)
        edit_menu.add_command(label=" Redo", image=self.menu_icons["redo"], compound="left", command=self.redo)

    def build_status_bar(self):
        """Build status bar at bottom of window."""
        # Create status frame
        self.status_frame = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color="#222222")
        self.status_frame.pack(side="bottom", fill="x")
        
        # Create status label
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready", 
            text_color="gray", 
            font=("Arial", 11), 
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=2)

    def build_controls(self):
        """Build control panel with effects, adjustments, and transformations."""
        # Main control frame
        control_frame = ctk.CTkFrame(
            self, 
            fg_color=("#E0E0E0", "#2B2B2B"), 
            height=160, 
            corner_radius=15
        )
        control_frame.pack(side="bottom", fill="x", padx=20, pady=10) 

        # Left column - Effects
        col1 = ctk.CTkFrame(control_frame, fg_color="transparent")
        col1.pack(side="left", fill="y", padx=20, pady=20)
        
        # Effects section
        ctk.CTkLabel(col1, text="EFFECTS", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        ctk.CTkButton(col1, text="Grayscale", width=100, command=self.grayscale).pack(pady=5)
        ctk.CTkButton(col1, text="Edge Detect", width=100, command=self.edge).pack(pady=5)

        # Middle column - Adjustments
        col2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=20, pady=10)
        
        # Adjustments section label
        ctk.CTkLabel(col2, text="ADJUSTMENTS", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))

        # Helper function to create slider with label and reset button
        def make_slider(parent, name, f, t, default_val, cmd_drag, cmd_rel, show_reset=True):
            """Create slider widget with label and optional reset button."""
            # Create container frame
            sub = ctk.CTkFrame(parent, fg_color="transparent")
            sub.pack(fill="x", pady=2)
            
            # Create label with current value
            lbl_text = f"{name}: {default_val}"
            lbl = ctk.CTkLabel(sub, text=lbl_text, width=110, anchor="w", font=("Arial", 11))
            lbl.pack(side="left")
            self.slider_labels[name] = lbl

            # Update label text on drag
            def on_drag_wrapper(val):
                # Format value for display
                if name == "Blur" or name == "Brightness": 
                    display_val = int(val)
                else: 
                    display_val = f"{val:.2f}"
                
                # Update label
                self.slider_labels[name].configure(text=f"{name}: {display_val}")
                
                # Call drag callback
                cmd_drag(val)

            # Reset button action
            def reset_action():
                # Reset slider to default
                slider.set(default_val)
                
                # Update label
                on_drag_wrapper(default_val) 
                
                # Call release callback
                cmd_rel(None)

            # Create reset button if needed
            if show_reset:
                btn_reset = ctk.CTkButton(
                    sub, 
                    text="⟲", 
                    width=25, 
                    height=20, 
                    fg_color="transparent", 
                    border_width=1, 
                    border_color="gray",
                    text_color=("black", "white"), 
                    font=("Arial", 10, "bold"),
                    command=reset_action
                )
                btn_reset.pack(side="left", padx=(0, 5))
            else:
                # Placeholder for alignment
                ctk.CTkFrame(sub, width=25, height=20, fg_color="transparent").pack(side="left", padx=(0, 5))

            # Create and configure slider
            slider = ctk.CTkSlider(sub, from_=f, to=t, height=18)
            slider.set(default_val)
            slider.pack(side="left", fill="x", expand=True, padx=5)
            
            # Bind slider events
            slider.configure(command=on_drag_wrapper)
            slider.bind("<ButtonRelease-1>", cmd_rel)
            
            return slider

        # Create adjustment sliders
        self.s_br = make_slider(col2, "Brightness", -100, 100, 0, self.on_br_change, self.on_release, show_reset=True)
        self.s_ct = make_slider(col2, "Contrast", 0.5, 2.0, 1.0, self.on_ct_change, self.on_release, show_reset=True)
        self.s_bl = make_slider(col2, "Blur", 0, 20, 0, self.on_bl_change, self.on_release, show_reset=True)
        self.s_sz = make_slider(col2, "Resize", 0.1, 3.0, 1.0, self.on_sz_change, self.on_release, show_reset=True)

        # Right column - Transformations
        col3 = ctk.CTkFrame(control_frame, fg_color="transparent")
        col3.pack(side="right", fill="y", padx=20, pady=20)
        
        # Transformations section
        ctk.CTkLabel(col3, text="TRANSFORM", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        
        # Button row
        row = ctk.CTkFrame(col3, fg_color="transparent")
        row.pack(pady=5)
        ctk.CTkButton(row, text="90°", width=60, command=lambda: self.rotate(90)).pack(side="left", padx=2)
        ctk.CTkButton(row, text="Flip H", width=60, command=self.flip_h).pack(side="left", padx=2)
        ctk.CTkButton(row, text="Flip V", width=60, command=self.flip_v).pack(side="left", padx=2)

    def refresh(self):
        """Update display and status information."""
        # Skip if no image loaded
        if self.model.current_img is None: 
            return
        
        # Update canvas with current image
        self.image_area.update_image(self.model.current_img)
        
        # Get image dimensions
        h, w = self.model.current_img.shape[:2]
        
        # Format modified indicator
        mod_mark = "*" if self.model.is_modified else ""
        
        # Get filename for display
        file_name = os.path.basename(self.model.img_path) if self.model.img_path else "Untitled"
        
        # Update status bar with file info and image stats
        self.status_label.configure(
            text=f"File: {file_name}{mod_mark}  |  Resolution: {w} x {h} px  |  Zoom: {self.model.scale:.1f}x"
        )
        
        # Update window title
        self.title(f"Assignment 3 - {file_name}{mod_mark}")

    def sync_sliders(self):
        """Synchronize slider positions with model values."""
        # Update slider positions
        self.s_br.set(self.model.brightness)
        self.s_ct.set(self.model.contrast)
        self.s_bl.set(self.model.blur)
        self.s_sz.set(self.model.scale)
        
        # Update slider labels
        self.slider_labels["Brightness"].configure(text=f"Brightness: {self.model.brightness}")
        self.slider_labels["Contrast"].configure(text=f"Contrast: {self.model.contrast:.2f}")
        self.slider_labels["Blur"].configure(text=f"Blur: {self.model.blur}")
        self.slider_labels["Resize"].configure(text=f"Resize: {self.model.scale:.2f}")

    def on_resize(self, event):
        """Handle window resize event."""
        pass
    
    def confirm_exit(self):
        """Ask user to save before exiting if there are unsaved changes."""
        # Check for unsaved changes
        if self.model.is_modified and self.model.current_img is not None:
            # Ask user about saving
            answer = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "You have unsaved changes. Do you want to save before exiting?"
            )
            
            # Handle user response
            if answer is True:
                # Save and exit if successful
                if self.save(): 
                    self.quit()
            elif answer is False:
                # Exit without saving
                self.quit()
        else:
            # Ask confirmation if no changes
            if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
                self.quit()

    def open_image(self):
        """Open image file dialog and load image."""
        # Check for unsaved changes
        if self.model.is_modified and self.model.current_img is not None:
            # Ask about saving
            answer = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "You have unsaved changes. Save before opening new image?"
            )
            
            # Handle user response
            if answer is True:
                # Cancel if save failed
                if not self.save(): 
                    return 
            elif answer is None:
                # Cancel operation
                return

        # Show file dialog
        p = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.bmp")])
        
        # Load image if selected
        if p:
            try:
                # Load image
                self.model.open_image(p)
                
                # Update UI
                self.sync_sliders()
                self.refresh()
            except ValueError:
                # Handle corrupted files
                messagebox.showerror("Error", "Could not load image. The file might be corrupted or unsupported.")
            except Exception as e:
                # Handle other errors
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    
    def save(self):
        """Save image to current file path."""
        # Check if image exists
        if self.model.current_img is None:
            messagebox.showwarning("Warning", "No image loaded to save!")
            return False

        # Save to existing path
        if self.model.img_path:
            try:
                # Write image
                cv2.imwrite(self.model.img_path, self.model.current_img)
                
                # Update state
                self.model.is_modified = False
                
                # Update display
                self.refresh()
                
                # Show success message
                messagebox.showinfo("Success", "Image saved successfully!")
                return True
            except Exception as e:
                # Handle save error
                messagebox.showerror("Error", f"Could not save image: {e}")
                return False
        else:
            # No path set, use Save As
            return self.save_as()
            
    def save_as(self):
        """Save image to new file path."""
        # Check if image exists
        if self.model.current_img is None:
            messagebox.showwarning("Warning", "No image loaded to save!")
            return False
            
        # Show save dialog
        p = filedialog.asksaveasfilename(
            defaultextension=".jpg", 
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")]
        )
        
        # Save if path selected
        if p:
            try:
                # Write image
                cv2.imwrite(p, self.model.current_img)
                
                # Update path and state
                self.model.img_path = p
                self.model.is_modified = False
                
                # Update display
                self.refresh()
                
                # Show success message
                messagebox.showinfo("Success", "Image saved successfully!")
                return True
            except Exception as e:
                # Handle save error
                messagebox.showerror("Error", f"Could not save image: {e}")
                return False
        
        return False

    def undo(self):
        """Undo last action."""
        # Execute undo and refresh if successful
        if self.model.undo(): 
            self.sync_sliders()
            self.refresh()
    
    def redo(self):
        """Redo last undone action."""
        # Execute redo and refresh if successful
        if self.model.redo(): 
            self.sync_sliders()
            self.refresh()

    def grayscale(self):
        """Apply grayscale effect."""
        # Apply and refresh
        self.model.grayscale()
        self.refresh()
    
    def edge(self):
        """Apply edge detection effect."""
        # Apply and refresh
        self.model.edge()
        self.refresh()
    
    def rotate(self, a):
        """Rotate image by angle."""
        # Apply and refresh
        self.model.rotate(a)
        self.refresh()
    
    def flip_h(self):
        """Flip image horizontally."""
        # Apply and refresh
        self.model.flip_h()
        self.refresh()
    
    def flip_v(self):
        """Flip image vertically."""
        # Apply and refresh
        self.model.flip_v()
        self.refresh()

    def on_release(self, e):
        """Handle slider release event."""
        # Push undo state after slider adjustment
        self.model.push_undo()
    
    def on_br_change(self, v):
        """Handle brightness slider change."""
        # Update brightness and refresh
        self.model.brightness = int(v)
        self.model.apply_all()
        self.refresh()
    
    def on_ct_change(self, v):
        """Handle contrast slider change."""
        # Update contrast and refresh
        self.model.contrast = float(v)
        self.model.apply_all()
        self.refresh()
    
    def on_bl_change(self, v):
        """Handle blur slider change."""
        # Update blur and refresh
        self.model.blur = int(v)
        self.model.apply_all()
        self.refresh()
    
    def on_sz_change(self, v):
        """Handle resize slider change."""
        # Update scale and refresh
        self.model.scale = float(v)
        self.model.apply_all()
        self.refresh()


if __name__ == "__main__":
    # Create and run application
    app = App()
    app.mainloop()
