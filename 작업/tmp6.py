from openai import OpenAI
import os
from getpass import getpass

# Colab에 API 키를 안전하게 입력받기
api_key = getpass("OpenAI API 키를 입력하세요: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")

# API 키를 환경 변수에 저장
os.environ['OPENAI_API_KEY'] = api_key

def create_chat_completion(system_input, user_input, model="gpt-4o-mini", temperature=1.15, max_tokens=150):
    try:
        # 메시지 목록을 자동으로 생성해요
        messages = [
            {"role": "system", "content": system_input},
            {"role": "user", "content": user_input}
        ]

        response = OpenAI().chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens  # 최대 토큰 수를 지정해요
        )
        # 생성된 응답을 반환해요
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# 메시지 목록 예시
system_input = "넌 AI 전문 강사아. AI, 개발에 관련된 질문에만 친절하고 간략하게 답변해줘"
user_input = "LLM으로 무엇을 할 수 있는지 설명해줘."

# API 호출 및 결과 출력
responses = create_chat_completion(system_input, user_input)
print(responses)
print(responses.choices[0].message.content)