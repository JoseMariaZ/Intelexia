#!/usr/bin/env python3
"""
Test script to verify response completeness for various types of requests
"""
import os
import json
import openvino_genai as ov_genai

def test_response_completeness():
    """Test various scenarios that might cause incomplete responses"""
    print("Testing response completeness...")
    
    # Load config
    with open("config.json", "r") as f:
        config = json.load(f)
    
    model_path = os.path.join("Models", config["Model"])
    device = config["LLMDevice"]
    
    print(f"Loading model from: {model_path}")
    print(f"Using device: {device}")
    
    try:
        # Load model
        pipe = ov_genai.LLMPipeline(model_path, device)
        print("✓ Model loaded successfully")
        
        # Test scenarios that might cause truncation
        test_scenarios = [
            {
                "name": "Short Response",
                "prompt": "What is Python?",
                "expected_min_length": 50
            },
            {
                "name": "Code Example",
                "prompt": "Write a simple Python function to add two numbers.",
                "expected_min_length": 100
            },
            {
                "name": "List Generation",
                "prompt": "List 5 benefits of exercise.",
                "expected_min_length": 150
            },
            {
                "name": "Explanation",
                "prompt": "Explain how machine learning works in simple terms.",
                "expected_min_length": 200
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n--- Test {i}: {scenario['name']} ---")
            print(f"Prompt: {scenario['prompt']}")
            
            # Format prompt for TinyLlama
            formatted_prompt = f"<|system|>\nYou are Intellexia, a helpful and lovely assistant</|system|>\nUser: {scenario['prompt']}\n<|assistant|>\n"
            
            # Generation config - optimized for TinyLlama
            config_llm = ov_genai.GenerationConfig(
                max_new_tokens=384,
                top_k=40,
                top_p=0.85,
                temperature=0.8,
                repetition_penalty=1.15,
                do_sample=True,
                eos_token_id=2
            )
            
            # Generate response
            pipe.start_chat()
            response = pipe.generate(formatted_prompt, config_llm)
            pipe.finish_chat()
            
            # Clean response using improved cleaning function
            def clean_response_improved(response):
                if not response:
                    return ""

                # Remove special tokens
                response = response.replace("<|assistant|>", "").replace("<|system|>", "").replace("<|user|>", "")
                response = response.replace("</s>", "").replace("<s>", "")
                response = response.strip()

                # Check for obvious repetition patterns
                lines = response.split('\n')
                cleaned_lines = []
                seen_lines = set()

                for line in lines:
                    line = line.strip()
                    if not line:
                        cleaned_lines.append("")
                        continue

                    # Check for exact line repetition
                    if line in seen_lines and len(line) > 20:
                        continue

                    cleaned_lines.append(line)
                    if len(line) > 20:
                        seen_lines.add(line)

                result = '\n'.join(cleaned_lines)

                # Remove excessive word repetition
                words = result.split()
                if len(words) > 10:
                    word_counts = {}
                    for word in words:
                        if len(word) > 3:
                            word_counts[word] = word_counts.get(word, 0) + 1

                    max_repetition = max(word_counts.values()) if word_counts else 0
                    if max_repetition > 4:
                        most_repeated = max(word_counts, key=word_counts.get)
                        words_clean = []
                        repeat_count = 0
                        for word in words:
                            if word == most_repeated:
                                repeat_count += 1
                                if repeat_count > 2:
                                    if len(words_clean) > 0 and words_clean[-1].endswith('.'):
                                        break
                                    elif len(words_clean) > 10:
                                        break
                            words_clean.append(word)
                        result = ' '.join(words_clean)

                        # Ensure proper ending
                        if result and not result.endswith(('.', '!', '?', '```')):
                            last_sentence_end = max(
                                result.rfind('.'),
                                result.rfind('!'),
                                result.rfind('?')
                            )
                            if last_sentence_end > len(result) * 0.7:
                                result = result[:last_sentence_end + 1]

                return result.strip()

            cleaned = clean_response_improved(response)
            
            print(f"Response length: {len(cleaned)} characters")
            print(f"Expected minimum: {scenario['expected_min_length']} characters")
            
            # Check completeness
            is_complete = True
            issues = []
            
            # Check length
            if len(cleaned) < scenario['expected_min_length']:
                is_complete = False
                issues.append(f"Too short ({len(cleaned)} < {scenario['expected_min_length']})")
            
            # Check for abrupt endings
            if cleaned and not cleaned[-1] in '.!?':
                is_complete = False
                issues.append("Doesn't end with proper punctuation")
            
            # Check for incomplete code blocks
            if '```' in cleaned:
                code_blocks = cleaned.count('```')
                if code_blocks % 2 == 1:
                    is_complete = False
                    issues.append("Incomplete code block")
            
            # Check for repetitive patterns
            words = cleaned.split()
            if len(words) > 10:
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                max_repetition = max(word_counts.values()) if word_counts else 0
                if max_repetition > 5:
                    is_complete = False
                    issues.append(f"Excessive repetition (word repeated {max_repetition} times)")
            
            # Display results
            if is_complete:
                print("✓ Response appears complete")
            else:
                print("⚠ Response may be incomplete:")
                for issue in issues:
                    print(f"  - {issue}")
            
            print(f"Response preview: {cleaned[:200]}...")
            
            # Show full response for code examples
            if "code" in scenario['name'].lower() or "function" in scenario['prompt'].lower():
                print(f"Full response:\n{cleaned}")
        
        print("\n" + "="*50)
        print("Completeness test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_response_completeness()
