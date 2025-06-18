# Custom PDF MCP Server

基于 FastMCP 构建的自定义 PDF 处理服务器，专为毕业论文文献处理设计。

## 功能特性

- **读取PDF文本**: 支持提取整个PDF或指定页面的文本内容
- **提取表格数据**: 可选择提取PDF中的表格结构
- **获取PDF信息**: 提取PDF的元数据信息（作者、标题等）
- **列出PDF文件**: 扫描目录下所有PDF文件
- **安全限制**: 只能访问当前工作目录下的文件

## 安装方法

### 方法一：使用 uv（推荐）
```bash
# 克隆项目
git clone https://github.com/yourusername/pdf-mcp.git
cd pdf-mcp

# 创建虚拟环境并安装依赖
uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方法二：使用 pip
```bash
# 克隆项目
git clone https://github.com/yourusername/pdf-mcp.git
cd pdf-mcp

# 安装依赖
pip install . --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 使用方法

### 1. 直接运行测试
```bash
# 如果使用 uv
uv run pdf-mcp

# 如果使用传统方式
python src/pdf_mcp_server.py
```

### 2. 配置 Claude Desktop

在 `claude_desktop_config.json` 中添加以下配置：

```json
{
  "mcpServers": {
    "pdf-reader-custom": {
      "command": "uv",
      "args": [
         "--directory",
         "path/to/your/pdf-mcp"
         "run",
         "pdf-mcp"
      ],
    }
  }
}
```

**注意**：
- 将 `path/to/your/pdf-mcp` 替换为实际的项目路径

## 可用工具

### read_pdf_text
读取PDF文件并提取文本内容

参数：
- `file_path`: PDF文件路径（相对于工作目录）
- `page_numbers`: 可选，要提取的页面号列表
- `extract_tables`: 可选，是否提取表格数据

### get_pdf_info
获取PDF文件的基本信息和元数据

参数：
- `file_path`: PDF文件路径

### list_pdfs_in_directory
列出指定目录下的所有PDF文件

参数：
- `directory_path`: 目录路径，默认为当前目录

## 使用示例

1. **读取整个PDF**:
   ```
   read_pdf_text("文献整理/某篇论文.pdf")
   ```

2. **只读取特定页面**:
   ```
   read_pdf_text("文献整理/某篇论文.pdf", [1, 2, 3])
   ```

3. **提取表格数据**:
   ```
   read_pdf_text("文献整理/某篇论文.pdf", extract_tables=True)
   ```

4. **获取PDF信息**:
   ```
   get_pdf_info("文献整理/某篇论文.pdf")
   ```

5. **列出所有PDF**:
   ```
   list_pdfs_in_directory("文献整理")
   ``` 