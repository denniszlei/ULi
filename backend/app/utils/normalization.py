"""
模型名称标准化工具
"""
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse


class ModelNameNormalizer:
    """模型名称标准化器"""
    
    # 默认标准化规则
    DEFAULT_RULES = [
        (r'-\d{8}$', ''),  # 移除日期后缀: gpt-4-20240101 -> gpt-4
        (r'-\d{4}-\d{2}-\d{2}$', ''),  # 移除日期后缀: gpt-4-2024-01-01 -> gpt-4
        (r'-preview$', ''),  # 移除preview后缀
        (r'-latest$', ''),  # 移除latest后缀
        (r'-\d{4}$', ''),  # 移除年份后缀
    ]
    
    def __init__(self, custom_rules: List[tuple] = None):
        """
        初始化标准化器
        
        Args:
            custom_rules: 自定义规则列表 [(pattern, replacement), ...]
        """
        self.rules = custom_rules or self.DEFAULT_RULES
    
    def normalize(self, model_name: str) -> str:
        """
        标准化模型名称
        
        规则：
        1. 移除provider前缀（如 openai/, anthropic/）
        2. 移除版本后缀中的日期
        3. 移除preview、latest等后缀
        4. 统一转小写
        5. 移除多余空格和连字符
        
        Args:
            model_name: 原始模型名称
            
        Returns:
            标准化后的名称
        """
        if not model_name:
            return ""
        
        normalized = model_name.strip()
        
        # 移除provider前缀
        if '/' in normalized:
            parts = normalized.split('/')
            normalized = parts[-1]  # 取最后一部分
        
        # 应用所有规则
        for pattern, replacement in self.rules:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # 转小写
        normalized = normalized.lower()
        
        # 移除多余的连字符
        normalized = re.sub(r'-+', '-', normalized)
        normalized = normalized.strip('-')
        
        # 移除多余空格
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def batch_normalize(self, model_names: List[str]) -> Dict[str, str]:
        """
        批量标准化模型名称
        
        Args:
            model_names: 模型名称列表
            
        Returns:
            {original_name: normalized_name}
        """
        return {name: self.normalize(name) for name in model_names}


def normalize_model_name(name: str) -> str:
    """
    标准化模型名称（便捷函数）
    
    Args:
        name: 原始模型名称
        
    Returns:
        标准化后的名称
    """
    normalizer = ModelNameNormalizer()
    return normalizer.normalize(name)


def normalize_url(url: str) -> str:
    """
    URL标准化（确保以/v1结尾）
    
    Args:
        url: 原始URL
        
    Returns:
        标准化后的URL
    """
    if not url:
        return ""
    
    # 移除末尾的斜杠
    url = url.rstrip('/')
    
    # 确保以/v1结尾
    if not url.endswith('/v1'):
        url = f"{url}/v1"
    
    return url


def extract_provider_from_model(name: str) -> Optional[str]:
    """
    从模型名称中提取provider前缀
    
    Args:
        name: 模型名称（可能包含provider前缀）
        
    Returns:
        provider前缀，如果没有则返回None
        
    Examples:
        >>> extract_provider_from_model("openai/gpt-4")
        "openai"
        >>> extract_provider_from_model("gpt-4")
        None
    """
    if not name or '/' not in name:
        return None
    
    parts = name.split('/')
    if len(parts) >= 2:
        return parts[0]
    
    return None


def remove_version_suffix(name: str) -> str:
    """
    移除版本后缀
    
    Args:
        name: 模型名称
        
    Returns:
        移除版本后缀后的名称
        
    Examples:
        >>> remove_version_suffix("gpt-4-20240101")
        "gpt-4"
        >>> remove_version_suffix("claude-3-opus-20240229")
        "claude-3-opus"
    """
    if not name:
        return ""
    
    # 移除日期后缀
    name = re.sub(r'-\d{8}$', '', name)
    name = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', name)
    
    # 移除年份后缀
    name = re.sub(r'-\d{4}$', '', name)
    
    return name


def validate_url(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: URL字符串
        
    Returns:
        是否为有效的URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_provider_name(name: str) -> str:
    """
    清理provider名称，使其适合作为ID
    
    Args:
        name: 原始名称
        
    Returns:
        清理后的名称
    """
    if not name:
        return ""
    
    # 转小写
    sanitized = name.lower()
    
    # 替换空格和特殊字符为连字符
    sanitized = re.sub(r'[^\w\-]', '-', sanitized)
    
    # 移除多余的连字符
    sanitized = re.sub(r'-+', '-', sanitized)
    sanitized = sanitized.strip('-')
    
    return sanitized