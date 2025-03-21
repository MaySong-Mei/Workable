"""
测试WorkableManager类
"""

import unittest
import logging
import uuid
from unittest.mock import patch, MagicMock

from workable.core.manager import WorkableManager
from workable.core.workable import Workable
from workable.core.exceptions import WorkableError, ManagerError

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class TestWorkableManager(unittest.TestCase):
    """测试WorkableManager类"""
    
    def setUp(self):
        """每个测试前执行"""
        self.manager = WorkableManager()
        
        # 创建一些测试Workable
        self.atom1 = Workable(
            name="Atom 1",
            logic_description="Atomic workable 1",
            is_atom=True,
            content_str="Content 1",
            content_type="text"
        )
        
        self.atom2 = Workable(
            name="Atom 2",
            logic_description="Atomic workable 2",
            is_atom=True,
            content_str="Content 2",
            content_type="code"
        )
        
        self.composite1 = Workable(
            name="Composite 1",
            logic_description="Composite workable 1",
            is_atom=False
        )
        
        self.composite2 = Workable(
            name="Composite 2",
            logic_description="Composite workable 2",
            is_atom=False
        )
    
    def test_register_workable(self):
        """测试register_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.atom1)
        self.manager.register_workable(self.composite1)
        
        # 验证注册结果
        self.assertEqual(len(self.manager.workables), 2)
        self.assertIn(self.atom1.uuid, self.manager.workables)
        self.assertIn(self.composite1.uuid, self.manager.workables)
        
        # 注册相同UUID的Workable应该失败
        duplicate = Workable(
            name="Duplicate",
            logic_description="Duplicate workable",
            is_atom=True,
            content_str="Duplicate content"
        )
        duplicate.uuid = self.atom1.uuid  # 手动设置相同的UUID
        
        with self.assertRaises(WorkableError):
            self.manager.register_workable(duplicate)
    
    def test_unregister_workable(self):
        """测试unregister_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.atom1)
        self.manager.register_workable(self.composite1)
        
        # 验证是否已注册
        self.assertEqual(len(self.manager.workables), 2)
        
        # 注销Workable
        result = self.manager.unregister_workable(self.atom1.uuid)
        
        # 验证是否已注销
        self.assertTrue(result)
        self.assertEqual(len(self.manager.workables), 1)
        self.assertNotIn(self.atom1.uuid, self.manager.workables)
        
        # 注销不存在的Workable
        result = self.manager.unregister_workable("non-existent-uuid")
        
        # 验证结果
        self.assertFalse(result)
    
    def test_get_workable(self):
        """测试get_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.atom1)
        
        # 获取Workable
        workable = self.manager.get_workable(self.atom1.uuid)
        
        # 验证获取的Workable
        self.assertEqual(workable, self.atom1)
        
        # 获取不存在的Workable
        workable = self.manager.get_workable("non-existent-uuid")
        
        # 验证结果
        self.assertIsNone(workable)
    
    def test_get_all_workables(self):
        """测试get_all_workables方法"""
        # 注册Workable
        self.manager.register_workable(self.atom1)
        self.manager.register_workable(self.atom2)
        self.manager.register_workable(self.composite1)
        
        # 获取所有Workable
        workables = self.manager.get_all_workables()
        
        # 验证获取的Workables
        self.assertEqual(len(workables), 3)
        self.assertIn(self.atom1.uuid, workables)
        self.assertIn(self.atom2.uuid, workables)
        self.assertIn(self.composite1.uuid, workables)
        
        # 验证返回的是副本
        workables[self.atom1.uuid] = None
        self.assertEqual(len(self.manager.workables), 3)
    
    def test_get_workables_by_type(self):
        """测试get_workables_by_type方法"""
        # 注册Workable
        self.manager.register_workable(self.atom1)
        self.manager.register_workable(self.atom2)
        self.manager.register_workable(self.composite1)
        self.manager.register_workable(self.composite2)
        
        # 获取所有原子模式Workable
        atoms = self.manager.get_workables_by_type(is_atom=True)
        
        # 验证获取的原子模式Workables
        self.assertEqual(len(atoms), 2)
        self.assertIn(self.atom1.uuid, atoms)
        self.assertIn(self.atom2.uuid, atoms)
        self.assertNotIn(self.composite1.uuid, atoms)
        self.assertNotIn(self.composite2.uuid, atoms)
        
        # 获取所有复合模式Workable
        composites = self.manager.get_workables_by_type(is_atom=False)
        
        # 验证获取的复合模式Workables
        self.assertEqual(len(composites), 2)
        self.assertIn(self.composite1.uuid, composites)
        self.assertIn(self.composite2.uuid, composites)
        self.assertNotIn(self.atom1.uuid, composites)
        self.assertNotIn(self.atom2.uuid, composites)
    
    def test_create_workable(self):
        """测试create_workable方法"""
        # 创建原子模式Workable
        atom = self.manager.create_workable(
            name="New Atom",
            logic_description="New atomic workable",
            is_atom=True,
            content="New content",
            content_type="text"
        )
        
        # 验证创建结果
        self.assertEqual(len(self.manager.workables), 1)
        self.assertIn(atom.uuid, self.manager.workables)
        self.assertTrue(atom.is_atom())
        self.assertEqual(atom.content_str, "New content")
        self.assertEqual(atom.content_type, "text")
        
        # 创建复合模式Workable
        composite = self.manager.create_workable(
            name="New Complex",
            logic_description="New complex workable",
            is_atom=False
        )
        
        # 验证创建结果
        self.assertEqual(len(self.manager.workables), 2)
        self.assertIn(composite.uuid, self.manager.workables)
        self.assertTrue(composite.is_complex())
    
    def test_update_workable(self):
        """测试update_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.atom1)
        
        # 更新Workable
        result = self.manager.update_workable(
            self.atom1.uuid,
            name="Updated Atom",
            logic_description="Updated description"
        )
        
        # 验证更新结果
        self.assertTrue(result)
        
        # 验证更新的Workable
        workable = self.manager.get_workable(self.atom1.uuid)
        self.assertEqual(workable.name, "Updated Atom")
        self.assertEqual(workable.logic_description, "Updated description")
        
        # 更新不存在的Workable
        result = self.manager.update_workable(
            "non-existent-uuid",
            name="Updated Name"
        )
        
        # 验证结果
        self.assertFalse(result)
    
    def test_update_workable_content(self):
        """测试update_simple_workable_content方法"""
        # 注册原子模式Workable
        self.manager.register_workable(self.atom1)
        
        # 更新原子模式Workable内容
        result = self.manager.update_simple_workable_content(
            self.atom1.uuid,
            "Updated content"
        )
        
        # 验证更新结果
        self.assertTrue(result)
        
        # 验证更新的原子模式Workable
        workable = self.manager.get_workable(self.atom1.uuid)
        self.assertEqual(workable.content_str, "Updated content")
        
        # 更新复合模式Workable内容（应该失败）
        self.manager.register_workable(self.composite1)
        
        result = self.manager.update_simple_workable_content(
            self.composite1.uuid,
            "This should fail"
        )
        
        # 验证结果
        self.assertFalse(result)
        
        # 更新不存在的Workable
        result = self.manager.update_simple_workable_content(
            "non-existent-uuid",
            "This should fail"
        )
        
        # 验证结果
        self.assertFalse(result)
    
    def test_delete_workable(self):
        """测试delete_workable方法"""
        # 注册Workable
        self.manager.register_workable(self.atom1)
        
        # 删除Workable
        result = self.manager.delete_workable(self.atom1.uuid)
        
        # 验证删除结果
        self.assertTrue(result)
        self.assertEqual(len(self.manager.workables), 0)
        
        # 删除不存在的Workable
        result = self.manager.delete_workable("non-existent-uuid")
        
        # 验证结果
        self.assertFalse(result)
    
    def test_create_simple_workable_backward_compatibility(self):
        """测试create_simple_workable向后兼容方法"""
        # 使用旧方法创建原子模式Workable
        atom_uuid = self.manager.create_simple_workable(
            name="Legacy Atom",
            logic_description="Legacy atomic workable",
            content_str="Legacy content",
            content_type="text"
        )
        
        # 验证创建的原子模式Workable
        workable = self.manager.get_workable(atom_uuid)
        self.assertEqual(workable.name, "Legacy Atom")
        self.assertTrue(workable.is_atom())
        self.assertEqual(workable.content_str, "Legacy content")
    
    def test_create_complex_workable_backward_compatibility(self):
        """测试create_complex_workable向后兼容方法"""
        # 使用旧方法创建复合模式Workable
        composite_uuid = self.manager.create_complex_workable(
            name="Legacy Composite",
            logic_description="Legacy composite workable"
        )
        
        # 验证创建的复合模式Workable
        workable = self.manager.get_workable(composite_uuid)
        self.assertEqual(workable.name, "Legacy Composite")
        self.assertTrue(workable.is_complex())


if __name__ == "__main__":
    unittest.main() 