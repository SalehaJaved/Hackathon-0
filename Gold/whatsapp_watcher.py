"""
WhatsApp Watcher for the Personal AI Employee Hackathon

This script monitors WhatsApp Web for new messages using Playwright automation
and creates action files when relevant messages are detected.
"""

import time
import logging
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

# Add TEST_MODE flag for debugging and testing
TEST_MODE = os.getenv('WHATSAPP_TEST_MODE', 'False').lower() == 'true'


class WhatsAppWatcher:
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = 30  # 30 seconds
        self.session_path = Path(session_path) if session_path else self.vault_path / 'whatsapp_session'
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'needed', 'important', 'now']

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create session directory
        self.session_path.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self):
        """Check for new unread messages in WhatsApp Web"""
        messages = []

        try:
            with sync_playwright() as p:
                # Launch browser with saved session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Set to True for headless operation
                    viewport={'width': 1200, 'height': 800}
                )

                page = browser.new_page()
                page.goto('https://web.whatsapp.com')

                # Wait for WhatsApp to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                except:
                    # If not logged in, user needs to scan QR code
                    self.logger.info("Please scan the QR code to log in to WhatsApp Web")
                    page.wait_for_timeout(30000)  # Wait 30 seconds for login
                    page.reload()
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)

                # Find unread messages
                unread_selectors = [
                    '[data-testid="default-list"] [data-testid="chat"] .x1hx0egp',  # Unread indicator
                    '[data-testid="default-list"] [data-testid="chat"] .x14y16vw',  # Unread indicator alt
                    '[data-testid="chat"] .x1hx0egp'  # Alternative selector
                ]

                for selector in unread_selectors:
                    try:
                        unread_elements = page.query_selector_all(selector)
                        for element in unread_elements:
                            # Get the parent chat element
                            chat_element = element.query_selector('xpath=../../../..') or element.query_selector('xpath=../../..')
                            if chat_element:
                                chat_name = chat_element.get_attribute('title') or chat_element.get_attribute('data-testid')
                                if chat_name:
                                    messages.append({
                                        'chat_name': chat_name,
                                        'text_preview': element.inner_text() if element.inner_text() else 'New message',
                                        'timestamp': datetime.now().isoformat()
                                    })
                    except Exception:
                        continue  # Try next selector if this one fails

                # Alternative approach: look for chats with unread indicators
                try:
                    chat_elements = page.query_selector_all('[data-testid="chat"]')
                    for chat_element in chat_elements:
                        # Check if there's an unread indicator
                        unread_indicator = chat_element.query_selector('[data-testid="default-list"] .x1hx0egp')
                        if unread_indicator:
                            chat_name = chat_element.get_attribute('title') or 'Unknown'
                            messages.append({
                                'chat_name': chat_name,
                                'text_preview': 'Unread message',
                                'timestamp': datetime.now().isoformat()
                            })
                except Exception as e:
                    self.logger.warning(f"Alternative chat detection failed: {e}")

                browser.close()

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            # Ensure browser is closed in case of error
            try:
                browser.close()
            except:
                pass

        return messages

    def create_action_file(self, message_info):
        """Create an action file in the Needs_Action folder"""
        try:
            # Create action file content
            content = f"""---
type: whatsapp_message
from: {message_info['chat_name']}
received: {message_info['timestamp']}
priority: high
status: pending
---

## WhatsApp Message
**From:** {message_info['chat_name']}

**Preview:** {message_info['text_preview']}

## Suggested Actions
- [ ] Check WhatsApp for full message
- [ ] Respond appropriately
- [ ] Follow up as needed

## Context
This message was detected as potentially important based on keywords or unread status.
"""

            # Create unique filename
            safe_chat_name = "".join(c for c in message_info['chat_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_chat_name = safe_chat_name[:50]  # Limit length
            filename = f"WHATSAPP_{safe_chat_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.needs_action / filename

            # Write content to file
            filepath.write_text(content)

            self.logger.info(f"Created WhatsApp action file: {filename}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error creating WhatsApp action file: {e}")
            return None

    def run(self):
        """Main loop to continuously monitor WhatsApp"""
        self.logger.info('Starting WhatsApp Watcher')
        cycle_count = 0

        while True:
            try:
                messages = self.check_for_updates()
                for message in messages:
                    # Check if message contains important keywords
                    message_text = message['text_preview'].lower()
                    if any(keyword in message_text for keyword in self.keywords) or len(messages) > 0:
                        action_file = self.create_action_file(message)
                        if action_file:
                            self.logger.info(f"Processed WhatsApp message from: {message['chat_name']}")

                cycle_count += 1
                self.logger.info(f"WhatsApp Watcher cycle {cycle_count} completed")

                # If in test mode, run only one cycle
                if TEST_MODE:
                    self.logger.info("TEST_MODE: Completed one cycle, exiting...")
                    break

            except Exception as e:
                self.logger.error(f'WhatsApp Watcher error: {e}')
                if TEST_MODE:
                    break

            # Wait before next check
            time.sleep(self.check_interval)


def main():
    """Main function to run the WhatsApp Watcher"""
    vault_path = Path(__file__).parent  # Current directory as vault

    # Create Needs_Action folder if it doesn't exist
    needs_action_path = vault_path / 'Needs_Action'
    needs_action_path.mkdir(exist_ok=True)

    # Create session directory
    session_path = vault_path / 'whatsapp_session'
    session_path.mkdir(exist_ok=True)

    watcher = WhatsAppWatcher(vault_path, session_path)

    # Run the watcher
    watcher.run()


if __name__ == "__main__":
    main()