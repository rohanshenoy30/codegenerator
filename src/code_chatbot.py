from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re

class CodeGenerationChatBot:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Using a more powerful code generation model
        self.tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Python-hf")
        self.model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-Python-hf").to(self.device)
        self.chat_history = []
        
        # Configure tokenizer properly
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_code(self, user_prompt):
        self.chat_history.append(f"User: {user_prompt}")
        
        # Create a more specific prompt structure
        prompt = f"""Task: {user_prompt}
Language: Python

Please write complete, functional code that solves the task. Include all necessary imports and helper functions.

Solution:
```python
"""
        
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            return_attention_mask=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=300,
                temperature=0.2,
                top_k=40,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        code = self._clean_code_response(full_response, prompt)
        self.chat_history.append(f"Bot: {code}")
        return code

    def _clean_code_response(self, response, prompt):
        """Extract and clean the generated code"""
        # Remove the prompt part
        code = response[len(prompt):]
        
        # Extract just the Python code block
        code = re.sub(r'.*?(```python.*?```)', r'\1', code, flags=re.DOTALL)
        
        # Clean up the code block markers
        code = re.sub(r'^```python|```$', '', code, flags=re.IGNORECASE).strip()
        
        # Ensure we have valid Python code
        if not any(kw in code for kw in ['def ', 'class ', 'import ', 'return ']):
            # If generation failed completely, try again with simpler parameters
            return self._retry_generation(prompt)
        
        return code

    def _retry_generation(self, prompt):
        """Retry generation with more constrained parameters"""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            return_attention_mask=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=200,
                temperature=0.1,  # More deterministic
                top_k=20,
                top_p=0.8,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return full_response[len(prompt):].strip()

    def get_chat_history(self):
        return self.chat_history