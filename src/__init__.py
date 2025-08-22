#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProjecTo - 智能交互投影系统

一个集成计算机视觉、人机交互和机器人技术的智能展览交互系统。
通过多阶段交互设计，将非接触式手势识别与物理机械臂反馈相结合，
为展览环境提供自然直观的人机交互体验。
"""

__version__ = "1.0.0"
__author__ = "ProjecTo Team"
__email__ = "team@projecto.dev"
__license__ = "MIT"
__description__ = "智能交互投影系统"

# 导出主要类和函数
from .core.system import ProjecToSystem
from .core.stage_controller import StageController
from .vision.gesture_detector import GestureDetector
from .vision.object_detector import ObjectDetector
from .vision.camera_manager import CameraManager

# 可选的机械臂支持
try:
    from .robot.robot_interface import RobotInterface
    from .robot.motion_controller import MotionController
    ROBOT_AVAILABLE = True
except ImportError:
    RobotInterface = None
    MotionController = None
    ROBOT_AVAILABLE = False

__all__ = [
    'ProjecToSystem',
    'StageController', 
    'GestureDetector',
    'ObjectDetector',
    'CameraManager',
    'RobotInterface',
    'MotionController',
    'ROBOT_AVAILABLE',
]

# 版本信息
def get_version():
    """获取版本信息"""
    return __version__

def get_system_info():
    """获取系统信息"""
    import platform
    import sys
    
    info = {
        "projecto_version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "robot_available": ROBOT_AVAILABLE,
    }
    
    # 检查重要依赖
    try:
        import cv2
        info["opencv_version"] = cv2.__version__
    except ImportError:
        info["opencv_version"] = "Not installed"
    
    try:
        import mediapipe as mp
        info["mediapipe_version"] = mp.__version__
    except ImportError:
        info["mediapipe_version"] = "Not installed"
        
    try:
        from PyQt6 import QtCore
        info["pyqt6_version"] = QtCore.PYQT_VERSION_STR
    except ImportError:
        info["pyqt6_version"] = "Not installed"
    
    if ROBOT_AVAILABLE:
        try:
            import lerobot
            info["lerobot_version"] = getattr(lerobot, '__version__', 'Unknown')
        except ImportError:
            info["lerobot_version"] = "Not installed"
    
    return info

def print_system_info():
    """打印系统信息"""
    info = get_system_info()
    print("=" * 50)
    print("ProjecTo System Information")
    print("=" * 50)
    for key, value in info.items():
        print(f"{key:20}: {value}")
    print("=" * 50)
