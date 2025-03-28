import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"

model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, device_map= "auto")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True,torch_dtype=torch.float16, device_map="auto")

class LLMHandler:
    def __init__(self):
        self.tokenizer = tokenizer
        self.model = model
    
    def generate_response(self, question, context):
        """Tạo câu trả lời dựa trên ngữ cảnh"""
        # Tạo prompt chi tiết
        prompt = f"""Context: {context[0] if context else "No relevant context found."}

Question: {question}

Based on the given context, please provide a detailed and accurate answer to the question. If the context does not contain sufficient information, explain that you cannot provide a complete answer."""

        # Tokenize và generate
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=True).to(self.model.device)
        outputs = self.model.generate(
            inputs.input_ids, 
            max_length=1000, 
            temperature=0.7, 
            do_sample=True
        )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response