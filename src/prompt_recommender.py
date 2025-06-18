# src/prompt_recommender.py
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

class CodePromptRecommender:
    def __init__(self, data_path="data/code_prompts.json"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.prompts = []
        self.embeddings = None
        
        if os.path.exists(data_path):
            self.load_data(data_path)
        else:
            # Initialize with code generation prompts
            self.prompts = [
                "Write a Python function to reverse a string",
                "Create a React component for a login form",
                "How to make an HTTP GET request in JavaScript?",
                "Implement binary search in Java",
                "Show me a SQL query to find the second highest salary",
                "Write a Dockerfile for a Python Flask app",
                "Create a Python script to scrape a website",
                "How to implement JWT authentication in Node.js?",
                "Write a C++ program to find prime numbers",
                "Show me how to use pandas to read a CSV file",
                "Implement a linked list in Python",
                "How to create a REST API with Express.js?",
                "Write a bash script to backup files",
                "Create a Python decorator to measure function execution time",
                "How to implement pagination in SQL queries?"
            ]
            self.save_data(data_path)
        
        self.generate_embeddings()
    
    def load_data(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
            self.prompts = data['prompts']
    
    def save_data(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump({"prompts": self.prompts}, f)
    
    def generate_embeddings(self):
        self.embeddings = self.model.encode(self.prompts)
    
    def recommend_prompts(self, chat_history, top_n=3):
        if not chat_history:
            return np.random.choice(self.prompts, size=min(top_n, len(self.prompts)), replace=False).tolist()
        
        context = "\n".join(chat_history[-2:])
        context_embedding = self.model.encode([context])
        
        similarities = cosine_similarity(context_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        
        return [self.prompts[i] for i in top_indices]
    
    def add_prompt(self, new_prompt):
        if new_prompt not in self.prompts:
            self.prompts.append(new_prompt)
            new_embedding = self.model.encode([new_prompt])
            if self.embeddings is None:
                self.embeddings = new_embedding
            else:
                self.embeddings = np.vstack([self.embeddings, new_embedding])