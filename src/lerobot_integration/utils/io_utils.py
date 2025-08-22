# -*- coding: utf-8 -*-
"""
输入输出工具函数
基于LeRobot的IO工具，适配ProjecTo项目
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Union, Optional

def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """加载JSON文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict[str, Any]: 加载的数据
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"JSON文件不存在: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"加载JSON文件失败: {e}")

def save_json(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2) -> bool:
    """保存数据到JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 文件路径
        indent: 缩进空格数
        
    Returns:
        bool: 保存是否成功
    """
    file_path = Path(file_path)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"保存JSON文件失败: {e}")
        return False

def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """加载YAML文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict[str, Any]: 加载的数据
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"YAML文件不存在: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"加载YAML文件失败: {e}")

def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
    """保存数据到YAML文件
    
    Args:
        data: 要保存的数据
        file_path: 文件路径
        
    Returns:
        bool: 保存是否成功
    """
    file_path = Path(file_path)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        logging.error(f"保存YAML文件失败: {e}")
        return False

def ensure_directory(dir_path: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        Path: 目录路径对象
    """
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def find_files_with_extension(
    directory: Union[str, Path], 
    extension: str, 
    recursive: bool = False
) -> list[Path]:
    """查找指定扩展名的文件
    
    Args:
        directory: 搜索目录
        extension: 文件扩展名（如'.json'）
        recursive: 是否递归搜索
        
    Returns:
        list[Path]: 文件路径列表
    """
    directory = Path(directory)
    
    if not directory.exists():
        return []
    
    if recursive:
        pattern = f"**/*{extension}"
        return list(directory.glob(pattern))
    else:
        pattern = f"*{extension}"
        return list(directory.glob(pattern))

def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小（字节）
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return 0
    
    return file_path.stat().st_size

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化的大小字符串
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def backup_file(file_path: Union[str, Path], backup_suffix: str = ".bak") -> Optional[Path]:
    """备份文件
    
    Args:
        file_path: 原文件路径
        backup_suffix: 备份文件后缀
        
    Returns:
        Optional[Path]: 备份文件路径，失败返回None
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    
    backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        logging.error(f"备份文件失败: {e}")
        return None

def load_config_with_fallback(
    primary_path: Union[str, Path], 
    fallback_path: Union[str, Path],
    create_default: bool = True
) -> Dict[str, Any]:
    """加载配置文件，支持备选路径
    
    Args:
        primary_path: 主配置文件路径
        fallback_path: 备选配置文件路径
        create_default: 如果都不存在是否创建默认配置
        
    Returns:
        Dict[str, Any]: 配置数据
    """
    primary_path = Path(primary_path)
    fallback_path = Path(fallback_path)
    
    # 尝试加载主配置
    if primary_path.exists():
        try:
            return load_json(primary_path)
        except Exception as e:
            logging.warning(f"加载主配置失败: {e}")
    
    # 尝试加载备选配置
    if fallback_path.exists():
        try:
            config = load_json(fallback_path)
            # 将备选配置复制到主路径
            save_json(config, primary_path)
            return config
        except Exception as e:
            logging.warning(f"加载备选配置失败: {e}")
    
    # 创建默认配置
    if create_default:
        default_config = {}
        save_json(default_config, primary_path)
        return default_config
    
    raise FileNotFoundError(f"配置文件不存在: {primary_path} 和 {fallback_path}")

def safe_file_write(file_path: Union[str, Path], data: str, encoding: str = 'utf-8') -> bool:
    """安全地写入文件（先写临时文件再重命名）
    
    Args:
        file_path: 目标文件路径
        data: 要写入的数据
        encoding: 文件编码
        
    Returns:
        bool: 写入是否成功
    """
    file_path = Path(file_path)
    temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
    
    try:
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入临时文件
        with open(temp_path, 'w', encoding=encoding) as f:
            f.write(data)
        
        # 重命名临时文件
        temp_path.replace(file_path)
        return True
        
    except Exception as e:
        logging.error(f"安全写入文件失败: {e}")
        # 清理临时文件
        if temp_path.exists():
            temp_path.unlink()
        return False

def get_project_root(marker_files: list[str] = None) -> Optional[Path]:
    """获取项目根目录
    
    Args:
        marker_files: 标识项目根目录的文件列表
        
    Returns:
        Optional[Path]: 项目根目录路径
    """
    if marker_files is None:
        marker_files = ['setup.py', 'pyproject.toml', '.git', 'README.md']
    
    current_path = Path.cwd()
    
    while current_path != current_path.parent:
        for marker in marker_files:
            if (current_path / marker).exists():
                return current_path
        current_path = current_path.parent
    
    return None
