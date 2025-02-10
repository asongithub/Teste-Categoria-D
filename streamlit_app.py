import random
import pandas as pd
import streamlit as st

# Load the dataset
file_path = "/mnt/data/Lista Intrebari clasa D.xlsx"
try:
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name="Sheet1")
except FileNotFoundError:
    st.error("Error: The dataset file was not found.")
    st.stop()
except Exception as e:
    st.error(f"Error loading the dataset: {e}")
    st.stop()

# Rename columns for consistency
df.rename(columns={"Categorie": "Category", "Intrebare": "Question"}, inplace=True)

# Define category selection rules
category_selection = {
    "1.RND": 10,
    "2.Marinarie": 7,
    "3.Conducere si manevra": 7,
    "4.Prim ajutor": 1,
    "5.Legislatie": 1,
}

def select_questions():
    """Randomly selects the required number of questions from each category."""
    selected_questions = []
    for category, count in category_selection.items():
        subset = df[df["Category"] == category]
        if len(subset) < count:
            count = len(subset)
        selected_questions.extend(subset.sample(n=count, random_state=random.randint(1, 1000)).to_dict("records"))
    random.shuffle(selected_questions)
    return selected_questions

# Streamlit App UI
st.title("Quiz Training System")

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
    st.session_state.questions = []
    st.session_state.current_index = 0
    st.session_state.score = 0

if not st.session_state.quiz_started:
    if st.button("Start Quiz"):
        st.session_state.quiz_started = True
        st.session_state.questions = select_questions()
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.experimental_rerun()
else:
    questions = st.session_state.questions
    index = st.session_state.current_index
    
    if index < len(questions):
        q = questions[index]
        st.subheader(f"{index+1}. {q['Question']}")
        options = [q.get('Raspuns', 'N/A'), q.get('Raspuns 2', 'N/A'), q.get('Raspuns 3', 'N/A')]
        random.shuffle(options)
        
        user_answer = st.radio("Select your answer:", options, key=f"q{index}")
        if st.button("Submit Answer", key=f"submit{index}"):
            correct_answers = [q["Corect 1"], q["Corect 2"], q["Corect 3"]]
            correct_index = correct_answers.index(1) if 1 in correct_answers else None
            
            if correct_index is not None and user_answer == options[correct_index]:
                st.session_state.score += 1
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect! Correct answer was: {options[correct_index] if correct_index is not None else 'Unknown'}")
            
            st.session_state.current_index += 1
            st.experimental_rerun()
    else:
        st.success(f"Quiz Completed! Your Score: {st.session_state.score}/{len(questions)} ({(st.session_state.score/len(questions))*100:.2f}%)")
        st.session_state.quiz_started = False
        if st.button("Restart Quiz"):
            st.experimental_rerun()
