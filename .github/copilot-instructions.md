# AI Coding Agent Instructions

## Project Overview
**DAN-EXT12_Assigment3** is a collection of assignment projects combining:
1. **Question 1** - Cryptography: Custom encryption/decryption system with Caesar-style shifting
2. **Question 2** - Data Analysis: Temperature data processing from 1986-2005 with seasonal aggregations
3. **Question 3** - GUI Application: Image processing utility with undo/redo functionality

The codebase is organized by contributor (Hao/, assigment 3 EDY/) with Assignment 2 as reference implementation in parent directory.

## Architecture & Data Flow

### Encryption Pipeline (Q1)
- **`_1_encrypt.py`**: Reads `raw_text.txt`, applies 4-case shifting rules (a-m, n-z, A-M, N-Z), generates numeric key
- **`_2_decrypt.py`**: Reverses shifts using key, outputs `decrypted_text.txt`
- **`_3_verify.py`**: Compares decrypted with raw using character-level diff
- **`_4_main.py`**: Orchestrator - imports all modules, handles user input validation (shift1/shift2 as integers), manages exceptions

**Key Pattern**: Sequential workflow with explicit error handling for missing files; returns key string from encryption for decryption dependency.

### Data Processing Pipeline (Q2)
- **`S1_data_load.py`**: Loads all `temperatures/*.csv` files, sorts by year, converts string temps to numeric, concatenates into wide-format DataFrame
- **`S2_data_transform.py`**: Reshapes to long format, adds SEASON column (months→quarters), normalizes data types
- **`S3_result*.py`** (3 files): Generates statistics (seasonal avg, temp range, stability/std-dev), exports to `.txt` files
- **`S4_main_result.py`**: Main entry point - orchestrates S1→S2→S3 pipeline with error checks for empty data

**Key Pattern**: Staged data transformation (S1→S4 naming convention). All month data stored as list in identifier_cols structure. Empty DataFrame checks prevent downstream crashes.

### Image Processing GUI (Q3)
- **`Hao/Hao.py`** (customtkinter): MVC-style - ImageModel class manages state (original/current image, parameters), undo/redo via snapshot/restore
- **`assigment 3 EDY/TK.py`** (tkinter): Alternative implementation with `imgprocess` class and separate `undo_redo` stack handler

**Key Pattern**: State preserved in model, undo implemented via deep copy snapshots (Hao) or separate stack tracking (EDY). Both use cv2.imread() and PIL for display.

## Developer Workflows

### Running Assignment Code
- **Q1 (Encryption)**: `python _4_main.py` from Question 1 directory; prompts for shift1/shift2 integers
- **Q2 (Data)**: `python S4_main_result.py` from Question 2 directory; requires `temperatures/` subfolder with `stations_group_YYYY.csv` files
- **Q3 (GUI)**: `python Hao.py` or `python assigment\ 3\ EDY/TK.py`; opens file dialog for image selection

### File Dependencies
- Q1: Expects `raw_text.txt` in same directory; creates `encrypted_text.txt`, `decrypted_text.txt`
- Q2: Expects `temperatures/` folder relative to script; outputs 3 `.txt` files (Seasonal_Average, Temperature_Range, Temperature_Stability)
- Q3: Uses local `icons/` and image files from Hao directory

## Project-Specific Conventions

### Code Organization
- **Numbered module prefix**: `_1_`, `_2_`, `_3_`, `_4_` indicates execution order (not alphabetical import)
- **S-prefix stages**: S1-S4 denote pipeline stages; S# naming mirrors stage number
- **Contributor folders**: Each person's code in isolated folder; review both Hao/ and EDY/ for context on same feature

### Error Handling Pattern
```python
try:
    # Main workflow
except FileNotFoundError:
    print("ERROR: File or directory not found...")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```
Always catch FileNotFoundError explicitly before generic Exception.

### Data Structure Conventions
- **Q1**: Returns key as string of digits (1-6 mapping character types)
- **Q2**: DataFrames use identifier_cols and month_cols lists; wide format initially, converted to long; years extracted from filename
- **Q3**: Image state stored as dict with keys: "base", "brightness", "contrast", "scale", "blur"

## Integration Points & Dependencies

### External Libraries
- **Q1**: Built-in only (str, ord, chr, file I/O)
- **Q2**: pandas (read_csv, concat, apply, to_numeric), pathlib (Path, glob)
- **Q3**: customtkinter, tkinter, cv2 (OpenCV), PIL (Image, ImageTk, ImageDraw), numpy (in EDY version)

### Cross-Component Communication
- Q1 modules: All write to/read from shared disk files (raw_text.txt, encrypted_text.txt, decrypted_text.txt)
- Q2 modules: DataFrame passed between stages; column structure must match (identifier_cols + month_cols)
- Q3 GUI: Model state encapsulated; no direct GUI↔file I/O (mediated through model methods)

## Critical Implementation Notes

1. **Path Handling**: Use `Path(__file__).resolve().parent` in Q2 to locate relative directories (not hardcoded paths)
2. **Numeric Conversion**: Q2 uses `pd.to_numeric(..., errors="coerce")` to handle non-numeric values gracefully
3. **Deep Copy**: Q3 Hao.py uses `copy.deepcopy()` for undo snapshots; shallow copy will cause aliasing bugs
4. **Key Format**: Q1 encryption key must preserve character-to-shift mapping exactly (1-6 digits) for round-trip decryption
5. **DataFrame Concatenation**: Q2 must use `ignore_index=True` when concatenating years to maintain row continuity
