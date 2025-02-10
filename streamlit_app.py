import random
import pandas as pd
import streamlit as st

# Load the dataset
file_path = "Lista Intrebari clasa D.xlsx"
try:
    xls = pd.ExcelFile(file_path, engine='openpyxl')
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
    "1.RND": 1,
    "2.Marinarie": 1,
    "3.Conducere si manevra": 1
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

# Initialize tracking of question statistics
if 'question_stats' not in st.session_state:
    # Load history if available
    history_columns = ['Times Asked', 'Correct Answers', 'Wrong Answers']
    for col in history_columns:
    if col not in df.columns:
        df[col] = 0
            df[col] = 0
        df[col] = 0

df = df.drop_duplicates(subset=['Question'])
history_columns = ['Times Asked', 'Correct Answers', 'Wrong Answers']
if 'question_stats' not in st.session_state:
    st.session_state.question_stats = {}
    for col in history_columns:
        if col not in df.columns:
            df[col] = 0
    df = df.drop_duplicates(subset=['Question'])
    st.session_state.question_stats = df.set_index('Question')[history_columns].to_dict(orient='index')

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0

if not st.session_state.quiz_started:
    if st.button("Start Quiz"):
        st.session_state.quiz_started = True
        st.session_state.questions = select_questions()
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.rerun()
else:
    questions = st.session_state.questions
    index = st.session_state.current_index
    
    if index < len(questions):
        q = questions[index]
        st.subheader(f"{index+1}. {q['Question']}")
        options = [q.get('Raspuns', 'N/A'), q.get('Raspuns 2', 'N/A'), q.get('Raspuns 3', 'N/A')]
        if f'options_{index}' not in st.session_state:
            st.session_state[f'options_{index}'] = options
        options = list(st.session_state[f'options_{index}'])
        
        user_answer = st.radio("Select your answer:", options, index=None, key=f"q{index}")
        st.session_state[f'answer_{index}'] = user_answer
        if st.button("Submit Answer", key=f"submit{index}"):
            # Track question appearance
            question_text = q['Question']
            if question_text not in st.session_state.question_stats:
                st.session_state.question_stats[question_text] = {'times_asked': 0, 'times_wrong': 0, 'correct_answers': 0}
            
            st.session_state.question_stats[question_text]['Times Asked'] += 1
            
            # Check correctness
            correct_answers = [q["Corect 1"], q["Corect 2"], q["Corect 3"]]
            correct_index = next((i for i, val in enumerate(correct_answers) if val == 1), None)
            
            if correct_index is not None and options[correct_index] == q.get(f'Raspuns {correct_index + 1}', 'N/A') and user_answer == q[f'Raspuns {correct_index + 1}']:
                st.session_state.question_stats[question_text]['Correct Answers'] += 1
                st.session_state.score += 1
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect! Correct answer was: {options[correct_index] if correct_index is not None else 'Unknown'}")
            
            st.session_state.current_index += 1
            st.rerun()
    else:
        if len(questions) > 0:
            st.success(f"Quiz Completed! Your Score: {st.session_state.score}/{len(questions)} ({(st.session_state.score/len(questions))*100:.2f}%)")
        else:
            st.success("Quiz Completed! No questions were available.")
        
        # Review Section with stats
        st.subheader("Review Your Answers")
        for idx, q in enumerate(st.session_state.questions):
            question_text = q['Question']
            options = st.session_state[f'options_{idx}']
            user_answer = st.session_state.get(f'answer_{idx}', "Not Answered")
            correct_answers = [q['Corect 1'], q['Corect 2'], q['Corect 3']]
            correct_index = correct_answers.index(1) if 1 in correct_answers else None
            correct_answer = options[correct_index] if correct_index is not None else "Unknown"
            
            st.write(f"**{idx+1}. {question_text}**")
            st.write(f"- **Your Answer:** {user_answer}")
            st.write(f"- ✅ **Correct Answer:** {correct_answer}")
            
            # Display tracking stats
            stats = st.session_state.question_stats.get(question_text, {'times_asked': 0, 'times_wrong': 0})
            st.write(f"- 📊 **Times Asked:** {stats.get('Times Asked', 0)}")
            st.write(f"- ✅ **Times Answered Correctly:** {stats.get('Correct Answers', 0)}")
            st.write(f"- ❌ **Times Answered Wrong:** {stats.get('Wrong Answers', 0)}")
            st.write("---")
        
        # Save updated history back to Excel
        history_df = pd.DataFrame.from_dict(st.session_state.question_stats, orient='index')
        for col in history_columns:
            if col in df.columns and col in history_df.columns:
                df[col] = history_df[col].reindex(df['Question']).fillna(0).astype(int)
        try:
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False)
        st.success("History successfully saved to Excel!")
        except Exception as e:
            st.error(f"Error saving history to Excel: {e}")
        
        # Review Section
        st.session_state.quiz_started = False

