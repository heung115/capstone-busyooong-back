import google.generativeai as genai
import os
from dotenv import load_dotenv
from env import getEnv

genai.configure(api_key=getEnv("GOOGLE_API_KEY"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

# API 키를 생성자에 전달하여 모델 생성
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

origin_prompt_parts = [
        "input: 주공아파트요",
        "output: 주공아파트",
        "input: 그 어디였더라 저기 광교에 있는 경기도청까지 어떻게 가요",
        "output: 경기도청",
        "input: 저기 그 경기대학교까지 갈라고 하는데요",
        "output: 경기대학교",
        "input: 아이파크캐슬 2단지 가요?",
        "output: 아이파크 캐슬 2단지",
        "input: 저기 뭐더라 제가 청계마을까지 가야하거든요",
        "output: 청계마을",
    ]
def generate_response(user_input):
    prompt_parts = origin_prompt_parts[::]
    prompt_parts.append("input: " + user_input)
    response = model.generate_content(prompt_parts)
    return response.text

def update_prompt(_input, _output):
    origin_prompt_parts.append("input: " + _input)
    origin_prompt_parts.append("output: " + _output)
