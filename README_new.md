# 🛍️ ShopifyLLM - Specialized E-commerce Assistant

A fine-tuned language model built on TinyLlama-1.1B-Chat, specifically trained to help Shopify merchants set up and manage their online stores. This AI assistant provides expert guidance on product management, inventory tracking, shipping configuration, and general e-commerce best practices.

## 🎯 Project Overview

**ShopifyLLM** transforms a general-purpose language model into a specialized e-commerce consultant using:
- **Base Model**: TinyLlama/TinyLlama-1.1B-Chat-v1.0 (1.1B parameters)
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation) for efficient training
- **Training Data**: Custom Shopify-focused conversation dataset
- **Deployment**: Streamlit web interface for easy interaction

## 🚀 Features

- **Specialized Knowledge**: Trained specifically on Shopify workflows and best practices
- **Lightweight**: Uses LoRA for efficient fine-tuning without full model retraining
- **Interactive**: Web-based chat interface for real-time assistance
- **Production Ready**: Deployable chatbot suitable for integration into Shopify stores
- **Fast Inference**: Optimized for quick responses to merchant questions

## 📁 Project Structure

```
ShopifyLLM/
├── 📄 train.py              # Training script with LoRA configuration
├── 📄 inference.py          # CLI interface for testing the model
├── 📄 app.py               # Streamlit web interface
├── 📄 shopify_data.jsonl   # Training dataset (10 conversation examples)
├── 📄 requirements.txt     # Python dependencies
├── 🗂️ fine_tuned_model/   # Saved LoRA adapters
├── 🗂️ base_model/         # Original TinyLlama model files
└── 🗂️ results/            # Training checkpoints and logs
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- CUDA-capable GPU (recommended)
- 8GB+ RAM

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Ninjtheturtle/ShopifyLLM.git
cd ShopifyLLM
```

2. **Create and activate virtual environment:**
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### 1. Training the Model

To retrain with your own data:
```bash
python train.py
```

### 2. Testing via CLI

Test the model with predefined questions:
```bash
python inference.py --test
```

Start an interactive chat session:
```bash
python inference.py
```

### 3. Web Interface

Launch the Streamlit web app:
```bash
streamlit run app.py
```

Access the interface at `http://localhost:8501`

## 📊 Model Configuration

### LoRA Parameters
- **Rank (r)**: 8
- **Alpha**: 16
- **Target Modules**: `["q_proj", "v_proj"]` (attention layers)
- **Dropout**: 5%
- **Task Type**: Causal Language Modeling

### Training Settings
- **Batch Size**: 2 per device
- **Epochs**: 3
- **Learning Rate**: 5e-4
- **Max Sequence Length**: 512 tokens
- **Precision**: FP16 for efficiency

## 💡 What the Assistant Can Help With

- ✅ **Product Management**: Adding products, organizing collections, optimizing listings
- ✅ **Inventory Tracking**: Stock management, low-stock alerts, inventory best practices
- ✅ **Shipping Setup**: Configuring rates, international shipping, carrier integration
- ✅ **Payment Processing**: Setting up payment methods, handling transactions
- ✅ **Order Fulfillment**: Processing orders, shipping workflows, customer communication
- ✅ **Store Optimization**: SEO, conversion rate optimization, photo guidelines
- ✅ **Customer Service**: Returns, refunds, support best practices

## 📈 Training Results

- **Final Training Loss**: ~2.47
- **Training Time**: ~47 seconds for 3 epochs
- **Dataset Size**: 10 conversation examples
- **Model Size**: Base model + lightweight LoRA adapters (~8MB)

## 🔧 Customization

### Adding More Training Data

Expand `shopify_data.jsonl` with additional conversations:
```json
{"messages": [
    {"role": "user", "content": "Your question here"},
    {"role": "assistant", "content": "Expert response here"}
]}
```

### Adjusting LoRA Parameters

Modify `train.py` to experiment with different configurations:
- Increase `r` for more capacity (but larger model size)
- Adjust `lora_alpha` for adaptation strength
- Target additional modules for broader fine-tuning

## 🚀 Deployment Ideas

1. **Shopify App**: Integrate into a Shopify app for direct merchant access
2. **Website Widget**: Embed as a chat widget on e-commerce websites
3. **Discord/Slack Bot**: Deploy as a bot for merchant communities
4. **API Service**: Expose via REST API for third-party integrations

## 📝 Sample Interactions

**Q:** How do I add a product to my store?
**A:** Go to Products > Add product. Fill in details like title, price, and inventory. Make sure to add high-quality images, write compelling descriptions, and set up proper SEO with relevant keywords.

**Q:** What payment methods should I enable?
**A:** Enable Shopify Payments for credit cards as it's the most seamless option. Also consider PayPal, Apple Pay, Google Pay, and Shop Pay for better conversion.

## 🤝 Contributing

1. Fork the repository
2. Add more training data to improve the model
3. Experiment with different LoRA configurations
4. Submit pull requests with improvements

## 📄 License

This project is open source. Please check the base model license for TinyLlama.

## 🙏 Acknowledgments

- TinyLlama team for the base model
- Hugging Face for the transformers library
- Microsoft for the LoRA implementation (PEFT)

---

**Built with ❤️ for the Shopify merchant community**
