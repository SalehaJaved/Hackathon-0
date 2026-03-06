import os
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

class InboxHandler(FileSystemEventHandler):
    def __init__(self, inbox_folder, needs_action_folder):
        self.inbox_folder = inbox_folder
        self.needs_action_folder = needs_action_folder

    def on_created(self, event):
        if event.is_directory:
            return
        
        # Process the new file
        self.process_new_file(event.src_path)

    def process_new_file(self, file_path):
        try:
            # Extract file information
            original_name = os.path.basename(file_path)
            timestamp = datetime.now().isoformat()
            
            # Define destination paths
            dest_file_path = os.path.join(self.needs_action_folder, original_name)
            
            # Copy file to Needs_Action folder
            shutil.copy2(file_path, dest_file_path)
            
            # Create metadata dictionary
            metadata = {
                "type": "file_drop",
                "original_name": original_name,
                "timestamp": timestamp,
                "status": "pending"
            }
            
            # Create metadata file path (same name with .md extension)
            metadata_file_path = os.path.splitext(dest_file_path)[0] + ".json"
            
            # Write metadata to JSON file
            with open(metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Processed file: {original_name}")
            print(f"Copied to Needs_Action folder")
            print(f"Metadata created: {metadata_file_path}")
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")

def main():
    # Define folder paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    inbox_folder = os.path.join(base_dir, "Inbox")
    needs_action_folder = os.path.join(base_dir, "Needs_Action")
    
    # Create folders if they don't exist
    os.makedirs(inbox_folder, exist_ok=True)
    os.makedirs(needs_action_folder, exist_ok=True)
    
    # Create event handler
    event_handler = InboxHandler(inbox_folder, needs_action_folder)
    
    # Create observer
    observer = Observer()
    observer.schedule(event_handler, inbox_folder, recursive=False)
    
    # Start the observer
    observer.start()
    print(f"Watching {inbox_folder} folder...")
    
    try:
        # Keep the script running
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping file watcher...")
    
    observer.join()

if __name__ == "__main__":
    main()