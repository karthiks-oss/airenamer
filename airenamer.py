#!/usr/bin/env python
"""
airenamer - A macOS CLI tool for renaming screenshots
"""

import sys
import re
import os
import base64
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List


def is_screenshot_file(filename: str) -> bool:
    """Check if a file is a macOS screenshot based on naming pattern."""
    screenshot_patterns = [
        r'^Screenshot \d{4}-\d{2}-\d{2} at \d{1,2}\.\d{2}\.\d{2} (AM|PM)\.png$',
        r'^Screen Shot \d{4}-\d{2}-\d{2} at \d{1,2}\.\d{2}\.\d{2} (AM|PM)\.png$',
        r'^CleanShot.*\.png$',
        r'^CleanShot.*\.jpg$',
        r'^CleanShot.*\.jpeg$',
        r'^Screenshot.*\.png$',
        r'^Screen Shot.*\.png$',
    ]
    
    filename_lower = filename.lower()
    if not (filename_lower.endswith('.png') or filename_lower.endswith('.jpg') or 
            filename_lower.endswith('.jpeg')):
        return False
    
    for pattern in screenshot_patterns:
        if re.match(pattern, filename, re.IGNORECASE):
            return True
    
    return False


def analyze_image_with_openai(image_path: Path) -> Optional[str]:
    """Analyze image content using OpenAI Vision API and generate a descriptive filename."""
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ Error: openai package not installed. Install it with: pip install openai")
        return None
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        return None
    
    # Read and encode image
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error reading image file: {e}")
        return None
    
    # Determine image format
    image_format = image_path.suffix.lower()
    if image_format == '.jpg' or image_format == '.jpeg':
        mime_type = 'image/jpeg'
    elif image_format == '.png':
        mime_type = 'image/png'
    else:
        mime_type = 'image/png'  # default
    
    client = OpenAI(api_key=api_key)
    
    try:
        print("🤖 Analyzing image content with OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this screenshot and generate a concise, descriptive filename (without extension). "
                                   "The filename should be: "
                                   "- Short and descriptive (max 50 characters) "
                                   "- Use lowercase letters, numbers, hyphens, and underscores only "
                                   "- No spaces (use hyphens or underscores) "
                                   "- Describe the main content or purpose of the screenshot "
                                   "Examples: 'login-page', 'error-message', 'dashboard-view', 'code-snippet'"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=50
        )
        
        description = response.choices[0].message.content.strip()
        
        # Clean up the description to make it a valid filename
        # Remove any file extension if present
        description = description.split('.')[0]
        # Replace spaces and invalid characters with hyphens
        description = re.sub(r'[^\w\-]', '-', description)
        # Replace multiple hyphens with single hyphen
        description = re.sub(r'-+', '-', description)
        # Remove leading/trailing hyphens
        description = description.strip('-')
        # Limit length
        description = description[:50]
        
        if not description:
            return None
        
        return description.lower()
        
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        return None


def extract_datetime_from_screenshot(filename: str) -> Optional[datetime]:
    """Extract datetime from macOS screenshot filename."""
    # Patterns for different screenshot tools:
    # "Screenshot 2024-01-01 at 10.00.00 AM.png"
    # "CleanShot 2024-01-01 at 10.00.00 AM.png"
    # "CleanShot X 2024-01-01 at 10.00.00 AM.png" (with version)
    patterns = [
        r'(?:Screenshot|CleanShot)(?:\s+\w+)?\s+(\d{4})-(\d{2})-(\d{2})\s+at\s+(\d{1,2})\.(\d{2})\.(\d{2})\s+(AM|PM)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            hour, minute, second = int(match.group(4)), int(match.group(5)), int(match.group(6))
            am_pm = match.group(7).upper()
            
            # Convert to 24-hour format
            if am_pm == 'PM' and hour != 12:
                hour += 12
            elif am_pm == 'AM' and hour == 12:
                hour = 0
            
            try:
                return datetime(year, month, day, hour, minute, second)
            except ValueError:
                continue
    
    return None


def generate_new_name(old_name: str, pattern: str = "datetime", prefix: str = "", 
                      suffix: str = "", file_path: Optional[Path] = None) -> str:
    """Generate a new name for the screenshot."""
    file_ext = Path(old_name).suffix
    base_name = Path(old_name).stem
    
    if pattern == "ai" or pattern == "content":
        # Use OpenAI to analyze image content
        if file_path is None:
            print("⚠️  Warning: File path required for AI pattern. Falling back to datetime.")
            pattern = "datetime"
        else:
            ai_name = analyze_image_with_openai(file_path)
            if ai_name:
                new_name = ai_name
                # Skip to prefix/suffix handling
                if prefix:
                    new_name = f"{prefix}_{new_name}"
                if suffix:
                    new_name = f"{new_name}_{suffix}"
                return f"{new_name}{file_ext}"
            else:
                print("⚠️  Warning: Failed to analyze image. Falling back to datetime.")
                pattern = "datetime"
    
    if pattern == "datetime":
        dt = extract_datetime_from_screenshot(old_name)
        if dt:
            new_name = dt.strftime("%Y-%m-%d_%H-%M-%S")
        else:
            # Fallback to current timestamp
            new_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    elif pattern == "timestamp":
        new_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    elif pattern == "date":
        dt = extract_datetime_from_screenshot(old_name)
        if dt:
            new_name = dt.strftime("%Y-%m-%d")
        else:
            new_name = datetime.now().strftime("%Y-%m-%d")
    else:
        # Custom pattern or keep original
        new_name = base_name
    
    # Add prefix and suffix
    if prefix:
        new_name = f"{prefix}_{new_name}"
    if suffix:
        new_name = f"{new_name}_{suffix}"
    
    return f"{new_name}{file_ext}"


def find_screenshots(directory: Path, recursive: bool = False) -> List[Path]:
    """Find all screenshot files in a directory."""
    screenshots = []
    
    if recursive:
        files = list(directory.glob("**/*.png")) + list(directory.glob("**/*.jpg")) + list(directory.glob("**/*.jpeg"))
    else:
        files = list(directory.glob("*.png")) + list(directory.glob("*.jpg")) + list(directory.glob("*.jpeg"))
    
    for file_path in files:
        if file_path.is_file() and is_screenshot_file(file_path.name):
            screenshots.append(file_path)
    
    return sorted(screenshots)


def rename_screenshot(file_path: Path, new_name: str, dry_run: bool = False) -> bool:
    """Rename a screenshot file."""
    new_path = file_path.parent / new_name
    
    if new_path.exists():
        print(f"⚠️  Warning: {new_name} already exists. Skipping {file_path.name}")
        return False
    
    if dry_run:
        print(f"Would rename: {file_path.name} -> {new_name}")
        return True
    
    try:
        file_path.rename(new_path)
        print(f"✅ Renamed: {file_path.name} -> {new_name}")
        return True
    except Exception as e:
        print(f"❌ Error renaming {file_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Rename macOS screenshots with various naming patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rename a screenshot file with datetime pattern
  airenamer "Screenshot 2024-01-01 at 10.00.00 AM.png"

  # Rename with custom prefix
  airenamer screenshot.png --prefix "project"

  # Dry run to see what would be renamed
  airenamer screenshot.png --dry-run

  # Use date-only pattern
  airenamer screenshot.png --pattern date

  # Use timestamp pattern
  airenamer screenshot.png --pattern timestamp

  # Use AI to analyze content and generate descriptive name
  airenamer screenshot.png --pattern ai

  # Rename all screenshots in a folder
  airenamer --folder ~/Desktop

  # Rename screenshots recursively
  airenamer --folder ~/Desktop --recursive
        """
    )
    
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        help="Path to the screenshot file to rename"
    )
    
    parser.add_argument(
        "--folder", "-f",
        type=str,
        help="Path to folder containing screenshots to rename"
    )
    
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Search for screenshots recursively in subdirectories (only with --folder)"
    )
    
    parser.add_argument(
        "--pattern", "-p",
        choices=["datetime", "timestamp", "date", "ai", "content"],
        default="datetime",
        help="Naming pattern (default: datetime). Use 'ai' or 'content' for OpenAI-based naming."
    )
    
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Prefix to add to new filename"
    )
    
    parser.add_argument(
        "--suffix",
        type=str,
        default="",
        help="Suffix to add to new filename"
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be renamed without actually renaming"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rename even if target file exists (adds number suffix)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.folder:
        parser.error("Either a file path or --folder must be provided")
    
    if args.file and args.folder:
        parser.error("Cannot specify both file and --folder. Use one or the other.")
    
    files_to_process = []
    
    if args.folder:
        # Process folder
        folder_path = Path(args.folder).expanduser()
        if not folder_path.is_absolute():
            folder_path = Path.cwd() / folder_path
        
        if not folder_path.exists():
            print(f"❌ Error: Folder not found: {folder_path}")
            sys.exit(1)
        
        if not folder_path.is_dir():
            print(f"❌ Error: Not a directory: {folder_path}")
            sys.exit(1)
        
        files_to_process = find_screenshots(folder_path, args.recursive)
        
        if not files_to_process:
            print(f"ℹ️  No screenshots found in {folder_path}")
            sys.exit(0)
        
        print(f"Found {len(files_to_process)} screenshot(s) to process\n")
    else:
        # Process single file
        file_path = Path(args.file).expanduser()
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path
        
        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path}")
            sys.exit(1)
        
        if not file_path.is_file():
            print(f"❌ Error: Not a file: {file_path}")
            sys.exit(1)
        
        # Warn if not a screenshot (but allow it)
        if not is_screenshot_file(file_path.name):
            print(f"⚠️  Warning: {file_path.name} doesn't appear to be a screenshot")
            if not args.dry_run:
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    sys.exit(0)
        
        files_to_process = [file_path]
    
    # Process all files
    success_count = 0
    for file_path in files_to_process:
        # Generate new name
        new_name = generate_new_name(
            file_path.name,
            pattern=args.pattern,
            prefix=args.prefix,
            suffix=args.suffix,
            file_path=file_path if args.pattern in ["ai", "content"] else None
        )
        
        # Handle duplicates if force is set
        if args.force:
            base_path = file_path.parent / new_name
            counter = 1
            while base_path.exists():
                name_parts = Path(new_name).stem, Path(new_name).suffix
                new_name = f"{name_parts[0]}_{counter:03d}{name_parts[1]}"
                base_path = file_path.parent / new_name
                counter += 1
        
        # Rename the file
        if rename_screenshot(file_path, new_name, args.dry_run):
            success_count += 1
    
    if args.dry_run:
        print(f"\n💡 This was a dry run. {len(files_to_process)} file(s) would be renamed.")
        print("   Use without --dry-run to actually rename the files.")
    else:
        print(f"\n✅ Successfully processed {success_count} of {len(files_to_process)} file(s).")


if __name__ == "__main__":
    main()

