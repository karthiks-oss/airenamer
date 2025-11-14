# airenamer

A macOS CLI tool for renaming screenshots with clean, organized naming patterns.

## Features

- 🎯 Automatically detects macOS screenshot files (Screenshot, Screen Shot, CleanShot)
- 📅 Multiple naming patterns (datetime, timestamp, date, AI/content-based)
- 🤖 **AI-powered naming** - Uses OpenAI Vision API to analyze image content and generate descriptive names
- 🧪 Dry-run mode to preview changes
- 🎨 Custom prefix and suffix support
- ⚡ Fast and lightweight

## Installation

### Option 1: Direct Usage (No Installation)

Simply run the script directly:

```bash
python3 airenamer.py --help
```

### Option 2: Install as System Command

1. Make the script executable (already done):
   ```bash
   chmod +x airenamer.py
   ```

2. Create a symlink or copy to a directory in your PATH:
   ```bash
   # Option A: Symlink (recommended)
   sudo ln -s $(pwd)/airenamer.py /usr/local/bin/airenamer
   
   # Option B: Copy
   sudo cp airenamer.py /usr/local/bin/airenamer
   ```

3. Or add to your local bin:
   ```bash
   mkdir -p ~/bin
   cp airenamer.py ~/bin/airenamer
   echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

Or use the installation script:
```bash
./install.sh
```

### Install Dependencies

For AI-powered naming, install the OpenAI package:
```bash
pip install -r requirements.txt
# or
pip install openai
```

### Setup OpenAI API Key

For AI-based naming, you need an OpenAI API key:

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set it as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
3. Add to your `~/.zshrc` or `~/.bash_profile` to make it persistent:
   ```bash
   echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

## Usage

### Basic Usage

**Rename a single screenshot file:**
```bash
airenamer "Screenshot 2024-01-01 at 10.00.00 AM.png"
```

Rename a screenshot in the current directory:
```bash
airenamer screenshot.png
```

Rename with full path:
```bash
airenamer ~/Desktop/Screenshot\ 2024-01-01\ at\ 10.00.00\ AM.png
```

**Rename all screenshots in a folder:**
```bash
airenamer --folder ~/Desktop
```

Rename screenshots recursively (including subdirectories):
```bash
airenamer --folder ~/Desktop --recursive
```

### Naming Patterns

**Datetime pattern** (default): `2024-01-01_10-00-00.png`
```bash
airenamer screenshot.png --pattern datetime
```

**Timestamp pattern**: `20240101_100000.png`
```bash
airenamer screenshot.png --pattern timestamp
```

**Date pattern**: `2024-01-01.png`
```bash
airenamer screenshot.png --pattern date
```

**AI/Content pattern**: Analyzes image content and generates descriptive names (e.g., `login-page.png`, `error-message.png`)
```bash
airenamer screenshot.png --pattern ai
# or
airenamer screenshot.png --pattern content
```

> **Note:** AI pattern requires OpenAI API key. See [Setup OpenAI API Key](#setup-openai-api-key) section.

### Custom Prefix and Suffix

```bash
# Add prefix
airenamer screenshot.png --prefix "project"

# Add suffix
airenamer screenshot.png --suffix "final"

# Both
airenamer screenshot.png --prefix "project" --suffix "v1"
```

### Dry Run

Preview what would be renamed without actually renaming:
```bash
airenamer screenshot.png --dry-run
```

### Force Rename (Handle Duplicates)

If a target filename already exists, add a number suffix:
```bash
airenamer screenshot.png --force
```

## Examples

### Example 1: Basic Rename
```bash
# Preview changes
airenamer "Screenshot 2024-01-01 at 10.00.00 AM.png" --dry-run

# Apply changes
airenamer "Screenshot 2024-01-01 at 10.00.00 AM.png"
```

### Example 2: Rename with Project Prefix
```bash
airenamer screenshot.png --prefix "myproject" --pattern datetime
```

### Example 3: Rename with AI (Content-Based)
```bash
# Analyze image content and generate descriptive name
airenamer screenshot.png --pattern ai

# With prefix
airenamer screenshot.png --pattern ai --prefix "project"
```

### Example 4: Rename All Screenshots in a Folder
```bash
# Rename all screenshots in Desktop
airenamer --folder ~/Desktop

# With dry-run to preview
airenamer --folder ~/Desktop --dry-run

# Recursively rename in subdirectories
airenamer --folder ~/Desktop --recursive
```

### Example 5: Rename Multiple Files with AI (using shell loop)
```bash
# Rename all screenshots with AI analysis
for file in ~/Desktop/Screenshot*.png; do
    airenamer "$file" --pattern ai
done
```

## Default Behavior

- Either a file path or `--folder` must be provided (not both)
- Screenshots are detected by their naming pattern (e.g., "Screenshot YYYY-MM-DD at HH.MM.SS AM.png", "CleanShot YYYY-MM-DD at HH.MM.SS AM.png")
- The default naming pattern is `datetime` (YYYY-MM-DD_HH-MM-SS.png)
- Files are not overwritten unless `--force` is used
- Works with any image file, but warns if it doesn't match screenshot patterns
- When using `--folder`, only files matching screenshot patterns are processed

## Requirements

- Python 3.6+
- macOS (for screenshot detection patterns)
- `openai` package (for AI-based naming): `pip install openai`
- OpenAI API key (for AI-based naming) - Get one at [platform.openai.com](https://platform.openai.com/api-keys)

## License

MIT
