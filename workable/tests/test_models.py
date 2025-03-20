"""
测试基础数据模型
"""

import unittest
from dataclasses import asdict

from workable.core.models import WorkableFrame, Message, Relation

class TestWorkableFrame(unittest.TestCase):
    """测试WorkableFrame类"""
    
    def test_frame_init(self):
        """测试初始化WorkableFrame"""
        frame = WorkableFrame(
            name="Test Frame",
            logic_description="Test description",
            snapshot="Test snapshot",
            exref="external-uuid",
            lnref=None
        )
        
        self.assertEqual(frame.name, "Test Frame")
        self.assertEqual(frame.logic_description, "Test description")
        self.assertEqual(frame.snapshot, "Test snapshot")
        self.assertEqual(frame.exref, "external-uuid")
        self.assertIsNone(frame.lnref)
    
    def test_is_external(self):
        """测试is_external方法"""
        external_frame = WorkableFrame(
            name="External Frame",
            logic_description="External reference",
            exref="external-uuid"
        )
        
        local_frame = WorkableFrame(
            name="Local Frame",
            logic_description="Local reference",
            lnref="local-uuid"
        )
        
        self.assertTrue(external_frame.is_external())
        self.assertFalse(local_frame.is_external())


class TestMessage(unittest.TestCase):
    """测试Message类"""
    
    def test_message_init(self):
        """测试初始化Message"""
        message = Message(
            content="Test message content",
            sender="sender-uuid",
            receiver="receiver-uuid"
        )
        
        self.assertEqual(message.content, "Test message content")
        self.assertEqual(message.sender, "sender-uuid")
        self.assertEqual(message.receiver, "receiver-uuid")
        self.assertEqual(message.status, "inbox")  # 默认状态
    
    def test_message_post_init(self):
        """测试Message的__post_init__方法"""
        # 测试有效状态
        valid_message = Message(
            content="Valid status",
            sender="sender",
            receiver="receiver",
            status="processing"
        )
        self.assertEqual(valid_message.status, "processing")
        
        # 测试无效状态，应自动设为"inbox"
        invalid_message = Message(
            content="Invalid status",
            sender="sender",
            receiver="receiver",
            status="unknown"
        )
        self.assertEqual(invalid_message.status, "inbox")


class TestRelation(unittest.TestCase):
    """测试Relation类"""
    
    def test_relation_init(self):
        """测试初始化Relation"""
        relation = Relation(target_uuid="target-uuid")
        
        self.assertEqual(relation.target_uuid, "target-uuid")
        self.assertIsNotNone(relation.meta)
        self.assertEqual(relation.meta, {})
    
    def test_relation_with_meta(self):
        """测试带元数据的Relation"""
        meta = {"key": "value", "priority": 1}
        relation = Relation(target_uuid="target-uuid", meta=meta)
        
        self.assertEqual(relation.target_uuid, "target-uuid")
        self.assertEqual(relation.meta, meta)
        
        # 测试元数据可以更新
        relation.meta["new_key"] = "new_value"
        self.assertEqual(relation.meta["new_key"], "new_value")


if __name__ == "__main__":
    unittest.main() 