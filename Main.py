import json
import requests

# ========= 配置项 ========= #
JSON_FILE_PATH = "Questions.json"  # 本地 JSON 文件路径
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # 本地 Ollama 服务地址
OLLAMA_MODEL_NAME = "deepseek-r1:14b"  # 使用的模型名称，根据你的本地模型修改
# ========================= #

# 读取本地 JSON 问题库
def load_question_bank(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# 构建发送给 DeepSeek 模型的 prompt
def build_prompt(question, options, user_answer):
    prompt = f"你是一位严格但耐心的驾驶培训老师。\n\n"
    prompt += f"请判断学生回答是否正确并详细解析。\n\n"
    prompt += f"题目：{question}\n"
    for key, val in options.items():
        prompt += f"{key}. {val['text']}\n"
    selected_option = options.get(user_answer, {"text": "未知选项"})['text']
    prompt += f"\n学生选择了：{user_answer}. {selected_option}\n"
    prompt += f"请你根据正确答案与法规判断正误，并说明原因、提供法规引用和建议。"
    return prompt

# 向 Ollama 发送请求
def ask_deepseek(prompt):
    payload = {
        "model": OLLAMA_MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json().get("text", "").strip()
    except Exception as e:
        return f"❌ 请求失败：{e}"

# 主流程
def run_quiz():
    questions = load_question_bank(JSON_FILE_PATH)

    for idx, q in enumerate(questions, 1):
        question_text = q['question']['text']
        options = q['options']
        correct_option = q['answer_summary']['correct_option']

        print(f"\n📌 第{idx}题：{question_text}")
        for key, val in options.items():
            print(f"{key}. {val['text']}")

        user_answer = input("👉 请输入你的答案（A/B/C/D）：").strip().upper()
        prompt = build_prompt(question_text, options, user_answer)
        print("\n🤖 正在请教 DeepSeek 老师，请稍候...\n")
        reply = ask_deepseek(prompt)
        print("📚 DeepSeek 老师解析：\n")
        print(reply)
        print("-" * 80)

if __name__ == "__main__":
    run_quiz()
