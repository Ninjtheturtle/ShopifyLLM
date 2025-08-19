# Shopify Store Builder AI (Fine-tuned GPT-Neo 1.3B)

A fine-tuned GPT-Neo 1.3B + LoRA/QLoRA system that creates premium Shopify store content with high-quality, conversion-optimized product descriptions.

---

## 🎯 Problem Solved
- **Eliminates generic AI copy** – no more “high-quality product with advanced features.”
- **Brand voice replication** – mimics Apple, Nike, Patagonia, and other top brands.
- **SEO-driven content** – naturally integrates keywords with a focus on conversions.
- **Validated on real data** – fine-tuned on 300+ premium brand examples.

---

## 🧠 How It Works
Fine-tuned **GPT-Neo 1.3B** using **LoRA/QLoRA** on real Shopify product data, leveraging **CUDA acceleration** for efficient GPU-based training.  
Instead of generating bland, generic text, the model produces descriptions that **sell**.  

Key features:
- **Conversion-optimized copy** trained on real premium product descriptions.  
- **SEO-focused language** that balances readability with discoverability.  
- **Brand voice styling** aligned to premium e-commerce brands.  

---

## 📊 Real-Time A/B Testing

To validate performance beyond “good-looking copy,” the system includes a built-in **A/B testing engine** with statistical rigor:

- **Deterministic Variant Assignment**  
  Each user is consistently assigned to a control or treatment group using a hash-based allocation. This prevents variant switching across sessions and ensures unbiased exposure.  

- **Event Tracking & Metrics**  
  Tracks **add-to-cart rate** at the session level. Data is logged and aggregated in real time to measure actual business impact, not just text quality.  

- **Multi-Armed Bandit Optimization**  
  Implements **epsilon-greedy and UCB1 (Upper Confidence Bound)** strategies to adapt traffic allocation. Poor-performing variants are phased out automatically, while higher-converting ones get more traffic.  

✅ This means every description generated isn’t just AI-generated—it’s **tested, validated, and optimized in production**.

---

## ⚙️ Tech Stack
- **Model**: GPT-Neo 1.3B fine-tuned with LoRA/QLoRA  
- **Training**: CUDA-accelerated GPU training for efficient fine-tuning  
- **Frameworks**: Hugging Face Transformers, PEFT, Datasets  
- **Web App**: Flask for the builder interface  
- **Testing Engine**: Python-based, statistical analysis + bandit optimization  
- **Deployment**: Shopify API integration for store updates  

---
