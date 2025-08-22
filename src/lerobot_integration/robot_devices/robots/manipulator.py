# -*- coding: utf-8 -*-
"""
机械臂控制器
基于LeRobot的ManipulatorRobot，专为ProjecTo项目简化和优化
"""

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
# Licensed under the Apache License, Version 2.0

import json
import logging
import time
import warnings
from pathlib import Path
from typing import Dict, Optional, Union

import numpy as np
import torch

from .configs import ManipulatorRobotConfig

def ensure_safe_goal_position(
    goal_pos: torch.Tensor, 
    present_pos: torch.Tensor, 
    max_relative_target: Union[float, list[float]]
) -> torch.Tensor:
    """确保目标位置的安全性
    
    通过限制相对位置变化的幅度来保证机械臂运动的安全性
    """
    # 计算位置差值
    diff = goal_pos - present_pos
    max_relative_target = torch.tensor(max_relative_target)
    
    # 限制差值幅度
    safe_diff = torch.minimum(diff, max_relative_target)
    safe_diff = torch.maximum(safe_diff, -max_relative_target)
    safe_goal_pos = present_pos + safe_diff

    if not torch.allclose(goal_pos, safe_goal_pos):
        logging.warning(
            "Relative goal position magnitude had to be clamped to be safe.\n"
            f"  requested relative goal position target: {diff}\n"
            f"    clamped relative goal position target: {safe_diff}"
        )

    return safe_goal_pos

class ManipulatorRobot:
    """操作臂机器人控制器
    
    这是一个简化版本的机械臂控制器，专为ProjecTo项目优化。
    支持模拟模式和真实硬件模式。
    
    主要功能：
    - 机械臂连接和初始化
    - 位置控制和读取
    - 安全保护机制
    - 模拟模式支持
    """

    def __init__(self, config: ManipulatorRobotConfig):
        """初始化机械臂控制器
        
        Args:
            config: 机械臂配置对象
        """
        self.config = config
        self.is_connected = False
        self.mock_mode = config.mock
        
        # 设备存储
        self.leader_arms = {}
        self.follower_arms = {}
        self.cameras = {}
        
        # 位置存储
        self.leader_pos = {}
        self.follower_pos = {}
        
        # 模拟位置（用于mock模式）
        self.mock_positions = {}
        
        print(f"机械臂控制器初始化完成 ({'模拟模式' if self.mock_mode else '真实模式'})")

    def connect(self) -> bool:
        """连接机械臂和相关设备
        
        Returns:
            bool: 连接是否成功
        """
        if self.is_connected:
            print("机械臂已经连接")
            return True
        
        try:
            if self.mock_mode:
                print("🎭 模拟模式：模拟机械臂连接...")
                self._connect_mock_devices()
            else:
                print("🔌 真实模式：连接物理设备...")
                self._connect_real_devices()
            
            self.is_connected = True
            print("✅ 机械臂连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 机械臂连接失败: {e}")
            return False

    def disconnect(self) -> bool:
        """断开机械臂连接
        
        Returns:
            bool: 断开是否成功
        """
        if not self.is_connected:
            print("机械臂未连接")
            return True
        
        try:
            if not self.mock_mode:
                # 断开真实设备
                self._disconnect_real_devices()
            
            # 清理状态
            self.leader_arms.clear()
            self.follower_arms.clear()
            self.cameras.clear()
            self.is_connected = False
            
            print("✅ 机械臂断开连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 机械臂断开连接失败: {e}")
            return False

    def _connect_mock_devices(self):
        """连接模拟设备"""
        # 初始化模拟位置
        for arm_name in self.config.follower_arms:
            motors = self.config.follower_arms[arm_name].motors
            self.mock_positions[arm_name] = {
                motor_name: 0.0 for motor_name in motors.keys()
            }
        
        print("🎭 模拟设备连接完成")

    def _connect_real_devices(self):
        """连接真实设备"""
        # 这里应该是真实的设备连接逻辑
        # 由于ProjecTo项目可能不总是有硬件，我们提供一个占位实现
        
        try:
            # 尝试导入真实的LeRobot组件
            from lerobot.common.robot_devices.motors.utils import make_motors_buses_from_configs
            from lerobot.common.robot_devices.cameras.utils import make_cameras_from_configs
            
            # 连接电机总线
            if self.config.follower_arms:
                self.follower_arms = make_motors_buses_from_configs(self.config.follower_arms)
                print(f"✅ Follower机械臂连接成功: {list(self.follower_arms.keys())}")
            
            if self.config.leader_arms:
                self.leader_arms = make_motors_buses_from_configs(self.config.leader_arms)
                print(f"✅ Leader机械臂连接成功: {list(self.leader_arms.keys())}")
            
            # 连接摄像头
            if self.config.cameras:
                self.cameras = make_cameras_from_configs(self.config.cameras)
                print(f"✅ 摄像头连接成功: {list(self.cameras.keys())}")
                
        except ImportError:
            print("⚠️ LeRobot硬件组件不可用，切换到模拟模式")
            self.mock_mode = True
            self._connect_mock_devices()

    def _disconnect_real_devices(self):
        """断开真实设备"""
        # 断开电机总线
        for arm in self.follower_arms.values():
            if hasattr(arm, 'disconnect'):
                arm.disconnect()
        
        for arm in self.leader_arms.values():
            if hasattr(arm, 'disconnect'):
                arm.disconnect()
        
        # 断开摄像头
        for camera in self.cameras.values():
            if hasattr(camera, 'disconnect'):
                camera.disconnect()

    def read_position(self, arm_type: str = "follower") -> Dict[str, torch.Tensor]:
        """读取机械臂位置
        
        Args:
            arm_type: "follower" 或 "leader"
            
        Returns:
            Dict[str, torch.Tensor]: 各关节位置
        """
        if not self.is_connected:
            raise RuntimeError("机械臂未连接")
        
        if self.mock_mode:
            return self._read_mock_position(arm_type)
        else:
            return self._read_real_position(arm_type)

    def _read_mock_position(self, arm_type: str) -> Dict[str, torch.Tensor]:
        """读取模拟位置"""
        if arm_type == "follower" and self.config.follower_arms:
            arm_name = list(self.config.follower_arms.keys())[0]
            positions = self.mock_positions.get(arm_name, {})
            return {name: torch.tensor([pos]) for name, pos in positions.items()}
        
        return {}

    def _read_real_position(self, arm_type: str) -> Dict[str, torch.Tensor]:
        """读取真实位置"""
        try:
            if arm_type == "follower" and self.follower_arms:
                arm_name = list(self.follower_arms.keys())[0]
                arm = self.follower_arms[arm_name]
                return arm.read("Present_Position")
            elif arm_type == "leader" and self.leader_arms:
                arm_name = list(self.leader_arms.keys())[0]
                arm = self.leader_arms[arm_name]
                return arm.read("Present_Position")
            
            return {}
            
        except Exception as e:
            print(f"读取位置失败: {e}")
            return {}

    def write_position(self, position: Dict[str, torch.Tensor], arm_type: str = "follower") -> bool:
        """写入机械臂位置
        
        Args:
            position: 目标位置字典
            arm_type: "follower" 或 "leader"
            
        Returns:
            bool: 写入是否成功
        """
        if not self.is_connected:
            raise RuntimeError("机械臂未连接")
        
        # 安全检查
        if self.config.max_relative_target is not None:
            current_pos = self.read_position(arm_type)
            if current_pos:
                # 应用安全限制
                safe_position = {}
                for motor_name, target_pos in position.items():
                    if motor_name in current_pos:
                        current = current_pos[motor_name]
                        safe_pos = ensure_safe_goal_position(
                            target_pos, current, self.config.max_relative_target
                        )
                        safe_position[motor_name] = safe_pos
                    else:
                        safe_position[motor_name] = target_pos
                position = safe_position
        
        if self.mock_mode:
            return self._write_mock_position(position, arm_type)
        else:
            return self._write_real_position(position, arm_type)

    def _write_mock_position(self, position: Dict[str, torch.Tensor], arm_type: str) -> bool:
        """写入模拟位置"""
        if arm_type == "follower" and self.config.follower_arms:
            arm_name = list(self.config.follower_arms.keys())[0]
            if arm_name not in self.mock_positions:
                self.mock_positions[arm_name] = {}
            
            for motor_name, pos in position.items():
                self.mock_positions[arm_name][motor_name] = float(pos.item() if isinstance(pos, torch.Tensor) else pos)
            
            print(f"🎭 模拟位置写入: {arm_name} -> {position}")
            return True
        
        return False

    def _write_real_position(self, position: Dict[str, torch.Tensor], arm_type: str) -> bool:
        """写入真实位置"""
        try:
            if arm_type == "follower" and self.follower_arms:
                arm_name = list(self.follower_arms.keys())[0]
                arm = self.follower_arms[arm_name]
                arm.write("Goal_Position", position)
                print(f"✅ 真实位置写入: {arm_name}")
                return True
            elif arm_type == "leader" and self.leader_arms:
                arm_name = list(self.leader_arms.keys())[0]
                arm = self.leader_arms[arm_name]
                arm.write("Goal_Position", position)
                print(f"✅ 真实位置写入: {arm_name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"写入位置失败: {e}")
            return False

    def get_current_positions(self) -> Dict[str, float]:
        """获取当前位置（简化格式）
        
        Returns:
            Dict[str, float]: 关节名称到位置的映射
        """
        positions = self.read_position("follower")
        return {
            name: float(pos.item() if isinstance(pos, torch.Tensor) else pos)
            for name, pos in positions.items()
        }

    def move_to_position(self, target_positions: Dict[str, float]) -> bool:
        """移动到指定位置
        
        Args:
            target_positions: 目标位置字典
            
        Returns:
            bool: 移动是否成功
        """
        # 转换为torch.Tensor格式
        tensor_positions = {
            name: torch.tensor([pos]) for name, pos in target_positions.items()
        }
        
        return self.write_position(tensor_positions, "follower")

    def is_mock(self) -> bool:
        """检查是否为模拟模式"""
        return self.mock_mode

    def get_status(self) -> Dict[str, any]:
        """获取机械臂状态"""
        return {
            "connected": self.is_connected,
            "mock_mode": self.mock_mode,
            "follower_arms": list(self.config.follower_arms.keys()),
            "leader_arms": list(self.config.leader_arms.keys()),
            "cameras": list(self.config.cameras.keys()),
        }
