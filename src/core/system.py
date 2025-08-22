# -*- coding: utf-8 -*-
"""
ProjecTo System Main Controller
"""

import asyncio
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

from ..config.settings import AppSettings
from ..config.robot_config import RobotConfig
from ..config.camera_config import CameraConfig
from .stage_controller import StageController

# Optional robotic arm support
if AppSettings.ENABLE_ROBOT:
    try:
        from ..robot.robot_interface import RobotInterface
        from ..robot.motion_controller import MotionController
    except ImportError:
        print("⚠️ Robotic arm module import failed, will run in vision-only mode")
        AppSettings.ENABLE_ROBOT = False

class ProjecToSystem(QObject):
    """ProjecTo system main controller"""
    
    # Signal definitions
    system_ready = pyqtSignal()
    system_error = pyqtSignal(str)
    stage_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Configuration
        self.app_settings = AppSettings
        self.camera_config = CameraConfig()
        self.robot_config = RobotConfig() if AppSettings.ENABLE_ROBOT else None
        
        # Core components
        self.stage_controller = None
        self.robot_interface = None
        self.motion_controller = None
        
        # Status
        self.is_running = False
        self.is_initialized = False
        
        print("ProjecTo system initialization complete")
    
    def start(self) -> bool:
        """Start system"""
        print("Starting ProjecTo system...")
        
        try:
            # Initialize stage controller
            self.stage_controller = StageController(self)
            
            # Initialize robotic arm (if enabled)
            if AppSettings.ENABLE_ROBOT and self.robot_config:
                self._initialize_robot()
            
            # Connect signals
            self._connect_signals()
            
            # Start stage controller
            if not self.stage_controller.start():
                print("❌ Stage controller startup failed")
                return False
            
            self.is_running = True
            self.is_initialized = True
            
            print("✅ ProjecTo system startup successful")
            self.system_ready.emit()
            return True
            
        except Exception as e:
            print(f"❌ System startup failed: {e}")
            self.system_error.emit(str(e))
            return False
    
    def stop(self):
        """Stop system"""
        print("Stopping ProjecTo system...")
        
        try:
            self.is_running = False
            
            # Stop stage controller
            if self.stage_controller:
                self.stage_controller.stop()
            
            # Disconnect robotic arm
            if self.robot_interface:
                asyncio.create_task(self.robot_interface.disconnect())
            
            print("✅ ProjecTo system stopped")
            
        except Exception as e:
            print(f"⚠️ Error occurred while stopping system: {e}")
    
    def _initialize_robot(self):
        """Initialize robotic arm"""
        print("Initializing robotic arm...")
        
        try:
            from ..robot.robot_interface import RobotInterface
            from ..robot.motion_controller import MotionController
            
            self.robot_interface = RobotInterface(self.robot_config)
            self.motion_controller = MotionController(self.robot_interface)
            
            print("✅ Robotic arm initialization complete")
            
        except Exception as e:
            print(f"⚠️ Robotic arm initialization failed: {e}")
            print("Will continue in vision-only mode")
            AppSettings.ENABLE_ROBOT = False
    
    def _connect_signals(self):
        """Connect signal slots"""
        if self.stage_controller:
            self.stage_controller.stage_changed.connect(self.stage_changed.emit)
        
        if self.robot_interface:
            self.robot_interface.error_occurred.connect(self._on_robot_error)
    
    def _on_robot_error(self, error_message: str):
        """Handle robotic arm error"""
        print(f"🤖❌ Robotic arm error: {error_message}")
        self.system_error.emit(f"Robotic arm error: {error_message}")
    
    # ==================== Public Interface ====================
    
    def get_current_stage(self) -> str:
        """Get current stage"""
        if self.stage_controller:
            return self.stage_controller.current_stage
        return AppSettings.Stage.REST
    
    def change_stage(self, stage_name: str) -> bool:
        """Change stage"""
        if self.stage_controller:
            return self.stage_controller.change_stage(stage_name)
        return False
    
    def is_robot_available(self) -> bool:
        """Check if robotic arm is available"""
        return (AppSettings.ENABLE_ROBOT and 
                self.robot_interface and 
                self.robot_interface.is_robot_connected())
    
    def get_robot_interface(self) -> Optional['RobotInterface']:
        """Get robotic arm interface"""
        return self.robot_interface
    
    def get_motion_controller(self) -> Optional['MotionController']:
        """Get motion controller"""
        return self.motion_controller
    
    def get_stage_controller(self) -> Optional['StageController']:
        """Get stage controller"""
        return self.stage_controller
    
    def get_system_status(self) -> dict:
        """Get system status"""
        status = {
            "running": self.is_running,
            "initialized": self.is_initialized,
            "current_stage": self.get_current_stage(),
            "robot_available": self.is_robot_available(),
            "robot_enabled": AppSettings.ENABLE_ROBOT,
        }
        
        if self.robot_interface:
            status["robot_status"] = self.robot_interface.get_status()
            status["robot_position"] = self.robot_interface.get_current_position_name()
        
        return status
    
    def print_system_status(self):
        """Print system status"""
        status = self.get_system_status()
        print("=== ProjecTo System Status ===")
        for key, value in status.items():
            print(f"{key}: {value}")
        print("========================")
