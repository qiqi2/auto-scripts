#!/usr/bin/env python3
"""
🖼️ AI 智能照片去重工具
AI-Powered Photo Deduplicator

自动扫描目录中的重复照片，保留最高质量版本，删除重复文件。
"""

import os
import sys
import hashlib
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x, **kwargs: x


class PhotoDeduplicator:
    """智能照片去重器"""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    def __init__(self, path: str, algorithm: str = 'md5', dry_run: bool = True):
        self.path = Path(path)
        self.algorithm = algorithm.lower()
        self.dry_run = dry_run
        self.hash_map: Dict[str, List[Path]] = {}
        self.stats = {
            'total_files': 0,
            'duplicate_groups': 0,
            'files_to_delete': 0,
            'space_to_save': 0,
            'errors': []
        }
    
    def get_file_hash(self, file_path: Path) -> Optional[str]:
        """计算文件哈希值"""
        try:
            hash_func = hashlib.new(self.algorithm)
            with open(file_path, 'rb') as f:
                # 分块读取，避免大文件内存问题
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self.stats['errors'].append(f"Error hashing {file_path}: {e}")
            return None
    
    def get_image_info(self, file_path: Path) -> Dict:
        """获取图片详细信息"""
        info = {
            'size': file_path.stat().st_size,
            'path': str(file_path)
        }
        
        if HAS_PIL:
            try:
                with Image.open(file_path) as img:
                    info['width'] = img.width
                    info['height'] = img.height
                    info['pixels'] = img.width * img.height
                    info['format'] = img.format
            except Exception:
                pass
        
        return info
    
    def scan_directory(self) -> None:
        """扫描目录中的所有图片文件"""
        print(f"\n📂 扫描目录: {self.path}")
        
        image_files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            image_files.extend(self.path.rglob(f'*{ext}'))
            image_files.extend(self.path.rglob(f'*{ext.upper()}'))
        
        self.stats['total_files'] = len(image_files)
        print(f"📷 找到 {len(image_files)} 张图片\n")
        
        # 计算每个文件的哈希值
        print("🔐 计算文件哈希值...")
        for file_path in tqdm(image_files, disable=not tqdm):
            file_hash = self.get_file_hash(file_path)
            if file_hash:
                if file_hash not in self.hash_map:
                    self.hash_map[file_hash] = []
                self.hash_map[file_hash].append(file_path)
        
        # 筛选出有重复的组
        self.duplicates = {k: v for k, v in self.hash_map.items() if len(v) > 1}
        self.stats['duplicate_groups'] = len(self.duplicates)
    
    def select_files_to_delete(self) -> List[Tuple[Path, Path]]:
        """
        选择要删除的文件
        策略：保留分辨率最高、文件最大的版本
        """
        to_delete = []
        
        for hash_val, files in self.duplicates.items():
            # 按文件大小排序（从大到小），保留最大的
            files_with_size = [(f, f.stat().st_size) for f in files]
            files_with_size.sort(key=lambda x: x[1], reverse=True)
            
            # 保留第一个（最大的），标记其余为删除
            keep_file = files_with_size[0][0]
            print(f"\n🖼️  保留: {keep_file.name} ({files_with_size[0][1]:,} bytes)")
            
            for delete_file, size in files_with_size[1:]:
                to_delete.append((delete_file, keep_file))
                self.stats['files_to_delete'] += 1
                self.stats['space_to_save'] += size
                print(f"   🗑️  删除: {delete_file.name} ({size:,} bytes)")
        
        return to_delete
    
    def execute_deletion(self, files_to_delete: List[Tuple[Path, Path]]) -> None:
        """执行删除操作"""
        if self.dry_run:
            print("\n🔍 预览模式 - 未执行任何删除操作")
            print("   使用 --delete 参数实际执行删除")
        else:
            print("\n⚠️  执行删除操作...")
            for delete_file, keep_file in files_to_delete:
                try:
                    os.remove(delete_file)
                    print(f"   ✅ 已删除: {delete_file.name}")
                except Exception as e:
                    print(f"   ❌ 删除失败: {delete_file.name} - {e}")
    
    def generate_report(self, format: str = 'text') -> str:
        """生成去重报告"""
        if format == 'json':
            return json.dumps(self.stats, indent=2, ensure_ascii=False)
        
        # 文本格式
        report = []
        report.append("\n" + "="*50)
        report.append("📊 AI 智能照片去重 - 分析报告")
        report.append("="*50)
        report.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"扫描目录: {self.path}")
        report.append(f"算法: {self.algorithm.upper()}")
        report.append("-"*50)
        report.append(f"📷 总文件数: {self.stats['total_files']}")
        report.append(f"🔄 重复组数: {self.stats['duplicate_groups']}")
        report.append(f"🗑️  可删除文件: {self.stats['files_to_delete']}")
        report.append(f"💾 可节省空间: {self.stats['space_to_save'] / 1024 / 1024:.2f} MB")
        
        if self.stats['errors']:
            report.append(f"\n⚠️  错误数量: {len(self.stats['errors'])}")
        
        report.append("="*50)
        
        return "\n".join(report)
    
    def run(self, report_format: str = 'text') -> None:
        """运行去重流程"""
        print("🚀 AI 智能照片去重工具 v1.0")
        print("="*50)
        
        # 扫描
        self.scan_directory()
        
        if not self.duplicates:
            print("\n🎉 未发现重复照片！")
            print(self.generate_report(report_format))
            return
        
        # 选择要删除的文件
        files_to_delete = self.select_files_to_delete()
        
        # 执行或预览
        self.execute_deletion(files_to_delete)
        
        # 生成报告
        print(self.generate_report(report_format))


def main():
    parser = argparse.ArgumentParser(
        description='🤖 AI 智能照片去重工具 - 自动清理重复照片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -p ~/Photos                    # 预览模式
  %(prog)s -p ~/Photos --delete           # 执行删除
  %(prog)s -p ~/Photos --report json      # JSON 格式报告
  %(prog)s -p ~/Photos --algorithm sha256 # 使用 SHA256
        """
    )
    
    parser.add_argument('-p', '--path', required=True, help='要扫描的目录路径')
    parser.add_argument('-d', '--delete', action='store_true', help='实际执行删除操作（默认预览）')
    parser.add_argument('-a', '--algorithm', default='md5', choices=['md5', 'sha256'], 
                        help='哈希算法 (默认: md5)')
    parser.add_argument('-r', '--report', default='text', choices=['text', 'json'],
                        help='报告格式 (默认: text)')
    
    args = parser.parse_args()
    
    # 验证路径
    if not os.path.isdir(args.path):
        print(f"❌ 错误: 目录不存在: {args.path}")
        sys.exit(1)
    
    # 创建去重器并运行
    deduplicator = PhotoDeduplicator(
        path=args.path,
        algorithm=args.algorithm,
        dry_run=not args.delete
    )
    
    deduplicator.run(args.report)


if __name__ == '__main__':
    main()
