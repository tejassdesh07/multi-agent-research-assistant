import os
import json
from typing import Optional
from datetime import datetime
from crewai_tools import tool
import yaml


class FileSystemTool:
    def __init__(self, base_directory: str = "./data/research"):
        self.base_directory = base_directory
        os.makedirs(base_directory, exist_ok=True)
        
    def _get_safe_path(self, filename: str) -> str:
        filename = os.path.basename(filename)
        full_path = os.path.join(self.base_directory, filename)
        if not os.path.abspath(full_path).startswith(os.path.abspath(self.base_directory)):
            raise ValueError("Invalid file path")
        return full_path
    
    def save_research(self, content: str, filename: Optional[str] = None, format: str = "txt") -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_{timestamp}.{format}"
        file_path = self._get_safe_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def load_research(self, filename: str) -> str:
        file_path = self._get_safe_path(filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {filename}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_files(self) -> list:
        files = []
        for filename in os.listdir(self.base_directory):
            file_path = os.path.join(self.base_directory, filename)
            if os.path.isfile(file_path):
                files.append({
                    'filename': filename,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).isoformat()
                })
        return files


# Global file system instance
_fs_instance = None

def get_fs_instance() -> FileSystemTool:
    """Get or create global file system instance"""
    global _fs_instance
    if _fs_instance is None:
        _fs_instance = FileSystemTool()
    return _fs_instance


@tool("save_to_file")
def save_to_file_tool(content: str, filename: str) -> str:
    """Save research data or findings to a file for later reference."""
    fs = get_fs_instance()
    file_path = fs.save_research(content, filename)
    return f"Successfully saved to: {file_path}"


@tool("load_from_file")
def load_from_file_tool(filename: str) -> str:
    """Load previously saved research data from a file."""
    fs = get_fs_instance()
    try:
        content = fs.load_research(filename)
        return content
    except FileNotFoundError:
        return f"File not found: {filename}"


@tool("list_research_files")
def list_research_files_tool() -> str:
    """List all saved research files."""
    fs = get_fs_instance()
    files = fs.list_files()
    return json.dumps(files, indent=2)

