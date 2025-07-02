import json
import requests
import logging
import re
from typing import Dict, List

from django.conf import settings
from openai import OpenAI

PROMPT_TEMPLATE = """
You are a Korean-English vocabulary normaliser.

Return ONE JSON object whose keys are **exactly** the surface tokens supplied
by the user (unchanged, including particles, punctuation, quotes).

For every key provide:
  "base"    — dictionary form (verbs/adjectives end in -다; nouns without particles)
  "meaning" — concise English gloss.
              • If the word is a verb, start with "to " (e.g. "to eat").
  "partOfSpeach: - classification of "base" based on their grammatical function and the roles they play within a sentence.

Return nothing but valid JSON.
""".strip()



def userInputProcess(input: str) -> List[str]:
    inputTokens = input.split(" ")

    Filtered_Tokens = []
    for word in inputTokens:

        stripped_word = word.strip()

        if stripped_word == " " or stripped_word == "\n" or stripped_word == "":
            continue
        Filtered_Tokens.append(stripped_word)

    return Filtered_Tokens

def callLocalMachine_TranslationwContext(
        tokens: List[str],
        model: str = "gemma3:4b",
): #-> Dict[str, Dict[str, str]]:
    """Call Local LLM once and parse JSON."""

    message_user = "Surface tokens (one per line):\n" + "\n".join(tokens)

    # print(message_user)

    url = "http://localhost:11434/api/generate"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "system": PROMPT_TEMPLATE,
        # "system": "What is the law of graviry?",
        "prompt": message_user,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0,
        },
    }

    response = requests.post(url, headers = headers, data = json.dumps(data))

    if response.status_code == 200:
        response_text = response.text
        data = json.loads(response_text)
        actual_response = data["response"]
        print(actual_response)
    else:
        print("Error: ", response.status_code, response.text)
    
    return json.loads(actual_response)


def callOpenAI_TranslationwContext(
    client: OpenAI,
    tokens: List[str],
    model: str = "gpt-4.1-mini",
) -> Dict[str, Dict[str, str]]:
    """Call OpenAI once and parse JSON."""
    message_user = "Surface tokens (one per line):\n" + "\n".join(tokens)
    rsp = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": PROMPT_TEMPLATE},
            {"role": "user", "content": message_user},
        ],
    )

    return json.loads(rsp.choices[0].message.content)

if __name__ == "__main__":
    User_Input = """
    막차는 좀처럼 오지 않았다

    대합실 밖에는 밤새 송이눈이 쌓이고

    흰 보라 수수꽃 눈시린 유리창마다

    톱밥난로가 지펴지고 있었다

    그믐처럼 몇은 졸고

    몇은 감기에 쿨럭이고

    그리웠던 순간들을 생각하며 나는

    한줌의 톱밥을 불빛 속에 던져 주었다



    내면 깊숙이 할 말들은 가득해도

    청색의 손 바닥을 불빛 속에 적셔두고

    모두들 아무 말도 하지 않았다



    산다는 것이 때론 술에 취한 듯

    한 두릅의 굴비 한 광주리의 사과를

    만지작 거리며 귀향하는 기분으로

    침묵해야 한다는 것을

    모두들 알고 있었다



    오래 앓은 기침소리와

    쓴약 같은 입술담배 연기 속에서

    싸륵싸륵 눈꽃은 쌓이고

    그래 지금은 모두들

    눈꽃의 화음에 귀를 적신다



    자정 넘으면

    낯설음도 뼈아픔도 다 설원인데

    단풍잎 같은 몇 잎의 차장을 달고

    밤열차는 또 어디로 흘러가는지



    그리웠던 순간들을 호명하며 나는

    한줌의 눈물을 불빛 속에 던져주었다
    """

    print(userInputProcess(User_Input))
    # callLocalMachine_TranslationwContext(tokens= userInputProcess)
    # callLocalMachine_TranslationwContext(tokens=User_Input)