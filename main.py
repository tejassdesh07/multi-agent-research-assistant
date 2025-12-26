import os
import sys
import warnings

os.environ['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
from src.orchestrator import MultiAgentOrchestrator

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("Error: OPENAI_API_KEY not found in .env file")
    
    orchestrator = MultiAgentOrchestrator(config_path="config.yaml",
        model_name="gpt-3.5-turbo", verbose=False)
    
    topic = input("Enter research topic: ").strip()
    if not topic:
        topic = "AI agents and multi-agent systems"
    
    focus_input = input("Enter focus areas (comma-separated): ").strip()
    focus_areas = [a.strip() for a in focus_input.split(",")] if focus_input else ["technology", "applications"]
    
    result = orchestrator.research_and_summarize(topic=topic,
        focus_areas=focus_areas, save_results=True)
    
    if result['success']:
        print(f"\nResearch completed successfully.")
        print(f"Session: {result['session_id']}")
        print(f"Files saved to: data/research/")
    else:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    main()

