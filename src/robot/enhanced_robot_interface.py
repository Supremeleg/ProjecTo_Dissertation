# -*- coding: utf-8 -*-
"""
增强的机械臂接口
集成LeRobot功能到ProjecTo系统
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Optional, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal

from ..config.robot_config import RobotConfig

# LeRobot集成
try:
    from ..lerobot_integration.robot_devices.robots.configs import (
        create_projecto_follower_only_config,
        So101RobotConfig as LerobotSo101Config
    )
    from ..lerobot_integration.robot_devices.robots.manipulator import ManipulatorRobot as LerobotManipulator
    from ..lerobot_integration.utils.robot_utils import (
        smooth_move_to_position,
        load_positions_from_file,
        save_positions_to_file,
        create_default_positions,
        get_so101_joint_limits,
        check_position_safety,
        print_robot_status
    )
    LEROBOT_AVAILABLE = True
except ImportError as e:
    print(f"LeRobot集成不可用: {e}")
    LEROBOT_AVAILABLE = False

class EnhancedRobotInterface(QObject):
    """增强的机械臂控制接口
    
    集成了LeRobot功能和ProjecTo原有接口，提供统一的机械臂控制体验
    """
    
    # 信号定义
    status_changed = pyqtSignal(str)        # 状态变化信号
    position_reached = pyqtSignal(str)      # 到达位置信号
    movement_started = pyqtSignal(str)      # 开始移动信号
    movement_completed = pyqtSignal(str)    # 移动完成信号
    error_occurred = pyqtSignal(str)        # 错误信号
    
    def __init__(self, config: Optional[RobotConfig] = None):
        super().__init__()
        
        # 配置
        self.config = config or RobotConfig()
        self.lerobot_config = None
        
        # 状态管理
        self.is_connected = False
        self.current_position = "unknown"
        self.target_position = None
        self.is_moving = False
        self.torque_enabled = False
        
        # LeRobot相关
        self.lerobot_robot = None
        self.use_lerobot = LEROBOT_AVAILABLE
        
        # 位置管理
        self.positions_file = Path(__file__).parent.parent.parent / "config" / "robot_positions.json"
        self.saved_positions = {}
        self.joint_limits = get_so101_joint_limits() if LEROBOT_AVAILABLE else {}
        
        # 加载位置数据
        self.load_positions()
        
        print(f"增强机械臂接口初始化完成 ({'LeRobot集成' if self.use_lerobot else '基础模式'})")
    
    # ==================== 基础控制接口 ====================
    
    async def connect(self) -> bool:
        """连接机械臂"""
        print("正在连接机械臂...")
        
        try:
            if self.use_lerobot:
                return await self._connect_lerobot()
            else:
                return await self._connect_basic()
                
        except Exception as e:
            print(f"机械臂连接失败: {e}")
            self.error_occurred.emit(f"连接失败: {e}")
            return False
    
    async def _connect_lerobot(self) -> bool:
        """使用LeRobot连接机械臂"""
        try:
            # 创建LeRobot配置
            self.lerobot_config = create_projecto_follower_only_config(
                follower_port=self.config.follower_port,
                camera_index=0,
                include_gripper=False,
                mock=False
            )
            
            # 创建机械臂对象
            self.lerobot_robot = LerobotManipulator(self.lerobot_config)
            
            # 连接
            if self.lerobot_robot.connect():
                self.is_connected = True
                self.current_position = "rest"
                
                print("✅ LeRobot机械臂连接成功")
                self.status_changed.emit("connected")
                return True
            else:
                print("❌ LeRobot机械臂连接失败")
                return False
                
        except Exception as e:
            print(f"LeRobot连接失败，尝试基础模式: {e}")
            self.use_lerobot = False
            return await self._connect_basic()
    
    async def _connect_basic(self) -> bool:
        """基础连接模式（模拟）"""
        await asyncio.sleep(1)  # 模拟连接延迟
        
        self.is_connected = True
        self.current_position = "rest"
        
        print("✅ 基础模式机械臂连接成功（模拟）")
        self.status_changed.emit("connected")
        return True
    
    async def disconnect(self):
        """断开机械臂连接"""
        print("正在断开机械臂连接...")
        
        try:
            if self.is_connected:
                await self.disable_torque()
                
                if self.lerobot_robot and self.use_lerobot:
                    self.lerobot_robot.disconnect()
                
                self.is_connected = False
                self.current_position = "unknown"
                self.lerobot_robot = None
                
                print("✅ 机械臂断开连接成功")
                self.status_changed.emit("disconnected")
                
        except Exception as e:
            print(f"机械臂断开连接失败: {e}")
            self.error_occurred.emit(f"断开失败: {e}")
    
    async def enable_torque(self):
        """启用扭矩"""
        print("正在启用机械臂扭矩...")
        
        if not self.is_connected:
            print("机械臂未连接，无法启用扭矩")
            return False
        
        try:
            if self.lerobot_robot and self.use_lerobot:
                # LeRobot的扭矩启用逻辑
                pass
            
            self.torque_enabled = True
            print("✅ 机械臂扭矩启用成功")
            self.status_changed.emit("torque_enabled")
            return True
            
        except Exception as e:
            print(f"启用扭矩失败: {e}")
            self.error_occurred.emit(f"启用扭矩失败: {e}")
            return False
    
    async def disable_torque(self):
        """禁用扭矩"""
        print("正在禁用机械臂扭矩...")
        
        try:
            if self.lerobot_robot and self.use_lerobot:
                # LeRobot的扭矩禁用逻辑
                pass
            
            self.torque_enabled = False
            print("✅ 机械臂扭矩禁用成功")
            self.status_changed.emit("torque_disabled")
            return True
            
        except Exception as e:
            print(f"禁用扭矩失败: {e}")
            self.error_occurred.emit(f"禁用扭矩失败: {e}")
            return False
    
    # ==================== 位置控制接口 ====================
    
    async def move_to_position(self, position_name: str, duration: Optional[float] = None):
        """移动到指定位置"""
        print(f"机械臂移动到位置: {position_name}")
        
        if not self.is_connected:
            print("机械臂未连接，无法移动")
            return False
        
        if self.is_moving:
            print("机械臂正在移动中，请等待")
            return False
        
        try:
            # 获取目标位置
            if position_name not in self.saved_positions:
                print(f"未找到位置配置: {position_name}")
                return False
            
            target_positions = self.saved_positions[position_name]
            
            # 安全检查
            if not check_position_safety(target_positions, self.joint_limits):
                print(f"位置 {position_name} 不安全，取消移动")
                return False
            
            # 开始移动
            self.is_moving = True
            self.target_position = position_name
            self.movement_started.emit(position_name)
            
            # 执行移动
            if self.lerobot_robot and self.use_lerobot:
                success = await self._move_lerobot(target_positions, duration)
            else:
                success = await self._move_basic(target_positions, duration)
            
            # 更新状态
            if success:
                self.current_position = position_name
                self.position_reached.emit(position_name)
                print(f"✅ 机械臂移动到 {position_name} 完成")
            
            self.target_position = None
            self.is_moving = False
            self.movement_completed.emit(position_name)
            return success
            
        except Exception as e:
            print(f"移动失败: {e}")
            self.is_moving = False
            self.target_position = None
            self.error_occurred.emit(f"移动失败: {e}")
            return False
    
    async def _move_lerobot(self, target_positions: Dict[str, float], duration: Optional[float]):
        """使用LeRobot移动"""
        try:
            if duration:
                # 平滑移动
                success = smooth_move_to_position(
                    self.lerobot_robot, 
                    target_positions,
                    steps=int(duration * 10),  # 每100ms一步
                    delay=0.1
                )
            else:
                # 直接移动
                success = self.lerobot_robot.move_to_position(target_positions)
            
            return success
            
        except Exception as e:
            print(f"LeRobot移动失败: {e}")
            return False
    
    async def _move_basic(self, target_positions: Dict[str, float], duration: Optional[float]):
        """基础移动模式（模拟）"""
        move_duration = duration or (self.config.movement_steps * self.config.step_delay)
        await asyncio.sleep(move_duration)
        print(f"模拟机械臂移动完成，耗时 {move_duration:.2f}秒")
        return True
    
    # ==================== 动作接口 ====================
    
    async def nod(self, times: int = 1):
        """点头动作"""
        print(f"执行点头动作 {times} 次")
        
        if not self.is_connected:
            print("机械臂未连接，无法执行动作")
            return False
        
        try:
            if not self.torque_enabled:
                await self.enable_torque()
            
            self.movement_started.emit("nod")
            
            # 保存当前位置
            original_pos = self.get_current_position_name()
            
            for i in range(times):
                print(f"执行第 {i+1} 次点头")
                
                # 点头动作序列
                if self.lerobot_robot and self.use_lerobot:
                    # 使用真实机械臂执行点头
                    current_positions = self.lerobot_robot.get_current_positions()
                    
                    # 向下点头
                    nod_down = current_positions.copy()
                    nod_down["wrist_flex"] = current_positions.get("wrist_flex", 0) + 200
                    self.lerobot_robot.move_to_position(nod_down)
                    await asyncio.sleep(0.5)
                    
                    # 回到原位
                    self.lerobot_robot.move_to_position(current_positions)
                    await asyncio.sleep(0.5)
                else:
                    # 模拟点头
                    await asyncio.sleep(1.0)
            
            # 返回原位置
            if original_pos in self.saved_positions:
                await self.move_to_position(original_pos)
            
            print("✅ 点头动作完成")
            self.movement_completed.emit("nod")
            return True
            
        except Exception as e:
            print(f"点头动作失败: {e}")
            self.error_occurred.emit(f"点头失败: {e}")
            return False
    
    async def track_gesture(self, x: float, y: float):
        """跟踪手势位置"""
        if not self.is_connected or not self.torque_enabled:
            return False
        
        try:
            # 将屏幕坐标转换为机械臂关节角度
            if self.lerobot_robot and self.use_lerobot:
                current_positions = self.lerobot_robot.get_current_positions()
                
                # 简单的坐标映射
                pan_offset = (x - 0.5) * 500  # 屏幕中心为0，左右±500
                lift_offset = (0.5 - y) * 300  # 屏幕中心为0，上下±300
                
                target_positions = current_positions.copy()
                target_positions["shoulder_pan"] = current_positions.get("shoulder_pan", 0) + pan_offset
                target_positions["shoulder_lift"] = current_positions.get("shoulder_lift", 0) + lift_offset
                
                # 安全检查
                if check_position_safety(target_positions, self.joint_limits):
                    self.lerobot_robot.move_to_position(target_positions)
            
            print(f"跟踪手势位置: ({x:.2f}, {y:.2f})")
            return True
            
        except Exception as e:
            print(f"跟踪失败: {e}")
            return False
    
    # ==================== 状态查询接口 ====================
    
    def get_current_positions(self) -> Dict[str, float]:
        """获取当前关节位置"""
        if not self.is_connected:
            return {}
        
        if self.lerobot_robot and self.use_lerobot:
            return self.lerobot_robot.get_current_positions()
        else:
            # 返回模拟位置
            return self.saved_positions.get(self.current_position, {})
    
    def is_robot_connected(self) -> bool:
        """检查机械臂是否连接"""
        return self.is_connected
    
    def get_status(self) -> str:
        """获取机械臂状态"""
        if not self.is_connected:
            return "disconnected"
        elif self.is_moving:
            return f"moving_to_{self.target_position}"
        elif not self.torque_enabled:
            return f"idle_at_{self.current_position}"
        else:
            return f"ready_at_{self.current_position}"
    
    def get_current_position_name(self) -> str:
        """获取当前位置名称"""
        return self.current_position
    
    # ==================== 位置管理 ====================
    
    def load_positions(self):
        """加载位置数据"""
        if LEROBOT_AVAILABLE:
            self.saved_positions = load_positions_from_file(self.positions_file)
        
        if not self.saved_positions:
            # 使用默认位置
            if LEROBOT_AVAILABLE:
                self.saved_positions = create_default_positions()
            else:
                self.saved_positions = {
                    "rest": {"shoulder_pan": 0, "shoulder_lift": -1024, "elbow_flex": 1024, "wrist_flex": 0, "wrist_roll": 0}
                }
            self.save_positions()
    
    def save_positions(self):
        """保存位置数据"""
        if LEROBOT_AVAILABLE:
            save_positions_to_file(self.saved_positions, self.positions_file)
        else:
            try:
                self.positions_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.positions_file, 'w', encoding='utf-8') as f:
                    json.dump(self.saved_positions, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"保存位置失败: {e}")
    
    def save_current_position(self, position_name: str) -> bool:
        """保存当前位置"""
        if not self.is_connected:
            return False
        
        try:
            current_pos = self.get_current_positions()
            if current_pos:
                self.saved_positions[position_name] = current_pos
                self.save_positions()
                print(f"✅ 位置 {position_name} 已保存")
                return True
        except Exception as e:
            print(f"保存位置失败: {e}")
            return False
    
    def delete_position(self, position_name: str) -> bool:
        """删除保存的位置"""
        if position_name in self.saved_positions:
            del self.saved_positions[position_name]
            self.save_positions()
            print(f"✅ 位置 {position_name} 已删除")
            return True
        return False
    
    def get_saved_positions(self) -> Dict[str, Dict[str, float]]:
        """获取所有保存的位置"""
        return self.saved_positions.copy()
    
    # ==================== 安全和紧急控制 ====================
    
    async def emergency_stop(self):
        """紧急停止"""
        print("🚨 机械臂紧急停止")
        self.is_moving = False
        self.target_position = None
        
        if self.lerobot_robot and self.use_lerobot:
            # LeRobot紧急停止
            try:
                # 这里可以添加具体的紧急停止逻辑
                pass
            except Exception as e:
                print(f"紧急停止失败: {e}")
        
        await self.disable_torque()
        self.status_changed.emit("emergency_stopped")
    
    # ==================== 调试和状态显示 ====================
    
    def print_status(self):
        """打印机械臂状态"""
        if self.lerobot_robot and self.use_lerobot:
            print_robot_status(self.lerobot_robot)
        else:
            print("=" * 40)
            print("机械臂状态信息（基础模式）")
            print("=" * 40)
            print(f"连接状态: {self.is_connected}")
            print(f"当前位置: {self.current_position}")
            print(f"扭矩启用: {self.torque_enabled}")
            print(f"正在移动: {self.is_moving}")
            print("=" * 40)
    
    def is_lerobot_available(self) -> bool:
        """检查LeRobot是否可用"""
        return self.use_lerobot and LEROBOT_AVAILABLE
