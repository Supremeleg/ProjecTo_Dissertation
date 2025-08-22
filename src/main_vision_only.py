#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProjecTo - 仅视觉交互模式
不包含机械臂功能，适用于演示和测试
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 强制禁用机械臂
from config.settings import AppSettings
AppSettings.ENABLE_ROBOT = False

from main import main

if __name__ == "__main__":
    print("🎮 启动仅视觉交互模式（无机械臂）")
    sys.exit(main())
