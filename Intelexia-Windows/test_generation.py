#!/usr/bin/env python3
"""
Test script to verify improved text generation without repetition
"""
import os
import json
import openvino_genai as ov_genai

def clean_response(response):
    """Clean up AI response to remove repetition and unwanted tokens"""
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
            # Skip this line if it's a repetition of a longer line
            continue

        cleaned_lines.append(line)
        if len(line) > 20:  # Only track longer lines for repetition detection
            seen_lines.add(line)

    # Join lines back
    result = '\n'.join(cleaned_lines)

    # Remove excessive repetition within the same line
    words = result.split()
    if len(words) > 10:
        # Check for word-level repetition
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        # If any word appears more than 5 times, it's likely repetitive
        max_repetition = max(word_counts.values()) if word_counts else 0
        if max_repetition > 5:
            # Find the most repeated word and truncate at its excessive repetition
            most_repeated = max(word_counts, key=word_counts.get)
            words_clean = []
            repeat_count = 0
            for word in words:
                if word == most_repeated:
                    repeat_count += 1
                    if repeat_count > 3:  # Allow up to 3 repetitions
                        break
                words_clean.append(word)
            result = ' '.join(words_clean)

    # Ensure response doesn't end abruptly in the middle of a code block or sentence
    if '```' in result:
        # Count code block markers
        code_blocks = result.count('```')
        if code_blocks % 2 == 1:  # Odd number means unclosed code block
            result += '\n```'

    return result.strip()

def test_generation():
    """Test the improved generation settings"""
    print("Testing improved text generation...")
    
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
        
        # Test prompts including longer responses
        test_prompts = [
            "Hello, how are you today?",
            "What is artificial intelligence?",
            "Create a simple HTML boilerplate for a webpage."
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Test {i} ---")
            print(f"Prompt: {prompt}")
            
            # Format prompt for TinyLlama
            formatted_prompt = f"<|system|>\nYou are Intellexia, a helpful and lovely assistant</|system|>\nUser: {prompt}\n<|assistant|>\n"
            
            # Generation config with anti-repetition settings and longer responses
            config_llm = ov_genai.GenerationConfig(
                max_new_tokens=512,
                top_k=50,
                top_p=0.9,
                temperature=0.7,
                repetition_penalty=1.1,
                do_sample=True,
                eos_token_id=2
            )
            
            # Generate response
            pipe.start_chat()
            response = pipe.generate(formatted_prompt, config_llm)
            pipe.finish_chat()
            
            # Clean response
            cleaned = clean_response(response)
            
            print(f"Raw response: {response[:200]}...")
            print(f"Cleaned response: {cleaned}")
            print(f"Length: {len(cleaned)} characters")
            
            # Check for repetition
            words = cleaned.split()
            unique_words = set(words)
            repetition_ratio = len(words) / len(unique_words) if unique_words else 0
            print(f"Repetition ratio: {repetition_ratio:.2f} (lower is better)")
            
            if repetition_ratio > 2.0:
                print("⚠ High repetition detected")
            else:
                print("✓ Repetition within acceptable range")
        
        print("\n" + "="*50)
        print("Generation test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_generation()
