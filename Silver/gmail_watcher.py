"""
Gmail Watcher for the Personal AI Employee Hackathon

This script monitors Gmail for new important messages and creates action files
in the /Needs_Action folder when relevant messages are detected.
"""

import time
import logging
from pathlib import Path
from datetime import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

class GmailWatcher:
    def __init__(self, vault_path: str, credentials_path: str = None):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = 120  # 2 minutes
        self.processed_ids = set()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Initialize Gmail service
        self.service = self._authenticate(credentials_path)

        # Load previously processed IDs from a file to avoid reprocessing
        self._load_processed_ids()

    def _authenticate(self, credentials_path: str = None):
        """Authenticate with Gmail API using OAuth2"""
        creds = None

        # Use default token file or provided credentials path
        token_path = self.vault_path / 'token.json'
        credentials_path = credentials_path or self.vault_path / 'credentials.json'

        # Load existing credentials
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            except ValueError:
                self.logger.warning("Invalid token file, will need to re-authenticate")

        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    self.logger.error("Refresh token expired. Please re-authenticate.")
                    creds = None
            else:
                creds = None

            if not creds:
                if not credentials_path.exists():
                    self.logger.error(f"Credentials file not found: {credentials_path}")
                    self.logger.error("Please follow Gmail API setup instructions to create credentials.json")
                    return None

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def _load_processed_ids(self):
        """Load previously processed message IDs to avoid reprocessing"""
        processed_file = self.vault_path / 'processed_gmail_ids.json'
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    self.processed_ids = set(json.load(f))
            except (json.JSONDecodeError, FileNotFoundError):
                self.processed_ids = set()

    def _save_processed_ids(self):
        """Save processed message IDs to file"""
        processed_file = self.vault_path / 'processed_gmail_ids.json'
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def check_for_updates(self):
        """Check for new important messages in Gmail"""
        if not self.service:
            self.logger.error("Gmail service not available")
            return []

        try:
            # Query for unread important messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important after:2024-01-01'
            ).execute()
            messages = results.get('messages', [])

            # Filter out already processed messages
            new_messages = []
            for message in messages:
                if message['id'] not in self.processed_ids:
                    new_messages.append(message)

            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []

    def create_action_file(self, message):
        """Create an action file in the Needs_Action folder"""
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me', id=message['id']
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}

            # Extract message snippet
            snippet = msg.get('snippet', 'No content available')

            # Create action file content
            content = f"""---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {headers.get('Date', datetime.now().isoformat())}
priority: high
status: pending
gmail_id: {message['id']}
---

## Email Content
{snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Additional Context
- Thread ID: {msg.get('threadId', 'Unknown')}
- Labels: {', '.join(msg.get('labelIds', []))}
"""

            # Create unique filename
            safe_subject = "".join(c for c in headers.get('Subject', 'no-subject') if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_subject = safe_subject[:50]  # Limit length
            filename = f"GMAIL_{message['id']}_{safe_subject}.md"
            filepath = self.needs_action / filename

            # Write content to file
            filepath.write_text(content)

            # Mark as processed
            self.processed_ids.add(message['id'])

            self.logger.info(f"Created action file: {filename}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error creating action file for message {message['id']}: {e}")
            return None

    def run(self):
        """Main loop to continuously monitor Gmail"""
        self.logger.info('Starting Gmail Watcher')

        while True:
            try:
                messages = self.check_for_updates()
                for message in messages:
                    action_file = self.create_action_file(message)
                    if action_file:
                        self.logger.info(f"Processed Gmail message: {message['id']}")

                # Save processed IDs periodically
                self._save_processed_ids()

            except Exception as e:
                self.logger.error(f'Gmail Watcher error: {e}')

            # Wait before next check
            time.sleep(self.check_interval)


def main():
    """Main function to run the Gmail Watcher"""
    vault_path = Path(__file__).parent  # Current directory as vault
    credentials_path = vault_path / 'credentials.json'  # Expected credentials file

    # Create Needs_Action folder if it doesn't exist
    needs_action_path = vault_path / 'Needs_Action'
    needs_action_path.mkdir(exist_ok=True)

    watcher = GmailWatcher(vault_path, credentials_path)

    # Run the watcher
    watcher.run()


if __name__ == "__main__":
    main()