# src/main.py
from code_chatbot import CodeGenerationChatBot
from prompt_recommender import CodePromptRecommender
from autocomplete import CodeAutocomplete
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

class CodeGenApp:
    def __init__(self):
        self.chatbot = CodeGenerationChatBot()
        self.recommender = CodePromptRecommender()
        self.autocomplete = CodeAutocomplete(self.recommender)
    
    def format_code(self, code, language='python'):
        try:
            lexer = get_lexer_by_name(language)
            formatter = TerminalFormatter()
            return pygments.highlight(code, lexer, formatter)
        except:
            return code
    
    def run(self):
        print("=== Code Generation Chatbot ===")
        print("Type your code request or '...' at the end for suggestions")
        print("Example prompts:")
        for i, prompt in enumerate(self.recommender.recommend_prompts([])[:3], 1):
            print(f"{i}. {prompt}")
        
        while True:
            user_input = input("\n>>> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                break
                
            # Handle autocomplete requests
            if user_input.endswith('...'):
                partial = user_input[:-3].strip()
                suggestions = self.autocomplete.get_completions(partial)
                if suggestions:
                    print("\nSuggestions:")
                    for i, sugg in enumerate(suggestions, 1):
                        print(f"{i}. {sugg}")
                continue
                
            # Generate and display code
            generated_code = self.chatbot.generate_code(user_input)
            print("\nGenerated Code:")
            print(self.format_code(generated_code))
            
            # Show follow-up prompts
            history = self.chatbot.get_chat_history()
            recommendations = self.recommender.recommend_prompts(history)
            
            if recommendations:
                print("\nTry asking:")
                for i, prompt in enumerate(recommendations, 1):
                    print(f"{i}. {prompt}")

if __name__ == "__main__":
    app = CodeGenApp()
    app.run()