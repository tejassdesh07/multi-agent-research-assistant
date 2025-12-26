"""
Safety Controls and Guardrails for Agent System
Implements content filtering, validation, and safety checks
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import tiktoken


class SafetyGuardrails:
    """Comprehensive safety controls for agent operations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize safety guardrails with configuration"""
        self.config = config or self._default_config()
        
        # Track agent operations for rate limiting
        self.operation_history = []
        
        # Content filters
        self.blocked_terms = self.config.get('blocked_terms', [])
        self.max_content_length = self.config.get('max_content_length', 50000)
        self.max_tokens = self.config.get('max_tokens', 4000)
        
        # Rate limiting
        self.rate_limit = self.config.get('rate_limit_requests', 10)
        self.rate_window = self.config.get('rate_limit_window', 60)
        
        # Validation settings
        self.require_citations = self.config.get('require_citations', True)
        self.min_confidence = self.config.get('min_confidence_score', 0.7)
        
        # Token encoder for counting
        self.encoder = tiktoken.get_encoding("cl100k_base")
        
    def _default_config(self) -> Dict[str, Any]:
        """Default safety configuration"""
        return {
            'blocked_terms': [
                'malware', 'exploit', 'hack', 'phishing',
                'illegal', 'piracy', 'crack', 'keygen'
            ],
            'max_content_length': 50000,
            'max_tokens': 4000,
            'rate_limit_requests': 10,
            'rate_limit_window': 60,
            'require_citations': True,
            'min_confidence_score': 0.7
        }
    
    def validate_input(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate input content for safety
        
        Args:
            content: Content to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for blocked terms
        content_lower = content.lower()
        for term in self.blocked_terms:
            if term.lower() in content_lower:
                return False, f"Content contains blocked term: {term}"
        
        # Check content length
        if len(content) > self.max_content_length:
            return False, f"Content exceeds maximum length ({self.max_content_length} chars)"
        
        # Check for potential injection attacks
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'on\w+\s*=',  # Event handlers
            r'eval\(',  # Eval function
            r'exec\(',  # Exec function
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False, "Content contains potentially malicious patterns"
        
        return True, None
    
    def validate_output(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate output content before returning to user
        
        Args:
            content: Output content to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation
        is_valid, error = self.validate_input(content)
        if not is_valid:
            return is_valid, error
        
        # Check if output meets quality standards
        if len(content.strip()) < 50:
            return False, "Output is too short to be useful"
        
        # Check for citations if required
        if self.require_citations:
            has_urls = bool(re.search(r'https?://[^\s]+', content))
            has_sources = bool(re.search(r'(source|reference|citation):', content, re.IGNORECASE))
            
            if not (has_urls or has_sources):
                return False, "Output missing required citations/sources"
        
        return True, None
    
    def check_rate_limit(self, agent_id: str = "default") -> Tuple[bool, Optional[str]]:
        """
        Check if agent is within rate limits
        
        Args:
            agent_id: ID of the agent making the request
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=self.rate_window)
        
        # Remove old operations
        self.operation_history = [
            op for op in self.operation_history
            if op['timestamp'] > cutoff_time
        ]
        
        # Count operations for this agent
        agent_operations = [
            op for op in self.operation_history
            if op['agent_id'] == agent_id
        ]
        
        if len(agent_operations) >= self.rate_limit:
            return False, f"Rate limit exceeded. Please wait before making more requests."
        
        # Record this operation
        self.operation_history.append({
            'agent_id': agent_id,
            'timestamp': current_time
        })
        
        return True, None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(text))
    
    def truncate_to_tokens(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Truncate text to specified token count
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens (default: self.max_tokens)
            
        Returns:
            Truncated text
        """
        max_tokens = max_tokens or self.max_tokens
        tokens = self.encoder.encode(text)
        
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return self.encoder.decode(truncated_tokens) + "..."
    
    def sanitize_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate and sanitize URLs
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, sanitized_url or error_message)
        """
        # Check for valid URL format
        url_pattern = r'^https?://[^\s<>\"]+$'
        if not re.match(url_pattern, url):
            return False, "Invalid URL format"
        
        # Check for suspicious patterns
        suspicious = ['javascript:', 'data:', 'file:', 'ftp:']
        for pattern in suspicious:
            if pattern in url.lower():
                return False, f"Blocked URL protocol: {pattern}"
        
        # Basic sanitization
        sanitized = url.strip()
        return True, sanitized
    
    def validate_research_quality(self, research: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate quality of research output
        
        Args:
            research: Research data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['findings', 'sources']
        
        for field in required_fields:
            if field not in research:
                return False, f"Missing required field: {field}"
        
        # Check for minimum content
        findings = research.get('findings', '')
        if len(findings) < 100:
            return False, "Research findings are insufficient"
        
        # Check for sources
        sources = research.get('sources', [])
        if len(sources) < 2:
            return False, "Insufficient number of sources (minimum 2 required)"
        
        return True, None
    
    def log_operation(
        self, 
        agent_id: str, 
        operation: str, 
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log agent operations for audit trail
        
        Args:
            agent_id: ID of the agent
            operation: Operation performed
            status: Status (success/failure/warning)
            metadata: Additional metadata
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'operation': operation,
            'status': status,
            'metadata': metadata or {}
        }


# Global guardrails instance
_guardrails_instance = None

def get_guardrails() -> SafetyGuardrails:
    """Get or create global guardrails instance"""
    global _guardrails_instance
    if _guardrails_instance is None:
        _guardrails_instance = SafetyGuardrails()
    return _guardrails_instance

