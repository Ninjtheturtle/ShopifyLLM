#!/usr/bin/env python3
"""
Dataset Quality Validator
Validates the clean premium dataset for consistency and quality
"""

import json
import re
from collections import defaultdict, Counter

def validate_clean_dataset(filename="premium_ecommerce_clean_300.jsonl"):
    """Validate dataset quality and consistency"""
    
    print(f"🔍 Validating dataset: {filename}")
    print("="*60)
    
    examples = []
    issues = []
    
    # Load dataset
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                example = json.loads(line.strip())
                examples.append(example)
            except json.JSONDecodeError as e:
                issues.append(f"Line {line_num}: JSON decode error - {e}")
    
    print(f"📊 Loaded {len(examples)} examples")
    
    # Validation checks
    categories = Counter()
    brands = Counter()
    feature_combinations = []
    output_lengths = []
    inconsistencies = []
    
    for i, example in enumerate(examples, 1):
        # Check structure
        if "messages" not in example:
            issues.append(f"Example {i}: Missing 'messages' field")
            continue
            
        messages = example["messages"]
        if len(messages) != 3:
            issues.append(f"Example {i}: Expected 3 messages, got {len(messages)}")
            continue
        
        # Extract components
        system_msg = messages[0]["content"]
        user_msg = messages[1]["content"]
        assistant_msg = messages[2]["content"]
        
        # Check message roles
        expected_roles = ["system", "user", "assistant"]
        actual_roles = [msg["role"] for msg in messages]
        if actual_roles != expected_roles:
            issues.append(f"Example {i}: Wrong roles - expected {expected_roles}, got {actual_roles}")
        
        # Check content quality
        if len(assistant_msg) < 50:
            issues.append(f"Example {i}: Assistant response too short ({len(assistant_msg)} chars)")
        
        if len(assistant_msg) > 1000:
            issues.append(f"Example {i}: Assistant response too long ({len(assistant_msg)} chars)")
        
        # Collect stats
        categories[example.get("category", "Unknown")] += 1
        brands[example.get("brand", "Unknown")] += 1
        output_lengths.append(len(assistant_msg))
        
        # Check for problematic feature combinations
        user_lower = user_msg.lower()
        problematic_combos = [
            ("fragrance", "battery"),
            ("dress", "interface"),
            ("jewelry", "charging"),
            ("art", "wifi"),
            ("books", "battery life"),
            ("fragrance", "voice control")
        ]
        
        for combo in problematic_combos:
            if combo[0] in user_lower and combo[1] in user_lower:
                inconsistencies.append(f"Example {i}: Problematic combo '{combo[0]}' + '{combo[1]}' in: {user_msg[:100]}...")
    
    # Report results
    print(f"\n📈 VALIDATION RESULTS:")
    print(f"✅ Total examples: {len(examples)}")
    print(f"❌ Issues found: {len(issues)}")
    print(f"⚠️  Inconsistencies: {len(inconsistencies)}")
    
    if issues:
        print(f"\n🚨 ISSUES:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"   {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more issues")
    
    if inconsistencies:
        print(f"\n⚠️  INCONSISTENCIES:")
        for inc in inconsistencies[:5]:  # Show first 5 inconsistencies
            print(f"   {inc}")
        if len(inconsistencies) > 5:
            print(f"   ... and {len(inconsistencies) - 5} more inconsistencies")
    
    print(f"\n📊 CATEGORY DISTRIBUTION:")
    for category, count in categories.most_common():
        print(f"   {category}: {count} examples")
    
    print(f"\n🏷️  BRAND DISTRIBUTION:")
    real_brands = {k: v for k, v in brands.items() if "Premium" not in k}
    synthetic_brands = {k: v for k, v in brands.items() if "Premium" in k}
    
    print(f"   Real brands ({len(real_brands)}): {sum(real_brands.values())} examples")
    for brand, count in real_brands.items():
        print(f"     {brand}: {count}")
    
    print(f"   Synthetic brands ({len(synthetic_brands)}): {sum(synthetic_brands.values())} examples")
    
    print(f"\n📏 OUTPUT LENGTH STATS:")
    print(f"   Average: {sum(output_lengths)/len(output_lengths):.1f} chars")
    print(f"   Min: {min(output_lengths)} chars")
    print(f"   Max: {max(output_lengths)} chars")
    
    # Quality score
    total_checks = len(examples) * 3  # 3 quality checks per example
    passed_checks = total_checks - len(issues) - len(inconsistencies)
    quality_score = (passed_checks / total_checks) * 100
    
    print(f"\n🎯 QUALITY SCORE: {quality_score:.1f}%")
    
    if quality_score >= 95:
        print("🟢 Excellent quality - ready for training!")
    elif quality_score >= 90:
        print("🟡 Good quality - minor issues to address")
    else:
        print("🔴 Quality issues need fixing before training")
    
    return quality_score >= 90

def main():
    """Main validation function"""
    print("🔍 DATASET QUALITY VALIDATOR")
    print("Checking clean premium dataset for inconsistencies")
    print("="*60)
    
    is_valid = validate_clean_dataset()
    
    print(f"\n{'✅ DATASET VALIDATION PASSED' if is_valid else '❌ DATASET NEEDS FIXES'}")
    print("="*60)
    
    return is_valid

if __name__ == "__main__":
    main()
