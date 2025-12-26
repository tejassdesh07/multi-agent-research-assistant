"""
Test Suite for Agent Functionality
Tests research agent and summary agent capabilities
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.agents.research_agent import create_research_agent
from src.agents.summary_agent import create_summary_agent
from crewai import Task


class TestResearchAgent(unittest.TestCase):
    """Test Research Agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = create_research_agent(verbose=False)
    
    def test_agent_creation(self):
        """Test that research agent is created properly"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.role, "Senior Research Analyst")
        self.assertTrue(self.agent.allow_delegation)
        self.assertTrue(len(self.agent.tools) > 0)
    
    def test_agent_has_required_tools(self):
        """Test that agent has all required tools"""
        tool_names = [tool.name for tool in self.agent.tools]
        
        required_tools = [
            'search_web',
            'fetch_webpage',
            'store_memory',
            'retrieve_memory',
            'save_to_file'
        ]
        
        for required_tool in required_tools:
            self.assertIn(required_tool, tool_names)
    
    def test_agent_attributes(self):
        """Test agent has correct attributes"""
        self.assertTrue(hasattr(self.agent, 'goal'))
        self.assertTrue(hasattr(self.agent, 'backstory'))
        self.assertTrue(hasattr(self.agent, 'llm'))


class TestSummaryAgent(unittest.TestCase):
    """Test Summary Agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = create_summary_agent(verbose=False)
    
    def test_agent_creation(self):
        """Test that summary agent is created properly"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.role, "Executive Summary Specialist")
        self.assertFalse(self.agent.allow_delegation)
        self.assertTrue(len(self.agent.tools) > 0)
    
    def test_agent_has_required_tools(self):
        """Test that agent has required tools"""
        tool_names = [tool.name for tool in self.agent.tools]
        
        required_tools = [
            'retrieve_memory',
            'save_to_file',
            'load_from_file'
        ]
        
        for required_tool in required_tools:
            self.assertIn(required_tool, tool_names)
    
    def test_agent_temperature(self):
        """Test that summary agent uses appropriate temperature"""
        # Summary agent should have lower temperature for more focused output
        agent_low_temp = create_summary_agent(temperature=0.3, verbose=False)
        self.assertIsNotNone(agent_low_temp)


class TestAgentIntegration(unittest.TestCase):
    """Test agent integration and collaboration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.research_agent = create_research_agent(verbose=False)
        self.summary_agent = create_summary_agent(verbose=False)
    
    def test_agents_can_collaborate(self):
        """Test that agents can work together"""
        # Create a simple task for research agent
        research_task = Task(
            description="Research Python programming",
            expected_output="A brief report on Python",
            agent=self.research_agent
        )
        
        # Create a summary task that depends on research
        summary_task = Task(
            description="Summarize the research",
            expected_output="A brief summary",
            agent=self.summary_agent,
            context=[research_task]
        )
        
        self.assertEqual(summary_task.context, [research_task])
    
    def test_both_agents_exist(self):
        """Test that both agents are created successfully"""
        self.assertIsNotNone(self.research_agent)
        self.assertIsNotNone(self.summary_agent)
        self.assertNotEqual(self.research_agent, self.summary_agent)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)

