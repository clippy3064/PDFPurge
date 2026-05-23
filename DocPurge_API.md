# DocPurge_API.md - Interface Specifications

## 1. CLI Interface (User Entry)

The tool is executed via `main.py`.

### Command Usage
```bash
python main.py [options]
```

### Arguments
| Flag | Long Form | Description | Default |
| :--- | :--- | :--- | :--- |
| `-i` | `--input` | Path to input folder or specific file | `config.paths.input_dir` |
| `-o` | `--output` | Path to output folder | `config.paths.output_dir` |
| `-c` | `--config` | Path to the `settings.yaml` file | `./config/settings.yaml` |
| `-d` | `--dry-run` | Preview changes without writing files | `false` |
| `-v` | `--verbose` | Enable detailed debug logging | `false` |

---

## 2. Internal Function API

### 2.1 `core.pdf_engine`
**`clean_pdf(input_path: Path, output_path: Path, settings: dict) -> bool`**
- **Input:** Path to source PDF, Path for output, and the settings dictionary.
- **Logic:** Orchestrates the Rasterize $\rightarrow$ Detect $\rightarrow$ Erase $\rightarrow$ Reconstruct flow.
- **Return:** True if successful, False otherwise.

**`_detect_fragments(image: np.ndarray, targets: list) -> list[Box]`**
- **Input:** Preprocessed image and list of words to find.
- **Return:** A list of bounding boxes `(x, y, w, h)`.

### 2.2 `core.word_engine`
**`clean_word(input_path: Path, output_path: Path, settings: dict) -> bool`**
- **Input:** Path to source Word doc, Path for output, and settings.
- **Logic:** Strips shapes, inline shapes, and metadata.
- **Return:** True if successful.

### 2.3 `core.processor`
**`process_directory(root_dir: Path, output_dir: Path, settings: dict)`**
- **Logic:** Walks through the folder tree, identifies file extensions (`.pdf`, `.docx`, `.docm`), and dispatches to the correct engine.

### 2.4 `utils.config_loader`
**`load_config(config_path: Path) -> dict`**
- **Logic:** Reads YAML and returns a typed dictionary. Validates that required keys exist.
