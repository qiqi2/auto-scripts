# 🤖 Auto Scripts - 自动化脚本工具集

> 一键自动化处理重复照片、文件整理等繁琐任务

## ✨ 功能特性

### 🖼️ 智能照片清理 (photo-deduplicator.py)
- 自动扫描指定目录中的重复照片
- 支持多种哈希算法 (MD5, SHA256)
- 保留最高质量版本，智能删除重复
- 支持预览模式（只分析不删除）
- 生成详细清理报告

### 📁 文件整理 (file-organizer.py)
- 按文件类型自动分类
- 按日期整理文件
- 自定义规则支持

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/qiqi2/auto-scripts.git
cd auto-scripts

# 运行照片去重
python3 photo-deduplicator.py --path /path/to/photos --dry-run

# 实际执行清理
python3 photo-deduplicator.py --path /path/to/photos
```

## 📊 使用示例

### 照片去重
```bash
# 预览模式（分析但不做任何修改）
python3 photo-deduplicator.py -p ~/Photos --dry-run

# 执行清理（删除重复照片）
python3 photo-deduplicator.py -p ~/Photos --delete

# 使用 SHA256 算法（更精确但更慢）
python3 photo-deduplicator.py -p ~/Photos --algorithm sha256

# 生成 JSON 格式报告
python3 photo-deduplicator.py -p ~/Photos --report json
```

## 📋 要求

- Python 3.7+
- Pillow (图像处理)
- tqdm (进度条)

安装依赖：
```bash
pip3 install Pillow tqdm
```

## 📝 许可证

MIT License
