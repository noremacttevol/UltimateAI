import os
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sentence_transformers import SentenceTransformer
from supabase import create_client
import argparse
from datetime import datetime
import hashlib

# Load environment from streamlit secrets
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_watcher.log'),
        logging.StreamHandler()
    ]
)

class DocumentHandler(FileSystemEventHandler):
    def __init__(self):
        self.supabase = create_client(
            st.secrets["SUPABASE_URL"], 
            st.secrets["SUPABASE_KEY"]
        )
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.md', '.txt', '.pdf')):
            self.process_file(event.src_path)
            
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.md', '.txt', '.pdf')):
            self.process_file(event.src_path)
    
    def process_file(self, file_path):
        try:
            logging.info(f"Processing file: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create embedding
            embedding = self.model.encode(content).tolist()
            
            # Create unique ID based on file path and content
            file_id = hashlib.md5(f"{file_path}{content}".encode()).hexdigest()
            
            # Prepare data for Supabase
            data = {
                'id': file_id,
                'url': f"file://{file_path}",
                'content': content,
                'source': 'local_file',
                'file_name': os.path.basename(file_path),
                'summary': content[:200] + "..." if len(content) > 200 else content,
                'embedding': embedding
            }
            
            # Upsert to Supabase
            result = self.supabase.table('crawled_pages').upsert(data).execute()
            logging.info(f"Successfully processed: {file_path}")
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

def scan_once(folder_path):
    """Scan folder once and process all files"""
    handler = DocumentHandler()
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.md', '.txt', '.pdf')):
                file_path = os.path.join(root, file)
                handler.process_file(file_path)

def watch_daemon(folder_path):
    """Watch folder continuously"""
    event_handler = DocumentHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    
    logging.info(f"Started watching: {folder_path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Stopped watching")
    
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='File watcher for AI knowledge base')
    parser.add_argument('--once', action='store_true', help='Scan once and exit')
    parser.add_argument('--daemon', action='store_true', help='Watch continuously')
    
    args = parser.parse_args()
    
    folder_path = r"C:\AI_SecondBrain\personal_vault"
    
    # Create folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    if args.once:
        logging.info("Running one-time scan...")
        scan_once(folder_path)
    elif args.daemon:
        logging.info("Starting daemon mode...")
        watch_daemon(folder_path)
    else:
        print("Use --once for single scan or --daemon for continuous watching")