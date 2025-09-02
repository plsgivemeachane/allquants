# 🔢 AllQuants - Comprehensive Model Quantizer

AllQuants is a powerful tool that automates the complete workflow of downloading, converting, and quantizing language models using Hugging Face and LLAMA.cpp. It provides beautiful rich console output and handles the entire process from model download to Hugging Face repository upload.

## ✨ Features

- **🚀 Complete Workflow Automation**: Download → Convert → Quantize → Upload
- **🎨 Beautiful Rich Console**: Progress bars, tables, and colorful logging
- **📊 14 Quantization Types**: From Q2_K to Q8_0 with detailed specifications
- **☁️ Hugging Face Integration**: Automatic repository creation and model upload
- **🛠️ Robust Error Handling**: Comprehensive logging and error recovery
- **⚡ Central Command Runner**: Efficient subprocess management with real-time output

## 🏗️ Architecture

```
AllQuants/
├── main.py           # CLI interface with Click
├── quantizer.py      # Core quantization logic
├── convert.py        # LLAMA.cpp conversion script (existing)
├── TEMPLATE.md       # Model card template
├── requirements.txt  # Python dependencies
├── llama.cpp/        # LLAMA.cpp binaries and tools
├── models/           # Downloaded models (created automatically)
├── gguf/            # GGUF converted files (created automatically)
└── quantized/       # Final quantized models (created automatically)
```

## 📋 Prerequisites

1. **Python 3.8+**
2. **LLAMA.cpp** with quantization support built
3. **Hugging Face Token** (for uploading models)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment Check
```bash
python main.py setup --check-deps
```

### 3. Set Hugging Face Token
```bash
# Option 1: Environment variable
export HF_TOKEN="your_hugging_face_token"

# Option 2: Pass as argument
python main.py quantize microsoft/DialoGPT-small --hf-token your_token
```

### 4. Run Complete Quantization
```bash
# Quantize all types and upload
python main.py quantize microsoft/DialoGPT-small

# Quantize specific types only
python main.py quantize microsoft/DialoGPT-small --quant-types Q4_K_M Q8_0

# Skip upload (local only)
python main.py quantize microsoft/DialoGPT-small --no-upload
```

## 🔧 Available Commands

### `quantize` - Complete Workflow
```bash
python main.py quantize MODEL_NAME [OPTIONS]

Options:
  --hf-token TEXT        Hugging Face token
  --quant-types TEXT     Specific quantization types (multiple)
  --no-upload           Skip uploading to Hugging Face
  --show-types          Show available quantization types
```

### `types` - Show Quantization Types
```bash
python main.py types
```

### `download` - Download Model Only
```bash
python main.py download microsoft/DialoGPT-small
```

### `convert` - Convert to GGUF Only
```bash
python main.py convert ./models/microsoft_DialoGPT-small microsoft/DialoGPT-small
```

### `setup` - Environment Check
```bash
python main.py setup --check-deps
```

## 📊 Quantization Types

| Type    | Size      | Speed     | Quality    | Recommended For                      |
|---------|-----------|-----------|------------|--------------------------------------|
| Q2_K    | Smallest  | Fastest   | Low        | Prototyping, minimal RAM/CPU         |
| Q3_K_S  | Very Small| Very Fast | Low-Med    | Lightweight devices, testing         |
| Q3_K_M  | Small     | Fast      | Med        | Lightweight, slightly better quality |
| Q3_K_L  | Small-Med | Fast      | Med        | Faster inference, fair quality       |
| Q4_0    | Medium    | Fast      | Good       | General use, chats, low RAM          |
| Q4_1    | Medium    | Fast      | Good+      | Recommended, slightly better quality |
| Q4_K_S  | Medium    | Fast      | Good+      | Recommended, balanced                |
| Q4_K_M  | Medium    | Fast      | Good++     | **Recommended, best Q4 option**      |
| Q5_0    | Larger    | Moderate  | Very Good  | Chatbots, longer responses           |
| Q5_1    | Larger    | Moderate  | Very Good+ | More demanding tasks                 |
| Q5_K_S  | Larger    | Moderate  | Very Good+ | Advanced users, better accuracy      |
| Q5_K_M  | Larger    | Moderate  | Excellent  | Demanding tasks, high quality        |
| Q6_K    | Large     | Slower    | Near FP16  | Power users, best quantized quality  |
| Q8_0    | Largest   | Slowest   | FP16-like  | Maximum quality, high RAM/CPU        |

## 🔄 Workflow Details

### 1. **Model Download**
- Downloads full BF16 model from Hugging Face
- Stores in `models/` directory
- Handles authentication and large file downloads

### 2. **GGUF Conversion**
- Uses existing `convert.py` script
- Converts to F16 GGUF format
- Command: `python convert.py models/<model> --outfile gguf/<model>.gguf --outtype f16`

### 3. **Quantization**
- Uses `llama-quantize` executable
- Processes all 14 quantization types
- Parallel processing with progress tracking

### 4. **Repository Upload**
- Creates Hugging Face repository
- Uploads all quantized files
- Generates model card from template

## 🎨 Rich Console Features

- **Progress Bars**: Real-time progress for downloads, conversions, and quantization
- **Status Indicators**: Color-coded success/error messages
- **Tables**: Beautiful quantization type comparison
- **Panels**: Organized information display
- **Spinners**: Activity indicators for long-running tasks

## 🛠️ Technical Details

### Command Runner
The `CommandRunner` class provides:
- Real-time output streaming
- Error handling and logging
- Progress indication
- Cross-platform subprocess management

### Error Handling
- Comprehensive exception handling
- Graceful failure recovery
- Detailed error messages
- Cleanup of partial files

### File Management
- Automatic directory creation
- Duplicate file detection
- Cleanup utilities
- Path validation

## 📝 Example Usage

```bash
# Complete workflow with custom types
python main.py quantize microsoft/DialoGPT-small \
  --quant-types Q4_K_M Q5_K_M Q8_0 \
  --hf-token hf_your_token_here

# Local quantization only
python main.py quantize microsoft/DialoGPT-small --no-upload

# Check what quantization types are available
python main.py types

# Verify environment setup
python main.py setup --check-deps
```

## 🔧 Troubleshooting

### Common Issues

1. **Missing llama-quantize executable**
   ```bash
   # Build llama.cpp with quantization support
   cd llama.cpp
   make llama-quantize
   ```

2. **Hugging Face authentication**
   ```bash
   # Login via CLI
   huggingface-cli login
   
   # Or set environment variable
   export HF_TOKEN="your_token"
   ```

3. **Out of disk space**
   - Models can be large (several GB each)
   - Ensure sufficient disk space
   - Use `--no-upload` for local testing

4. **Memory issues during quantization**
   - Close other applications
   - Quantize fewer types at once
   - Use smaller models for testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LLAMA.cpp** - For the quantization tools
- **Hugging Face** - For model hosting and APIs
- **Rich** - For beautiful console output
- **Click** - For CLI framework

---

**Made with ❤️ by leeminwaan**
