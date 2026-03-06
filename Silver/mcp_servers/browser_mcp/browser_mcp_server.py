"""
Browser MCP Server for Gold Tier AI Employee
Implements web automation and browser-based actions
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from playwright.async_api import async_playwright


class BrowserMCPServer:
    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.audit_log = []

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load browser configuration from file or use defaults"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "headless": True,
                "timeout": 30000,
                "viewport": {"width": 1280, "height": 720}
            }

    async def get_contexts(self) -> List[Dict[str, Any]]:
        """MCP Protocol: Return available contexts"""
        return [
            {
                "type": "context",
                "id": "browser_operations",
                "name": "Browser Operations",
                "description": "Web automation, form filling, and browser-based actions"
            }
        ]

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """MCP Protocol: Return available prompts"""
        return [
            {
                "type": "prompt",
                "id": "navigate_and_scrape",
                "name": "Navigate and Scrape",
                "description": "Navigate to a URL and extract specific data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"},
                        "selectors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "CSS selectors to extract data from"
                        },
                        "wait_for": {"type": "string", "description": "CSS selector to wait for"}
                    },
                    "required": ["url"]
                }
            },
            {
                "type": "prompt",
                "id": "fill_form",
                "name": "Fill Form",
                "description": "Navigate to a page and fill out a form",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL containing the form"},
                        "form_data": {
                            "type": "object",
                            "description": "Key-value pairs of form fields and values"
                        },
                        "submit_button_selector": {"type": "string", "description": "CSS selector for submit button"}
                    },
                    "required": ["url", "form_data"]
                }
            },
            {
                "type": "prompt",
                "id": "click_element",
                "name": "Click Element",
                "description": "Click a specific element on the page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL of the page"},
                        "selector": {"type": "string", "description": "CSS selector of element to click"}
                    },
                    "required": ["url", "selector"]
                }
            },
            {
                "type": "prompt",
                "id": "take_screenshot",
                "name": "Take Screenshot",
                "description": "Take a screenshot of a web page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"},
                        "screenshot_path": {"type": "string", "description": "Path to save screenshot"}
                    },
                    "required": ["url", "screenshot_path"]
                }
            }
        ]

    async def call_tool(self, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP Protocol: Execute a tool"""
        try:
            if tool_id == "navigate_and_scrape":
                return await self.navigate_and_scrape(arguments)
            elif tool_id == "fill_form":
                return await self.fill_form(arguments)
            elif tool_id == "click_element":
                return await self.click_element(arguments)
            elif tool_id == "take_screenshot":
                return await self.take_screenshot(arguments)
            else:
                return {
                    "error": f"Unknown tool: {tool_id}",
                    "success": False
                }
        except Exception as e:
            self.logger.error(f"Error in call_tool: {e}")
            return {
                "error": str(e),
                "success": False
            }

    async def navigate_and_scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to URL and scrape data using selectors"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config.get("headless", True)
                )
                page = await browser.new_page()

                # Set viewport
                viewport = self.config.get("viewport", {"width": 1280, "height": 720})
                await page.set_viewport_size(viewport)

                # Navigate to URL
                url = params.get('url', '')
                await page.goto(url, wait_until="networkidle")

                # Wait for specific element if provided
                wait_for = params.get('wait_for')
                if wait_for:
                    await page.wait_for_selector(wait_for)

                # Extract data using provided selectors
                selectors = params.get('selectors', [])
                extracted_data = {}

                for selector in selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        element_texts = []
                        for element in elements:
                            text = await element.text_content()
                            element_texts.append(text.strip())
                        extracted_data[selector] = element_texts
                    except Exception as e:
                        self.logger.warning(f"Error extracting data for selector '{selector}': {e}")
                        extracted_data[selector] = []

                await browser.close()

                # Log the action
                self.log_action({
                    "type": "web_scraping",
                    "timestamp": datetime.now().isoformat(),
                    "url": url,
                    "selectors_used": selectors,
                    "data_extracted": len(extracted_data),
                    "status": "success"
                })

                return {
                    "success": True,
                    "result": extracted_data,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Failed to navigate and scrape: {e}")
            self.log_action({
                "type": "web_scraping_failed",
                "timestamp": datetime.now().isoformat(),
                "url": params.get('url', ''),
                "error": str(e),
                "status": "failed"
            })
            return {
                "success": False,
                "error": f"Failed to navigate and scrape: {str(e)}"
            }

    async def fill_form(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to a page and fill out a form"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config.get("headless", True)
                )
                page = await browser.new_page()

                # Set viewport
                viewport = self.config.get("viewport", {"width": 1280, "height": 720})
                await page.set_viewport_size(viewport)

                # Navigate to URL
                url = params.get('url', '')
                await page.goto(url, wait_until="networkidle")

                # Fill form with provided data
                form_data = params.get('form_data', {})
                for field_name, value in form_data.items():
                    try:
                        # Try different selectors for common input types
                        selectors = [
                            f'input[name="{field_name}"]',
                            f'input[id="{field_name}"]',
                            f'input:has-text("{field_name}")',
                            f'label:has-text("{field_name}") + input',
                            f'[placeholder="{field_name}"]',
                            f'*:has-text("{field_name}")'
                        ]

                        field_found = False
                        for selector in selectors:
                            try:
                                element = await page.query_selector(selector)
                                if element:
                                    await element.fill(str(value))
                                    field_found = True
                                    break
                            except:
                                continue

                        if not field_found:
                            # If specific field not found, try to find by accessibility labels or general input
                            await page.get_by_label(field_name).fill(str(value))
                    except Exception as e:
                        self.logger.warning(f"Could not fill field '{field_name}': {e}")

                # Click submit button if provided
                submit_selector = params.get('submit_button_selector')
                if submit_selector:
                    try:
                        await page.click(submit_selector)
                        # Wait for navigation or specific element to indicate success
                        await page.wait_for_load_state("networkidle")
                    except Exception as e:
                        self.logger.warning(f"Could not click submit button: {e}")

                await browser.close()

                # Log the action
                self.log_action({
                    "type": "form_filling",
                    "timestamp": datetime.now().isoformat(),
                    "url": url,
                    "fields_filled": len(form_data),
                    "submit_attempted": bool(submit_selector),
                    "status": "success"
                })

                return {
                    "success": True,
                    "result": f"Form filled and submitted (if submit button provided) on {url}",
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Failed to fill form: {e}")
            self.log_action({
                "type": "form_filling_failed",
                "timestamp": datetime.now().isoformat(),
                "url": params.get('url', ''),
                "error": str(e),
                "status": "failed"
            })
            return {
                "success": False,
                "error": f"Failed to fill form: {str(e)}"
            }

    async def click_element(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Click a specific element on the page"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config.get("headless", True)
                )
                page = await browser.new_page()

                # Set viewport
                viewport = self.config.get("viewport", {"width": 1280, "height": 720})
                await page.set_viewport_size(viewport)

                # Navigate to URL
                url = params.get('url', '')
                await page.goto(url, wait_until="networkidle")

                # Click the element
                selector = params.get('selector', '')
                await page.click(selector)

                await browser.close()

                # Log the action
                self.log_action({
                    "type": "element_click",
                    "timestamp": datetime.now().isoformat(),
                    "url": url,
                    "selector": selector,
                    "status": "success"
                })

                return {
                    "success": True,
                    "result": f"Element clicked: {selector} on {url}",
                    "url": url,
                    "selector": selector,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Failed to click element: {e}")
            self.log_action({
                "type": "element_click_failed",
                "timestamp": datetime.now().isoformat(),
                "url": params.get('url', ''),
                "selector": params.get('selector', ''),
                "error": str(e),
                "status": "failed"
            })
            return {
                "success": False,
                "error": f"Failed to click element: {str(e)}"
            }

    async def take_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Take a screenshot of a web page"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config.get("headless", True)
                )
                page = await browser.new_page()

                # Set viewport
                viewport = self.config.get("viewport", {"width": 1280, "height": 720})
                await page.set_viewport_size(viewport)

                # Navigate to URL
                url = params.get('url', '')
                await page.goto(url, wait_until="networkidle")

                # Create directory if it doesn't exist
                screenshot_path = Path(params.get('screenshot_path', 'screenshot.png'))
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)

                # Take screenshot
                await page.screenshot(path=str(screenshot_path))

                await browser.close()

                # Log the action
                self.log_action({
                    "type": "screenshot_taken",
                    "timestamp": datetime.now().isoformat(),
                    "url": url,
                    "screenshot_path": str(screenshot_path),
                    "status": "success"
                })

                return {
                    "success": True,
                    "result": f"Screenshot saved to {screenshot_path}",
                    "url": url,
                    "screenshot_path": str(screenshot_path),
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            self.log_action({
                "type": "screenshot_failed",
                "timestamp": datetime.now().isoformat(),
                "url": params.get('url', ''),
                "screenshot_path": params.get('screenshot_path', ''),
                "error": str(e),
                "status": "failed"
            })
            return {
                "success": False,
                "error": f"Failed to take screenshot: {str(e)}"
            }

    def log_action(self, action: Dict[str, Any]):
        """Log an action to the audit trail"""
        self.audit_log.append(action)

        # Also write to a log file
        log_file = Path("Logs") / f"browser_mcp_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(action) + "\n")

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the browser MCP server"""
        try:
            # Test if Playwright can be initialized
            try:
                import playwright
                playwright_available = True
            except ImportError:
                playwright_available = False

            status = "healthy" if playwright_available else "degraded"

            return {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "playwright_available": playwright_available,
                    "headless_mode": self.config.get("headless", True),
                    "last_action": self.audit_log[-1] if self.audit_log else None
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Example usage
if __name__ == "__main__":
    import os
    os.makedirs("Logs", exist_ok=True)

    server = BrowserMCPServer()

    # Example of how to use
    async def example():
        result = await server.health_check()
        print(json.dumps(result, indent=2))

        prompts = await server.list_prompts()
        print(f"Available prompts: {len(prompts)}")

    # In a real implementation, this would be run as part of the MCP server ecosystem
    print("Browser MCP Server initialized")