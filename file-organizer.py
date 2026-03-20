#!/usr/bin/env python3
"""
📁 智能文件整理工具
Smart File Organizer

自动按类型、日期整理文件
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict


class FileOrganizer:
    """智能文件整理器"""
    
    FILE_CATEGORIES = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'],
        'Videos': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        'Code': ['.py', '.js', '.java', '.c', '.cpp', '.h', '.html', '.css', '.json', '.xml', '.sh'],
        'Data': ['.json', '.xml', '.csv', '.sql', '.db', '.sqlite'],
    }
    
    def __init__(self, path: str, organize_by: str = 'type', dry_run: bool = True):
        self.path = Path(path)
        self.organize_by = organize_by
        self.dry_run = dry_run
        self.stats = {
            'total_files': 0,
            'organized': 0,
            'errors': []
        }
    
    def get_category(self, file_path: Path) -> str:
        """获取文件分类"""
        ext = file_path.suffix.lower()
        for category, extensions in self.FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return 'Others'
    
    def organize_by_type(self) -> None:
        """按类型整理"""
        print(f"\n📂 按文件类型整理: {self.path}")
        
        for file_path in self.path.iterdir():
            if not file_path.is_file():
                continue
            
            self.stats['total_files'] += 1
            category = self.get_category(file_path)
            target_dir = self.path / category
            
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                # 检查是否是照片（可能有拍摄日期）
                try:
                    mtime = file_path.stat().st_mtime
                    date = datetime.fromtimestamp(mtime).strftime('%Y-%m')
                    target_dir = self.path / category / date
                except:
                    pass
            
            if not self.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(target_dir / file_path.name))
            
            print(f"   {file_path.name} → {target_dir.name}/")
            self.stats['organized'] += 1
    
    def organize_by_date(self) -> None:
        """按日期整理"""
        print(f"\n📅 按修改日期整理: {self.path}")
        
        date_groups = defaultdict(list)
        
        for file_path in self.path.iterdir():
            if not file_path.is_file():
                continue
            
            self.stats['total_files'] += 1
            try:
                mtime = file_path.stat().st_mtime
                date = datetime.fromtimestamp(mtime).strftime('%Y-%m')
                date_groups[date].append(file_path)
            except Exception as e:
                self.stats['errors'].append(f"{file_path.name}: {e}")
        
        for date, files in sorted(date_groups.items()):
            target_dir = self.path / date
            
            if not self.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in files:
                if not self.dry_run:
                    shutil.move(str(file_path), str(target_dir / file_path.name))
                print(f"   {file_path.name} → {date}/")
                self.stats['organized'] += 1
    
    def run(self) -> None:
        """运行整理流程"""
        print("🚀 智能文件整理工具 v1.0")
        print("="*50)
        
        if self.organize_by == 'type':
            self.organize_by_type()
        elif self.organize_by == 'date':
            self.organize_by_date()
        
        mode = "🔍 预览模式" if self.dry_run else "⚠️  执行整理"
        print(f"\n{mode}")
        print(f"📊 总文件: {self.stats['total_files']}, 已整理: {self.stats['organized']}")
        
        if self.stats['errors']:
            print(f"⚠️  错误: {len(self.stats['errors'])}")


def main():
    parser = argparse.ArgumentParser(description='📁 智能文件整理工具')
    parser.add_argument('-p', '--path', required=True, help='要整理的目录')
    parser.add_argument('-m', '--mode', default='type', choices=['type', 'date'], 
                        help='整理模式: type=按类型, date=按日期')
    parser.add_argument('-d', '--delete', action='store_true', help='执行整理（默认预览）')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"❌ 错误: 目录不存在: {args.path}")
        return
    
    organizer = FileOrganizer(args.path, args.mode, dry_run=not args.delete)
    organizer.run()


if __name__ == '__main__':
    main()
