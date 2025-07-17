import os
import google.generativeai as genai
import json
import time # Import time for sleep

API_KEY = 'Paste your api key here'

def get_gemini_questions(category, num_questions=10):
    genai.configure(api_key=API_KEY)

    model_to_use = None
    print("Attempting to find a suitable Gemini model...")
    try:
        # Prioritize newer, stable models with higher free tier limits
        # Check for specific stable versions first, then the -latest alias
        preferred_models = [
            "models/gemini-1.5-flash-latest", # Highest free tier limits
            "models/gemini-1.5-pro-latest",   # Next best, but with lower free tier limits
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "models/gemini-pro" # Legacy fallback
        ]

        available_models_with_content_gen = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models_with_content_gen.append(m.name)

        for pref_model in preferred_models:
            if pref_model in available_models_with_content_gen:
                model_to_use = pref_model
                break

        if not model_to_use:
            raise Exception("No suitable Gemini model found that supports 'generateContent'.")

        print(f"Using model: {model_to_use}")
        model = genai.GenerativeModel(model_to_use)

    except Exception as e:
        print(f"Error initializing Gemini model: {e}")
        print("Please check your API key, ensure the Generative Language API is enabled, and you have access to the models.")
        raise

    prompt = (
        f"Generate {num_questions} multiple-choice questions about {category}. "
        "Each question should have 1 correct answer and 3 incorrect options. "
        "Format the response as a JSON list of objects with 'question', 'options', and 'answer' fields."
    )

    try:
        response = model.generate_content(prompt)

        if response.text:
            try:
                raw = response.text.strip()
                # Remove Markdown code block if present
                if raw.startswith('```'):
                    import re
                    raw = re.sub(r'^```(?:json)?\s*|```$', '', raw, flags=re.IGNORECASE | re.MULTILINE).strip()
                questions = json.loads(raw)
                return questions
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response from model: {e}")
                print(f"Raw response text received:\n{response.text}")
                print("The model might not have generated a valid JSON. Adjusting the prompt can help.")
                return []
        else:
            print("The model did not return any text in the response.")
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                print(f"Prompt was blocked due to: {response.prompt_feedback.block_reason}")
            elif response.candidates and response.candidates[0].finish_reason:
                 print(f"Candidate finished with reason: {response.candidates[0].finish_reason}")
            return []

    except genai.types.BlockedPromptException as e:
        print(f"The prompt was blocked: {e.response.prompt_feedback}")
        return []
    except Exception as e:
        # Catch the quota error specifically
        if "429 Quota exceeded" in str(e):
            print(f"Quota Exceeded Error: {e}")
            print("Consider enabling billing for higher limits, or switch to a model like gemini-1.5-flash with higher free tier quotas.")
            # You could add a retry mechanism here with a backoff, but it's best to fix the root cause (quota)
        else:
            print(f"An unexpected error occurred during content generation: {e}")
        return []

