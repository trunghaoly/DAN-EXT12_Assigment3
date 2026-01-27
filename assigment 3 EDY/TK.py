import tkinter as tk 
from tkinter import filedialog, messagebox, Menu
import cv2
import numpy as num
from PIL import Image, ImageTk  
import copy

class imgprocess:
    def __init__(self):
        self.crunnet_image = None
        self.original_image = None

    def load_img(self, path):
        self.original_image = cv2.imread(path)
        if self.original_image is not None:
            return False
        self.crunnet_image = self.original_image.copy()
        return True
    def apply_blur(self,path):
        if self.crunnet_image is None:
            return False
        self.crunnet_image = cv2.GaussianBlur(self.crunnet_image, (15, 15), 0)
        return True
    
    def grayscale(self,path):
        if self.crunnet_image is None:
            return False
        self.crunnet_image = cv2.cvtColor(self.crunnet_image, cv2.COLOR_BGR2GRAY)
        self.crunnet_image = cv2.cvtColor(self.crunnet_image, cv2.COLOR_GRAY2BGR)
        return True
    def save_img(  self, path):
        if self.crunnet_image is None:
            return False
        cv2.imwrite(path, self.crunnet_image)
        return True
    
class undo_redo:
    def __init__(self, max_history=10):
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = max_history
    
    def push(self, image):
        self.undo_stack.append(copy.deepcopy(image))
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            return self.undo_stack[-1]
        return None
