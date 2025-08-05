# Your PKM Agent

This is a simple Personal Knowledge Management agent that actually works.

## Setup (One Time Only)

1. **Test if it works** - In terminal:
   ```
   python pkm_agent.py
   ```
   If you see "PKM Agent Ready!" then it works. Type `quit` to exit.

2. **Your notes will be stored in:** `C:\MyNotes`
   (It creates this folder automatically)

## How to Use in Cursor with Claude

Just ask me (Claude) things like:

- "Add a note about my project ideas"
- "Search my notes for python"
- "List all my notes"
- "Remember that I prefer dark mode"
- "What do you remember about my preferences?"

I'll run the code for you and show you the results.

## How to Use Standalone

Run in terminal:
```
python pkm_agent.py
```

Commands:
- `add` - Create a new note
- `search` - Search all notes
- `list` - List all notes
- `read` - Read a specific note
- `remember` - Save something to memory
- `recall` - Get info from memory
- `quit` - Exit

## That's It!

No databases. No servers. No complex setup.
Just markdown files in a folder and a simple memory system. 