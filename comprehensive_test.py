import sys
import os
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow

def run_tests():
    print("Starting Agentic System Comprehensive Tests...")
    print("=" * 50)
    
    workflow = create_agentic_rag_workflow()
    
    test_queries = [
        {
            "name": "Arithmetic Test",
            "query": "What is 15% of 4500?"
        },
        {
            "name": "University Info Test",
            "query": "What are the admission requirements for B.Tech in NIT Kurukshetra?"
        },
        {
            "name": "Real-time Search Test",
            "query": "What is the latest news or events happening at NIT Kurukshetra this week?"
        }
    ]
    
    results = []
    
    for test in test_queries:
        print(f"\nRunning: {test['name']}")
        print(f"Query: {test['query']}")
        
        start_time = time.time()
        try:
            result = workflow.invoke({"query": test['query']})
            duration = time.time() - start_time
            
            print(f"Status: SUCCESS")
            print(f"Duration: {duration:.2f}s")
            print(f"Intent: {result.get('intent')}")
            print(f"Tools: {result.get('tools_used')}")
            print(f"Response Preview: {result.get('response', '')[:100]}...")
            
            if not result.get('response') or len(result.get('response')) < 10:
                print("FAILED: Response too short or empty")
                results.append({"name": test['name'], "status": "FAIL", "reason": "Empty response"})
            else:
                results.append({"name": test['name'], "status": "PASS"})
                
        except Exception as e:
            print(f"FAILED: Exception occurred: {e}")
            results.append({"name": test['name'], "status": "FAIL", "reason": str(e)})
            
        print("-" * 30)

    print("\nFINAL TEST SUMMARY:")
    print("=" * 50)
    passed = 0
    for r in results:
        status_icon = "[PASS]" if r['status'] == "PASS" else "[FAIL]"
        print(f"{status_icon} {r['name']}: {r['status']}")
        if r['status'] == "PASS":
            passed += 1
        else:
            print(f"   Reason: {r.get('reason')}")
            
    print(f"\nTOTAL: {passed}/{len(results)} PASSED")

if __name__ == "__main__":
    run_tests()
