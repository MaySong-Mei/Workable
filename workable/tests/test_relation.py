"""
测试关系管理器
"""

import unittest
import logging
from unittest.mock import patch, MagicMock

from workable.core.relation import RelationManager
from workable.core.models import Relation
from workable.core.exceptions import RelationError

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)

class TestRelationManager(unittest.TestCase):
    """测试RelationManager类"""
    
    def setUp(self):
        """每个测试前执行"""
        self.manager = RelationManager()
        
        # 创建一些测试关系
        self.relation1 = Relation(
            target_uuid="target-1"
        )
        
        self.relation2 = Relation(
            target_uuid="target-2",
            meta={"type": "parent"}
        )
        
        self.relation3 = Relation(
            target_uuid="target-3",
            meta={"type": "child"}
        )
    
    def test_init(self):
        """测试初始化RelationManager"""
        self.assertEqual(len(self.manager.relations), 0)
    
    def test_add(self):
        """测试add方法"""
        # 添加关系
        self.manager.add(self.relation1)
        
        # 验证关系已添加
        self.assertEqual(len(self.manager.relations), 1)
        self.assertIn(self.relation1.target_uuid, self.manager.relations)
        self.assertEqual(self.manager.relations[self.relation1.target_uuid], self.relation1)
        
        # 添加具有相同目标的关系（应覆盖）
        relation_duplicate = Relation(
            target_uuid="target-1",
            meta={"type": "sibling"}
        )
        self.manager.add(relation_duplicate)
        
        # 验证关系已覆盖
        self.assertEqual(len(self.manager.relations), 1)
        self.assertEqual(self.manager.relations[self.relation1.target_uuid].meta["type"], "sibling")
        
        # 添加无效关系
        with self.assertRaises(RelationError):
            self.manager.add("not a relation")
    
    def test_remove(self):
        """测试remove方法"""
        # 添加关系
        self.manager.add(self.relation1)
        self.manager.add(self.relation2)
        
        # 验证关系已添加
        self.assertEqual(len(self.manager.relations), 2)
        
        # 移除关系
        result = self.manager.remove(self.relation1.target_uuid)
        
        # 验证关系已移除
        self.assertTrue(result)
        self.assertEqual(len(self.manager.relations), 1)
        self.assertNotIn(self.relation1.target_uuid, self.manager.relations)
        
        # 移除不存在的关系
        result = self.manager.remove("non-existent-target")
        
        # 验证结果
        self.assertFalse(result)
    
    def test_get(self):
        """测试get方法"""
        # 添加关系
        self.manager.add(self.relation1)
        
        # 获取关系
        relation = self.manager.get(self.relation1.target_uuid)
        
        # 验证获取的关系
        self.assertEqual(relation, self.relation1)
        
        # 获取不存在的关系
        relation = self.manager.get("non-existent-target")
        
        # 验证结果
        self.assertIsNone(relation)
    
    def test_get_all(self):
        """测试get_all方法"""
        # 添加关系
        self.manager.add(self.relation1)
        self.manager.add(self.relation2)
        self.manager.add(self.relation3)
        
        # 获取所有关系
        relations = self.manager.get_all()
        
        # 验证获取的关系
        self.assertEqual(len(relations), 3)
        target_uuids = [rel.target_uuid for rel in relations]
        self.assertIn(self.relation1.target_uuid, target_uuids)
        self.assertIn(self.relation2.target_uuid, target_uuids)
        self.assertIn(self.relation3.target_uuid, target_uuids)
        
        # 验证返回的是副本
        initial_length = len(relations)
        relations.append(Relation(target_uuid="new-target"))
        self.assertEqual(len(self.manager.relations), 3)
    
    def test_update_meta(self):
        """测试update_meta方法"""
        # 添加关系
        self.manager.add(self.relation2)
        
        # 初始元数据
        self.assertEqual(self.relation2.meta["type"], "parent")
        
        # 更新元数据
        result = self.manager.update_meta(
            self.relation2.target_uuid,
            {"type": "updated-type", "new-key": "new-value"}
        )
        
        # 验证更新结果
        self.assertTrue(result)
        
        # 验证更新的元数据
        relation = self.manager.get(self.relation2.target_uuid)
        self.assertEqual(relation.meta["type"], "updated-type")
        self.assertEqual(relation.meta["new-key"], "new-value")
        
        # 更新不存在的关系
        result = self.manager.update_meta(
            "non-existent-target",
            {"type": "updated-type"}
        )
        
        # 验证结果
        self.assertFalse(result)
    
    def test_get_related_by_meta(self):
        """测试get_related_by_meta方法"""
        # 添加关系
        self.manager.add(self.relation1)
        self.manager.add(self.relation2)
        self.manager.add(self.relation3)
        
        # 为relation1添加元数据
        self.manager.update_meta(
            self.relation1.target_uuid,
            {"type": "sibling", "priority": "high"}
        )
        
        # 根据元数据获取关系
        relations_by_type = self.manager.get_related_by_meta("type", "parent")
        
        # 验证获取的关系
        self.assertEqual(len(relations_by_type), 1)
        self.assertIn(self.relation2.target_uuid, relations_by_type)
        
        # 获取具有多个关系的元数据
        self.manager.update_meta(
            self.relation3.target_uuid,
            {"type": "sibling", "priority": "low"}
        )
        
        relations_by_type = self.manager.get_related_by_meta("type", "sibling")
        
        # 验证获取的关系
        self.assertEqual(len(relations_by_type), 2)
        self.assertIn(self.relation1.target_uuid, relations_by_type)
        self.assertIn(self.relation3.target_uuid, relations_by_type)
        
        # 获取不存在的元数据
        relations_by_non_existent = self.manager.get_related_by_meta("non-existent-key", "value")
        
        # 验证结果
        self.assertEqual(len(relations_by_non_existent), 0)
    
    def test_clear(self):
        """测试clear方法"""
        # 添加关系
        self.manager.add(self.relation1)
        self.manager.add(self.relation2)
        
        # 验证关系已添加
        self.assertEqual(len(self.manager.relations), 2)
        
        # 清空关系
        self.manager.clear()
        
        # 验证关系已清空
        self.assertEqual(len(self.manager.relations), 0)
    
    def test_has_relation(self):
        """测试has_relation方法"""
        # 添加关系
        self.manager.add(self.relation1)
        
        # 验证关系存在
        result = self.manager.has_relation(self.relation1.target_uuid)
        self.assertTrue(result)
        
        # 验证关系不存在
        result = self.manager.has_relation("non-existent-target")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main() 