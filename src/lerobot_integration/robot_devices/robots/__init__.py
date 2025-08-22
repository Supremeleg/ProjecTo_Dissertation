# -*- coding: utf-8 -*-
"""
机械臂控制模块
"""

from .configs import RobotConfig, ManipulatorRobotConfig, So101RobotConfig

# 可选的机械臂控制器
try:
    from .manipulator import ManipulatorRobot
    MANIPULATOR_AVAILABLE = True
except ImportError:
    ManipulatorRobot = None
    MANIPULATOR_AVAILABLE = False

__all__ = [
    'RobotConfig',
    'ManipulatorRobotConfig', 
    'So101RobotConfig',
    'ManipulatorRobot',
    'MANIPULATOR_AVAILABLE',
]
