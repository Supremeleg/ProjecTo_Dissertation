# -*- coding: utf-8 -*-
"""
机械臂控制模块

支持基于LeRobot框架的机械臂控制，作为可选依赖。
如果LeRobot未安装，将使用模拟模式运行。
"""

from .robot_interface import RobotInterface
from .motion_controller import MotionController

# 检查LeRobot可用性
try:
    import lerobot
    LEROBOT_AVAILABLE = True
    print("✅ LeRobot框架可用")
except ImportError:
    LEROBOT_AVAILABLE = False
    print("⚠️ LeRobot框架不可用，机械臂将运行在模拟模式")

__all__ = [
    'RobotInterface',
    'MotionController',
    'LEROBOT_AVAILABLE',
]
