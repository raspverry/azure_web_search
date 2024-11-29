# src/chatgpt.py
import requests

def openai_generate_response(OPENAI_API_KEY, OPENAI_API_URL, prompt, model="gpt-4o-mini"):
    """
    OpenAIのGPTモデルを使用して指定されたプロンプトに対する応答を生成する。
    
    Parameters:
        prompt (str): GPTに渡すプロンプト。
        model (str): 使用するGPTモデル。
    
    Returns:
        dict: APIからのJSONレスポンス。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "n": 1,
        "stop": None,
        "temperature": 0.7
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()