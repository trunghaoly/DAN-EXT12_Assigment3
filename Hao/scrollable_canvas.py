"""
ScrollableImageCanvas class for displaying images with scrollbars.

Provides a canvas with vertical and horizontal scrollbars for viewing
images that may be larger than the available display area.
"""
import tkinter as tk
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk


class ScrollableImageCanvas(ctk.CTkFrame):
    """
    Custom frame widget for displaying images with scrollbars.
    
    Displays images with automatic scaling and provides both vertical
    and horizontal scrollbars for navigation.
    """
    
    def __init__(self, master, **kwargs):
        """Initialize scrollable canvas with configured layout."""
        super().__init__(master, **kwargs)
        
        # Configure grid layout weights for responsiveness
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main canvas
        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create vertical scrollbar
        self.v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        
        # Create horizontal scrollbar
        self.h_scroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        # Bind scrollbars to canvas
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        
        # Store reference to current Tkinter image
        self.current_tk_image = None

    def update_image(self, cv_img):
        """Update canvas to display new image."""
        # Clear canvas if image is None
        if cv_img is None:
            self.canvas.delete("all")
            return

        # Convert BGR to RGB color space
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image format
        pil = Image.fromarray(rgb)
        
        # Convert to Tkinter-compatible format
        self.current_tk_image = ImageTk.PhotoImage(pil)
        
        # Clear previous image
        self.canvas.delete("all")
        
        # Display new image
        self.canvas.create_image(0, 0, anchor="nw", image=self.current_tk_image)
        
        # Update scroll region based on image size
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
