import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow

def test_intent_routing():
    """Test intent routing with different query types."""
    # Create workflow
    workflow = create_agentic_rag_workflow()
    
    # Test different query types
    test_cases = [
        {'query': 'What is 2+2?', 'expected_intent': 'calculation'},
        {'query': 'How is the weather at Kurukshetra?', 'expected_intent': 'real_time_info'},
        {'query': 'What are CSE admission requirements?', 'expected_intent': 'university_info'}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f'Test {i}: {test_case["query"]}')
        try:
            result = workflow.invoke({'query': test_case['query']})
            print(f'  ✅ Intent: {result["intent"]}')
            print(f'  ✅ Tools used: {result["tools_used"]}')
            print(f'  ✅ Response length: {len(result["response"])} chars')
            
            # Check if intent matches expectation
            if result["intent"] == test_case["expected_intent"]:
                print(f'  ✅ Intent correctly identified!')
            else:
                print(f'  ❌ Expected {test_case["expected_intent"]}, got {result["intent"]}')
                
        except Exception as e:
            print(f'  ❌ Error: {e}')
        print('---')

if __name__ == "__main__":
    test_intent_routing()
