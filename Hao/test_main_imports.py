"""
Test file for main application imports and basic functionality
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Testing main application imports...")

try:
    import importlib
    image_model_module = importlib.import_module("1_image_model")
    scrollable_canvas_module = importlib.import_module("2_scrollable_canvas")
    
    ImageModel = image_model_module.ImageModel
    ScrollableImageCanvas = scrollable_canvas_module.ScrollableImageCanvas
    
    print("✓ Successfully imported ImageModel")
    print("✓ Successfully imported ScrollableImageCanvas")
    
    # Test instantiation
    model = ImageModel()
    print("✓ ImageModel() instantiation works")
    
    # Test that classes are available
    print(f"✓ ImageModel class available: {ImageModel}")
    print(f"✓ ScrollableImageCanvas class available: {ScrollableImageCanvas}")
    
    print("\n✅ All main imports and basic functionality tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
