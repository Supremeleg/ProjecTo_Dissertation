#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProjecTo Main Program
Intelligent Interactive Projection System - Professional Robotic Arm Control Based on LeRobot Framework
"""

import sys
import signal
import asyncio
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import AppSettings

def setup_signal_handlers(app):
    """Setup signal handlers"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, exiting safely...")
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def check_lerobot_integration():
    """Check LeRobot integration status"""
    try:
        from lerobot_integration import LEROBOT_AVAILABLE
        if LEROBOT_AVAILABLE:
            print("✅ LeRobot integration available")
            return True
        else:
            print("⚠️ LeRobot integration unavailable")
            return False
    except ImportError:
        print("❌ LeRobot integration module not found")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("ProjecTo - Intelligent Interactive Projection System")
    print("Professional Robotic Arm Control Based on LeRobot Framework")
    print("=" * 60)
    
    # Check LeRobot integration
    lerobot_available = check_lerobot_integration()
    
    # Validate configuration
    AppSettings.setup_directories()
    AppSettings.validate_paths()
    AppSettings.print_config_summary()
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("ProjecTo")
    app.setApplicationVersion("1.0.0")
    
    # Setup signal handling
    setup_signal_handlers(app)
    
    # Choose system based on LeRobot availability
    try:
        if lerobot_available:
            try:
                from core.enhanced_system import EnhancedProjecToSystem
                system = EnhancedProjecToSystem()
                print("🚀 Starting full-featured system (LeRobot integration)")
            except ImportError:
                from core.system import ProjecToSystem  
                system = ProjecToSystem()
                print("🚀 Starting basic system (LeRobot import failed)")
        else:
            from core.system import ProjecToSystem  
            system = ProjecToSystem()
            print("🚀 Starting basic system")
        
        # Check command line arguments
        enable_robot = "--enable-robot" in sys.argv or AppSettings.ENABLE_ROBOT
        force_lerobot = "--force-lerobot" in sys.argv
        
        if enable_robot:
            if lerobot_available or force_lerobot:
                print("🤖 Enable robotic arm mode (LeRobot integration)")
                AppSettings.ENABLE_ROBOT = True
            else:
                print("🤖 Enable basic robotic arm mode")
                AppSettings.ENABLE_ROBOT = True
        else:
            print("🎮 Vision-only interaction mode")
            AppSettings.ENABLE_ROBOT = False
        
        # Check debug options
        if "--debug" in sys.argv:
            AppSettings.DEBUG_MODE = True
            AppSettings.SHOW_CAMERA_WINDOW = True
            print("🔍 Debug mode enabled")
        
        # Check windowed mode
        if "--windowed" in sys.argv:
            AppSettings.FULLSCREEN = False
            print("🪟 Windowed mode enabled")
        
        # Start system
        if not system.start():
            print("❌ System startup failed")
            return 1
        
        print("✅ System startup successful")
        print("Press Ctrl+C to exit")
        
        # If robotic arm is enabled, show additional information
        if AppSettings.ENABLE_ROBOT:
            print("\n🤖 Robotic arm features:")
            print("- Support for LeRobot-integrated SO101/SO100 robotic arms")
            print("- Automatic fallback to simulation mode (if hardware unavailable)")
            print("- Complete safety protection mechanisms")
            print("- Position saving and management functions")
        
        # Run application
        result = app.exec()
        
        # Clean up resources
        system.stop()
        print("✅ System exited safely")
        
        return result
        
    except KeyboardInterrupt:
        print("\n⚠️ User interrupt, exiting...")
        return 0
    except Exception as e:
        print(f"❌ System runtime error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())