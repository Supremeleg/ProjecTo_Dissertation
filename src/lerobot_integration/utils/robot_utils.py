# -*- coding: utf-8 -*-
"""
机械臂工具函数
提供机械臂操作的通用工具函数
"""

import json
import time
import numpy as np
import torch
from pathlib import Path
from typing import Dict, List, Union, Optional, Tuple

def interpolate_positions(
    start_pos: Dict[str, float], 
    end_pos: Dict[str, float], 
    steps: int
) -> List[Dict[str, float]]:
    """在两个位置之间进行线性插值
    
    Args:
        start_pos: 起始位置
        end_pos: 结束位置
        steps: 插值步数
        
    Returns:
        List[Dict[str, float]]: 插值位置列表
    """
    interpolated = []
    
    for step in range(steps + 1):
        t = step / steps
        pos = {}
        
        for joint in start_pos:
            if joint in end_pos:
                pos[joint] = start_pos[joint] + t * (end_pos[joint] - start_pos[joint])
            else:
                pos[joint] = start_pos[joint]
        
        interpolated.append(pos)
    
    return interpolated

def smooth_move_to_position(
    robot, 
    target_positions: Dict[str, float], 
    steps: int = 30, 
    delay: float = 0.06
) -> bool:
    """平滑移动到目标位置
    
    Args:
        robot: 机械臂对象
        target_positions: 目标位置
        steps: 移动步数
        delay: 每步延迟时间
        
    Returns:
        bool: 移动是否成功
    """
    try:
        # 获取当前位置
        current_positions = robot.get_current_positions()
        
        # 生成插值路径
        path = interpolate_positions(current_positions, target_positions, steps)
        
        # 逐步移动
        for i, pos in enumerate(path):
            print(f"移动步骤 {i+1}/{len(path)}")
            robot.move_to_position(pos)
            time.sleep(delay)
        
        print("✅ 平滑移动完成")
        return True
        
    except Exception as e:
        print(f"❌ 平滑移动失败: {e}")
        return False

def load_positions_from_file(file_path: Union[str, Path]) -> Dict[str, Dict[str, float]]:
    """从文件加载位置数据
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict[str, Dict[str, float]]: 位置数据
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"位置文件不存在: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            positions = json.load(f)
        print(f"✅ 已加载位置文件: {file_path}")
        return positions
    except Exception as e:
        print(f"❌ 加载位置文件失败: {e}")
        return {}

def save_positions_to_file(
    positions: Dict[str, Dict[str, float]], 
    file_path: Union[str, Path]
) -> bool:
    """保存位置数据到文件
    
    Args:
        positions: 位置数据
        file_path: 文件路径
        
    Returns:
        bool: 保存是否成功
    """
    file_path = Path(file_path)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(positions, f, indent=2, ensure_ascii=False)
        print(f"✅ 位置已保存到: {file_path}")
        return True
    except Exception as e:
        print(f"❌ 保存位置文件失败: {e}")
        return False

def check_position_safety(
    positions: Dict[str, float], 
    limits: Dict[str, Tuple[float, float]]
) -> bool:
    """检查位置是否在安全范围内
    
    Args:
        positions: 要检查的位置
        limits: 各关节的限制范围
        
    Returns:
        bool: 位置是否安全
    """
    for joint, pos in positions.items():
        if joint in limits:
            min_pos, max_pos = limits[joint]
            if not (min_pos <= pos <= max_pos):
                print(f"⚠️ 关节 {joint} 位置 {pos} 超出安全范围 [{min_pos}, {max_pos}]")
                return False
    
    return True

def calculate_movement_distance(
    pos1: Dict[str, float], 
    pos2: Dict[str, float]
) -> float:
    """计算两个位置之间的欧几里得距离
    
    Args:
        pos1: 位置1
        pos2: 位置2
        
    Returns:
        float: 距离
    """
    distance = 0.0
    common_joints = set(pos1.keys()) & set(pos2.keys())
    
    for joint in common_joints:
        diff = pos1[joint] - pos2[joint]
        distance += diff * diff
    
    return np.sqrt(distance)

def create_default_positions() -> Dict[str, Dict[str, float]]:
    """创建默认的机械臂位置
    
    Returns:
        Dict[str, Dict[str, float]]: 默认位置集合
    """
    return {
        "rest": {
            "shoulder_pan": 0,
            "shoulder_lift": -1024,
            "elbow_flex": 1024,
            "wrist_flex": 0,
            "wrist_roll": 0,
        },
        "V": {
            "shoulder_pan": 0,
            "shoulder_lift": -1024,
            "elbow_flex": 2048,
            "wrist_flex": -1024,
            "wrist_roll": 0,
        },
        "tracking": {
            "shoulder_pan": 0,
            "shoulder_lift": -512,
            "elbow_flex": 1536,
            "wrist_flex": -512,
            "wrist_roll": 0,
        },
        "vertical": {
            "shoulder_pan": 0,
            "shoulder_lift": 0,
            "elbow_flex": -1024,
            "wrist_flex": 1024,
            "wrist_roll": 0,
        }
    }

def get_so101_joint_limits() -> Dict[str, Tuple[float, float]]:
    """获取SO101机械臂关节限制
    
    Returns:
        Dict[str, Tuple[float, float]]: 关节限制
    """
    return {
        "shoulder_pan": (-2048, 2048),
        "shoulder_lift": (-2048, 2048),
        "elbow_flex": (-2048, 2048),
        "wrist_flex": (-2048, 2048),
        "wrist_roll": (-2048, 2048),
        "gripper": (0, 1024),
    }

def convert_positions_to_tensor(positions: Dict[str, float]) -> Dict[str, torch.Tensor]:
    """将位置字典转换为torch.Tensor格式
    
    Args:
        positions: 位置字典
        
    Returns:
        Dict[str, torch.Tensor]: 张量格式位置
    """
    return {
        name: torch.tensor([pos]) if not isinstance(pos, torch.Tensor) else pos
        for name, pos in positions.items()
    }

def convert_tensor_to_positions(tensor_positions: Dict[str, torch.Tensor]) -> Dict[str, float]:
    """将torch.Tensor格式转换为位置字典
    
    Args:
        tensor_positions: 张量格式位置
        
    Returns:
        Dict[str, float]: 位置字典
    """
    return {
        name: float(tensor.item() if isinstance(tensor, torch.Tensor) else tensor)
        for name, tensor in tensor_positions.items()
    }

def validate_robot_config(config) -> List[str]:
    """验证机械臂配置
    
    Args:
        config: 机械臂配置对象
        
    Returns:
        List[str]: 错误信息列表
    """
    errors = []
    
    # 检查基本配置
    if not config.follower_arms and not config.leader_arms:
        errors.append("至少需要配置一个机械臂（leader或follower）")
    
    # 检查端口配置
    for arm_name, arm_config in config.follower_arms.items():
        if not arm_config.port:
            errors.append(f"Follower臂 {arm_name} 缺少端口配置")
        
        if not arm_config.motors:
            errors.append(f"Follower臂 {arm_name} 缺少电机配置")
    
    for arm_name, arm_config in config.leader_arms.items():
        if not arm_config.port:
            errors.append(f"Leader臂 {arm_name} 缺少端口配置")
        
        if not arm_config.motors:
            errors.append(f"Leader臂 {arm_name} 缺少电机配置")
    
    return errors

def print_robot_status(robot) -> None:
    """打印机械臂状态信息
    
    Args:
        robot: 机械臂对象
    """
    print("=" * 40)
    print("机械臂状态信息")
    print("=" * 40)
    
    status = robot.get_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    if robot.is_connected:
        try:
            positions = robot.get_current_positions()
            print("\n当前位置:")
            for joint, pos in positions.items():
                print(f"  {joint}: {pos:.2f}")
        except Exception as e:
            print(f"无法读取位置: {e}")
    
    print("=" * 40)
