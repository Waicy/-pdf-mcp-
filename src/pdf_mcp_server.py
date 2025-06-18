#!/usr/bin/env python3
"""
Custom PDF MCP Server using FastMCP
支持读取PDF文件并提取文本内容
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import PyPDF2
import pdfplumber
from fastmcp import FastMCP

# 创建MCP应用实例
mcp = FastMCP("PDF Reader MCP")

@mcp.tool()
def read_pdf_text(
    file_path: str,
    page_numbers: Optional[List[int]] = None,
    extract_tables: bool = False
) -> Dict[str, Any]:
    """
    读取PDF文件并提取文本内容
    
    Args:
        file_path: PDF文件绝对路径（必须是绝对路径）
        page_numbers: 要提取的页面号列表，如果为None则提取所有页面
        extract_tables: 是否提取表格数据
    
    Returns:
        包含文本内容、页面信息等的字典
    """
    try:
        # 验证输入必须是绝对路径
        if not os.path.isabs(file_path):
            return {
                "success": False,
                "error": f"File path must be absolute path, got: {file_path}"
            }
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not file_path.lower().endswith('.pdf'):
            return {
                "success": False,
                "error": "File must be a PDF"
            }
        
        result = {
            "success": True,
            "file_path": file_path,
            "pages": [],
            "total_pages": 0,
            "full_text": ""
        }
        
        # 使用pdfplumber读取PDF（更好的文本提取能力）
        with pdfplumber.open(file_path) as pdf:
            result["total_pages"] = len(pdf.pages)
            
            # 确定要处理的页面
            if page_numbers is None:
                pages_to_process = range(len(pdf.pages))
            else:
                pages_to_process = [p - 1 for p in page_numbers if 0 < p <= len(pdf.pages)]
            
            full_text_parts = []
            
            for page_idx in pages_to_process:
                page = pdf.pages[page_idx]
                page_text = page.extract_text() or ""
                
                page_info = {
                    "page_number": page_idx + 1,
                    "text": page_text
                }
                
                # 如果需要提取表格
                if extract_tables:
                    try:
                        tables = page.extract_tables()
                        page_info["tables"] = tables if tables else []
                    except Exception as e:
                        page_info["tables"] = []
                        page_info["table_extraction_error"] = str(e)
                
                result["pages"].append(page_info)
                full_text_parts.append(page_text)
            
            result["full_text"] = "\n\n".join(full_text_parts)
        
        return result
        
    except PermissionError as e:
        return {
            "success": False,
            "error": f"Permission denied accessing file: {file_path}. Error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading PDF: {str(e)}"
        }

@mcp.tool()
def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """
    获取PDF文件的基本信息
    
    Args:
        file_path: PDF文件绝对路径（必须是绝对路径）
    
    Returns:
        包含PDF元数据信息的字典
    """
    try:
        # 验证输入必须是绝对路径
        if not os.path.isabs(file_path):
            return {
                "success": False,
                "error": f"File path must be absolute path, got: {file_path}"
            }
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # 使用PyPDF2获取元数据
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            info = {
                "success": True,
                "file_path": file_path,
                "page_count": len(pdf_reader.pages),
                "metadata": {}
            }
            
            # 提取元数据
            if pdf_reader.metadata:
                metadata = pdf_reader.metadata
                info["metadata"] = {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "creation_date": str(metadata.get("/CreationDate", "")),
                    "modification_date": str(metadata.get("/ModDate", ""))
                }
            
            # 文件大小
            info["file_size"] = os.path.getsize(file_path)
            
            return info
            
    except PermissionError as e:
        return {
            "success": False,
            "error": f"Permission denied accessing file: {file_path}. Error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting PDF info: {str(e)}"
        }

@mcp.tool()
def list_pdfs_in_directory(directory_path: str) -> Dict[str, Any]:
    """
    列出指定目录下的所有PDF文件
    
    Args:
        directory_path: 目录绝对路径（必须是绝对路径）
    
    Returns:
        包含PDF文件列表的字典
    """
    try:
        # 验证输入必须是绝对路径
        if not os.path.isabs(directory_path):
            return {
                "success": False,
                "error": f"Directory path must be absolute path, got: {directory_path}"
            }
        
        if not os.path.exists(directory_path):
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}"
            }
        
        if not os.path.isdir(directory_path):
            return {
                "success": False,
                "error": f"Path is not a directory: {directory_path}"
            }
        
        pdf_files = []
        
        # 递归查找PDF文件
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_path = os.path.abspath(os.path.join(root, file))
                    
                    # 计算相对路径（相对于搜索目录）
                    relative_path = os.path.relpath(full_path, directory_path)
                    
                    try:
                        file_size = os.path.getsize(full_path)
                        modification_time = os.path.getmtime(full_path)
                        
                        pdf_files.append({
                            "filename": file,
                            "full_path": full_path,
                            "relative_path": relative_path,
                            "directory": os.path.abspath(root),
                            "size": file_size,
                            "modified": modification_time
                        })
                    except PermissionError as e:
                        # 如果权限不足，仍然添加文件名但标记权限错误
                        pdf_files.append({
                            "filename": file,
                            "full_path": full_path,
                            "relative_path": relative_path,
                            "directory": os.path.abspath(root),
                            "permission_error": str(e)
                        })
                    except Exception as e:
                        # 如果无法获取文件信息，仍然添加文件名
                        pdf_files.append({
                            "filename": file,
                            "full_path": full_path,
                            "relative_path": relative_path,
                            "directory": os.path.abspath(root),
                            "error": str(e)
                        })
        
        return {
            "success": True,
            "search_directory": directory_path,
            "pdf_count": len(pdf_files),
            "pdf_files": pdf_files
        }
        
    except PermissionError as e:
        return {
            "success": False,
            "error": f"Permission denied accessing directory: {directory_path}. Error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error listing PDFs: {str(e)}"
        }

def main():
    mcp.run()

if __name__ == "__main__":
    main()