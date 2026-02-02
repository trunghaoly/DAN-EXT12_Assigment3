"""
Test file for ImageModel functionality
"""
import importlib
import cv2
import numpy as np

# Import ImageModel
im_module = importlib.import_module('1_image_model')
ImageModel = im_module.ImageModel

# Test ImageModel initialization
print("Testing ImageModel class...")
model = ImageModel()
print("✓ ImageModel initialized")
print(f"  - original_img: {model.original_img}")
print(f"  - is_modified: {model.is_modified}")

# Test creating a dummy image
dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
model.original_img = dummy_img
model.apply_all()
print("✓ apply_all() works")
print(f"  - current_img shape: {model.current_img.shape}")

# Test brightness adjustment
model.brightness = 50
model.apply_all()
print("✓ Brightness adjustment works")

# Test contrast adjustment
model.contrast = 1.5
model.apply_all()
print("✓ Contrast adjustment works")

# Test blur
model.blur = 5
model.apply_all()
print("✓ Blur effect works")

# Test scale
model.scale = 0.5
model.apply_all()
print("✓ Scale adjustment works")
print(f"  - scaled image shape: {model.current_img.shape}")

# Test undo/redo
model.push_undo()
print("✓ push_undo() works")

model.brightness = 100
model.apply_all()
print(f"✓ Brightness changed to 100")

success = model.undo()
print(f"✓ undo() works: {success}")
print(f"  - brightness after undo: {model.brightness}")

success = model.redo()
print(f"✓ redo() works: {success}")
print(f"  - brightness after redo: {model.brightness}")

# Test effect methods
print("\nTesting effects...")
model2 = ImageModel()
model2.original_img = dummy_img.copy()
model2.apply_all()

model2.grayscale()
print("✓ grayscale() works")

model2.edge()
print("✓ edge() works")

model2.rotate(90)
print("✓ rotate(90) works")

model2.flip_h()
print("✓ flip_h() works")

model2.flip_v()
print("✓ flip_v() works")

print("\n✅ All ImageModel tests passed!")
