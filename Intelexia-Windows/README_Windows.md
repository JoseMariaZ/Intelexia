# Intelexia Windows Setup Guide

This guide provides step-by-step instructions for setting up and running Intelexia on Windows with Intel NPU support.

> **⚠️ Important Note**: AI models are **NOT included** in this repository due to their large size (several GB). You will need to download them separately as part of the setup process.

## Prerequisites

### Hardware Requirements
- Intel Core Ultra processor (Meteor Lake or Lunar Lake) with NPU
- At least 16GB RAM (recommended for models >7B parameters)
- Windows 10 or Windows 11

### Software Requirements
- Python 3.8 or higher
- Git (for cloning repositories)
- **Internet connection** (for downloading AI models)
- **10GB+ free disk space** (for AI models)

## What's Included in This Repository

This Windows deployment includes:
- ✅ **Windows-compatible Python application** (`Intelexia-Free.py`)
- ✅ **Automated setup script** (`setup_windows.bat`)
- ✅ **Installation verification tools** (`test_installation.py`, `test_generation.py`)
- ✅ **Complete documentation** (this README and compatibility report)
- ✅ **Dependency management** (`requirements.txt`)
- ❌ **AI Models** (must be downloaded separately - see step 5)

## Quick Start (Recommended)

For first-time users, follow these steps for the fastest setup:

1. **Install Intel NPU Driver** (see step 1 below)
2. **Run automated setup**: `setup_windows.bat`
3. **Download default models** (TinyLlama + Stable Diffusion)
4. **Test the application**: `python Intelexia-Free.py`

Total setup time: ~30-45 minutes (including model downloads)

## Detailed Installation Steps

### 1. Install Intel NPU Driver

**IMPORTANT**: Install the Intel NPU driver first before setting up the application.

1. Download the latest Intel NPU Driver from:
   https://www.intel.com/content/www/us/en/download/794734/intel-npu-driver-windows.html

2. Run the installer as Administrator
3. Reboot your system after installation
4. Verify installation in Device Manager under "System devices" - you should see "Intel(R) AI Boost"

### 2. Clone and Setup Project

```powershell
# Clone the repository
git clone https://github.com/JoseMariaZ/Intelexia.git
cd Intelexia

# Copy Windows-specific files
# (This step is already done if you're reading this file)
```

### 3. Run Automated Setup

```powershell
# Run the Windows setup script
setup_windows.bat
```

This script will:
- Create a Python virtual environment
- Install all required dependencies
- Set up OpenVINO and related packages

### 4. Manual Setup (Alternative)

If the automated setup fails, you can install manually:

```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install individually:
pip install numpy Pillow
pip install --pre openvino openvino-tokenizers openvino-genai --extra-index-url https://storage.openvinotoolkit.org/simple/wheels/nightly
pip install optimum-intel diffusers
```

### 5. Download AI Models

**⚠️ REQUIRED STEP**: Models are not included in the repository and must be downloaded separately.

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Navigate to Models directory
cd Models

# Option 1: Download smaller models for testing (Recommended for first-time setup)
# LLM Model: TinyLlama (faster download, good for testing)
optimum-cli export openvino -m TinyLlama/TinyLlama-1.1B-Chat-v1.0 --weight-format int4 --sym --ratio 1.0 --group-size 128 TinyLlama-1.1B-Chat-v1.0

# Image Generation Model: Stable Diffusion v1.5
optimum-cli export openvino --model runwayml/stable-diffusion-v1-5 --task stable-diffusion --weight-format fp16 stable-diffusion-v1-5

# Option 2: Download larger models (Requires Hugging Face authentication)
# LLM Model: Llama 3.1 8B (requires HF login and model access)
# huggingface-cli login
# optimum-cli export openvino -m meta-llama/Llama-3.1-8B-Instruct --weight-format int4 --sym --ratio 1.0 --group-size -1 Llama-3.1-8B-Instruct

cd ..
```

**Important Notes**:
- **Model downloads are large** (2-8GB each) and may take 10-30 minutes depending on your internet connection
- **Disk space required**: At least 10GB free space for models
- **For Llama models**: You need a Hugging Face account and model access approval
- **Default configuration**: Uses TinyLlama and Stable Diffusion v1.5 (works out of the box)

### 6. Run the Application

```powershell
# Activate virtual environment (if not already active)
venv\Scripts\activate

# Run Intelexia
python Intelexia-Free.py
```

## Configuration

### Device Settings

Edit `config.json` to configure device usage:

```json
{
    "BotName": "Intellexia",
    "UserName": "User",
    "Model": "TinyLlama-1.1B-Chat-v1.0",
    "LoraModel": "stable-diffusion-v1-5",
    "systemPrompt": "You are Intellexia, a helpfully and lovely assistant",
    "LLMDevice": "NPU",
    "LoraDevice": "GPU"
}
```

**Model Configuration Notes**:
- **Default models**: TinyLlama for LLM, Stable Diffusion v1.5 for image generation
- **To use Llama 3.1 8B**: Change `"Model"` to `"Llama-3.1-8B-Instruct"` (requires separate download)
- **Model names must match**: The folder names in the `Models/` directory

**Device Options**:
- `"NPU"` - Use Intel NPU (recommended for LLM)
- `"GPU"` - Use Intel integrated GPU
- `"CPU"` - Use CPU (fallback option)

### Performance Tuning

For better performance, you can modify the pipeline configuration in the code:

```python
pipeline_config = {
    "MAX_PROMPT_LEN": 1024,      # Maximum input prompt length
    "MIN_RESPONSE_LEN": 128,     # Minimum response length
    "GENERATE_HINT": "BEST_PERF" # Performance mode
}
```

## Troubleshooting

### Common Issues

1. **NPU Not Detected**
   - Verify Intel NPU driver installation in Device Manager
   - Try changing `LLMDevice` to `"CPU"` or `"GPU"` in config.json

2. **Model Loading Errors**
   - Ensure models are downloaded completely
   - Check available disk space (models require several GB)
   - Verify internet connection during model download

3. **Import Errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Performance Issues**
   - Close other applications to free up memory
   - Try smaller models for testing
   - Monitor NPU/GPU usage in Task Manager

5. **Repetitive Text Generation**
   - ✅ **FIXED**: Updated generation parameters to prevent repetition
   - Uses improved prompt formatting for TinyLlama
   - Includes response cleaning to remove duplicate sentences
   - Repetition penalty and temperature controls added

### Environment Variables

If you encounter NPU memory allocation issues:

```powershell
# Disable NPU L0 memory allocation (for older drivers)
set DISABLE_OPENVINO_GENAI_NPU_L0=1
```

### Logs and Debugging

The application prints status messages to the console. Check the console output for detailed error messages if something goes wrong.

## Supported Models

The following models have been tested and work well with Intel NPU:

- meta-llama/Meta-Llama-3-8B-Instruct
- meta-llama/Llama-3.1-8B
- microsoft/Phi-3-mini-4k-instruct
- Qwen/Qwen2-7B
- mistralai/Mistral-7B-Instruct-v0.2
- TinyLlama/TinyLlama-1.1B-Chat-v1.0

## Repository Information

### Size and Download
- **Repository size**: ~2MB (excluding models)
- **With models**: ~10-15GB total
- **Models are downloaded separately** to keep the repository lightweight

### Deployment Notes
- This branch contains Windows-specific optimizations and fixes
- Models are excluded from version control due to size constraints
- All dependencies are managed through Python package managers
- Virtual environment (`.venv`) is automatically excluded from git

## Additional Resources

- [OpenVINO Documentation](https://docs.openvino.ai/)
- [Intel NPU Developer Guide](https://docs.openvino.ai/2025/openvino-workflow/running-inference/inference-devices-and-modes/npu-device.html)
- [OpenVINO GenAI Repository](https://github.com/openvinotoolkit/openvino.genai)
- [Windows Compatibility Report](WINDOWS_COMPATIBILITY_REPORT.md)

## Support

For issues specific to this Windows port, check the console output for error messages. For general Intelexia issues, refer to the main project repository.
