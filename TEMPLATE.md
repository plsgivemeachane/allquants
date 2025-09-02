---
license: apache-2.0
base_model: {{base_model_w_author}}
pipeline_tag: text-generation
---

# 🤖 Model Card for {{base_model}}-GGUF

This repo is packed with multiple quantized versions of {{base_model_w_author}} in GGUF format. 🚀✨  
Built for running efficiently on your everyday hardware - no need for enterprise-level specs to deploy these models. 💻🎯🔥  

## 📋 Model Details

### ⚡ Quantization Results

| Quantization | Size (vs. FP16) | Speed     | Quality    | Recommended For                      |
|--------------|-----------------|-----------|------------|--------------------------------------|
| Q2_K         | Tiny 🐭         | Lightning ⚡ | Basic 📉   | Quick prototypes, potato hardware 🧪 |
| Q3_K_S       | Mini 🐹         | Super fast 🚀| Decent 📊  | Mobile devices, quick tests 📱      |
| Q3_K_M       | Small 🐰        | Fast 💨   | Good 📈    | Lightweight but better quality      |
| Q3_K_L       | Small+ 🐱       | Fast ⚡   | Good 📊    | Speed with acceptable quality       |
| Q4_0         | Medium 🐺       | Quick ⚡   | Solid 👍   | Daily driver, casual chats 💬       |
| Q4_1         | Medium 🦊       | Quick 🚀   | Solid+ 👌  | Slight upgrade from Q4_0            |
| Q4_K_S       | Medium 🐻       | Quick 💨   | Nice ✨    | Well-balanced choice ⚖️            |
| Q4_K_M       | Medium 🦁       | Quick ⚡   | Really nice 🌟| The crowd favorite 🏅         |
| Q5_0         | Chunky 🐘       | Chill 🚶  | Great 💪   | Chatbots that actually make sense 🤖|
| Q5_1         | Chunky 🦏       | Chill ⏳  | Great+ 🔥  | When you need quality responses 💼  |
| Q5_K_S       | Big 🐳          | Chill 🕐  | Great+ ⭐  | For the quality-conscious 🎯        |
| Q5_K_M       | Big 🦣          | Chill ⌛  | Excellent 🏆| High-end performance 💎           |
| Q6_K         | Massive 🐋      | Slow 🐌   | Near perfect 👑| Enthusiasts only              |
| Q8_0         | Absolute unit 🦕| Turtle 🐢 | Basically perfect 💎| Max settings gang 🖥️    |

> **📝 Real talk:**  
> - Lower numbers = smaller files 📉, runs faster ⚡, but quality takes a hit 📊  
> - Q4_K_M hits different - it's the sweet spot most people actually want 👥  
> - Q6_K/Q8_0 are for perfectionists with beefy hardware 🏆🧙‍♂️  
> - Everything here runs on regular consumer hardware 💻 - pick what matches your vibe! 🎯


### 📝 Model Description

- **Quantized by:** leeminwaan 👨‍💻  
- **Funded by [optional]:** Solo project, no corporate backing 💰  
- **Shared by [optional]:** leeminwaan 🤝  
- **Model type:** Decoder-only transformer (the good stuff) 🧠🤖  
- **Language(s) (NLP):** Base on {{base_model}}
- **License:** Apache-2.0 (free to use, modify, distribute) 📄⚖️  

### 🔗 Model Sources

- **Repository:** [Hugging Face Repo](https://huggingface.co/leeminwaan/{{base_model}}-GGUF) 🤗📦  
- **Quantization Tool:** [AllQuants](https://github.com/plsgivemeachane/allquants) 🔢⚡  
- **Paper [optional]:** No research paper (this is practical, not academic) 📝❌  
- **Demo [optional]:** Demo coming soon™ 🎮🔜  

## 🚀 How to Get Started with the Model

```python
# 🐍 Quick start - literally just this:
from huggingface_hub import hf_hub_download

# 📥 Grab the model (Q4_K_M is the sweet spot for most people)
model_path = hf_hub_download("leeminwaan/{{base_model}}-GGUF", "{{base_model}}-q4_k_m.gguf")
print("Downloaded:", model_path) # 🎊 You're good to go!
````

Available flavors: 🎁📦

* Q2\_K, Q3\_K\_S, Q3\_K\_M, Q3\_K\_L 🏃‍♂️💨 (Speed demons - perfect for testing)
* Q4\_0, Q4\_1, Q4\_K\_S, Q4\_K\_M ⚖️✨ (The goldilocks zone - just right)
* Q5\_0, Q5\_1, Q5\_K\_S, Q5\_K\_M 💪🎯 (For when you need that extra quality)
* Q6\_K, Q8\_0 🏆👑 (Maxed out settings - if your hardware can handle it)

## 🎯 Training Details

### 📊 Training Data

* This is a straight quantization - no extra training or fine-tuning involved. ✨

### ⚙️ Training Procedure

* Took {{base_model_w_author}} and compressed it into these GGUF formats. 🔄

## 🔧 Technical Specifications

#### 💾 Software

* llama.cpp for the heavy lifting 🦙
* Python 3.10 + huggingface_hub for the workflow 🐍

## 📚 Citation

**BibTeX:** 📖🔬

```bibtex
@misc{{base_model}}-GGUF,
  title={{base_model}}-GGUF Quantized Models},
  author={leeminwaan},
  year={2025}, % 🎊 Hot off the press!
  howpublished={\url{https://huggingface.co/leeminwaan/{{base_model}}-GGUF}}
}
```

**APA:** 📝✨

```
leeminwaan. (2025). {{base_model}}-GGUF Quantized Models [Computer software]. 💻 Hugging Face. https://huggingface.co/leeminwaan/{{base_model}}-GGUF 🤗
```

## 📖 Glossary

* **Quantization:** Making models smaller by reducing number precision - trades some quality for efficiency. 🔢
* **GGUF:** The file format that llama.cpp loves - optimized for fast inference. ⚡

## ℹ️ More Information

* This is still a work in progress - expect some rough edges. 🧪
* More updates and proper benchmarks coming when I get around to it. 📈

## 👨‍💻 Model Card Authors

* leeminwaan 🚀👨‍💻✨

## 📧 Model Card Contact

* Hugging Face: [leeminwaan](https://huggingface.co/leeminwaan) 🤗💌🎉
