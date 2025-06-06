import os
import dashscope
from dashscope import Generation

class RecipeGenerator:
    """
    A class to generate recipes using the dashscope LLM API.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the RecipeGenerator with an API key.
        
        Args:
            api_key (str, optional): The API key for dashscope. If None, it will use the environment variable.
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set it as an argument or as DASHSCOPE_API_KEY environment variable.")
    
    def generate_recipe(self, ingredients, dietary_preference=None, goal=None, stream=False):
        """
        Generate a recipe based on the given ingredients and preferences.
        
        Args:
            ingredients (list): List of ingredients available.
            dietary_preference (str, optional): Dietary preference (e.g., "low-carb", "vegan").
            goal (str, optional): Nutritional goal (e.g., "muscle gain", "weight loss").
            stream (bool, optional): Whether to stream the response.
            
        Returns:
            dict: A dictionary containing the recipe and nutritional information.
        """
        # Construct the prompt
        prompt = self._construct_prompt(ingredients, dietary_preference, goal)
        
        # Set up the messages for the LLM
        messages = [
            {"role": "system", "content": "You are a helpful cooking assistant that creates recipes based on available ingredients and dietary preferences. You also provide nutritional analysis and suggestions for modifications."},
            {"role": "user", "content": prompt}
        ]
        
        # Call the LLM API
        if stream:
            return self._stream_generate(messages)
        else:
            return self._generate(messages)
    
    def _construct_prompt(self, ingredients, dietary_preference, goal):
        """
        Construct a prompt for the LLM based on the inputs.
        
        Args:
            ingredients (list): List of ingredients available.
            dietary_preference (str, optional): Dietary preference.
            goal (str, optional): Nutritional goal.
            
        Returns:
            str: The constructed prompt.
        """
        ingredients_str = ", ".join(ingredients)
        prompt = f"Create a recipe using these ingredients: {ingredients_str}."
        
        if dietary_preference:
            prompt += f" The recipe should be {dietary_preference}."
        
        if goal:
            prompt += f" The recipe should support {goal}."
        
        prompt += " Please provide the following information:\n"
        prompt += "1. Recipe name\n"
        prompt += "2. Ingredients with quantities\n"
        prompt += "3. Step-by-step cooking instructions\n"
        prompt += "4. Nutritional information (calories, protein, carbs, fat)\n"
        prompt += "5. Suggestions for modifications to better meet dietary preferences or goals\n"
        
        return prompt
    
    def _generate(self, messages):
        """
        Generate a response from the LLM.
        
        Args:
            messages (list): The messages to send to the LLM.
            
        Returns:
            dict: The parsed response.
        """
        response = Generation.call(
            api_key=self.api_key,
            model="qwen-plus",
            messages=messages,
            result_format="message",
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            return self._parse_recipe_response(content)
        else:
            raise Exception(f"Error: {response.code} - {response.message}")
    
    def _stream_generate(self, messages):
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages (list): The messages to send to the LLM.
            
        Returns:
            generator: A generator yielding response chunks.
        """
        responses = Generation.call(
            api_key=self.api_key,
            model="qwen-plus",
            messages=messages,
            result_format="message",
            stream=True,
            incremental_output=True,
        )
        
        full_content = ""
        for response in responses:
            chunk = response.output.choices[0].message.content
            full_content += chunk
            yield chunk
        
        return self._parse_recipe_response(full_content)
    
    def _parse_recipe_response(self, content):
        """
        Parse the LLM response into a structured recipe format.
        
        Args:
            content (str): The raw response from the LLM.
            
        Returns:
            dict: A structured recipe dictionary.
        """
        # This is a simple parsing implementation
        # In a real application, you might want to use more sophisticated parsing
        lines = content.strip().split('\n')
        
        recipe = {
            'name': '',
            'ingredients': [],
            'instructions': [],
            'nutrition': {},
            'suggestions': []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to identify sections
            if "Recipe name" in line or line.startswith("# "):
                recipe['name'] = line.replace("Recipe name:", "").replace("# ", "").strip()
                current_section = 'name'
            elif "Ingredients" in line or line.startswith("## Ingredients"):
                current_section = 'ingredients'
            elif "Instructions" in line or "Steps" in line or line.startswith("## Instructions"):
                current_section = 'instructions'
            elif "Nutritional" in line or line.startswith("## Nutrition"):
                current_section = 'nutrition'
            elif "Suggestions" in line or "Modifications" in line or line.startswith("## Suggestions"):
                current_section = 'suggestions'
            else:
                # Add content to the current section
                if current_section == 'ingredients':
                    recipe['ingredients'].append(line)
                elif current_section == 'instructions':
                    recipe['instructions'].append(line)
                elif current_section == 'nutrition':
                    # Try to parse nutrition information
                    if "calories" in line.lower():
                        recipe['nutrition']['calories'] = line
                    elif "protein" in line.lower():
                        recipe['nutrition']['protein'] = line
                    elif "carbs" in line.lower() or "carbohydrates" in line.lower():
                        recipe['nutrition']['carbs'] = line
                    elif "fat" in line.lower():
                        recipe['nutrition']['fat'] = line
                    else:
                        recipe['nutrition'][f'other_{len(recipe["nutrition"])}'] = line
                elif current_section == 'suggestions':
                    recipe['suggestions'].append(line)
        
        return recipe