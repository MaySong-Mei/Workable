"""
测试内容管理
"""

import unittest
import logging
from unittest.mock import patch, MagicMock

from workable.core.models import WorkableFrame
from workable.core.content import Content
from workable.core.exceptions import ContentError

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class MockSimpleWorkable:
    """模拟SimpleWorkable类"""
    
    def __init__(self, name, logic_description, content_str=""):
        self.uuid = f"mock-{name.lower().replace(' ', '-')}"
        self.name = name
        self.logic_description = logic_description
        self.content_str = content_str


class TestContent(unittest.TestCase):
    """测试Content类"""
    
    def setUp(self):
        """每个测试前执行"""
        self.content = Content()
        
        # 添加一些测试Frames
        self.frame1 = WorkableFrame(name="Frame 1", logic_description="Test frame 1", exref="ext-uuid-1")
        self.frame2 = WorkableFrame(name="Frame 2", logic_description="Test frame 2", lnref="local-uuid-1")
        
        # 添加一些测试Workables
        self.workable1 = MockSimpleWorkable(name="Workable 1", logic_description="Test workable 1")
        self.workable2 = MockSimpleWorkable(name="Workable 2", logic_description="Test workable 2")
    
    def test_frames_property(self):
        """测试frames属性"""
        # 添加Frame
        self.content.add_frame(self.frame1)
        
        # 获取frames副本
        frames = self.content.frames
        
        # 验证是否为副本
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].name, "Frame 1")
        
        # 修改副本不应影响原始数据
        frames.append(self.frame2)
        self.assertEqual(len(self.content.frames), 1)
    
    def test_workables_property(self):
        """测试workables属性"""
        # 添加本地Workable
        self.content._local_workables[self.workable1.uuid] = self.workable1
        
        # 获取workables副本
        workables = self.content.workables
        
        # 验证是否为副本
        self.assertEqual(len(workables), 1)
        self.assertEqual(list(workables.keys())[0], self.workable1.uuid)
        
        # 修改副本不应影响原始数据
        workables[self.workable2.uuid] = self.workable2
        self.assertEqual(len(self.content.workables), 1)
    
    def test_get_frame(self):
        """测试get_frame方法"""
        # 添加Frame
        self.content.add_frame(self.frame1)
        self.content.add_frame(self.frame2)
        
        # 获取有效索引
        frame = self.content.get_frame(1)
        self.assertEqual(frame.name, "Frame 2")
        
        # 获取无效索引
        frame = self.content.get_frame(2)
        self.assertIsNone(frame)
        
        frame = self.content.get_frame(-1)
        self.assertIsNone(frame)
    
    def test_get_workable(self):
        """测试get_workable方法"""
        # 添加本地Workable
        self.content._local_workables[self.workable1.uuid] = self.workable1
        
        # 获取有效UUID
        workable = self.content.get_workable(self.workable1.uuid)
        self.assertEqual(workable.name, "Workable 1")
        
        # 获取无效UUID
        workable = self.content.get_workable("invalid-uuid")
        self.assertIsNone(workable)
    
    def test_add_frame(self):
        """测试add_frame方法"""
        # 添加有效Frame
        index = self.content.add_frame(self.frame1)
        self.assertEqual(index, 0)
        self.assertEqual(len(self.content.frames), 1)
        
        # 添加无效Frame
        with self.assertRaises(ContentError):
            self.content.add_frame("not a frame")
    
    def test_add_local_workable(self):
        """测试add_local_workable方法"""
        # 添加有效Workable
        index = self.content.add_local_workable(self.workable1)
        self.assertEqual(index, 0)
        self.assertEqual(len(self.content.workables), 1)
        self.assertEqual(len(self.content.frames), 1)
        
        # 添加同一个Workable应该失败
        with self.assertRaises(ContentError):
            self.content.add_local_workable(self.workable1)
        
        # 添加无效Workable
        with self.assertRaises(ContentError):
            self.content.add_local_workable(None)
        
        with self.assertRaises(ContentError):
            self.content.add_local_workable("not a workable")
    
    def test_update_workable(self):
        """测试update_workable方法"""
        # 添加Workable
        self.content.add_local_workable(self.workable1)
        
        # 获取Frame
        frame = self.content.frames[0]
        self.assertEqual(frame.name, "Workable 1")
        
        # 更新Workable
        result = self.content.update_workable(
            self.workable1.uuid,
            name="Updated Name",
            logic_description="Updated description"
        )
        
        self.assertTrue(result)
        self.assertEqual(self.workable1.name, "Updated Name")
        self.assertEqual(self.workable1.logic_description, "Updated description")
        
        # 验证Frame也被更新
        frame = self.content.frames[0]
        self.assertEqual(frame.name, "Updated Name")
        self.assertEqual(frame.logic_description, "Updated description")
        
        # 更新不存在的Workable
        with self.assertRaises(ContentError):
            self.content.update_workable("invalid-uuid", name="New Name")
    
    def test_remove_frame(self):
        """测试remove_frame方法"""
        # 添加Frames
        self.content.add_frame(self.frame1)
        self.content.add_frame(self.frame2)
        
        # 移除有效索引
        frame = self.content.remove_frame(0)
        self.assertEqual(frame.name, "Frame 1")
        self.assertEqual(len(self.content.frames), 1)
        
        # 移除无效索引
        with self.assertRaises(ContentError):
            self.content.remove_frame(10)
    
    def test_remove_local_workable(self):
        """测试remove_local_workable方法"""
        # 添加Workables
        self.content.add_local_workable(self.workable1)
        self.content.add_local_workable(self.workable2)
        
        # 移除有效UUID
        result = self.content.remove_local_workable(self.workable1.uuid)
        self.assertTrue(result)
        self.assertEqual(len(self.content.workables), 1)
        self.assertEqual(len(self.content.frames), 1)
        
        # 确认正确的Frame被移除
        frame = self.content.frames[0]
        self.assertEqual(frame.name, "Workable 2")
        
        # 移除无效UUID
        with self.assertRaises(ContentError):
            self.content.remove_local_workable("invalid-uuid")
    
    def test_move_frame(self):
        """测试move_frame方法"""
        # 添加Frames
        self.content.add_frame(self.frame1)
        self.content.add_frame(self.frame2)
        
        # 移动Frame
        result = self.content.move_frame(0, 1)
        self.assertTrue(result)
        
        # 验证移动结果
        frames = self.content.frames
        self.assertEqual(frames[0].name, "Frame 2")
        self.assertEqual(frames[1].name, "Frame 1")
        
        # 测试无效索引
        with self.assertRaises(ContentError):
            self.content.move_frame(0, 10)
    
    def test_validate(self):
        """测试validate方法"""
        # 初始状态应该是有效的
        is_valid, orphans, ghosts = self.content.validate()
        self.assertTrue(is_valid)
        self.assertEqual(orphans, [])
        self.assertEqual(ghosts, [])
        
        # 添加一个本地Workable
        self.content.add_local_workable(self.workable1)
        is_valid, orphans, ghosts = self.content.validate()
        self.assertTrue(is_valid)
        
        # 创建孤立Frame
        orphan_frame = WorkableFrame(
            name="Orphan Frame",
            logic_description="Orphan frame",
            lnref="non-existent-uuid"
        )
        self.content.add_frame(orphan_frame)
        
        is_valid, orphans, ghosts = self.content.validate()
        self.assertFalse(is_valid)
        self.assertEqual(len(orphans), 1)
        self.assertEqual(orphans[0], 1)  # 第二个Frame (索引1)
        
        # 创建幽灵Workable（没有对应Frame引用）
        self.content._local_workables["ghost-uuid"] = MockSimpleWorkable(
            name="Ghost Workable",
            logic_description="Ghost workable"
        )
        
        is_valid, orphans, ghosts = self.content.validate()
        self.assertFalse(is_valid)
        self.assertEqual(len(ghosts), 1)
        self.assertEqual(ghosts[0], "ghost-uuid")
    
    def test_repair(self):
        """测试repair方法"""
        # 添加有效数据
        self.content.add_local_workable(self.workable1)
        
        # 添加孤立Frame
        orphan_frame = WorkableFrame(
            name="Orphan Frame",
            logic_description="Orphan frame",
            lnref="non-existent-uuid"
        )
        self.content.add_frame(orphan_frame)
        
        # 添加幽灵Workable
        ghost = MockSimpleWorkable(name="Ghost", logic_description="Ghost workable")
        self.content._local_workables[ghost.uuid] = ghost
        
        # 验证初始状态
        is_valid, orphans, ghosts = self.content.validate()
        self.assertFalse(is_valid)
        self.assertEqual(len(orphans), 1)
        self.assertEqual(len(ghosts), 1)
        
        # 修复数据
        result = self.content.repair()
        self.assertTrue(result)
        
        # 验证修复结果
        is_valid, orphans, ghosts = self.content.validate()
        self.assertTrue(is_valid)
        self.assertEqual(orphans, [])
        self.assertEqual(ghosts, [])
        
        # 验证数据正确性
        self.assertEqual(len(self.content.frames), 2)  # 1个有效 + 1个为幽灵Workable创建的


if __name__ == "__main__":
    unittest.main() 