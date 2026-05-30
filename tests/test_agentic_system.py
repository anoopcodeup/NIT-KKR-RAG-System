"""
Test Script for Agentic RAG System

This script tests the complete agentic system functionality
including all agents, tools, and workflow orchestration.
"""

import sys
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all modules can be imported."""
    print("=" * 60)
    print("Testing Imports...")
    print("=" * 60)
    
    try:
        # Test core imports
        from agentic_system.workflows.state_management import AgenticState, QueryIntent
        print("✅ State management imports successful")
        
        from agentic_system.agents.router_agent import RouterAgent
        print("✅ Router Agent import successful")
        
        from agentic_system.agents.evaluator_agent import EvaluatorAgent
        print("✅ Evaluator Agent import successful")
        
        from agentic_system.tools.vector_store_tool import VectorStoreTool
        print("✅ Vector Store Tool import successful")
        
        from agentic_system.tools.web_search_tool import WebSearchTool
        print("✅ Web Search Tool import successful")
        
        from agentic_system.tools.calculator_tool import CalculatorTool
        print("✅ Calculator Tool import successful")
        
        from agentic_system.workflows.agentic_rag import AgenticRAGWorkflow
        print("✅ Agentic Workflow import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_state_management():
    """Test state management functionality."""
    print("\n" + "=" * 60)
    print("Testing State Management...")
    print("=" * 60)
    
    try:
        from agentic_system.workflows.state_management import AgenticState, QueryIntent
        
        # Create test state
        state = AgenticState()
        print("✅ AgenticState created successfully")
        
        # Test intent enum
        intent = QueryIntent.UNIVERSITY_INFO
        print(f"✅ QueryIntent enum: {intent}")
        
        # Test state methods
        should_continue = state.should_continue()
        print(f"✅ Should continue: {should_continue}")
        
        # Add tool usage
        state.add_tool_usage("vector_store", 1.5)
        print(f"✅ Tool usage added: {state.tool_history}")
        
        # Test summary
        summary = state.get_summary()
        print(f"✅ State summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ State management test failed: {e}")
        return False

def test_agents():
    """Test individual agents."""
    print("\n" + "=" * 60)
    print("Testing Individual Agents...")
    print("=" * 60)
    
    try:
        from agentic_system.agents.router_agent import RouterAgent
        from agentic_system.agents.evaluator_agent import EvaluatorAgent
        from agentic_system.workflows.state_management import QueryIntent
        
        # Test Router Agent
        print("\n--- Testing Router Agent ---")
        router = RouterAgent()
        classification = router.classify_intent("What are CSE admission requirements?")
        print(f"✅ Intent classified: {classification.intent}")
        print(f"✅ Confidence: {classification.confidence}")
        print(f"✅ Tools: {classification.required_tools}")
        
        # Test Evaluator Agent
        print("\n--- Testing Evaluator Agent ---")
        evaluator = EvaluatorAgent()
        quality_grade = evaluator.evaluate_retrieved_info(
            "CSE admission requirements",
            "NIT KKR offers B.Tech in CSE with JEE Main qualification."
        )
        print(f"✅ Relevance score: {quality_grade.relevance_score}")
        print(f"✅ Should continue: {quality_grade.should_continue}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_tools():
    """Test individual tools."""
    print("\n" + "=" * 60)
    print("Testing Individual Tools...")
    print("=" * 60)
    
    try:
        from agentic_system.tools.calculator_tool import CalculatorTool
        
        # Test Calculator Tool
        print("\n--- Testing Calculator Tool ---")
        calculator = CalculatorTool()
        result = calculator.calculate("2 + 2")
        print(f"✅ Calculation result: {result}")
        
        # Test complex calculation
        complex_result = calculator.calculate("15% of 50000")
        print(f"✅ Complex calculation: {complex_result}")
        
        # Test tool stats
        stats = calculator.get_calculation_stats()
        print(f"✅ Calculator stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

def test_workflow():
    """Test the complete agentic workflow."""
    print("\n" + "=" * 60)
    print("Testing Complete Workflow...")
    print("=" * 60)
    
    try:
        from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow
        
        # Create workflow
        workflow = create_agentic_rag_workflow()
        print("✅ Agentic workflow created successfully")
        
        # Get workflow stats
        stats = workflow.get_workflow_stats()
        print(f"✅ Workflow stats: {stats}")
        
        # Test simple query (should work without vector store)
        print("\n--- Testing Simple Query ---")
        test_result = workflow.invoke({
            "query": "Calculate 15% of 50000",
            "session_id": "test_session_001"
        })
        
        print(f"✅ Query processed successfully")
        print(f"✅ Response: {test_result['response'][:200]}...")
        print(f"✅ Intent: {test_result['intent']}")
        print(f"✅ Tools used: {test_result['tools_used']}")
        print(f"✅ Iterations: {test_result['iterations']}")
        print(f"✅ Execution time: {test_result['execution_time']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        print(f"❌ Error details: {type(e).__name__}: {str(e)}")
        return False

def test_integration():
    """Test integration with existing RAG system."""
    print("\n" + "=" * 60)
    print("Testing Integration with Existing RAG...")
    print("=" * 60)
    
    try:
        # Check if vector store exists
        vector_store_path = "vector_store"
        if os.path.exists(vector_store_path):
            print(f"✅ Vector store found at: {vector_store_path}")
            
            # List vector store contents
            if os.path.isdir(vector_store_path):
                files = os.listdir(vector_store_path)
                print(f"✅ Vector store files: {files}")
        else:
            print(f"⚠️  Vector store not found at: {vector_store_path}")
            print("   Run 'python main.py embed' to create vector store")
        
        # Check if Groq API is configured
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            print("✅ Groq API key is configured")
        else:
            print("⚠️  Groq API key not found")
            print("   Run 'python setup_groq.py' to configure Groq")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🤖 Agentic RAG System Test Suite")
    print("Testing complete agentic system implementation...")
    
    test_results = []
    
    # Run all tests
    test_results.append(("Imports", test_imports()))
    test_results.append(("State Management", test_state_management()))
    test_results.append(("Individual Agents", test_agents()))
    test_results.append(("Individual Tools", test_tools()))
    test_results.append(("Complete Workflow", test_workflow()))
    test_results.append(("Integration", test_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agentic system is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
