# -*- coding: utf-8 -*-
"""
增强的ProjecTo系统控制器
集成LeRobot功能
"""

import asyncio
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

from ..config.settings import AppSettings
from ..config.robot_config import RobotConfig
from ..config.camera_config import CameraConfig
from .stage_controller import StageController

# 增强的机械臂接口
if AppSettings.ENABLE_ROBOT:
    try:
        from ..robot.enhanced_robot_interface import EnhancedRobotInterface
        from ..robot.motion_controller import MotionController
        ENHANCED_ROBOT_AVAILABLE = True
    except ImportError:
        print("⚠️ 增强机械臂模块导入失败，将使用基础模式")
        ENHANCED_ROBOT_AVAILABLE = False
        AppSettings.ENABLE_ROBOT = False

class EnhancedProjecToSystem(QObject):
    """增强的ProjecTo系统主控制器
    
    集成LeRobot功能，提供完整的机械臂控制体验
    """
    
    # 信号定义
    system_ready = pyqtSignal()
    system_error = pyqtSignal(str)
    stage_changed = pyqtSignal(str)
    robot_status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 配置
        self.app_settings = AppSettings
        self.camera_config = CameraConfig()
        self.robot_config = RobotConfig() if AppSettings.ENABLE_ROBOT else None
        
        # 核心组件
        self.stage_controller = None
        self.robot_interface = None
        self.motion_controller = None
        
        # 状态
        self.is_running = False
        self.is_initialized = False
        
        # 异步任务管理
        self.loop = None
        
        print("增强ProjecTo系统初始化完成")
    
    def start(self) -> bool:
        """启动系统"""
        print("正在启动增强ProjecTo系统...")
        
        try:
            # 初始化阶段控制器
            self.stage_controller = StageController(self)
            
            # 初始化机械臂（如果启用）
            if AppSettings.ENABLE_ROBOT and self.robot_config:
                self._initialize_enhanced_robot()
            
            # 连接信号
            self._connect_signals()
            
            # 启动阶段控制器
            if not self.stage_controller.start():
                print("❌ 阶段控制器启动失败")
                return False
            
            # 设置异步环境
            self._setup_async_environment()
            
            self.is_running = True
            self.is_initialized = True
            
            print("✅ 增强ProjecTo系统启动成功")
            self.system_ready.emit()
            return True
            
        except Exception as e:
            print(f"❌ 系统启动失败: {e}")
            self.system_error.emit(str(e))
            return False
    
    def stop(self):
        """停止系统"""
        print("正在停止增强ProjecTo系统...")
        
        try:
            self.is_running = False
            
            # 停止阶段控制器
            if self.stage_controller:
                self.stage_controller.stop()
            
            # 断开机械臂连接
            if self.robot_interface:
                # 使用异步方式断开连接
                if self.loop and self.loop.is_running():
                    asyncio.create_task(self.robot_interface.disconnect())
                else:
                    # 同步断开
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.robot_interface.disconnect())
                    loop.close()
            
            print("✅ 增强ProjecTo系统已停止")
            
        except Exception as e:
            print(f"⚠️ 系统停止时出现错误: {e}")
    
    def _initialize_enhanced_robot(self):
        """初始化增强机械臂"""
        print("正在初始化增强机械臂...")
        
        try:
            if ENHANCED_ROBOT_AVAILABLE:
                from ..robot.enhanced_robot_interface import EnhancedRobotInterface
                from ..robot.motion_controller import MotionController
                
                self.robot_interface = EnhancedRobotInterface(self.robot_config)
                self.motion_controller = MotionController(self.robot_interface)
                
                print("✅ 增强机械臂初始化完成")
            else:
                print("⚠️ 增强机械臂不可用，跳过初始化")
                AppSettings.ENABLE_ROBOT = False
                
        except Exception as e:
            print(f"⚠️ 增强机械臂初始化失败: {e}")
            print("将继续以仅视觉模式运行")
            AppSettings.ENABLE_ROBOT = False
    
    def _setup_async_environment(self):
        """设置异步环境"""
        try:
            # 获取当前事件循环或创建新的
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            print("✅ 异步环境设置完成")
            
        except Exception as e:
            print(f"⚠️ 异步环境设置失败: {e}")
    
    def _connect_signals(self):
        """连接信号槽"""
        if self.stage_controller:
            self.stage_controller.stage_changed.connect(self.stage_changed.emit)
        
        if self.robot_interface:
            self.robot_interface.error_occurred.connect(self._on_robot_error)
            self.robot_interface.status_changed.connect(self._on_robot_status_changed)
            self.robot_interface.movement_completed.connect(self._on_robot_movement_completed)
    
    def _on_robot_error(self, error_message: str):
        """处理机械臂错误"""
        print(f"🤖❌ 机械臂错误: {error_message}")
        self.system_error.emit(f"机械臂错误: {error_message}")
    
    def _on_robot_status_changed(self, status: str):
        """处理机械臂状态变化"""
        print(f"🤖 机械臂状态变化: {status}")
        self.robot_status_changed.emit(status)
    
    def _on_robot_movement_completed(self, position: str):
        """处理机械臂移动完成"""
        print(f"🤖✅ 机械臂移动完成: {position}")
    
    # ==================== 公共接口 ====================
    
    def get_current_stage(self) -> str:
        """获取当前阶段"""
        if self.stage_controller:
            return self.stage_controller.current_stage
        return AppSettings.Stage.REST
    
    def change_stage(self, stage_name: str) -> bool:
        """切换阶段"""
        if self.stage_controller:
            return self.stage_controller.change_stage(stage_name)
        return False
    
    def is_robot_available(self) -> bool:
        """检查机械臂是否可用"""
        return (AppSettings.ENABLE_ROBOT and 
                self.robot_interface and 
                self.robot_interface.is_robot_connected())
    
    def is_enhanced_robot_available(self) -> bool:
        """检查增强机械臂是否可用"""
        return (self.is_robot_available() and 
                hasattr(self.robot_interface, 'is_lerobot_available') and
                self.robot_interface.is_lerobot_available())
    
    def get_robot_interface(self) -> Optional['EnhancedRobotInterface']:
        """获取机械臂接口"""
        return self.robot_interface
    
    def get_motion_controller(self) -> Optional['MotionController']:
        """获取运动控制器"""
        return self.motion_controller
    
    def get_stage_controller(self) -> Optional['StageController']:
        """获取阶段控制器"""
        return self.stage_controller
    
    # ==================== 异步操作接口 ====================
    
    async def connect_robot_async(self) -> bool:
        """异步连接机械臂"""
        if self.robot_interface:
            return await self.robot_interface.connect()
        return False
    
    async def disconnect_robot_async(self):
        """异步断开机械臂"""
        if self.robot_interface:
            await self.robot_interface.disconnect()
    
    async def move_robot_to_position_async(self, position_name: str) -> bool:
        """异步移动机械臂到指定位置"""
        if self.robot_interface:
            return await self.robot_interface.move_to_position(position_name)
        return False
    
    def run_async_task(self, coro):
        """运行异步任务"""
        if self.loop and self.loop.is_running():
            return asyncio.create_task(coro)
        else:
            return asyncio.run(coro)
    
    # ==================== 系统状态 ====================
    
    def get_system_status(self) -> dict:
        """获取系统状态"""
        status = {
            "running": self.is_running,
            "initialized": self.is_initialized,
            "current_stage": self.get_current_stage(),
            "robot_available": self.is_robot_available(),
            "enhanced_robot_available": self.is_enhanced_robot_available(),
            "robot_enabled": AppSettings.ENABLE_ROBOT,
            "lerobot_integration": ENHANCED_ROBOT_AVAILABLE,
        }
        
        if self.robot_interface:
            status["robot_status"] = self.robot_interface.get_status()
            status["robot_position"] = self.robot_interface.get_current_position_name()
            status["robot_connected"] = self.robot_interface.is_robot_connected()
            
            if hasattr(self.robot_interface, 'is_lerobot_available'):
                status["lerobot_active"] = self.robot_interface.is_lerobot_available()
        
        return status
    
    def print_system_status(self):
        """打印系统状态"""
        status = self.get_system_status()
        print("=== 增强ProjecTo 系统状态 ===")
        for key, value in status.items():
            print(f"{key}: {value}")
        print("==============================")
        
        # 如果有机械臂，打印详细状态
        if self.robot_interface and hasattr(self.robot_interface, 'print_status'):
            self.robot_interface.print_status()
    
    # ==================== 便捷方法 ====================
    
    def connect_robot(self):
        """连接机械臂（同步封装）"""
        if self.robot_interface:
            return self.run_async_task(self.robot_interface.connect())
        return False
    
    def move_robot(self, position_name: str):
        """移动机械臂（同步封装）"""
        if self.robot_interface:
            return self.run_async_task(self.robot_interface.move_to_position(position_name))
        return False
    
    def save_robot_position(self, position_name: str):
        """保存机械臂当前位置"""
        if self.robot_interface:
            return self.robot_interface.save_current_position(position_name)
        return False
    
    def get_saved_robot_positions(self) -> dict:
        """获取保存的机械臂位置"""
        if self.robot_interface and hasattr(self.robot_interface, 'get_saved_positions'):
            return self.robot_interface.get_saved_positions()
        return {}
