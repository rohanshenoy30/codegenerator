# src/autocomplete.py
from collections import defaultdict
import re

class CodeAutocomplete:
    def __init__(self, prompt_recommender):
        self.prompt_recommender = prompt_recommender
        self.prefix_tree = self._build_prefix_tree()
        self.code_keywords = self._load_code_keywords()
    
    def _build_prefix_tree(self):
        tree = defaultdict(list)
        for prompt in self.prompt_recommender.prompts:
            # Split on code-related phrases
            parts = re.split(r'(?:write|create|implement|show|how to)', prompt.lower())
            for part in parts:
                part = part.strip()
                if part:
                    for i in range(1, len(part.split())+1):
                        prefix = " ".join(part.split()[:i])
                        tree[prefix].append(prompt)
        return tree
    
    def _load_code_keywords(self):
        return {
            'python': ['def', 'import', 'class', 'try', 'except', 'with', 'as'],
            'javascript': ['function', 'const', 'let', 'async', 'await', 'export'],
            'java': ['public', 'class', 'static', 'void', 'new'],
            'sql': ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY'],
            'general': ['function', 'loop', 'array', 'string', 'file']
        }
    
    def get_completions(self, partial_input):
        partial_input = partial_input.lower().strip()
        completions = set()
        
        # 1. Check for language-specific keywords
        lang = self._detect_language(partial_input)
        for kw in self.code_keywords.get(lang, []) + self.code_keywords['general']:
            if kw.startswith(partial_input):
                completions.add(kw)
        
        # 2. Check prefix tree
        for prefix in self.prefix_tree:
            if prefix.startswith(partial_input):
                completions.update(self.prefix_tree[prefix])
        
        # 3. If still empty, use semantic similarity
        if not completions:
            completions.update(self.prompt_recommender.recommend_prompts([partial_input]))
        
        return sorted(completions)[:5]
    
    def _detect_language(self, text):
        text = text.lower()
        if 'python' in text: return 'python'
        if 'javascript' in text or 'js' in text: return 'javascript'
        if 'java' in text: return 'java'
        if 'sql' in text: return 'sql'
        return 'general'