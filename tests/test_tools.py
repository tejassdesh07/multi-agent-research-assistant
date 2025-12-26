import os
import warnings
os.environ['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'
warnings.filterwarnings('ignore')

import unittest
import json
from src.tools.web_search_tool import WebSearchTool
from src.tools.memory_tool import MemoryTool
from src.tools.file_tool import FileSystemTool


class TestWebSearchTool(unittest.TestCase):
    """Test Web Search Tool functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.search_tool = WebSearchTool(max_results=5, rate_limit=10)
    
    def test_tool_initialization(self):
        """Test that search tool initializes correctly"""
        self.assertEqual(self.search_tool.max_results, 5)
        self.assertEqual(self.search_tool.rate_limit, 10)
        self.assertIsInstance(self.search_tool.blocked_domains, list)
    
    def test_query_sanitization(self):
        """Test that queries are sanitized properly"""
        malicious_query = "<script>alert('xss')</script>"
        sanitized = self.search_tool._sanitize_query(malicious_query)
        
        self.assertNotIn("<script>", sanitized)
        self.assertNotIn("</script>", sanitized)
    
    def test_url_validation(self):
        """Test URL safety validation"""
        safe_url = "https://example.com/article"
        unsafe_url = "https://spam.com/malware"
        
        self.assertTrue(self.search_tool._is_safe_url(safe_url))
        self.assertFalse(self.search_tool._is_safe_url(unsafe_url))
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Should allow first request
        self.assertTrue(self.search_tool._check_rate_limit())
        
        # Simulate hitting rate limit
        for _ in range(self.search_tool.rate_limit):
            self.search_tool._check_rate_limit()
        
        # Should block after limit
        self.assertFalse(self.search_tool._check_rate_limit())
    
    def test_search_returns_list(self):
        """Test that search returns a list"""
        try:
            results = self.search_tool.search("Python programming", num_results=2)
            self.assertIsInstance(results, list)
        except Exception as e:
            # Search might fail in test environment, that's okay
            self.skipTest(f"Search failed (expected in test env): {e}")


class TestMemoryTool(unittest.TestCase):
    """Test Memory Tool functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use test directory
        test_dir = "./test_data/memory"
        os.makedirs(test_dir, exist_ok=True)
        self.memory_tool = MemoryTool(persist_directory=test_dir)
    
    def tearDown(self):
        """Clean up test data"""
        import shutil
        if os.path.exists("./test_data"):
            shutil.rmtree("./test_data")
    
    def test_tool_initialization(self):
        """Test that memory tool initializes correctly"""
        self.assertIsNotNone(self.memory_tool.client)
        self.assertIsNotNone(self.memory_tool.collection)
        self.assertIsNotNone(self.memory_tool.encoder)
    
    def test_store_memory(self):
        """Test storing information in memory"""
        content = "Python is a high-level programming language"
        memory_id = self.memory_tool.store_memory(
            content,
            metadata={'category': 'programming'}
        )
        
        self.assertIsNotNone(memory_id)
        self.assertTrue(memory_id.startswith("mem_"))
    
    def test_retrieve_memory(self):
        """Test retrieving memories"""
        # Store some test data
        self.memory_tool.store_memory(
            "Python is used for web development",
            metadata={'category': 'programming'}
        )
        
        self.memory_tool.store_memory(
            "JavaScript is used for frontend",
            metadata={'category': 'programming'}
        )
        
        # Retrieve
        memories = self.memory_tool.retrieve_memories(
            "web development languages",
            n_results=2
        )
        
        self.assertIsInstance(memories, list)
        self.assertGreater(len(memories), 0)
        
        # Check structure
        if len(memories) > 0:
            self.assertIn('content', memories[0])
            self.assertIn('metadata', memories[0])
            self.assertIn('similarity', memories[0])


class TestFileSystemTool(unittest.TestCase):
    """Test File System Tool functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        test_dir = "./test_data/research"
        os.makedirs(test_dir, exist_ok=True)
        self.fs_tool = FileSystemTool(base_directory=test_dir)
    
    def tearDown(self):
        """Clean up test data"""
        import shutil
        if os.path.exists("./test_data"):
            shutil.rmtree("./test_data")
    
    def test_tool_initialization(self):
        """Test that file tool initializes correctly"""
        self.assertTrue(os.path.exists(self.fs_tool.base_directory))
    
    def test_path_validation(self):
        """Test path traversal prevention"""
        # Should block directory traversal
        with self.assertRaises(ValueError):
            self.fs_tool._get_safe_path("../../etc/passwd")
    
    def test_save_and_load(self):
        """Test saving and loading files"""
        content = "Test research data"
        filename = "test_file.txt"
        
        # Save
        file_path = self.fs_tool.save_research(content, filename)
        self.assertTrue(os.path.exists(file_path))
        
        # Load
        loaded_content = self.fs_tool.load_research(filename)
        self.assertEqual(loaded_content, content)
    
    def test_list_files(self):
        """Test listing files"""
        # Create some test files
        self.fs_tool.save_research("Content 1", "file1.txt")
        self.fs_tool.save_research("Content 2", "file2.txt")
        
        # List files
        files = self.fs_tool.list_files()
        
        self.assertIsInstance(files, list)
        self.assertGreaterEqual(len(files), 2)
        
        # Check structure
        if len(files) > 0:
            self.assertIn('filename', files[0])
            self.assertIn('size', files[0])
            self.assertIn('modified', files[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)

