"""
加密工具
用于加密和解密敏感信息（如API密钥）
"""
from cryptography.fernet import Fernet, InvalidToken
import base64
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        初始化加密管理器
        
        Args:
            encryption_key: 加密密钥（base64编码的Fernet密钥）
                          如果为None，将从环境变量ENCRYPTION_KEY读取
                          如果环境变量也不存在，将生成新密钥
        """
        try:
            if encryption_key is None:
                # 尝试从环境变量读取
                encryption_key = os.environ.get('ENCRYPTION_KEY')
                
                if encryption_key is None:
                    # 生成新密钥
                    logger.warning("未提供加密密钥，生成新密钥")
                    encryption_key = Fernet.generate_key().decode()
                    logger.info(f"生成的加密密钥: {encryption_key}")
            
            # 验证密钥格式
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            # 创建Fernet实例
            self.cipher = Fernet(encryption_key)
            self.key = encryption_key.decode() if isinstance(encryption_key, bytes) else encryption_key
            
            logger.info("加密管理器初始化成功")
            
        except Exception as e:
            logger.error(f"初始化加密管理器失败: {e}")
            raise ValueError(f"无效的加密密钥: {e}")
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密文本
        
        Args:
            plaintext: 明文
            
        Returns:
            密文（base64编码）
        """
        if not plaintext:
            return ""
        
        try:
            encrypted = self.cipher.encrypt(plaintext.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"加密失败: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密文本
        
        Args:
            ciphertext: 密文（base64编码）
            
        Returns:
            明文
        """
        if not ciphertext:
            return ""
        
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode('utf-8'))
            return decrypted.decode('utf-8')
        except InvalidToken:
            logger.error("解密失败: 无效的密文或密钥")
            raise ValueError("无效的密文或密钥")
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise
    
    def encrypt_dict(self, data: dict, keys_to_encrypt: list) -> dict:
        """
        加密字典中的指定字段
        
        Args:
            data: 原始字典
            keys_to_encrypt: 需要加密的键列表
            
        Returns:
            加密后的字典
        """
        encrypted_data = data.copy()
        
        for key in keys_to_encrypt:
            if key in encrypted_data and encrypted_data[key]:
                try:
                    encrypted_data[key] = self.encrypt(str(encrypted_data[key]))
                except Exception as e:
                    logger.error(f"加密字段 {key} 失败: {e}")
                    raise
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, keys_to_decrypt: list) -> dict:
        """
        解密字典中的指定字段
        
        Args:
            data: 加密的字典
            keys_to_decrypt: 需要解密的键列表
            
        Returns:
            解密后的字典
        """
        decrypted_data = data.copy()
        
        for key in keys_to_decrypt:
            if key in decrypted_data and decrypted_data[key]:
                try:
                    decrypted_data[key] = self.decrypt(str(decrypted_data[key]))
                except Exception as e:
                    logger.error(f"解密字段 {key} 失败: {e}")
                    raise
        
        return decrypted_data
    
    @staticmethod
    def generate_key() -> str:
        """
        生成新的加密密钥
        
        Returns:
            加密密钥（base64编码的Fernet密钥）
        """
        return Fernet.generate_key().decode('utf-8')
    
    def verify_key(self) -> bool:
        """
        验证当前密钥是否有效
        
        Returns:
            密钥是否有效
        """
        try:
            # 尝试加密和解密一个测试字符串
            test_string = "test_encryption"
            encrypted = self.encrypt(test_string)
            decrypted = self.decrypt(encrypted)
            return decrypted == test_string
        except Exception:
            return False


def encrypt_api_key(api_key: str, secret_key: str) -> str:
    """
    加密API密钥（便捷函数）
    
    Args:
        api_key: 要加密的API密钥
        secret_key: 加密密钥
        
    Returns:
        加密后的API密钥
    """
    manager = EncryptionManager(secret_key)
    return manager.encrypt(api_key)


def decrypt_api_key(encrypted_key: str, secret_key: str) -> str:
    """
    解密API密钥（便捷函数）
    
    Args:
        encrypted_key: 加密的API密钥
        secret_key: 加密密钥
        
    Returns:
        解密后的API密钥
    """
    manager = EncryptionManager(secret_key)
    return manager.decrypt(encrypted_key)


def generate_secret_key() -> str:
    """
    生成加密密钥（便捷函数）
    
    Returns:
        新的加密密钥
    """
    return EncryptionManager.generate_key()