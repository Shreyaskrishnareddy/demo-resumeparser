#!/usr/bin/env python3
"""
Image Resume Processor
Handles JPEG and other image formats for resume parsing using OCR
"""

import os
import logging
from typing import Dict, List, Optional
from PIL import Image
import pytesseract
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class ImageResumeProcessor:
    def __init__(self):
        """Initialize image processor with OCR configuration"""
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}

        # Configure Tesseract for better accuracy
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!@#$%^&*()_+-=[]{}|;:,.<>?/ '

        logger.info("🖼️ Image Resume Processor initialized")

    def is_image_file(self, file_path: str) -> bool:
        """Check if file is a supported image format"""
        return os.path.splitext(file_path.lower())[1] in self.supported_formats

    def process_image_resume(self, file_path: str) -> Dict[str, any]:
        """
        Process image-based resume and extract text using OCR

        Args:
            file_path: Path to image file

        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Image file not found: {file_path}")

            if not self.is_image_file(file_path):
                raise ValueError(f"Unsupported image format: {file_path}")

            # Load and preprocess image
            preprocessed_image = self._preprocess_image(file_path)

            # Extract text using OCR
            extracted_text = self._extract_text_ocr(preprocessed_image)

            # Get image metadata
            metadata = self._get_image_metadata(file_path)

            return {
                'success': True,
                'extracted_text': extracted_text,
                'metadata': metadata,
                'processing_method': 'OCR',
                'confidence_score': self._assess_ocr_confidence(extracted_text)
            }

        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'extracted_text': '',
                'metadata': {},
                'processing_method': 'OCR',
                'confidence_score': 0.0
            }

    def _preprocess_image(self, file_path: str) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        # Load image
        image = cv2.imread(file_path)

        if image is None:
            # Try with PIL if OpenCV fails
            pil_image = Image.open(file_path)
            image = np.array(pil_image)
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply preprocessing techniques
        processed = self._apply_image_enhancements(gray)

        return processed

    def _apply_image_enhancements(self, gray_image: np.ndarray) -> np.ndarray:
        """Apply various image enhancement techniques"""
        # Noise removal
        denoised = cv2.medianBlur(gray_image, 3)

        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)

        # Threshold to get black text on white background
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Morphological operations to clean up
        kernel = np.ones((1,1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return cleaned

    def _extract_text_ocr(self, image: np.ndarray) -> str:
        """Extract text from preprocessed image using Tesseract OCR"""
        try:
            # Convert numpy array to PIL Image for Tesseract
            pil_image = Image.fromarray(image)

            # Extract text with configuration
            text = pytesseract.image_to_string(pil_image, config=self.tesseract_config)

            # Clean up extracted text
            cleaned_text = self._clean_ocr_text(text)

            return cleaned_text

        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")
            return ""

    def _clean_ocr_text(self, raw_text: str) -> str:
        """Clean and normalize OCR extracted text"""
        if not raw_text:
            return ""

        # Remove excessive whitespace
        lines = raw_text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                # Remove common OCR artifacts
                line = line.replace('|', 'I')  # Common misread
                line = line.replace('0', 'O')  # In names/words context

                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _get_image_metadata(self, file_path: str) -> Dict[str, any]:
        """Extract metadata from image file"""
        try:
            with Image.open(file_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'dpi': img.info.get('dpi', (72, 72)),
                    'file_size': os.path.getsize(file_path),
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            logger.warning(f"Could not extract image metadata: {e}")
            return {
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }

    def _assess_ocr_confidence(self, text: str) -> float:
        """Assess OCR confidence based on text characteristics"""
        if not text:
            return 0.0

        # Basic heuristics for OCR quality
        total_chars = len(text)
        if total_chars == 0:
            return 0.0

        # Count readable characters vs noise
        readable_chars = len([c for c in text if c.isalnum() or c.isspace() or c in '.,;:!?-()[]{}'])
        readability_ratio = readable_chars / total_chars

        # Check for common resume words
        resume_indicators = [
            'experience', 'education', 'skills', 'work', 'job', 'company',
            'university', 'degree', 'email', 'phone', 'address', 'profile'
        ]

        text_lower = text.lower()
        found_indicators = sum(1 for word in resume_indicators if word in text_lower)
        indicator_score = min(found_indicators / 5, 1.0)  # Max score at 5+ indicators

        # Combine scores
        confidence = (readability_ratio * 0.7) + (indicator_score * 0.3)

        return min(confidence, 1.0)

    def batch_process_images(self, image_paths: List[str]) -> List[Dict[str, any]]:
        """Process multiple image files in batch"""
        results = []

        for path in image_paths:
            logger.info(f"Processing image: {path}")
            result = self.process_image_resume(path)
            result['file_path'] = path
            results.append(result)

        return results

    def validate_image_quality(self, file_path: str) -> Dict[str, any]:
        """Validate if image quality is suitable for OCR"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size

                # Check resolution
                min_dimension = min(width, height)
                quality_score = 1.0

                if min_dimension < 600:
                    quality_score *= 0.5  # Low resolution penalty
                elif min_dimension < 1000:
                    quality_score *= 0.8  # Medium resolution penalty

                # Check file size (very small files might be low quality)
                file_size = os.path.getsize(file_path)
                if file_size < 50000:  # Less than 50KB
                    quality_score *= 0.6

                return {
                    'is_suitable': quality_score > 0.5,
                    'quality_score': quality_score,
                    'resolution': f"{width}x{height}",
                    'file_size_kb': file_size / 1024,
                    'recommendations': self._get_quality_recommendations(quality_score, width, height, file_size)
                }

        except Exception as e:
            return {
                'is_suitable': False,
                'quality_score': 0.0,
                'error': str(e),
                'recommendations': ['File cannot be opened or is corrupted']
            }

    def _get_quality_recommendations(self, score: float, width: int, height: int, file_size: int) -> List[str]:
        """Get recommendations for improving image quality"""
        recommendations = []

        if score < 0.5:
            recommendations.append("Image quality may be too low for accurate OCR")

        if min(width, height) < 600:
            recommendations.append("Consider using higher resolution image (min 600px)")

        if file_size < 50000:
            recommendations.append("Image file size is very small, may indicate low quality")

        if width < height * 0.7 or height < width * 0.7:
            recommendations.append("Image aspect ratio seems unusual for a resume")

        if not recommendations:
            recommendations.append("Image quality looks good for OCR processing")

        return recommendations

# Test the processor
if __name__ == "__main__":
    processor = ImageResumeProcessor()

    print("🖼️ Image Resume Processor Test")
    print("=" * 40)

    # Test with sample image (if available)
    test_image = "sample_resume.jpg"

    if os.path.exists(test_image):
        print(f"Testing with: {test_image}")

        # Validate quality first
        quality = processor.validate_image_quality(test_image)
        print(f"Quality Assessment: {quality}")

        # Process the image
        result = processor.process_image_resume(test_image)

        if result['success']:
            print(f"✅ Processing successful")
            print(f"Confidence: {result['confidence_score']:.2f}")
            print(f"Text length: {len(result['extracted_text'])} characters")
            print(f"First 200 chars: {result['extracted_text'][:200]}...")
        else:
            print(f"❌ Processing failed: {result['error']}")
    else:
        print(f"No test image found at {test_image}")
        print("Processor initialized successfully - ready for image processing")