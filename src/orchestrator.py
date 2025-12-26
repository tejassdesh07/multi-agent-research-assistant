"""
Multi-Agent Orchestrator
Coordinates collaboration between Research and Summary agents
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import yaml
import os
from crewai import Crew, Task, Process
from src.agents.research_agent import create_research_agent
from src.agents.summary_agent import create_summary_agent
from src.guardrails.safety_controls import get_guardrails
from src.tools.memory_tool import get_memory_instance
from src.tools.file_tool import get_fs_instance


class MultiAgentOrchestrator:
    """
    Orchestrates multi-agent collaboration for research and summarization
    Implements safety controls, memory management, and agent coordination
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        model_name: str = "gpt-4-turbo-preview",
        verbose: bool = True
    ):
        """
        Initialize the orchestrator
        
        Args:
            config_path: Path to configuration file
            model_name: LLM model to use
            verbose: Whether to output detailed logs
        """
        self.config = self._load_config(config_path)
        self.model_name = model_name
        self.verbose = verbose
        
        # Initialize components
        self.guardrails = get_guardrails()
        self.memory = get_memory_instance()
        self.file_system = get_fs_instance()
        
        # Create agents
        self.research_agent = create_research_agent(
            model_name=model_name,
            verbose=verbose
        )
        self.summary_agent = create_summary_agent(
            model_name=model_name,
            temperature=0.5,
            verbose=verbose
        )
        
        # Session metadata
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default config
        return {
            'agents': {
                'research_agent': {'max_iterations': 5},
                'summary_agent': {'max_iterations': 3}
            },
            'tasks': {
                'research_task': {},
                'summary_task': {}
            }
        }
    
    def create_research_task(
        self,
        topic: str,
        focus_areas: Optional[List[str]] = None
    ) -> Task:
        """
        Create a research task for the research agent
        
        Args:
            topic: Topic to research
            focus_areas: Specific areas to focus on
            
        Returns:
            Configured Task object
        """
        focus_areas = focus_areas or ["general overview", "recent developments", "key statistics"]
        focus_str = ", ".join(focus_areas)
        
        description = f"""
        Research the following topic: {topic}
        
        Focus Areas: {focus_str}
        
        Your research should:
        1. Search for current, credible information from multiple sources
        2. Gather key facts, statistics, and insights
        3. Identify trends and patterns
        4. Verify information accuracy by cross-referencing sources
        5. Document all sources with URLs and dates
        6. Extract relevant quotes from authoritative sources
        7. Note any controversies or conflicting information
        
        Follow the research guidelines to ensure comprehensive coverage.
        Store important findings in memory for future reference.
        """
        
        expected_output = f"""
        A comprehensive research report on {topic} that includes:
        
        - Executive Summary (2-3 paragraphs)
        - Key Findings (at least 5 major findings with sources)
        - Detailed Analysis by subtopic
        - Statistics and Data Points (with sources)
        - Trends and Patterns identified
        - Notable Quotes from experts
        - Comprehensive list of sources (minimum 5 credible sources)
        - Research confidence assessment and limitations
        """
        
        task = Task(
            description=description,
            expected_output=expected_output,
            agent=self.research_agent,
        )
        
        return task
    
    def create_summary_task(
        self,
        topic: str,
        context_tasks: Optional[List[Task]] = None
    ) -> Task:
        """
        Create a summary task for the summary agent
        
        Args:
            topic: Topic being summarized
            context_tasks: Previous tasks to use as context
            
        Returns:
            Configured Task object
        """
        description = f"""
        Create an executive summary from the research findings on: {topic}
        
        Your summary should:
        1. Synthesize the research into a compelling narrative
        2. Highlight the most critical insights and findings
        3. Present key statistics in context
        4. Identify strategic implications
        5. Provide actionable recommendations
        6. Maintain professional, executive-level language
        7. Keep it concise (2-3 pages maximum)
        
        Follow the summary guidelines to ensure executive quality.
        """
        
        expected_output = f"""
        An executive summary on {topic} that includes:
        
        - Executive Overview (compelling 2-3 paragraphs)
        - Key Findings (3-5 top findings with supporting data)
        - Critical Data Points (key metrics and statistics)
        - Trends and Insights (analysis of patterns)
        - Strategic Implications (opportunities and risks)
        - Recommendations (prioritized action items)
        - Sources reference
        """
        
        task = Task(
            description=description,
            expected_output=expected_output,
            agent=self.summary_agent,
            context=context_tasks if context_tasks else []
        )
        
        return task
    
    def research_and_summarize(
        self,
        topic: str,
        focus_areas: Optional[List[str]] = None,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Execute complete research and summarization workflow
        
        Args:
            topic: Topic to research and summarize
            focus_areas: Specific areas to focus research on
            save_results: Whether to save results to files
            
        Returns:
            Dictionary containing research and summary results
        """
        
        # Validate input
        is_valid, error = self.guardrails.validate_input(topic)
        if not is_valid:
            return {
                'success': False,
                'error': f"Input validation failed: {error}",
                'topic': topic
            }
        
        # Check rate limits
        is_allowed, error = self.guardrails.check_rate_limit("orchestrator")
        if not is_allowed:
            return {
                'success': False,
                'error': error,
                'topic': topic
            }
        
        try:
            # Create tasks
            research_task = self.create_research_task(topic, focus_areas)
            summary_task = self.create_summary_task(topic, context_tasks=[research_task])
            
            # Create crew with sequential process
            crew = Crew(
                agents=[self.research_agent, self.summary_agent],
                tasks=[research_task, summary_task],
                process=Process.sequential,
                verbose=self.verbose,
                memory=True,
                cache=True,
                max_rpm=10,
                share_crew=False
            )
            
            # Execute workflow
            self.guardrails.log_operation(
                "orchestrator",
                "research_and_summarize",
                "started",
                {'topic': topic, 'session_id': self.session_id}
            )
            
            result = crew.kickoff()
            
            # Extract results
            research_output = str(research_task.output) if hasattr(research_task, 'output') else str(result)
            summary_output = str(summary_task.output) if hasattr(summary_task, 'output') else str(result)
            
            # Validate output
            is_valid, error = self.guardrails.validate_output(summary_output)
            if not is_valid:
                pass
            
            # Store in memory
            self.memory.store_memory(
                f"Research on {topic}: {research_output[:500]}",
                metadata={'type': 'research', 'topic': topic, 'session_id': self.session_id}
            )
            
            self.memory.store_memory(
                f"Summary of {topic}: {summary_output[:500]}",
                metadata={'type': 'summary', 'topic': topic, 'session_id': self.session_id}
            )
            
            # Save to files if requested
            if save_results:
                research_filename = f"research_{self.session_id}_{topic[:30].replace(' ', '_')}.txt"
                summary_filename = f"summary_{self.session_id}_{topic[:30].replace(' ', '_')}.txt"
                
                research_path = self.file_system.save_research(
                    research_output,
                    research_filename
                )
                summary_path = self.file_system.save_research(
                    summary_output,
                    summary_filename
                )
                
            
            self.guardrails.log_operation(
                "orchestrator",
                "research_and_summarize",
                "completed",
                {'topic': topic, 'session_id': self.session_id}
            )
            
            
            return {
                'success': True,
                'topic': topic,
                'research': research_output,
                'summary': summary_output,
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error during execution: {str(e)}"
            
            self.guardrails.log_operation(
                "orchestrator",
                "research_and_summarize",
                "failed",
                {'topic': topic, 'error': str(e)}
            )
            
            return {
                'success': False,
                'error': error_msg,
                'topic': topic,
                'session_id': self.session_id
            }
    
    def get_session_history(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve previous research sessions from memory
        
        Args:
            topic: Optional topic filter
            
        Returns:
            List of previous sessions
        """
        query = f"research on {topic}" if topic else "research"
        memories = self.memory.retrieve_memories(query, n_results=10)
        return memories

