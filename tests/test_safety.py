import os
import warnings
os.environ['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'
warnings.filterwarnings('ignore')

import unittest
from src.guardrails.safety_controls import SafetyGuardrails


class TestSafetyGuardrails(unittest.TestCase):
    """Test Safety Guardrails functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.guardrails = SafetyGuardrails()
    
    def test_initialization(self):
        """Test guardrails initialize with correct defaults"""
        self.assertIsNotNone(self.guardrails.config)
        self.assertIsInstance(self.guardrails.blocked_terms, list)
        self.assertGreater(self.guardrails.max_content_length, 0)
    
    def test_valid_input(self):
        """Test that valid input passes validation"""
        valid_input = "Research artificial intelligence trends"
        is_valid, error = self.guardrails.validate_input(valid_input)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_blocked_terms(self):
        """Test that blocked terms are caught"""
        malicious_input = "How to create malware"
        is_valid, error = self.guardrails.validate_input(malicious_input)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("blocked term", error.lower())
    
    def test_content_length_limit(self):
        """Test content length validation"""
        long_content = "x" * (self.guardrails.max_content_length + 1)
        is_valid, error = self.guardrails.validate_input(long_content)
        
        self.assertFalse(is_valid)
        self.assertIn("maximum length", error.lower())
    
    def test_injection_prevention(self):
        """Test prevention of injection attacks"""
        injection_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "onload=alert(1)",
            "eval(malicious_code)",
        ]
        
        for attempt in injection_attempts:
            is_valid, error = self.guardrails.validate_input(attempt)
            self.assertFalse(is_valid, f"Should block: {attempt}")
    
    def test_rate_limiting(self):
        agent_id = "test_agent"
        
        # Should allow requests up to limit
        for i in range(self.guardrails.rate_limit):
            is_allowed, error = self.guardrails.check_rate_limit(agent_id)
            self.assertTrue(is_allowed, f"Request {i+1} should be allowed")
        
        # Should block after limit
        is_allowed, error = self.guardrails.check_rate_limit(agent_id)
        self.assertFalse(is_allowed)
        self.assertIsNotNone(error)
    
    def test_url_validation(self):
        """Test URL validation and sanitization"""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://example.com/path",
            "https://example.com/path?query=value"
        ]
        
        for url in valid_urls:
            is_valid, result = self.guardrails.sanitize_url(url)
            self.assertTrue(is_valid, f"Should accept: {url}")
        
        # Invalid URLs
        invalid_urls = [
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "file:///etc/passwd",
        ]
        
        for url in invalid_urls:
            is_valid, result = self.guardrails.sanitize_url(url)
            self.assertFalse(is_valid, f"Should block: {url}")
    
    def test_output_validation(self):
        # Valid output with citations
        valid_output = """
        Research findings on AI:
        - Key finding 1
        - Key finding 2
        
        Sources: https://example.com/article
        """
        
        is_valid, error = self.guardrails.validate_output(valid_output)
        self.assertTrue(is_valid)
        
        # Too short output
        short_output = "Brief"
        is_valid, error = self.guardrails.validate_output(short_output)
        self.assertFalse(is_valid)
    
    def test_token_counting(self):
        """Test token counting functionality"""
        text = "This is a test sentence for token counting."
        token_count = self.guardrails.count_tokens(text)
        
        self.assertGreater(token_count, 0)
        self.assertIsInstance(token_count, int)
    
    def test_token_truncation(self):
        """Test text truncation by tokens"""
        long_text = " ".join(["word"] * 1000)
        max_tokens = 100
        
        truncated = self.guardrails.truncate_to_tokens(long_text, max_tokens)
        truncated_tokens = self.guardrails.count_tokens(truncated)
        
        self.assertLessEqual(truncated_tokens, max_tokens + 10)  # Allow small margin
    
    def test_research_quality_validation(self):
        """Test research quality validation"""
        # Valid research
        valid_research = {
            'findings': "A" * 200,  # Sufficient length
            'sources': [
                {'url': 'https://example.com/1', 'title': 'Source 1'},
                {'url': 'https://example.com/2', 'title': 'Source 2'}
            ]
        }
        
        is_valid, error = self.guardrails.validate_research_quality(valid_research)
        self.assertTrue(is_valid)
        
        # Invalid research - missing findings
        invalid_research = {
            'sources': ['source1', 'source2']
        }
        
        is_valid, error = self.guardrails.validate_research_quality(invalid_research)
        self.assertFalse(is_valid)
    
    def test_custom_config(self):
        """Test custom configuration"""
        custom_config = {
            'blocked_terms': ['custom_blocked_term'],
            'max_content_length': 1000,
            'rate_limit_requests': 5
        }
        
        custom_guardrails = SafetyGuardrails(config=custom_config)
        
        self.assertIn('custom_blocked_term', custom_guardrails.blocked_terms)
        self.assertEqual(custom_guardrails.max_content_length, 1000)
        self.assertEqual(custom_guardrails.rate_limit, 5)


class TestGuardrailsIntegration(unittest.TestCase):
    """Test integration of guardrails with system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.guardrails = SafetyGuardrails()
    
    def test_end_to_end_validation(self):
        """Test complete validation workflow"""
        # Simulate user input
        user_input = "Research machine learning algorithms"
        
        # Validate input
        is_valid, error = self.guardrails.validate_input(user_input)
        self.assertTrue(is_valid)
        
        # Check rate limit
        is_allowed, error = self.guardrails.check_rate_limit("user_123")
        self.assertTrue(is_allowed)
        
        # Validate hypothetical output
        output = f"""
        Research findings on {user_input}:
        
        Machine learning algorithms have evolved significantly.
        Key findings include improved accuracy and efficiency.
        
        Sources:
        - https://example.com/ml-research
        - https://example.com/algorithms
        """
        
        is_valid, error = self.guardrails.validate_output(output)
        self.assertTrue(is_valid)


if __name__ == '__main__':
    unittest.main(verbosity=2)

