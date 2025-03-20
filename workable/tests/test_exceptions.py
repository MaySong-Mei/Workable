"""
测试异常类
"""

import unittest
import logging

from workable.core.exceptions import (
    WorkableError, 
    MessageError,
    RelationError,
    ContentError,
    ManagerError,
    ConversionError
)

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class TestExceptions(unittest.TestCase):
    """测试Workable系统中的异常类"""
    
    def test_workable_error(self):
        """测试WorkableError异常"""
        # 创建异常
        error = WorkableError("Test workable error")
        
        # 验证异常消息
        self.assertEqual(str(error), "Test workable error")
        
        # 验证异常继承关系
        self.assertTrue(isinstance(error, Exception))
    
    def test_message_error(self):
        """测试MessageError异常"""
        # 创建异常
        error = MessageError("Test message error")
        
        # 验证异常消息
        self.assertEqual(str(error), "Test message error")
        
        # 验证异常继承关系
        self.assertTrue(isinstance(error, WorkableError))
        self.assertTrue(isinstance(error, Exception))
    
    def test_relation_error(self):
        """测试RelationError异常"""
        # 创建异常
        error = RelationError("Test relation error")
        
        # 验证异常消息
        self.assertEqual(str(error), "Test relation error")
        
        # 验证异常继承关系
        self.assertTrue(isinstance(error, WorkableError))
        self.assertTrue(isinstance(error, Exception))
    
    def test_content_error(self):
        """测试ContentError异常"""
        # 创建异常
        error = ContentError("Test content error")
        
        # 验证异常消息
        self.assertEqual(str(error), "Test content error")
        
        # 验证异常继承关系
        self.assertTrue(isinstance(error, WorkableError))
        self.assertTrue(isinstance(error, Exception))
    
    def test_manager_error(self):
        """测试ManagerError异常"""
        # 创建异常
        error = ManagerError("Test manager error")
        
        # 验证异常消息
        self.assertEqual(str(error), "Test manager error")
        
        # 验证异常继承关系
        self.assertTrue(isinstance(error, WorkableError))
        self.assertTrue(isinstance(error, Exception))
    
    def test_conversion_error(self):
        """测试ConversionError异常"""
        # 创建异常
        error = ConversionError("Test conversion error")
        
        # 验证异常消息
        self.assertEqual(str(error), "Test conversion error")
        
        # 验证异常继承关系
        self.assertTrue(isinstance(error, WorkableError))
        self.assertTrue(isinstance(error, Exception))
    
    def test_error_with_details(self):
        """测试带有详细信息的异常"""
        # 创建异常
        details = {"key": "value", "number": 123}
        error = WorkableError("Error with details", details=details)
        
        # 验证异常消息
        self.assertEqual(str(error), "Error with details")
        
        # 验证异常详细信息
        self.assertEqual(error.details, details)


if __name__ == "__main__":
    unittest.main() 