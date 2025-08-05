import json
import os
import re
from datetime import datetime
from pathlib import Path

# Configuration
BASE_INPUT = Path(r"C:\AI_SecondBrain\exports\temp_extract")
INPUT_JSON = BASE_INPUT / "conversations.json"
CHUNKS_DIR = BASE_INPUT / "splits"
OUTPUT_ROOT = Path(r"C:\AI_SecondBrain\local-ai-packaged\data\personal_vault")
LOG_FILE = Path(r"C:\AI_SecondBrain\scripts\chatgpt_export_log.txt")

# Folder mapping based on keywords
FOLDER_MAP = {
    "ai|model|machine learning|gpt|assistant": OUTPUT_ROOT / "AI_System_Building" / "HowTo_Guides",
    "fpa|prepper|disaster|survival|squad": OUTPUT_ROOT / "FPA_Building" / "Idea_Lists",
    "motorcycle|bike|repair|fix": OUTPUT_ROOT / "Motorcycle_Fixes" / "Fix_Logs",
}
DEFAULT_FOLDER = OUTPUT_ROOT / "AI_System_Building" / "HowTo_Guides"

# Initialize directories and log
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
for folder in FOLDER_MAP.values():
    folder.mkdir(parents=True, exist_ok=True)
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"Log started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def log_message(message):
    """Write to log file and print to console."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

def sanitize_filename(text):
    """Convert text to a safe filename."""
    text = re.sub(r'[^\w\s-]', '', text.strip())[:50]
    text = re.sub(r'\s+', '_', text)
    return text or "Conversation"

def extract_content(content):
    """Recursively extract text from any content structure."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        for key in content:
            result = extract_content(content[key])
            if result:
                return result
    if isinstance(content, list):
        return "\n".join(extract_content(item) for item in content if item).strip()
    return ""

def get_folder(title):
    """Assign folder based on title keywords."""
    title_lower = title.lower()
    for pattern, folder in FOLDER_MAP.items():
        if re.search(pattern, title_lower):
            return folder
    return DEFAULT_FOLDER

def process_conversation(conv, conv_index):
    """Process a single conversation and save to Markdown."""
    global replies_saved, replies_skipped
    title = conv.get("title", "Conversation")
    prompt = title

    # Find user prompt for title
    messages = conv.get("messages", []) or [
        m.get("message", {}) for m in conv.get("mapping", {}).values() if m.get("message")
    ]
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role") or msg.get("author", {}).get("role")
            if role == "user":
                content = msg.get("content", "")
                prompt = extract_content(content)[:50]
                break

    # Extract assistant messages
    assistant_texts = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role") or msg.get("author", {}).get("role")
            if role == "assistant":
                content = msg.get("content", "")
                text = extract_content(content)
                if text:
                    assistant_texts.append(text)

    if not assistant_texts:
        log_message(f"⚠️ Skipped (no assistant replies): {title}")
        log_message(f"  Structure: {json.dumps(conv, indent=2)[:500]}...")
        replies_skipped += 1
        return 0

    # Save to Markdown
    folder = get_folder(title)
    filename = f"{sanitize_filename(prompt)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{conv_index}.md"
    filepath = folder / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {prompt}\n\n")
        f.write("\n\n".join(assistant_texts) + "\n")

    log_message(f"✅ Saved {len(assistant_texts)} replies to {filepath}")
    return len(assistant_texts)

def main():
    """Process all JSON files and generate Markdown."""
    global replies_saved, replies_skipped
    replies_saved = 0
    replies_skipped = 0
    conv_total = 0
    conv_index = 0

    # Load JSON files
    json_files = []
    if INPUT_JSON.exists():
        json_files.append(INPUT_JSON)
    if CHUNKS_DIR.exists():
        json_files.extend(sorted(CHUNKS_DIR.glob("*.json")))
    
    log_message(f"Found {len(json_files)} JSON files to process")

    for file in json_files:
        log_message(f"Processing {file.name}...")
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                data = [data]
            
            for conv in data:
                if not isinstance(conv, dict):
                    log_message(f"⚠️ Skipped invalid conversation in {file.name}: {str(conv)[:50]}")
                    replies_skipped += 1
                    continue
                conv_total += 1
                replies = process_conversation(conv, conv_index)
                replies_saved += replies
                conv_index += 1
        
        except Exception as e:
            log_message(f"❌ Error processing {file.name}: {e}")
            replies_skipped += 1

    # Final summary
    summary = (
        f"✅ DONE: {replies_saved} assistant replies written to {OUTPUT_ROOT}\n"
        f"🗃️ Conversations processed: {conv_total}\n"
        f"⚠️ Skipped: {replies_skipped} (empty or invalid)\n"
        f"📜 Log saved to: {LOG_FILE}"
    )
    log_message(summary)
    
    if replies_saved == 0:
        log_message("❌ WARNING: No assistant messages extracted. Check JSON structure in log.")

if __name__ == "__main__":
    main()