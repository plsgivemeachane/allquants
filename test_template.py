#!/usr/bin/env python3
"""
Test script to verify template variable replacement
"""

from pathlib import Path

def test_template_replacement():
    """Test the template variable replacement logic"""
    
    # Read the template
    template_path = Path("TEMPLATE.md")
    if not template_path.exists():
        print("❌ TEMPLATE.md not found")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Test with a sample model name
    test_model_name = "microsoft/DialoGPT-medium"
    
    # Apply the same logic as in quantizer.py
    clean_model_name = test_model_name.split("/")[-1] if "/" in test_model_name else test_model_name
    model_card = template_content.replace("{{base_model}}", clean_model_name)
    model_card = model_card.replace("{{base_model_w_author}}", test_model_name)
    
    print(f"Test model: {test_model_name}")
    print(f"Clean model name: {clean_model_name}")
    print("\n" + "="*50)
    print("Template variables found and replaced:")
    print("="*50)
    
    # Check if variables were replaced
    if "{{base_model}}" in model_card:
        print("❌ {{base_model}} still found in template - not fully replaced")
    else:
        print("✅ {{base_model}} successfully replaced")
    
    if "{{base_model_w_author}}" in model_card:
        print("❌ {{base_model_w_author}} still found in template - not fully replaced")
    else:
        print("✅ {{base_model_w_author}} successfully replaced")
    
    # Show some key sections to verify replacement
    lines = model_card.split('\n')
    print("\nKey sections with replacements:")
    for i, line in enumerate(lines, 1):
        if any(keyword in line.lower() for keyword in ['title', 'repository', 'model card', 'original']):
            if 'DialoGPT' in line or 'microsoft' in line:
                print(f"Line {i}: {line}")

if __name__ == "__main__":
    test_template_replacement()
