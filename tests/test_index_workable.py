"""
测试文件，用于验证基于索引的Workable框架功能
"""

import unittest
import logging
import sys
import traceback

from workable.core.workable import Workable
from workable.core.models import WorkableFrame
from workable.core.content import Content
from workable.core.exceptions import WorkableError, ConversionError


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)


class TestIndexedWorkable(unittest.TestCase):
    """测试基于索引的Workable框架"""
    
    def test_frame_creation(self):
        """测试WorkableFrame创建和属性"""
        try:
            frame = WorkableFrame(
                name="测试框架",
                logic_description="测试框架的逻辑描述",
                seq=1,
                frame_type="reference",
                exref="test-uuid"
            )
            
            self.assertEqual(frame.name, "测试框架")
            self.assertEqual(frame.logic_description, "测试框架的逻辑描述")
            self.assertEqual(frame.seq, 1)
            self.assertEqual(frame.frame_type, "reference")
            self.assertEqual(frame.exref, "test-uuid")
            self.assertTrue(frame.is_external())
            self.assertFalse(frame.is_local())
            self.assertEqual(frame.get_reference_uuid(), "test-uuid")
            
            # 测试元数据
            frame.update_metadata("key", "value")
            self.assertEqual(frame.get_metadata("key"), "value")
            self.assertEqual(frame.get_metadata("not-exist", "default"), "default")
        except Exception as e:
            print(f"测试WorkableFrame失败: {e}")
            traceback.print_exc()
            raise
        
    def test_content_management(self):
        """测试Content索引管理功能"""
        try:
            content = Content(content_type="code", content="test content")
            
            # 测试基本属性
            self.assertEqual(content.content_type, "code")
            self.assertEqual(content.content, "test content")
            self.assertEqual(content.frame_count, 0)
            
            # 添加框架
            seq1 = content.add_frame(
                name="框架1",
                logic_description="描述1",
                frame_type="reference",
                uuid="uuid1"
            )
            
            seq2 = content.add_frame(
                name="框架2",
                logic_description="描述2",
                frame_type="child",
                uuid="uuid2"
            )
            
            seq3 = content.add_frame(
                name="框架3",
                logic_description="描述3",
                frame_type="local",
                uuid="uuid3",
                is_local=True
            )
            
            # 测试框架数量
            self.assertEqual(content.frame_count, 3)
            
            # 测试获取框架
            frame1 = content.get_frame(seq1)
            self.assertEqual(frame1.name, "框架1")
            self.assertEqual(frame1.frame_type, "reference")
            
            # 测试通过UUID获取框架
            frames = content.get_frame_by_uuid("uuid2")
            self.assertEqual(len(frames), 1)
            self.assertEqual(frames[0].name, "框架2")
            
            # 测试通过类型获取框架
            local_frames = content.get_frames_by_type("local")
            self.assertEqual(len(local_frames), 1)
            self.assertEqual(local_frames[0].name, "框架3")
            
            # 测试更新框架
            content.update_frame(seq1, name="更新的框架1")
            frame1 = content.get_frame(seq1)
            self.assertEqual(frame1.name, "更新的框架1")
            
            # 测试删除框架
            self.assertTrue(content.remove_frame(seq3))
            self.assertEqual(content.frame_count, 2)
            self.assertEqual(len(content.get_frames_by_type("local")), 0)
            
            # 测试验证
            self.assertTrue(content.validate())
            
            # 测试清空
            content.clear_frames()
            self.assertEqual(content.frame_count, 0)
        except Exception as e:
            print(f"测试Content管理功能失败: {e}")
            traceback.print_exc()
            raise
        
    def test_workable_operations(self):
        """测试基于索引的Workable操作"""
        try:
            # 创建简单Workable
            simple = Workable(
                name="简单工作单元",
                logic_description="这是一个简单工作单元",
                is_atom=True,
                content_str="简单内容",
                content_type="text"
            )
            
            # 检查简单Workable属性
            self.assertTrue(simple.is_atom())
            self.assertEqual(simple.content_str, "简单内容")
            self.assertEqual(simple.content_type, "text")
            
            # 创建复杂Workable
            complex = Workable(
                name="复杂工作单元",
                logic_description="这是一个复杂工作单元",
                is_atom=False
            )
            
            # 检查复杂Workable属性
            self.assertFalse(complex.is_atom())
            self.assertEqual(len(complex.get_children()), 0)
            
            # 添加本地Workable到复杂Workable
            local = Workable(
                name="本地工作单元",
                logic_description="这是一个本地工作单元",
                is_atom=True,
                content_str="本地内容",
                content_type="text"
            )
            
            complex.add_local(local)
            
            # 检查本地Workable
            locals = complex.get_locals()
            self.assertEqual(len(locals), 1)
            self.assertEqual(locals[0].name, "本地工作单元")
            
            # 添加简单Workable作为复杂Workable的子Workable
            complex.add_child(simple)
            
            # 检查子Workable
            children = complex.get_children()
            self.assertEqual(len(children), 1)
            self.assertEqual(children[0].uuid, simple.uuid)
            
            # 检查通过to_dict序列化
            simple_dict = simple.to_dict()
            self.assertEqual(simple_dict["name"], "简单工作单元")
            self.assertEqual(simple_dict["content"], "简单内容")
            
            complex_dict = complex.to_dict()
            self.assertEqual(complex_dict["name"], "复杂工作单元")
            self.assertFalse(complex_dict["is_atom"])
        except Exception as e:
            print(f"测试Workable操作失败: {e}")
            traceback.print_exc()
            raise
        
    def test_workable_conversion(self):
        """测试Workable转换功能"""
        try:
            # 创建简单Workable
            simple = Workable(
                name="可转换工作单元",
                logic_description="这是一个将被转换的简单工作单元",
                is_atom=True,
                content_str="转换前内容",
                content_type="text"
            )
            
            # 转换为复杂Workable
            complex = simple.make_complex()
            
            # 检查转换结果
            self.assertFalse(complex.is_atom())
            self.assertEqual(complex.uuid, simple.uuid)  # UUID应该保持不变
            
            # 检查本地Workable（原内容）
            locals = complex.get_locals()
            self.assertEqual(len(locals), 1)
            self.assertEqual(locals[0].content_str, "转换前内容")
            
            # 添加新的子Workable
            child = Workable(
                name="子工作单元",
                logic_description="子工作单元描述",
                is_atom=True,
                content_str="子内容",
                content_type="text"
            )
            
            complex.add_child(child)
            
            # 尝试转换回简单Workable（应该失败，因为有子Workable）
            with self.assertRaises(ConversionError):
                complex.make_simple()
            
            # 移除子Workable
            complex.remove_child(child.uuid)
            
            # 现在应该可以转换回简单Workable
            simple_again = complex.make_simple()
            
            # 检查转换结果
            self.assertTrue(simple_again.is_atom())
            self.assertEqual(simple_again.uuid, complex.uuid)  # UUID应该保持不变
            self.assertEqual(simple_again.content_str, "转换前内容")
        except Exception as e:
            print(f"测试Workable转换功能失败: {e}")
            traceback.print_exc()
            raise
        
        
if __name__ == "__main__":
    unittest.main() 