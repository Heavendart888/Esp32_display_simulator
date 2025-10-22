# designer.py
"""
Main entry point for the ESP32 Display Designer application.
Starts the display selection window.
"""
from display_designer.app import open_display_selector

if __name__ == "__main__":
    open_display_selector()