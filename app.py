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

    #Start of sirdard
    answers_prompt = "Provide the correct answers for the following quiz questions on the topic: {topic}. Each answer should match the choices provided previously.\n"
    for question in question_blocks:
        answers_prompt += f"{question}\n"

    # Generate answers
    answers = []
    answer_text = ""

    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": answers_prompt},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            answer_text += chunk.choices[0].delta.content

    # Parse the generated answers into a list
    quiz_answers = answer_text.strip().split('\n')

    # Print or use the answers as needed
    print("\n")
    for i, answer in enumerate(quiz_answers, start=1):
        print(f"{answer}")


    #End of sirdard
    
    for block in question_blocks[1:]:  # skip the first empty split
        lines = block.strip().split('\n')
        question_text = lines[0].strip()
        choices = []
        for line in lines[1:]:
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
