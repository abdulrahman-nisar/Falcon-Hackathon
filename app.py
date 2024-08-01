from flask import Flask, render_template, request
from ai71 import AI71
import re

app = Flask(__name__)
AI71_API_KEY = "ai71-api-bd8523eb-052d-478a-9967-fa02af9c98af"

def generate_quiz(topic, num_questions):
    questions = []
    prompt = f"Generate {num_questions} quiz questions on the topic: {topic} with choices"
    question_text = ""
    
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            question_text += chunk.choices[0].delta.content
    
    print("DEBUG: Full response from AI71:")
    print(question_text)
    
    # Split the questions based on numbered pattern
    question_blocks = re.split(r'\d+\.', question_text)
    
    for block in question_blocks[1:]:  # skip the first empty split
        lines = block.strip().split('\n')
        question_text = lines[0].strip()
        choices = []
        for line in lines[1:]:
            choice_match = re.match(r'[a-d]\)', line.strip())
            if choice_match:
                choices.append(line.strip())
        questions.append({"text": question_text, "choices": choices})
    
    return questions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form['topic']
    num_questions = request.form['num_questions']
    questions = generate_quiz(topic, num_questions)
    return render_template('quiz.html', topic=topic, questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
