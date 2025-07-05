#!/usr/bin/env python3
"""
Test script to verify Intelexia Windows installation
"""
import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ numpy {np.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print(f"✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
    
    try:
        import openvino_genai as ov_genai
        print(f"✓ openvino-genai imported successfully")
    except ImportError as e:
        print(f"✗ openvino-genai import failed: {e}")
        print("  Make sure you have installed OpenVINO GenAI")
        return False
    
    return True

def test_directories():
    """Test if required directories exist"""
    print("\nTesting directory structure...")
    
    required_dirs = ["Models", "Images"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name} directory exists")
        else:
            print(f"✗ {dir_name} directory missing")
            return False
    
    return True

def test_config():
    """Test if config.json is valid"""
    print("\nTesting configuration...")
    
    try:
        import json
        with open("config.json", "r") as f:
            config = json.load(f)
        
        required_keys = ["BotName", "UserName", "Model", "LoraModel", "LLMDevice", "LoraDevice"]
        for key in required_keys:
            if key in config:
                print(f"✓ Config has {key}: {config[key]}")
            else:
                print(f"✗ Config missing {key}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_openvino_devices():
    """Test OpenVINO device availability"""
    print("\nTesting OpenVINO devices...")
    
    try:
        import openvino as ov
        core = ov.Core()
        devices = core.available_devices
        
        print(f"Available devices: {devices}")
        
        # Check for NPU
        if "NPU" in devices:
            print("✓ NPU device available")
        else:
            print("⚠ NPU device not available (Intel NPU driver may not be installed)")
        
        # Check for GPU
        if "GPU" in devices:
            print("✓ GPU device available")
        else:
            print("⚠ GPU device not available")
        
        # CPU should always be available
        if "CPU" in devices:
            print("✓ CPU device available")
        else:
            print("✗ CPU device not available (this is unexpected)")
            return False
        
        return True
    except Exception as e:
        print(f"✗ OpenVINO device test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Intelexia Windows Installation Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Directory Structure", test_directories),
        ("Configuration", test_config),
        ("OpenVINO Devices", test_openvino_devices)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Intelexia is ready to use.")
        print("\nNext steps:")
        print("1. Download models using the instructions in README_Windows.md")
        print("2. Run: python Intelexia-Free.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("- Install Intel NPU driver for NPU support")
        print("- Run: pip install --pre openvino openvino-tokenizers openvino-genai --extra-index-url https://storage.openvinotoolkit.org/simple/wheels/nightly")
    
    print("=" * 50)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
