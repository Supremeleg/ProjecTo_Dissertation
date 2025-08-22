# -*- coding: utf-8 -*-
"""
电机配置模块
基于LeRobot的电机配置，适配ProjecTo项目
"""

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
# Licensed under the Apache License, Version 2.0

import abc
from dataclasses import dataclass
from typing import Dict, Tuple, List, Union

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
            return cls.__name__.lower().replace('motorsbusconfig', '')

@dataclass
class MotorsBusConfig(ChoiceRegistry if not DRACCUS_AVAILABLE else draccus.ChoiceRegistry, abc.ABC):
    """电机总线配置基类"""
    
    @property
    def type(self) -> str:
        if DRACCUS_AVAILABLE:
            return self.get_choice_name(self.__class__)
        else:
            return self.__class__.__name__.lower().replace('motorsbusconfig', '')

if DRACCUS_AVAILABLE:
    @MotorsBusConfig.register_subclass("dynamixel")
    @dataclass
    class DynamixelMotorsBusConfig(MotorsBusConfig):
        """Dynamixel电机总线配置"""
        port: str
        motors: Dict[str, Tuple[int, str]]
        mock: bool = False
else:
    @dataclass
    class DynamixelMotorsBusConfig(MotorsBusConfig):
        """Dynamixel电机总线配置"""
        port: str
        motors: Dict[str, Tuple[int, str]]
        mock: bool = False

if DRACCUS_AVAILABLE:
    @MotorsBusConfig.register_subclass("feetech")
    @dataclass 
    class FeetechMotorsBusConfig(MotorsBusConfig):
        """Feetech电机总线配置"""
        port: str
        motors: Dict[str, Union[Tuple[int, str], List]]
        mock: bool = False
else:
    @dataclass
    class FeetechMotorsBusConfig(MotorsBusConfig):
        """Feetech电机总线配置"""
        port: str
        motors: Dict[str, Union[Tuple[int, str], List]]
        mock: bool = False

# 默认电机配置
DEFAULT_SO101_MOTORS = {
    "shoulder_pan": [1, "sts3215"],
    "shoulder_lift": [2, "sts3215"], 
    "elbow_flex": [3, "sts3215"],
    "wrist_flex": [4, "sts3215"],
    "wrist_roll": [5, "sts3215"],
    "gripper": [6, "sts3215"],
}

def create_so101_motors_config(port: str = "COM4", include_gripper: bool = True) -> FeetechMotorsBusConfig:
    """创建SO101电机配置"""
    motors = DEFAULT_SO101_MOTORS.copy()
    if not include_gripper:
        motors.pop("gripper", None)
    
    return FeetechMotorsBusConfig(
        port=port,
        motors=motors,
        mock=False
    )
