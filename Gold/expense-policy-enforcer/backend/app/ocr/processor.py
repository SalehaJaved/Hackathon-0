"""
OCR Processor - Extract data from receipt images
Uses Tesseract OCR with OpenCV preprocessing
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from typing import Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Process receipt images and extract structured data"""
    
    def __init__(self, lang: str = "eng"):
        self.lang = lang
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Apply thresholding
        - Remove noise
        """
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        return denoised
    
    def extract_text(self, image_path: str) -> str:
        """Extract raw text from image"""
        try:
            # Preprocess
            processed = self.preprocess_image(image_path)
            
            # Run OCR
            text = pytesseract.image_to_string(processed, lang=self.lang)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def parse_amount(self, text: str) -> Optional[float]:
        """Extract amount from OCR text"""
        # Look for currency patterns
        patterns = [
            r'\$[\d,]+\.?\d*',      # $100.00
            r'[\d,]+\.?\d*\s*USD',  # 100.00 USD
            r'total[:\s]*\$?[\d,]+\.?\d*',  # total: $100
            r'amount[:\s]*\$?[\d,]+\.?\d*',  # amount: $100
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract just the number
                num_match = re.search(r'[\d,]+\.?\d*', match.group())
                if num_match:
                    try:
                        return float(num_match.group().replace(',', ''))
                    except ValueError:
                        continue
        
        # Fallback: find any dollar amount
        dollar_match = re.search(r'\$?([\d,]+\.?\d*)', text)
        if dollar_match:
            try:
                return float(dollar_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        return None
    
    def parse_vendor(self, text: str) -> str:
        """Extract vendor name from OCR text"""
        lines = text.split('\n')
        
        # Usually vendor is on first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 3:
                # Clean up common artifacts
                line = re.sub(r'[^\w\s\.\-\&]', '', line)
                if line:
                    return line[:100]  # Limit length
        
        return "Unknown Vendor"
    
    def parse_date(self, text: str) -> Optional[str]:
        """Extract date from OCR text"""
        # Common date patterns
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4})',           # MM/DD/YYYY
            r'(\d{1,2}-\d{1,2}-\d{2,4})',           # MM-DD-YYYY
            r'(\w{3,9}\s+\d{1,2},?\s+\d{4})',       # Month DD, YYYY
            r'(\d{1,2}\s+\w{3,9}\s+\d{4})',         # DD Month YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def parse_category(self, text: str, vendor: str) -> str:
        """Infer category from vendor and text"""
        vendor_lower = vendor.lower()
        text_lower = text.lower()
        
        # Category keywords
        categories = {
            'software': ['aws', 'azure', 'google cloud', 'saas', 'subscription'],
            'meals': ['restaurant', 'cafe', 'starbucks', 'mcdonald', 'lunch', 'dinner'],
            'travel': ['airline', 'delta', 'united', 'hotel', 'marriott', 'uber', 'lyft'],
            'office_supplies': ['staples', 'office depot', 'amazon'],
            'fuel': ['shell', 'exxon', 'chevron', 'gas', 'fuel'],
        }
        
        for category, keywords in categories.items():
            if any(kw in vendor_lower or kw in text_lower for kw in keywords):
                return category
        
        return 'general'
    
    def process_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Main method - process receipt and return structured data
        """
        # Extract raw text
        raw_text = self.extract_text(image_path)
        
        # Parse fields
        vendor = self.parse_vendor(raw_text)
        amount = self.parse_amount(raw_text)
        date_str = self.parse_date(raw_text)
        category = self.parse_category(raw_text, vendor)
        
        # Calculate confidence (simple heuristic)
        confidence = self._calculate_confidence(raw_text, amount, vendor)
        
        return {
            "vendor": vendor,
            "amount": float(amount) if amount else 0.0,
            "date": date_str,
            "category": category,
            "raw_text": raw_text[:500],  # Limit stored text
            "confidence": confidence,
        }
    
    def _calculate_confidence(self, text: str, amount: Optional[float], vendor: str) -> float:
        """Calculate OCR confidence score (0-1)"""
        score = 0.5  # Base score
        
        # More text = better confidence
        if len(text) > 100:
            score += 0.2
        elif len(text) > 50:
            score += 0.1
        
        # Valid amount extracted
        if amount and amount > 0:
            score += 0.2
        
        # Valid vendor extracted
        if vendor and vendor != "Unknown Vendor":
            score += 0.1
        
        return min(score, 1.0)


# Convenience function
def process_receipt(image_path: str, lang: str = "eng") -> Dict[str, Any]:
    """Process a receipt image and extract data"""
    processor = OCRProcessor(lang=lang)
    return processor.process_receipt(image_path)
