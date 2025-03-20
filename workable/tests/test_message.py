"""
测试消息管理器
"""

import unittest
import logging
from unittest.mock import patch, MagicMock

from workable.core.message import MessageManager
from workable.core.models import Message
from workable.core.exceptions import MessageError

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class TestMessageManager(unittest.TestCase):
    """测试MessageManager类"""
    
    def setUp(self):
        """每个测试前执行"""
        self.manager = MessageManager()
        
        # 创建一些测试消息
        self.message1 = Message(
            content="Message 1",
            sender="sender-1",
            receiver="receiver-1"
        )
        
        self.message2 = Message(
            content="Message 2",
            sender="sender-2",
            receiver="receiver-2"
        )
        
        self.message3 = Message(
            content="Message 3",
            sender="sender-3",
            receiver="receiver-3"
        )
    
    def test_init(self):
        """测试初始化MessageManager"""
        self.assertEqual(len(self.manager.inbox), 0)
        self.assertEqual(len(self.manager.processing), 0)
        self.assertEqual(len(self.manager.archive), 0)
    
    def test_append(self):
        """测试append方法"""
        # 添加消息
        self.manager.append(self.message1)
        
        # 验证消息已添加到收件箱
        self.assertEqual(len(self.manager.inbox), 1)
        self.assertEqual(self.manager.inbox[0], self.message1)
        self.assertEqual(self.message1.status, "inbox")
        
        # 添加无效消息
        with self.assertRaises(MessageError):
            self.manager.append("not a message")
    
    def test_process_next(self):
        """测试process_next方法"""
        # 添加消息
        self.manager.append(self.message1)
        self.manager.append(self.message2)
        
        # 处理下一条消息
        msg = self.manager.process_next()
        
        # 验证消息已从收件箱移动到处理中
        self.assertEqual(len(self.manager.inbox), 1)
        self.assertEqual(len(self.manager.processing), 1)
        self.assertEqual(msg, self.message1)
        self.assertEqual(msg.status, "processing")
        
        # 处理另一条消息
        msg = self.manager.process_next()
        
        # 验证消息已从收件箱移动到处理中
        self.assertEqual(len(self.manager.inbox), 0)
        self.assertEqual(len(self.manager.processing), 2)
        self.assertEqual(msg, self.message2)
        self.assertEqual(msg.status, "processing")
        
        # 尝试处理空收件箱
        msg = self.manager.process_next()
        
        # 验证结果
        self.assertIsNone(msg)
    
    def test_archive_message(self):
        """测试archive_message方法"""
        # 添加消息
        self.manager.append(self.message1)
        
        # 处理消息
        msg = self.manager.process_next()
        
        # 归档消息
        result = self.manager.archive_message(msg.id)
        
        # 验证消息已从处理中移动到归档
        self.assertTrue(result)
        self.assertEqual(len(self.manager.processing), 0)
        self.assertEqual(len(self.manager.archive), 1)
        self.assertEqual(self.manager.archive[0], msg)
        self.assertEqual(msg.status, "archive")
        
        # 尝试归档不存在的消息
        result = self.manager.archive_message("non-existent-id")
        
        # 验证结果
        self.assertFalse(result)
        
        # 尝试直接归档收件箱中的消息
        self.manager.append(self.message2)
        result = self.manager.archive_message(self.message2.id)
        
        # 验证结果
        self.assertTrue(result)
        self.assertEqual(len(self.manager.inbox), 0)
        self.assertEqual(len(self.manager.archive), 2)
        self.assertEqual(self.message2.status, "archive")
    
    def test_get_all_messages(self):
        """测试get_all_messages方法"""
        # 添加消息
        self.manager.append(self.message1)
        
        # 处理消息
        msg = self.manager.process_next()
        
        # 归档消息
        self.manager.archive_message(msg.id)
        
        # 添加更多消息
        self.manager.append(self.message2)
        self.manager.append(self.message3)
        
        # 获取所有消息
        messages = self.manager.get_all_messages()
        
        # 验证获取的消息
        self.assertEqual(len(messages), 3)
        self.assertIn(self.message1, messages)
        self.assertIn(self.message2, messages)
        self.assertIn(self.message3, messages)
    
    def test_get_messages_by_status(self):
        """测试get_messages_by_status方法"""
        # 添加消息
        self.manager.append(self.message1)
        self.manager.append(self.message2)
        
        # 处理消息
        msg = self.manager.process_next()
        
        # 归档消息
        self.manager.archive_message(msg.id)
        
        # 添加更多消息
        self.manager.append(self.message3)
        
        # 获取收件箱消息
        inbox_messages = self.manager.get_messages_by_status("inbox")
        
        # 验证收件箱消息
        self.assertEqual(len(inbox_messages), 2)
        self.assertIn(self.message2, inbox_messages)
        self.assertIn(self.message3, inbox_messages)
        
        # 获取处理中消息
        processing_messages = self.manager.get_messages_by_status("processing")
        
        # 验证处理中消息
        self.assertEqual(len(processing_messages), 0)
        
        # 获取归档消息
        archive_messages = self.manager.get_messages_by_status("archive")
        
        # 验证归档消息
        self.assertEqual(len(archive_messages), 1)
        self.assertIn(self.message1, archive_messages)
        
        # 获取无效状态消息
        with self.assertRaises(ValueError):
            self.manager.get_messages_by_status("invalid_status")
    
    def test_get_message_by_id(self):
        """测试get_message_by_id方法"""
        # 添加消息
        self.manager.append(self.message1)
        self.manager.append(self.message2)
        
        # 获取消息
        msg = self.manager.get_message_by_id(self.message1.id)
        
        # 验证获取的消息
        self.assertEqual(msg, self.message1)
        
        # 获取不存在的消息
        msg = self.manager.get_message_by_id("non-existent-id")
        
        # 验证结果
        self.assertIsNone(msg)
    
    def test_clear_messages(self):
        """测试clear_messages方法"""
        # 添加消息
        self.manager.append(self.message1)
        
        # 处理消息
        msg = self.manager.process_next()
        
        # 归档消息
        self.manager.archive_message(msg.id)
        
        # 添加更多消息
        self.manager.append(self.message2)
        self.manager.append(self.message3)
        
        # 清空消息
        self.manager.clear_messages()
        
        # 验证所有队列都为空
        self.assertEqual(len(self.manager.inbox), 0)
        self.assertEqual(len(self.manager.processing), 0)
        self.assertEqual(len(self.manager.archive), 0)
    
    def test_clear_inbox(self):
        """测试clear_inbox方法"""
        # 添加消息
        self.manager.append(self.message1)
        
        # 处理消息
        msg = self.manager.process_next()
        
        # 清空收件箱
        self.manager.clear_inbox()
        
        # 验证收件箱为空
        self.assertEqual(len(self.manager.inbox), 0)
        
        # 验证处理中消息未受影响
        self.assertEqual(len(self.manager.processing), 1)
    
    def test_clear_processing(self):
        """测试clear_processing方法"""
        # 添加消息
        self.manager.append(self.message1)
        self.manager.append(self.message2)
        
        # 处理消息
        msg = self.manager.process_next()
        
        # 清空处理中
        self.manager.clear_processing()
        
        # 验证处理中为空
        self.assertEqual(len(self.manager.processing), 0)
        
        # 验证收件箱未受影响
        self.assertEqual(len(self.manager.inbox), 1)
    
    def test_clear_archive(self):
        """测试clear_archive方法"""
        # 添加消息
        self.manager.append(self.message1)
        
        # 处理消息
        msg = self.manager.process_next()
        
        # 归档消息
        self.manager.archive_message(msg.id)
        
        # 添加更多消息
        self.manager.append(self.message2)
        
        # 清空归档
        self.manager.clear_archive()
        
        # 验证归档为空
        self.assertEqual(len(self.manager.archive), 0)
        
        # 验证收件箱未受影响
        self.assertEqual(len(self.manager.inbox), 1)


if __name__ == "__main__":
    unittest.main() 