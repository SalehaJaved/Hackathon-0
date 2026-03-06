"""
LinkedIn Watcher for the Personal AI Employee Hackathon

This script monitors LinkedIn for new messages, notifications, and updates using Playwright automation
and creates action files when relevant activities are detected.
"""

import time
import logging
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

# Add TEST_MODE flag for debugging and testing
TEST_MODE = os.getenv('LINKEDIN_TEST_MODE', 'False').lower() == 'true'


class LinkedInWatcher:
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = 60  # 1 minute for testing, can be increased later
        self.session_path = Path(session_path) if session_path else self.vault_path / 'linkedin_session'
        self.keywords = ['urgent', 'asap', 'meeting', 'help', 'needed', 'important', 'now', 'proposal', 'sales', 'opportunity']

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create session directory
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.browser = None
        self.context = None
        self.page = None

    def is_logged_in(self):
        """Check if user is logged in by looking for LinkedIn feed elements"""
        try:
            # Check for feed elements that indicate we're logged in
            if self.page.url.startswith('https://www.linkedin.com/feed'):
                return True

            # Look for profile avatar or navigation elements that indicate login
            if self.page.query_selector('img[alt*="Photo of"], [data-test-id="profile-badge"]'):
                return True

            # Look for main navigation elements
            if self.page.query_selector('a[aria-label="LinkedIn"]'):  # LinkedIn logo
                return True

            # Check if still on login page
            if 'login' in self.page.url or 'checkpoint' in self.page.url:
                return False

            return False
        except Exception as e:
            self.logger.warning(f"Error checking login status: {e}")
            return False

    def authenticate_with_session(self):
        """Try to authenticate using saved session, otherwise prompt for login"""
        try:
            self.logger.info("Attempting to launch LinkedIn with persistent context...")

            # Launch browser with saved session
            headless_setting = os.getenv('LINKEDIN_HEADLESS', 'False').lower() == 'true'
            if TEST_MODE and not headless_setting:
                # Force headless=False for authentication setup when TEST_MODE is False
                headless_setting = False

            self.context = self.playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=headless_setting,
                viewport={'width': 1200, 'height': 800},
                # Add user agent to make it look more like a real browser
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = self.context.new_page()
            self.page.goto('https://www.linkedin.com/feed/')

            # Wait a bit for page to load
            time.sleep(3)

            # Wait for potential redirect to login page or for feed to load
            try:
                # Wait for either the feed to load or login page to appear
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                # If timeout, we might still be on a page - that's ok
                pass

            # Check if we're logged in
            if not self.is_logged_in():
                self.logger.info("Not logged in. Please log in to LinkedIn manually.")
                self.logger.info("Browser launched in non-headless mode for authentication.")

                # Wait for manual login
                if not TEST_MODE:
                    self.logger.info("Waiting 60 seconds for manual login...")
                    time.sleep(60)
                else:
                    self.logger.info("TEST_MODE: Waiting 30 seconds for manual login...")
                    time.sleep(30)

                # Reload to check if login was successful
                self.page.reload()
                time.sleep(5)

                if self.is_logged_in():
                    self.logger.info("Login successful! Session saved.")
                else:
                    self.logger.warning("Still not logged in after waiting. Please ensure you're logged in.")

        except Exception as e:
            self.logger.error(f"Error during authentication: {e}")
            raise

    def initialize_browser(self):
        """Initialize the Playwright browser"""
        try:
            self.playwright = sync_playwright().start()
            self.authenticate_with_session()
        except Exception as e:
            self.logger.error(f"Error initializing browser: {e}")
            raise

    def check_for_updates(self):
        """Check for new notifications, messages, and relevant updates on LinkedIn"""
        updates = []

        try:
            # Ensure we're on the right page
            if 'linkedin.com' not in self.page.url:
                self.page.goto('https://www.linkedin.com/feed/')
                time.sleep(2)

            # Check if we're still logged in
            if not self.is_logged_in():
                self.logger.warning("Not logged in, attempting to re-authenticate")
                self.authenticate_with_session()
                if not self.is_logged_in():
                    self.logger.error("Cannot authenticate to LinkedIn")
                    return updates

            # Check notifications
            try:
                # Click on notifications tab
                notifications_link = self.page.query_selector('a[href="/notifications/"]')
                if notifications_link:
                    notifications_count_elem = notifications_link.query_selector('span[aria-hidden="true"]')
                    if notifications_count_elem:
                        notifications_text = notifications_count_elem.inner_text()
                        if notifications_text and notifications_text.strip() != '0':
                            self.logger.info(f"New notification detected: {notifications_text}")

                            # Go to notifications page to get details
                            original_url = self.page.url
                            notifications_link.click()
                            time.sleep(3)

                            # Get notification details
                            notification_elements = self.page.query_selector_all('.notification-card')
                            for elem in notification_elements[:5]:  # Check first 5 notifications
                                try:
                                    title_elem = elem.query_selector('.notification-title')
                                    subtitle_elem = elem.query_selector('.notification-subtitle')
                                    if title_elem:
                                        title = title_elem.inner_text()
                                        subtitle = subtitle_elem.inner_text() if subtitle_elem else 'No details'

                                        # Check if notification contains important keywords
                                        text_content = f"{title} {subtitle}".lower()
                                        if any(keyword in text_content for keyword in self.keywords):
                                            updates.append({
                                                'type': 'notification',
                                                'title': title,
                                                'details': subtitle,
                                                'timestamp': datetime.now().isoformat()
                                            })
                                except:
                                    continue

                            # Return to original page
                            self.page.goto(original_url)
                            time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Error checking notifications: {e}")

            # Check for new messages in inbox
            try:
                # Look for messages/inbox elements
                messages_link = self.page.query_selector('a[href^="/messaging/"]')
                if messages_link:
                    # Check for unread message indicators
                    unread_indicators = self.page.query_selector_all('.msg-conversation-listitem--has-unread')
                    for indicator in unread_indicators:
                        try:
                            sender_elem = indicator.query_selector('.msg-conversation-card__name')
                            preview_elem = indicator.query_selector('.msg-conversation-card__message-preview')

                            if sender_elem:
                                sender = sender_elem.inner_text()
                                preview = preview_elem.inner_text() if preview_elem else 'New message'

                                # Check if message contains important keywords
                                text_content = preview.lower()
                                if any(keyword in text_content for keyword in self.keywords) or len(unread_indicators) > 0:
                                    updates.append({
                                        'type': 'message',
                                        'sender': sender,
                                        'preview': preview,
                                        'timestamp': datetime.now().isoformat()
                                    })
                        except:
                            continue
            except Exception as e:
                self.logger.warning(f"Error checking messages: {e}")

            # Check for connection requests
            try:
                connection_requests = self.page.query_selector_all('button[aria-label*="Accept"], button[aria-label*="Ignore"]')
                if connection_requests:
                    for request in connection_requests[:3]:  # Check first 3 requests
                        try:
                            # Find the name of the connection request
                            name_elem = request.query_selector('..')  # Go to parent
                            if name_elem:
                                name_text = name_elem.inner_text()
                                updates.append({
                                    'type': 'connection_request',
                                    'name': name_text,
                                    'timestamp': datetime.now().isoformat()
                                })
                        except:
                            continue
            except Exception as e:
                self.logger.warning(f"Error checking connection requests: {e}")

            # Check for mentions or comments on posts
            try:
                # Look for mention notifications
                mention_elements = self.page.query_selector_all('div:has-text("mentioned you"), div:has-text("commented")')
                for elem in mention_elements:
                    try:
                        text = elem.inner_text()
                        updates.append({
                            'type': 'mention_or_comment',
                            'content': text,
                            'timestamp': datetime.now().isoformat()
                        })
                    except:
                        continue
            except Exception as e:
                self.logger.warning(f"Error checking mentions: {e}")

        except Exception as e:
            self.logger.error(f"Error checking LinkedIn for updates: {e}")

        return updates

    def create_action_file(self, update_info):
        """Create an action file in the Needs_Action folder"""
        try:
            # Create action file content
            content = f"""---
type: linkedin_{update_info['type']}
received: {update_info['timestamp']}
priority: medium
status: pending
---

## LinkedIn Update
**Type:** {update_info['type'].replace('_', ' ').title()}

**Details:** {update_info.get('title', update_info.get('sender', update_info.get('name', update_info.get('content', 'N/A'))))}
"""

            # Add more specific details based on type
            if update_info['type'] == 'notification':
                content += f"""
**Title:** {update_info.get('title', 'N/A')}
**Details:** {update_info.get('details', 'N/A')}
"""
            elif update_info['type'] == 'message':
                content += f"""
**Sender:** {update_info.get('sender', 'N/A')}
**Preview:** {update_info.get('preview', 'N/A')}
"""
            elif update_info['type'] == 'connection_request':
                content += f"""
**Name:** {update_info.get('name', 'N/A')}
"""
            elif update_info['type'] == 'mention_or_comment':
                content += f"""
**Content:** {update_info.get('content', 'N/A')}
"""

            content += """

## Suggested Actions
- [ ] Review on LinkedIn
- [ ] Respond appropriately
- [ ] Follow up as needed

## Context
This update was detected as potentially important based on keywords or activity type.
"""

            # Create unique filename
            safe_type = update_info['type'].replace(' ', '_').replace('-', '_')
            text_to_process = update_info.get('title', update_info.get('sender', update_info.get('name', update_info.get('content', 'update'))))[:30]
            safe_details = "".join(c for c in text_to_process if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_details = safe_details[:30]  # Limit length
            filename = f"LINKEDIN_{safe_type.upper()}_{safe_details}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.needs_action / filename

            # Write content to file
            filepath.write_text(content)

            self.logger.info(f"Created LinkedIn action file: {filename}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error creating LinkedIn action file: {e}")
            return None

    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def run(self):
        """Main loop to continuously monitor LinkedIn"""
        self.logger.info('Starting LinkedIn Watcher')
        cycle_count = 0

        try:
            self.initialize_browser()

            while True:
                try:
                    updates = self.check_for_updates()
                    for update in updates:
                        action_file = self.create_action_file(update)
                        if action_file:
                            self.logger.info(f"Processed LinkedIn {update['type']}: {update.get('title', update.get('sender', update.get('name', update.get('content', 'update'))))}")

                    cycle_count += 1
                    self.logger.info(f"LinkedIn Watcher cycle {cycle_count} completed")

                    # If in test mode, run only one cycle
                    if TEST_MODE:
                        self.logger.info("TEST_MODE: Completed one cycle, exiting...")
                        break

                except Exception as e:
                    self.logger.error(f'LinkedIn Watcher error: {e}')
                    if TEST_MODE:
                        break

                # Wait before next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("LinkedIn Watcher stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error in LinkedIn Watcher: {e}")
        finally:
            self.cleanup()


def main():
    """Main function to run the LinkedIn Watcher"""
    vault_path = Path(__file__).parent  # Current directory as vault

    # Create Needs_Action folder if it doesn't exist
    needs_action_path = vault_path / 'Needs_Action'
    needs_action_path.mkdir(exist_ok=True)

    # Create session directory
    session_path = vault_path / 'linkedin_session'
    session_path.mkdir(exist_ok=True)

    watcher = LinkedInWatcher(vault_path, session_path)

    # Run the watcher
    watcher.run()


if __name__ == "__main__":
    main()