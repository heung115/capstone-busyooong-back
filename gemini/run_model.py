import google.generativeai as genai
from gemini.load_creds import load_creds
try:
    creds = load_creds()
    genai.configure(credentials=creds)
except Exception as e:
    print(f"Error loading credentials or configuring the API: {e}")
    exit(1)

name = "bus-destination-tune-epoch-5"
model_name = f"tunedModels/{name}"
try:
    model = genai.GenerativeModel(model_name=model_name)
    print(model)
except Exception as e:
    print(f"Error initializing the generative model: {e}")
    exit(1)

def generate_response(user_input):
    try:
        result = model.generate_content(user_input)
        return result.text
    except Exception as e:
        print(f"Error during content generation: {e}")
