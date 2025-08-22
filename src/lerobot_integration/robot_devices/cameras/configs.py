# -*- coding: utf-8 -*-
"""
摄像头配置模块
基于LeRobot的摄像头配置，适配ProjecTo项目
"""

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
# Licensed under the Apache License, Version 2.0

import abc
from dataclasses import dataclass
from typing import Optional

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
            return cls.__name__.lower().replace('cameraconfig', '')

@dataclass
class CameraConfig(ChoiceRegistry if not DRACCUS_AVAILABLE else draccus.ChoiceRegistry, abc.ABC):
    """摄像头配置基类"""
    
    @property
    def type(self) -> str:
        if DRACCUS_AVAILABLE:
            return self.get_choice_name(self.__class__)
        else:
            return self.__class__.__name__.lower().replace('cameraconfig', '')

if DRACCUS_AVAILABLE:
    @CameraConfig.register_subclass("opencv")
    @dataclass
    class OpenCVCameraConfig(CameraConfig):
        """OpenCV摄像头配置
        
        适用于USB摄像头和其他OpenCV支持的设备
        
        示例配置：
        - OpenCVCameraConfig(0, 30, 640, 480)  # USB摄像头
        - OpenCVCameraConfig(0, 60, 1280, 720) # 高分辨率
        """
        camera_index: int
        fps: Optional[int] = None
        width: Optional[int] = None
        height: Optional[int] = None
        color_mode: str = "rgb"
        channels: Optional[int] = None
        rotation: Optional[int] = None
        mock: bool = False

        def __post_init__(self):
            if self.color_mode not in ["rgb", "bgr"]:
                raise ValueError(
                    f"`color_mode` is expected to be 'rgb' or 'bgr', but {self.color_mode} is provided."
                )

            self.channels = 3

            if self.rotation not in [-90, None, 90, 180]:
                raise ValueError(f"`rotation` must be in [-90, None, 90, 180] (got {self.rotation})")
else:
    @dataclass
    class OpenCVCameraConfig(CameraConfig):
        """OpenCV摄像头配置"""
        camera_index: int
        fps: Optional[int] = None
        width: Optional[int] = None
        height: Optional[int] = None
        color_mode: str = "rgb"
        channels: Optional[int] = None
        rotation: Optional[int] = None
        mock: bool = False

        def __post_init__(self):
            if self.color_mode not in ["rgb", "bgr"]:
                raise ValueError(
                    f"`color_mode` is expected to be 'rgb' or 'bgr', but {self.color_mode} is provided."
                )

            self.channels = 3

            if self.rotation not in [-90, None, 90, 180]:
                raise ValueError(f"`rotation` must be in [-90, None, 90, 180] (got {self.rotation})")

if DRACCUS_AVAILABLE:
    @CameraConfig.register_subclass("intelrealsense")
    @dataclass
    class IntelRealSenseCameraConfig(CameraConfig):
        """Intel RealSense摄像头配置
        
        适用于Intel RealSense D4xx系列深度摄像头
        
        示例配置：
        - IntelRealSenseCameraConfig(128422271347, 30, 640, 480)
        - IntelRealSenseCameraConfig(128422271347, 30, 640, 480, use_depth=True)
        """
        name: Optional[str] = None
        serial_number: Optional[int] = None
        fps: int = 30
        width: int = 640
        height: int = 480
        color_mode: str = "rgb"
        use_depth: bool = False
        rotation: Optional[int] = None
        mock: bool = False

        def __post_init__(self):
            if self.color_mode not in ["rgb", "bgr"]:
                raise ValueError(
                    f"`color_mode` is expected to be 'rgb' or 'bgr', but {self.color_mode} is provided."
                )

            if self.rotation not in [-90, None, 90, 180]:
                raise ValueError(f"`rotation` must be in [-90, None, 90, 180] (got {self.rotation})")
else:
    @dataclass
    class IntelRealSenseCameraConfig(CameraConfig):
        """Intel RealSense摄像头配置"""
        name: Optional[str] = None
        serial_number: Optional[int] = None
        fps: int = 30
        width: int = 640
        height: int = 480
        color_mode: str = "rgb"
        use_depth: bool = False
        rotation: Optional[int] = None
        mock: bool = False

        def __post_init__(self):
            if self.color_mode not in ["rgb", "bgr"]:
                raise ValueError(
                    f"`color_mode` is expected to be 'rgb' or 'bgr', but {self.color_mode} is provided."
                )

            if self.rotation not in [-90, None, 90, 180]:
                raise ValueError(f"`rotation` must be in [-90, None, 90, 180] (got {self.rotation})")

# 便利函数
def create_default_camera_config(camera_index: int = 0, fps: int = 30, 
                                width: int = 640, height: int = 480) -> OpenCVCameraConfig:
    """创建默认的OpenCV摄像头配置"""
    return OpenCVCameraConfig(
        camera_index=camera_index,
        fps=fps,
        width=width,
        height=height,
        color_mode="rgb",
        mock=False
    )
