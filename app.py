from flask import Flask, render_template, request
from ai71 import AI71

app = Flask(__name__)
AI71_API_KEY = "ai71-api-bd8523eb-052d-478a-9967-fa02af9c98af"

def generate_quiz(topic, num_questions):
    questions = []
    prompt = f"Generate {num_questions} quiz questions on the topic: {topic}"
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            questions.append(chunk.choices[0].delta.content)
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
