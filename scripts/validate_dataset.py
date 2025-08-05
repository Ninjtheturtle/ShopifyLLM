#!/usr/bin/env python3
"""
Dataset validation script for Shopify training data
"""

import json
from collections import defaultdict

def validate_dataset(file_path):
    print(f"Validating dataset: {file_path}")
    
    examples = []
    errors = []
    categories = defaultdict(int)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                # Validate structure
                if 'messages' not in data:
                    errors.append(f"Line {line_num}: Missing 'messages' field")
                    continue
                
                messages = data['messages']
                if len(messages) != 2:
                    errors.append(f"Line {line_num}: Expected 2 messages, got {len(messages)}")
                    continue
                
                user_msg = messages[0]
                assistant_msg = messages[1]
                
                if user_msg.get('role') != 'user':
                    errors.append(f"Line {line_num}: First message should be 'user' role")
                    continue
                
                if assistant_msg.get('role') != 'assistant':
                    errors.append(f"Line {line_num}: Second message should be 'assistant' role")
                    continue
                
                # Categorize examples
                user_content = user_msg.get('content', '').lower()
                if 'store' in user_content or 'sell' in user_content:
                    categories['store_generation'] += 1
                elif 'how' in user_content or 'strategy' in user_content:
                    categories['business_guidance'] += 1
                else:
                    categories['other'] += 1
                
                examples.append({
                    'line': line_num,
                    'user_length': len(user_msg.get('content', '')),
                    'assistant_length': len(assistant_msg.get('content', ''))
                })
                
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: JSON decode error - {str(e)}")
    
    # Report results
    print(f"\n📊 Dataset Validation Results:")
    print(f"Total examples: {len(examples)}")
    print(f"Errors found: {len(errors)}")
    
    if errors:
        print(f"\n❌ Errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    else:
        print("✅ No structural errors found!")
    
    print(f"\n📈 Content Statistics:")
    for category, count in categories.items():
        print(f"  {category}: {count} examples")
    
    if examples:
        avg_user_length = sum(ex['user_length'] for ex in examples) / len(examples)
        avg_assistant_length = sum(ex['assistant_length'] for ex in examples) / len(examples)
        
        print(f"\n📝 Length Statistics:")
        print(f"  Average user message length: {avg_user_length:.0f} characters")
        print(f"  Average assistant message length: {avg_assistant_length:.0f} characters")
        
        max_length = max(ex['assistant_length'] for ex in examples)
        print(f"  Longest assistant response: {max_length} characters")
    
    return len(errors) == 0

if __name__ == "__main__":
    is_valid = validate_dataset("comprehensive_shopify_data.jsonl")
    if is_valid:
        print("\n🎉 Dataset is ready for training!")
    else:
        print("\n⚠️  Please fix errors before training.")
