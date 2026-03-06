import os
import time
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)

def check_needs_action_folder():
    """Check if /Needs_Action folder contains any files"""
    base_dir = Path(__file__).parent
    needs_action_path = base_dir / "Needs_Action"
    
    if not needs_action_path.exists():
        logging.warning("Needs_Action folder does not exist")
        return False
    
    # Check if folder contains any files
    files = list(needs_action_path.iterdir())
    return len(files) > 0

def run_claude_command():
    """Execute the Claude CLI command to run the process_needs_action skill"""
    try:
        cmd = ["claude", "Run process_needs_action skill"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logging.info(f"Successfully executed Claude command: {result.stdout}")
        else:
            logging.error(f"Error executing Claude command: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logging.error("Claude command timed out after 5 minutes")
    except FileNotFoundError:
        logging.error("Claude CLI not found. Please ensure it's installed and in PATH")
    except Exception as e:
        logging.error(f"Unexpected error running Claude command: {str(e)}")

def main():
    logging.info("Starting orchestrator...")
    
    while True:
        try:
            if check_needs_action_folder():
                logging.info("Found files in Needs_Action folder, triggering Claude command")
                run_claude_command()
            else:
                logging.info("No files in Needs_Action folder, skipping Claude command")
            
            # Wait for 60 seconds before next check
            time.sleep(60)
            
        except KeyboardInterrupt:
            logging.info("Orchestrator stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error in orchestrator loop: {str(e)}")
            # Continue the loop even if there's an error

if __name__ == "__main__":
    main()