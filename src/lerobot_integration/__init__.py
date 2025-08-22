# -*- coding: utf-8 -*-
"""
LeRobot集成模块

这个模块包含了从LeRobot项目中提取的核心机械臂控制功能，
专门为ProjecTo项目进行了适配和优化。

主要功能：
- 机械臂配置管理
- 电机控制
- 摄像头接口
- 工具函数

注意：这些代码基于LeRobot项目，遵循Apache 2.0许可证。
"""

# 版本信息
__version__ = "1.0.0"
__lerobot_version__ = "unknown"

# 检查LeRobot可用性
try:
    import lerobot
    __lerobot_version__ = getattr(lerobot, '__version__', 'unknown')
    LEROBOT_AVAILABLE = True
except ImportError:
    LEROBOT_AVAILABLE = False

# 导出主要类
from .robot_devices.robots.configs import So101RobotConfig, RobotConfig
from .robot_devices.robots.manipulator import ManipulatorRobot
from .robot_devices.cameras.configs import OpenCVCameraConfig
from .robot_devices.motors.configs import FeetechMotorsBusConfig

__all__ = [
    'So101RobotConfig',
    'RobotConfig', 
    'ManipulatorRobot',
    'OpenCVCameraConfig',
    'FeetechMotorsBusConfig',
    'LEROBOT_AVAILABLE',
]
