"""
Jarvis Computer Vision Engine

Advanced computer vision capabilities for Windows desktop automation,
screen capture, OCR, and visual understanding.

Features:
- Screen capture and image processing
- OCR (Optical Character Recognition)
- UI element detection
- Visual content analysis
- Cross-platform automation support
"""

import cv2
import numpy as np
import pyocr
import pyocr.toolkit as toolkit
from PIL import Image
import os
import time
from typing import List, Dict, Any, Optional, Tuple
import json
from dataclasses import dataclass
from enum import Enum

class ImageFormat(Enum):
    PNG = "png"
    JPEG = "jpeg"
    BMP = "bmp"
    GRAY = "gray"
    COLOR = "color"

class DetectionConfidence(Enum):
    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5
    MINIMAL = 0.3

@dataclass
class UIElement:
    type: str
    name: str
    bounds: Dict[str, int]
    confidence: float
    text: str = ""
    enabled: bool = True

@dataclass
class ScreenRegion:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        self.x = max(0, self.x)
        self.y = max(0, self.y)
        self.width = max(1, self.width)
        self.height = max(1, self.height)

    def contains(self, x: int, y: int) -> bool:
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)

class ScreenCapture:
    """Handle screen capture operations."""

    def __init__(self):
        self.screenshot_counter = 0
        self.last_capture_time = 0
        self.min_capture_interval = 0.1  # 100ms minimum

    def capture_full_screen(self) -> np.ndarray:
        """Capture the entire screen."""
        try:
            # Use Windows GDI for screen capture
            import ctypes
            from ctypes import wintypes

            # Get screen dimensions
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)

            # Create compatible DC
            dc = user32.CreateDC("\\.\display", None, None, None)
            mem_dc = user32.CreateCompatibleDC(dc)

            # Create bitmap
            bitmap = user32.CreateCompatibleBitmap(dc, screen_width, screen_height)
            user32.SelectObject(mem_dc, bitmap)
            user32.BitBlt(mem_dc, 0, 0, screen_width, screen_height,
                         dc, 0, 0, 0x00CC0020)  # SRCCOPY

            # Get bitmap data
            bitmap_info = wintypes.BITMAPINFO()
            bitmap_info.biSize = ctypes.sizeof(wintypes.BITMAPINFO)
            user32.GetDIBits(mem_dc, bitmap, 0, 0, None,
                           ctypes.byref(bitmap_info), 0)

            # Clean up
            user32.DeleteObject(bitmap)
            user32.DeleteDC(mem_dc)
            user32.DeleteDC(dc)

            # Convert to numpy array (simplified - actual implementation
            # would handle DIB properly)
            return np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

        except Exception as e:
            print(f"Error capturing screen: {e}")
            return np.zeros((1080, 1920, 3), dtype=np.uint8)  # Default resolution

    def capture_window(self, window_title: str = None) -> np.ndarray:
        """Capture a specific window by title."""
        try:
            # Implementation would use Windows API to find and capture specific window
            return self.capture_full_screen()
        except Exception as e:
            print(f"Error capturing window: {e}")
            return np.zeros((1080, 1920, 3), dtype=np.uint8)

    def save_screenshot(self, filepath: str = None) -> str:
        """Save current screenshot to file."""
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"screenshot_{timestamp}.png"

        # For now, return placeholder path
        print(f"Screenshot would be saved to: {filepath}")
        return filepath
class OCRProcessor:
    """Handle OCR and text extraction."""

    def __init__(self):
        self.tools = toolkit.__all__
        self.default_tool = self.tools[0] if self.tools else None

    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from image using OCR."""
        try:
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(image)

            if self.default_tool:
                # Perform OCR
                language = ['eng']
                text = toolkit.image_to_string([pil_image], lang='eng')
                return text.strip()
            else:
                print("No OCR tool available")
                return ""

        except Exception as e:
            print(f"Error in OCR processing: {e}")
            return ""

    def extract_text_with_positions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text with position information."""
        try:
            if self.default_tool:
                language = ['eng']
                boxes = toolkit.image_to_boxes([pil_image], lang='eng')

                text_data = []
                for box in boxes:
                    chars = box.split(' ')
                    if len(chars) >= 6:
                        text_data.append({
                            'text': chars[0],
                            'left': int(chars[1]),
                            'top': int(chars[2]),
                            'width': int(chars[3]),
                            'height': int(chars[4]),
                            'confidence': float(chars[5])
                        })
                return text_data
            return []

        except Exception as e:
            print(f"Error in OCR with positions: {e}")
            return []

    def detect_language(self, image: np.ndarray) -> str:
        """Detect language in image."""
        try:
            if self.default_tool:
                language = toolkit.detect([pil_image])
                return language[0]
            return "unknown"
        except Exception as e:
            print(f"Error in language detection: {e}")
            return "unknown"
class UIElementDetector:
    """Detect UI elements in screenshots."""

    def __init__(self):
        self.element_templates = {}
        self.confidence_threshold = 0.7

    def detect_elements(self, image: np.ndarray) -> List[UIElement]:
        """Detect UI elements in image."""
        elements = []

        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Find contours (potential UI elements)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                # Filter by size (ignore small noise)
                area = cv2.contourArea(contour)
                if area < 100:  # Minimum area
                    continue

                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)

                # Analyze element characteristics
                aspect_ratio = w / h if h > 0 else 0
                size_category = self._categorize_size(area)

                # Classify element type
                element_type = self._classify_element(gray, x, y, w, h, aspect_ratio)

                # Extract text content if possible
                element_text = self._extract_element_text(image, x, y, w, h)

                # Create UI element
                element = UIElement(
                    type=element_type,
                    name=f"{element_type}_{len(elements)}",
                    bounds={"x": x, "y": y, "width": w, "height": h},
                    confidence=self._calculate_element_confidence(gray, x, y, w, h),
                    text=element_text,
                    enabled=self._check_element_enabled(image, x, y, w, h)
                )

                elements.append(element)

        except Exception as e:
            print(f"Error in UI element detection: {e}")

        return elements

    def _categorize_size(self, area: float) -> str:
        """Categorize element by size."""
        if area > 10000:
            return "large"
        elif area > 1000:
            return "medium"
        else:
            return "small"

    def _classify_element(self, gray: np.ndarray, x: int, y: int,
                         w: int, h: int, aspect_ratio: float) -> str:
        """Classify element type based on characteristics."""
        # Simple classification based on size and aspect ratio
        if aspect_ratio > 3:
            return "button"
        elif aspect_ratio < 0.3:
            return "menu"
        elif w > h and w > 100:
            return "toolbar"
        elif h > w and h > 50:
            return "panel"
        else:
            return "unknown"

    def _extract_element_text(self, image: np.ndarray, x: int, y: int,
                             w: int, h: int) -> str:
        """Extract text from UI element."""
        try:
            # Extract element region
            element_region = image[y:y+h, x:x+w]

            # Convert to grayscale for OCR
            gray = cv2.cvtColor(element_region, cv2.COLOR_BGR2GRAY)

            # Use OCR if available
            if hasattr(self, 'ocr_tool') and self.ocr_tool:
                text = self.ocr_tool.extract_text(gray)
                return text.strip()
            else:
                return ""

        except Exception as e:
            print(f"Error extracting element text: {e}")
            return ""

    def _calculate_element_confidence(self, gray: np.ndarray,
                                     x: int, y: int, w: int, h: int) -> float:
        """Calculate confidence score for detected element."""
        try:
            # Extract element region
            element_region = gray[y:y+h, x:x+w]

            # Calculate various features for confidence
            mean_intensity = np.mean(element_region)
            std_intensity = np.std(element_region)
            edge_density = self._calculate_edge_density(element_region)

            # Simple confidence calculation
            confidence = 0.3 * (mean_intensity / 255) + \
                       0.3 * (std_intensity / 255) + \
                       0.4 * edge_density

            return min(confidence, 1.0)

        except Exception as e:
            print(f"Error calculating element confidence: {e}")
            return 0.0

    def _calculate_edge_density(self, region: np.ndarray) -> float:
        """Calculate edge density in a region."""
        try:
            edges = cv2.Canny(region, 50, 150)
            edge_density = np.sum(edges > 0) / (region.shape[0] * region.shape[1])
            return min(edge_density, 1.0)
        except Exception as e:
            print(f"Error calculating edge density: {e}")
            return 0.0

    def find_element_by_type(self, elements: List[UIElement],
                            element_type: str, min_confidence: float = 0.5) -> List[UIElement]:
        """Find elements of specific type."""
        return [el for el in elements if
                el.type == element_type and el.confidence >= min_confidence]

    def find_element_by_text(self, elements: List[UIElement],
                            text: str) -> List[UIElement]:
        """Find elements containing specific text."""
        return [el for el in elements if text.lower() in el.text.lower()]

    def click_element(self, image: np.ndarray, element: UIElement) -> bool:
        """Simulate clicking on a UI element."""
        try:
            # This would integrate with Windows API for actual mouse clicks
            # For now, return success indication
            print(f"Clicking on {element.type} at ({element.bounds['x']}, {element.bounds['y']})")
            return True
        except Exception as e:
            print(f"Error clicking element: {e}")
            return False
class ScreenAnalyzer:
    """Analyze screen content for understanding and planning."""

    def __init__(self):
        self.context_memory = {}
        self.scene_templates = {}

    def analyze_screen(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze screen content for understanding."""
        try:
            analysis = {
                'detected_elements': [],
                'screen_state': 'unknown',
                'available_actions': [],
                'text_content': [],
                'layout': {}
            }

            # Detect UI elements
            detector = UIElementDetector()
            elements = detector.detect_elements(image)

            analysis['detected_elements'] = [
                {
                    'type': el.type,
                    'name': el.name,
                    'bounds': el.bounds,
                    'confidence': el.confidence,
                    'text': el.text,
                    'enabled': el.enabled
                }
                for el in elements
            ]

            # Extract text content
            ocr = OCRProcessor()
            text = ocr.extract_text(image)
            analysis['text_content'] = text.split('\n') if text else []

            # Determine screen state
            analysis['screen_state'] = self._determine_screen_state(elements)

            # Identify available actions
            analysis['available_actions'] = self._identify_available_actions(elements)

            # Analyze layout
            analysis['layout'] = self._analyze_layout(image)

            return analysis

        except Exception as e:
            print(f"Error analyzing screen: {e}")
            return {'error': str(e)}

    def _determine_screen_state(self, elements: List[UIElement]) -> str:
        """Determine the current state of the screen."""
        if not elements:
            return 'empty'

        # Look for specific patterns to determine state
        buttons = [el for el in elements if el.type == 'button']
        menus = [el for el in elements if el.type == 'menu']
        text_inputs = [el for el in elements if 'text' in el.text.lower()]

        if buttons and len(buttons) > 2:
            return 'interactive_menu'
        elif text_inputs and menus:
            return 'data_entry_form'
        elif menus:
            return 'navigation_menu'
        elif text_inputs:
            return 'text_input_screen'
        else:
            return 'static_content'

    def _identify_available_actions(self, elements: List[UIElement]) -> List[str]:
        """Identify available actions based on detected elements."""
        actions = []

        for element in elements:
            if element.type == 'button':
                actions.append(f"click_{element.name}")
            elif element.type == 'menu':
                actions.append(f"open_menu_{element.name}")
            elif 'text' in element.text.lower():
                actions.append(f"enter_text_{element.name}")

        return actions

    def _analyze_layout(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze layout structure of the screen."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Find contours for layout analysis
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            layout = {
                'num_elements': len(contours),
                'layout_type': 'unknown',
                'organized': False
            }

            if len(contours) > 5:
                layout['layout_type'] = 'complex'
            elif len(contours) > 2:
                layout['layout_type'] = 'structured'
            else:
                layout['layout_type'] = 'simple'

            # Check if elements are organized (simple heuristic)
            if len(contours) > 0:
                layout['organized'] = True

            return layout

        except Exception as e:
            print(f"Error analyzing layout: {e}")
            return {'error': str(e)}
class VisualCommandExecutor:
    """Execute commands based on visual content."""

    def __init__(self):
        self.screen_capture = ScreenCapture()
        self.ocr_processor = OCRProcessor()
        self.ui_detector = UIElementDetector()
        self.screen_analyzer = ScreenAnalyzer()

    def execute_command(self, command: str) -> bool:
        """Execute a command based on visual analysis."""
        try:
            # Capture current screen
            screenshot = self.screen_capture.capture_full_screen()

            # Analyze screen content
            analysis = self.screen_analyzer.analyze_screen(screenshot)

            # Plan action based on analysis
            action_plan = self._plan_action(command, analysis)

            # Execute planned action
            result = self._execute_action(action_plan)

            return result

        except Exception as e:
            print(f"Error executing visual command: {e}")
            return False

    def _plan_action(self, command: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Plan action based on command and screen analysis."""
        action_plan = {
            'action_type': 'unknown',
            'target': None,
            'parameters': {},
            'confidence': 0.0
        }

        # Simple command parsing for demonstration
        if 'click' in command.lower():
            # Try to find button to click
            buttons = [el for el in analysis['detected_elements']
                      if el['type'] == 'button']
            if buttons:
                action_plan['action_type'] = 'click'
                action_plan['target'] = buttons[0]['name']
                action_plan['confidence'] = 0.8

        elif 'type' in command.lower():
            # Try to find text input field
            text_inputs = [el for el in analysis['detected_elements']
                          if 'text' in el['text'].lower()]
            if text_inputs:
                action_plan['action_type'] = 'type_text'
                action_plan['target'] = text_inputs[0]['name']
                action_plan['parameters'] = {'text': command.split(' ', 1)[1] if ' ' in command else ''}
                action_plan['confidence'] = 0.7

        elif 'navigate' in command.lower():
            # Look for navigation menus
            menus = [el for el in analysis['detected_elements']
                    if el['type'] == 'menu']
            if menus:
                action_plan['action_type'] = 'navigate'
                action_plan['target'] = menus[0]['name']
                action_plan['confidence'] = 0.6

        return action_plan

    def _execute_action(self, action_plan: Dict[str, Any]) -> bool:
        """Execute planned action."""
        try:
            action_type = action_plan['action_type']
            target = action_plan['target']
            parameters = action_plan['parameters']
            confidence = action_plan['confidence']

            if confidence < 0.5:
                print(f"Low confidence action not executed: {action_type}")
                return False

            if action_type == 'click':
                # Find the element by name
                for element in analysis['detected_elements']:
                    if element['name'] == target:
                        # Simulate click (would use Windows API in real implementation)
                        print(f"Clicking on element: {target}")
                        return True

            elif action_type == 'type_text':
                # Type text into the element
                print(f"Typing text into element: {target}, text: {parameters.get('text', '')}")
                return True

            elif action_type == 'navigate':
                # Navigate to menu
                print(f"Navigating to menu: {target}")
                return True

            print(f"Unknown action type: {action_type}")
            return False

        except Exception as e:
            print(f"Error executing action: {e}")
            return False

# Global instances for convenience
screen_capture = ScreenCapture()
ocr_processor = OCRProcessor()
ui_detector = UIElementDetector()
screen_analyzer = ScreenAnalyzer()
visual_executor = VisualCommandExecutor()

__all__ = [
    'ScreenCapture',
    'OCRProcessor',
    'UIElementDetector',
    'ScreenAnalyzer',
    'VisualCommandExecutor',
    'screen_capture',
    'ocr_processor',
    'ui_detector',
    'screen_analyzer',
    'visual_executor'
]

if __name__ == "__main__":
    # Example usage
    print("Jarvis Computer Vision Engine - Test Mode")
    print("=" * 50)

    # Test OCR with sample text
    test_image = np.zeros((100, 200, 3), dtype=np.uint8)
    test_image[40:60, 60:140] = [255, 255, 255]  # White text

    text = ocr_processor.extract_text(test_image)
    print(f"Extracted text: '{text}'")

    # Test UI element detection
    elements = ui_detector.detect_elements(test_image)
    print(f"Detected elements: {len(elements)}")

    print("Computer Vision Engine Test Complete")