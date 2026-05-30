#!/usr/bin/env python3

from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow

# Test just one query
workflow = create_agentic_rag_workflow()

print('Testing calculator query...')
result = workflow.invoke({'query': 'What is 2+2?'})
print('Intent:', result['intent'])
print('Tools:', result['tools_used'])
print('Response:', result['response'][:100] + '...')

print('\nTesting weather query...')
result = workflow.invoke({'query': 'How is the weather at Kurukshetra?'})
print('Intent:', result['intent'])
print('Tools:', result['tools_used'])
print('Response:', result['response'][:100] + '...')
