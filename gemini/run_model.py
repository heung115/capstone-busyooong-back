import google.generativeai as genai
from load_creds import load_creds

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

input_text = input("Enter the input text: ")
result = model.generate_content(input_text)
print(result.text)


def generate_response(user_input):
    try:
        result = model.generate_content(input_text)
        return result.text
    except Exception as e:
        print(f"Error during content generation: {e}")
