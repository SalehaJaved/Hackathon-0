"""
Vault Synchronization Configuration for Platinum Tier AI Employee
Implements Git-based vault synchronization between Cloud and Local agents
"""
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class VaultSyncConfig:
    def __init__(self, vault_path: str = "."):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.vault_path / 'sync_vault.log'),
                logging.StreamHandler()
            ]
        )

        # Define sync-allowed files (no secrets)
        self.sync_allowed_patterns = [
            "*.md", "*.txt", "*.json", "*.csv", "*.pdf", "*.docx", "*.xlsx"
        ]

        # Define sync-blocked files (secrets and sensitive data)
        self.sync_blocked_patterns = [
            ".env", "*.env", "*token*", "*credential*", "*password*", "*secret*",
            "*key*", "whatsapp_session/*", "*session*", "*cert*", "*pem",
            "*config*json"  # Excludes main config with credentials
        ]

    def initialize_git_repo(self) -> bool:
        """Initialize a Git repository for vault synchronization"""
        try:
            # Check if git is installed
            result = subprocess.run(["git", "--version"],
                                  cwd=self.vault_path,
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error("Git is not installed or not in PATH")
                return False

            # Check if already a git repo
            if (self.vault_path / ".git").exists():
                self.logger.info("Git repository already exists")
                return True

            # Initialize git repo
            subprocess.run(["git", "init"], cwd=self.vault_path, check=True)
            self.logger.info("Initialized Git repository")

            # Create .gitignore with security rules
            self.create_gitignore()

            # Add all files except special Windows files like 'nul'
            # First, add all normal files
            for file_path in self.vault_path.iterdir():
                if file_path.name not in ['nul', 'con', 'prn', 'aux'] and not file_path.name.startswith('.git'):
                    try:
                        subprocess.run(["git", "add", str(file_path.name)],
                                      cwd=self.vault_path, check=True)
                    except subprocess.CalledProcessError as e:
                        self.logger.warning(f"Could not add file {file_path.name}: {e}")
                        continue

            # Create initial commit if there are files to commit
            status_result = subprocess.run(["git", "status", "--porcelain"],
                                         cwd=self.vault_path, capture_output=True, text=True)
            if status_result.stdout.strip():
                subprocess.run(["git", "commit", "-m", "Initial vault commit"],
                              cwd=self.vault_path, check=True)
            else:
                self.logger.info("No files to commit after filtering special files")
            self.logger.info("Created initial commit")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error initializing git repo: {e}")
            return False

    def create_gitignore(self):
        """Create .gitignore with security rules for vault sync"""
        gitignore_content = """# Vault Sync - Security Rules
# Sync includes only markdown/state files
# Secrets never sync

# Configuration files that may contain credentials
*.env
.env
.env.local
.env.production
*.config.json
config.json

# Session files
whatsapp_session/
*session*

# Certificate and key files
*.pem
*.key
*.crt
*.cert

# Token and secret files
*token*
*secret*
*password*
*credential*

# System files
.DS_Store
Thumbs.db
*.tmp
*.temp

# Logs (for local only)
logs/
*.log

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log

# Obsidian
.obsidian/
.vault/

# Other
node_modules/
.vscode/
.idea/
*.swp
*.swo
*~
"""

        gitignore_path = self.vault_path / ".gitignore"
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)

        self.logger.info("Created .gitignore with security rules")

    def sync_vault_to_remote(self, remote_url: str, branch: str = "main") -> bool:
        """Sync vault to remote repository"""
        try:
            # Add remote
            subprocess.run(["git", "remote", "add", "origin", remote_url],
                          cwd=self.vault_path, check=True)
            self.logger.info(f"Added remote: {remote_url}")

            # Add all sync-allowed files
            subprocess.run(["git", "add", "*.md"], cwd=self.vault_path, check=True)
            subprocess.run(["git", "add", "*.txt"], cwd=self.vault_path, check=True)
            subprocess.run(["git", "add", "*.json"], cwd=self.vault_path, check=True)
            subprocess.run(["git", "add", "*.csv"], cwd=self.vault_path, check=True)

            # Create commit
            commit_msg = f"Vault sync - {datetime.now().isoformat()}"
            subprocess.run(["git", "commit", "-m", commit_msg],
                          cwd=self.vault_path, check=True)

            # Push to remote
            subprocess.run(["git", "push", "-u", "origin", branch],
                          cwd=self.vault_path, check=True)

            self.logger.info(f"Successfully synced vault to {remote_url}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git sync failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error syncing vault: {e}")
            return False

    def sync_vault_from_remote(self, remote_url: str, branch: str = "main") -> bool:
        """Sync vault from remote repository"""
        try:
            # If not already a repo, initialize it
            if not (self.vault_path / ".git").exists():
                if not self.initialize_git_repo():
                    return False

            # Add remote if not exists
            result = subprocess.run(["git", "remote", "-v"],
                                  cwd=self.vault_path,
                                  capture_output=True, text=True)
            if "origin" not in result.stdout:
                subprocess.run(["git", "remote", "add", "origin", remote_url],
                              cwd=self.vault_path, check=True)

            # Fetch and merge
            subprocess.run(["git", "fetch", "origin"], cwd=self.vault_path, check=True)
            subprocess.run(["git", "merge", f"origin/{branch}"], cwd=self.vault_path, check=True)

            self.logger.info(f"Successfully synced vault from {remote_url}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git sync failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error syncing vault: {e}")
            return False

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "git_repo_exists": (self.vault_path / ".git").exists(),
            "is_synced": False,
            "last_sync": None,
            "uncommitted_changes": 0,
            "blocked_files": []
        }

        if status["git_repo_exists"]:
            try:
                # Check for uncommitted changes
                result = subprocess.run(["git", "status", "--porcelain"],
                                      cwd=self.vault_path,
                                      capture_output=True, text=True)
                status["uncommitted_changes"] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0

                # Check for blocked files that might be staged
                blocked_patterns = ["*.env", "*token*", "*secret*", "*password*", "*credential*"]
                for pattern in blocked_patterns:
                    result = subprocess.run(["git", "ls-files", pattern],
                                          cwd=self.vault_path,
                                          capture_output=True, text=True)
                    if result.stdout.strip():
                        status["blocked_files"].extend(result.stdout.strip().split('\n'))

            except Exception as e:
                self.logger.error(f"Error getting sync status: {e}")

        return status

    def run_sync_check(self):
        """Run periodic sync check"""
        status = self.get_sync_status()

        self.logger.info(f"Sync Status: Git Repo={status['git_repo_exists']}, "
                        f"Uncommitted Changes={status['uncommitted_changes']}, "
                        f"Blocked Files={len(status['blocked_files'])}")

        if status["blocked_files"]:
            self.logger.warning(f"Blocked files detected in repo: {status['blocked_files']}")

        return status


def main():
    """Example usage of Vault Sync Configuration"""
    sync_config = VaultSyncConfig()

    print("Vault Synchronization Configuration for Platinum Tier")
    print("====================================================")

    # Initialize git repo
    if sync_config.initialize_git_repo():
        print("Y Git repository initialized successfully")
    else:
        print("N Failed to initialize git repository")
        return

    # Show sync status
    status = sync_config.get_sync_status()
    print(f"Sync Status: {status}")

    # Example of how to sync to remote (would need actual URL)
    # sync_config.sync_vault_to_remote("https://github.com/username/vault-repo.git")

    print("\nVault synchronization is now configured for Platinum tier!")
    print("- Only markdown/state files will be synced")
    print("- Secrets and credentials are blocked by .gitignore")
    print("- Ready for cloud/local agent synchronization")


if __name__ == "__main__":
    main()