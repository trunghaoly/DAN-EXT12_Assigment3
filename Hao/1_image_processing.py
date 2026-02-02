"""
ImageModel class for managing image processing operations.

Handles image state, transformations (brightness, contrast, blur, resize),
and undo/redo functionality using snapshot-based history.
"""
import cv2


class ImageModel:
    """
    Model class for image processing with undo/redo capabilities.
    
    Manages image data, adjustment parameters, and maintains undo/redo stacks
    through snapshot-based state management.
    """
    
    def __init__(self):
        """Initialize image model with default state."""
        # Image data
        self.original_img = None
        self.color_img = None
        self.current_img = None
        self.img_path = ""
        
        # Adjustment parameters
        self.brightness = 0
        self.contrast = 1.0
        self.scale = 1.0
        self.blur = 0
        
        # Undo/Redo history
        self.undo_stack = []
        self.redo_stack = []
        
        # State flags
        self.is_modified = False
        self.is_grayscale = False

    def snapshot(self):
        """Create a snapshot of current state for undo/redo."""
        # Copy image and parameters
        return {
            "base": self.original_img.copy() if self.original_img is not None else None,
            "color": self.color_img.copy() if self.color_img is not None else None,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "scale": self.scale,
            "blur": self.blur,
            "is_grayscale": self.is_grayscale
        }

    def restore(self, s):
        """Restore state from a snapshot."""
        # Skip if snapshot is empty
        if s["base"] is None: 
            return
        
        # Restore all parameters
        self.original_img = s["base"]
        self.color_img = s.get("color")
        self.brightness = s["brightness"]
        self.contrast = s["contrast"]
        self.scale = s["scale"]
        self.blur = s["blur"]
        self.is_grayscale = s.get("is_grayscale", False)
        
        # Reapply transformations
        self.apply_all()

    def push_undo(self):
        """Push current state to undo stack."""
        # Save state only if image exists
        if self.original_img is not None:
            self.undo_stack.append(self.snapshot())
            self.redo_stack.clear()

    def undo(self):
        """Undo last action."""
        # Return False if undo stack is empty
        if not self.undo_stack: 
            return False
        
        # Save current state to redo stack
        self.redo_stack.append(self.snapshot())
        
        # Restore previous state
        self.restore(self.undo_stack.pop())
        return True

    def redo(self):
        """Redo last undone action."""
        # Return False if redo stack is empty
        if not self.redo_stack: 
            return False
        
        # Save current state to undo stack
        self.undo_stack.append(self.snapshot())
        
        # Restore next state
        self.restore(self.redo_stack.pop())
        return True

    def open_image(self, path):
        """Load image from file path."""
        # Read image using OpenCV
        img = cv2.imread(path)
        
        # Raise error if image cannot be read
        if img is None:
            raise ValueError("Cannot read image file")
        
        # Store image path
        self.img_path = path
        
        # Set original image
        self.original_img = img
        
        # Store color version for toggle
        self.color_img = img.copy()
        
        # Reset all parameters to defaults
        self.brightness = 0
        self.contrast = 1.0
        self.scale = 1.0
        self.blur = 0
        self.is_grayscale = False
        
        # Clear undo/redo history
        self.undo_stack.clear()
        self.redo_stack.clear()
        
        # Apply transformations
        self.apply_all()
        
        # Mark as unmodified
        self.is_modified = False

    def apply_all(self):
        """Apply all transformations to generate current image."""
        # Skip if no image loaded
        if self.original_img is None: 
            return
        
        # Copy original image
        img = self.original_img.copy()

        # Apply resize transformation
        if self.scale != 1.0:
            img = cv2.resize(img, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_LINEAR)

        # Apply blur transformation
        if self.blur > 0:
            k = int(self.blur)
            # Ensure kernel size is odd
            k = k if k % 2 == 1 else k + 1
            img = cv2.GaussianBlur(img, (k, k), 0)

        # Apply brightness and contrast
        img = cv2.convertScaleAbs(img, alpha=self.contrast, beta=self.brightness)
        
        # Store result
        self.current_img = img
        
        # Mark as modified
        self.is_modified = True

    def grayscale(self):
        """Convert image to grayscale (apply only once)."""
        # Save state to undo stack
        self.push_undo()
        
        if self.is_grayscale:
            # Toggle back to color
            self.original_img = self.color_img.copy()
            self.is_grayscale = False
        else:
            # Convert to grayscale then back to BGR (3 channels)
            g = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
            self.original_img = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
            self.is_grayscale = True
        
        # Reapply transformations
        self.apply_all()

    def edge(self):
        """Apply edge detection using Canny algorithm."""
        # Save state to undo stack
        self.push_undo()
        
        # Apply Canny edge detection
        e = cv2.Canny(self.original_img, 100, 200)
        
        # Convert edges to BGR format
        self.original_img = cv2.cvtColor(e, cv2.COLOR_GRAY2BGR)
        
        # Reapply transformations
        self.apply_all()

    def rotate(self, angle):
        """Rotate image by specified angle (90, 180, or 270 degrees)."""
        # Save state to undo stack
        self.push_undo()
        
        # Apply rotation based on angle
        if angle == 90: 
            self.original_img = cv2.rotate(self.original_img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180: 
            self.original_img = cv2.rotate(self.original_img, cv2.ROTATE_180)
        elif angle == 270: 
            self.original_img = cv2.rotate(self.original_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        # Reapply transformations
        self.apply_all()

    def flip_h(self):
        """Flip image horizontally."""
        # Save state to undo stack
        self.push_undo()
        
        # Flip horizontally (1 = horizontal axis)
        self.original_img = cv2.flip(self.original_img, 1)
        
        # Reapply transformations
        self.apply_all()

    def flip_v(self):
        """Flip image vertically."""
        # Save state to undo stack
        self.push_undo()
        
        # Flip vertically (0 = vertical axis)
        self.original_img = cv2.flip(self.original_img, 0)
        
        # Reapply transformations
        self.apply_all()
