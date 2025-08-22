# -*- coding: utf-8 -*-
"""
机械臂配置模块
基于LeRobot的机械臂配置，专为ProjecTo项目优化
"""

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
# Licensed under the Apache License, Version 2.0

import abc
from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional, Sequence

from ..cameras.configs import CameraConfig, OpenCVCameraConfig
from ..motors.configs import (
    MotorsBusConfig,
    FeetechMotorsBusConfig,
    DynamixelMotorsBusConfig,
    create_so101_motors_config,
)

try:
    import draccus
    DRACCUS_AVAILABLE = True
except ImportError:
    # 如果draccus不可用，提供简单的替代实现
    DRACCUS_AVAILABLE = False
    class ChoiceRegistry:
        @classmethod
        def register_subclass(cls, name):
            def decorator(subclass):
                return subclass
            return decorator
        
        def get_choice_name(self, cls):
            return cls.__name__.lower().replace('robotconfig', '')

@dataclass
class RobotConfig(ChoiceRegistry if not DRACCUS_AVAILABLE else draccus.ChoiceRegistry, abc.ABC):
    """机械臂配置基类"""
    
    @property
    def type(self) -> str:
        if DRACCUS_AVAILABLE:
            return self.get_choice_name(self.__class__)
        else:
            return self.__class__.__name__.lower().replace('robotconfig', '')

@dataclass
class ManipulatorRobotConfig(RobotConfig):
    """操作臂机器人配置基类"""
    
    leader_arms: Dict[str, MotorsBusConfig] = field(default_factory=dict)
    follower_arms: Dict[str, MotorsBusConfig] = field(default_factory=dict)
    cameras: Dict[str, CameraConfig] = field(default_factory=dict)

    # 安全限制：限制相对位置目标向量的幅度
    max_relative_target: Union[List[float], float, None] = None

    # 可选：将leader臂设置为扭矩模式，夹爪电机设置为此角度
    gripper_open_degree: Optional[float] = None

    # 模拟模式
    mock: bool = False

    def __post_init__(self):
        """初始化后处理"""
        if self.mock:
            # 如果是模拟模式，将所有设备设置为模拟模式
            for arm in self.leader_arms.values():
                if hasattr(arm, 'mock') and not arm.mock:
                    arm.mock = True
            for arm in self.follower_arms.values():
                if hasattr(arm, 'mock') and not arm.mock:
                    arm.mock = True
            for cam in self.cameras.values():
                if hasattr(cam, 'mock') and not cam.mock:
                    cam.mock = True

        # 验证max_relative_target配置
        if self.max_relative_target is not None and isinstance(self.max_relative_target, Sequence):
            for name in self.follower_arms:
                if len(self.follower_arms[name].motors) != len(self.max_relative_target):
                    raise ValueError(
                        f"len(max_relative_target)={len(self.max_relative_target)} but the follower arm with name {name} has "
                        f"{len(self.follower_arms[name].motors)} motors. Please make sure that the "
                        f"`max_relative_target` list has as many parameters as there are motors per arm."
                    )

if DRACCUS_AVAILABLE:
    @RobotConfig.register_subclass("so101")
    @dataclass
    class So101RobotConfig(ManipulatorRobotConfig):
        """SO101机械臂配置
        
        专为ProjecTo项目中的SO101机械臂优化的配置
        """
        calibration_dir: str = ".cache/calibration/so101"
        max_relative_target: Optional[int] = None

        leader_arms: Dict[str, MotorsBusConfig] = field(
            default_factory=lambda: {
                "main": FeetechMotorsBusConfig(
                    port="COM5",
                    motors={
                        "shoulder_pan": [1, "sts3215"],
                        "shoulder_lift": [2, "sts3215"],
                        "elbow_flex": [3, "sts3215"],
                        "wrist_flex": [4, "sts3215"],
                        "wrist_roll": [5, "sts3215"],
                        "gripper": [6, "sts3215"],
                    },
                ),
            }
        )

        follower_arms: Dict[str, MotorsBusConfig] = field(
            default_factory=lambda: {
                "main": FeetechMotorsBusConfig(
                    port="COM4",
                    motors={
                        "shoulder_pan": [1, "sts3215"],
                        "shoulder_lift": [2, "sts3215"],
                        "elbow_flex": [3, "sts3215"],
                        "wrist_flex": [4, "sts3215"],
                        "wrist_roll": [5, "sts3215"],
                        "gripper": [6, "sts3215"],
                    },
                ),
            }
        )

        cameras: Dict[str, CameraConfig] = field(
            default_factory=lambda: {
                "main": OpenCVCameraConfig(
                    camera_index=0,
                    fps=30,
                    width=640,
                    height=480,
                ),
            }
        )

        mock: bool = False
else:
    @dataclass
    class So101RobotConfig(ManipulatorRobotConfig):
        """SO101机械臂配置"""
        calibration_dir: str = ".cache/calibration/so101"
        max_relative_target: Optional[int] = None

        leader_arms: Dict[str, MotorsBusConfig] = field(
            default_factory=lambda: {
                "main": FeetechMotorsBusConfig(
                    port="COM5",
                    motors={
                        "shoulder_pan": [1, "sts3215"],
                        "shoulder_lift": [2, "sts3215"],
                        "elbow_flex": [3, "sts3215"],
                        "wrist_flex": [4, "sts3215"],
                        "wrist_roll": [5, "sts3215"],
                        "gripper": [6, "sts3215"],
                    },
                ),
            }
        )

        follower_arms: Dict[str, MotorsBusConfig] = field(
            default_factory=lambda: {
                "main": FeetechMotorsBusConfig(
                    port="COM4",
                    motors={
                        "shoulder_pan": [1, "sts3215"],
                        "shoulder_lift": [2, "sts3215"],
                        "elbow_flex": [3, "sts3215"],
                        "wrist_flex": [4, "sts3215"],
                        "wrist_roll": [5, "sts3215"],
                        "gripper": [6, "sts3215"],
                    },
                ),
            }
        )

        cameras: Dict[str, CameraConfig] = field(
            default_factory=lambda: {
                "main": OpenCVCameraConfig(
                    camera_index=0,
                    fps=30,
                    width=640,
                    height=480,
                ),
            }
        )

        mock: bool = False

# 便利函数
def create_projecto_so101_config(
    follower_port: str = "COM4",
    leader_port: str = "COM5", 
    camera_index: int = 0,
    include_gripper: bool = False,
    mock: bool = False
) -> So101RobotConfig:
    """创建ProjecTo专用的SO101配置
    
    Args:
        follower_port: Follower机械臂串口
        leader_port: Leader机械臂串口
        camera_index: 摄像头索引
        include_gripper: 是否包含夹爪
        mock: 是否为模拟模式
    """
    
    # 创建电机配置
    follower_motors = create_so101_motors_config(follower_port, include_gripper)
    leader_motors = create_so101_motors_config(leader_port, include_gripper)
    
    # 创建摄像头配置
    camera_config = OpenCVCameraConfig(
        camera_index=camera_index,
        fps=30,
        width=320,  # ProjecTo使用较小分辨率以提升性能
        height=240,
        mock=mock
    )
    
    config = So101RobotConfig(
        leader_arms={"main": leader_motors} if not mock else {},
        follower_arms={"main": follower_motors},
        cameras={"main": camera_config},
        mock=mock
    )
    
    return config

def create_projecto_follower_only_config(
    follower_port: str = "COM4",
    camera_index: int = 0, 
    include_gripper: bool = False,
    mock: bool = False
) -> So101RobotConfig:
    """创建仅Follower的SO101配置（ProjecTo常用配置）
    
    这是ProjecTo项目最常用的配置，只使用Follower机械臂
    """
    
    follower_motors = create_so101_motors_config(follower_port, include_gripper)
    camera_config = OpenCVCameraConfig(
        camera_index=camera_index,
        fps=30,
        width=320,
        height=240,
        mock=mock
    )
    
    config = So101RobotConfig(
        leader_arms={},  # 不使用Leader
        follower_arms={"main": follower_motors},
        cameras={"main": camera_config},
        mock=mock
    )
    
    return config
