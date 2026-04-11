#!/usr/bin/env python3
"""
APIFox JSON 解析脚本
用于快速提取接口定义和数据模型结构
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


class APIFoxParser:
    """APIFox JSON 解析器"""

    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self.data = self._load_json()

    def _load_json(self) -> Dict:
        """加载 JSON 文件"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_modules(self) -> List[Dict]:
        """获取所有模块"""
        modules = []
        for collection in self.data.get('apiCollection', []):
            for folder in collection.get('items', []):
                modules.append({
                    'name': folder.get('name'),
                    'id': folder.get('id'),
                    'apis': self._get_apis_from_folder(folder)
                })
        return modules

    def _get_apis_from_folder(self, folder: Dict) -> List[Dict]:
        """从文件夹中提取所有接口"""
        apis = []
        for item in folder.get('items', []):
            if 'api' in item:
                api = item['api']
                apis.append({
                    'name': item.get('name'),
                    'method': api.get('method'),
                    'path': api.get('path'),
                    'parameters': api.get('parameters', {}),
                    'request_body': api.get('requestBody', {}),
                    'responses': api.get('responses', []),
                })
        return apis

    def get_schemas(self) -> Dict:
        """获取所有数据模型定义"""
        schemas = {}
        for collection in self.data.get('schemaCollection', []):
            for category in collection.get('items', []):
                for schema in category.get('items', []):
                    schema_id = schema.get('id', '')
                    if schema_id.startswith('#/definitions/'):
                        schema_id = schema_id.replace('#/definitions/', '')
                    schemas[schema_id] = {
                        'name': schema.get('name'),
                        'display_name': schema.get('displayName'),
                        'json_schema': schema.get('schema', {}).get('jsonSchema', {})
                    }
        return schemas

    def print_summary(self):
        """打印解析摘要"""
        print("=" * 60)
        print("APIFox 接口文档解析摘要")
        print("=" * 60)

        modules = self.get_modules()
        print(f"\n📁 模块数量: {len(modules)}\n")

        for module in modules:
            print(f"模块: {module['name']}")
            print(f"  ID: {module['id']}")
            print(f"  接口数量: {len(module['apis'])}")
            print("  接口列表:")
            for api in module['apis']:
                print(f"    {api['method']:6} {api['path']}")
            print()

        schemas = self.get_schemas()
        print(f"📊 数据模型数量: {len(schemas)}\n")
        for schema_id, schema in schemas.items():
            print(f"  {schema_id}: {schema.get('display_name', schema.get('name'))}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python parse_apifox.py <apifox.json>")
        sys.exit(1)

    json_path = sys.argv[1]
    parser = APIFoxParser(json_path)
    parser.print_summary()


if __name__ == '__main__':
    main()
