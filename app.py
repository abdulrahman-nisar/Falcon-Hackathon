from flask import Flask, render_template, request
from ai71 import AI71
import re

questions_store = []        #Store the list of all questions
answers = []                #Store the list of answers

app = Flask(__name__)
AI71_API_KEY = "ai71-api-bd8523eb-052d-478a-9967-fa02af9c98af"

def generate_quiz(topic, num_questions):
    """Create the quiz"""
    
    #Declaring global variable
    global questions_store
    global answers
    
    
    questions = []  #store AI genrated text
    
    prompt = f"Generate {num_questions} quiz questions on the topic: {topic} with choices"
    question_text = ""
    
    #Getting quiz questions with choices
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

    #Get answers from the AI
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

    # Remove the first three characters from each answer
    quiz_answers = [s[3:] for s in quiz_answers]
    
    
    # Print or use the answers as needed
    print("\n")
    for answer in quiz_answers:
        print(f"{answer}")

    #parsing the AI text to seperate question and choices
    for block in question_blocks[1:]:  # skip the first empty split
        lines = block.strip().split('\n')   #Break each line into question and choices
        question_text = lines[0].strip()
        choices = []
        for line in lines[1:]:
            choices.append(line.strip())
        
        questions.append({"text": question_text, "choices": choices})   #stored whole quiz in questions in form of dictionary
    
    questions_store = [s["text"] for s in questions]    #Filling global variable
    answers = quiz_answers
   
    return questions

@app.route('/')
def home():
    """Starting web page"""
    return render_template('home.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Create the quiz page"""
    global questions
    topic = request.form['topic']
    num_questions = request.form['num_questions']
    questions = generate_quiz(topic, num_questions)
    return render_template('quiz.html', topic=topic, questions=questions)




@app.route('/submit', methods=['POST'])
def submit():
    """Show result"""
    global questions
    global answers

    # Clean user answers
    user_answers = {
        f"question_{index}": re.sub(r'^[a-dA-D]\.\s*', '', value) for index, (key, value) in enumerate(request.form.items())
    }

    score = 0  # User score
    total_score = len(questions)
    
    # Clean correct answers
    stripped_answers = [re.sub(r'^[a-d]\)\s*', '', answer) for answer in answers]

    # Calculate score
    for key, value in user_answers.items():
        question_index = int(key.split('_')[1])
        if value == stripped_answers[question_index]:
            score += 1
        print(f"User answer: {value}, Correct answer: {stripped_answers[question_index]}")

    # Prepare cleaned data for template
    cleaned_questions = [
        {
            'text': q['text'],
            'choices': [re.sub(r'^[a-d]\)\s*', '', choice) for choice in q['choices']]
        }
        for q in questions
    ]

    print(f"Stripped answers: {stripped_answers}")
    return render_template(
        'result.html',
        score=score,
        total_score=total_score,
        questions=cleaned_questions,
        user_answers=user_answers,
        answers=stripped_answers
    )


if __name__ == '__main__':
    app.run(debug=True)
