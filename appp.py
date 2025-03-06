import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()  # Remove extra spaces
    df.columns = df.columns.str.lower()  # Convert to lowercase
    return df

def categorize_experience(experience):
    try:
        experience = int(experience)
        if experience <= 1:
            return "Fresher"
        elif experience <= 3:
            return "Junior Developer"
        elif experience <= 6:
            return "Mid-Level Developer"
        else:
            return "Senior Developer"
    except ValueError:
        return "Other"

def calculate_score(row, age, location, job_title, experience, current_ctc):
    score = 0
    
    if 'age' in row and str(row['age']) == age:
        score += 10
    
    if 'location' in row and row['location'].lower() == location.lower():
        score += 15
    elif 'location' in row and location.lower() in row['location'].lower():
        score += 5
    
    if 'job title' in row and row['job title'].lower() == job_title.lower():
        score += 25
    
    if 'experience' in row:
        try:
            candidate_experience = int(row['experience'])
            required_experience = int(experience)
            if candidate_experience >= required_experience:
                score += 30
        except ValueError:
            pass
    
    if 'current_ctc' in row:
        try:
            candidate_ctc = float(row['current_ctc'])
            required_ctc = float(current_ctc)
            if candidate_ctc >= required_ctc:
                score += 20
        except ValueError:
            pass
    
    return score

def score_all_candidates(df, age, location, job_title, experience, current_ctc):
    required_columns = ['age', 'location', 'job title', 'experience', 'current_ctc']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Required columns missing: {', '.join(missing_columns)}. Please check the dataset.")
        return pd.DataFrame()
    
    df['experience_level'] = df['experience'].apply(categorize_experience)
    df['score'] = df.apply(lambda row: calculate_score(row, age, location, job_title, experience, current_ctc), axis=1)
    df = df.sort_values(by='score', ascending=False)
    
    return df

# Streamlit UI
st.title("📄 Resume Shortlisting System")

uploaded_file = st.file_uploader("Upload Resume Dataset (CSV)", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    age = st.text_input("Enter Age for Filtering:")
    location = st.text_input("Enter Location for Filtering:")
    job_title = st.text_input("Enter Required Job Title:")
    experience = st.text_input("Enter Required Experience:")
    current_ctc = st.text_input("Enter Minimum Current CTC:")
    
    if st.button("Show All Candidates with Scores"):
        scored_df = score_all_candidates(df, age, location, job_title, experience, current_ctc)
        
        if not scored_df.empty:
            st.write("### All Candidates with Scores:")
            st.dataframe(scored_df[['age', 'location', 'job title', 'experience_level', 'current_ctc', 'score']])
            
            # Generate Scatter Plot (Experience vs. Salary)
            st.write("### Scatter Plot: Experience vs. Current CTC")
            plt.figure(figsize=(10, 5))
            plt.scatter(scored_df['experience'], scored_df['current_ctc'], color='blue', alpha=0.5)
            plt.xlabel("Experience (Years)")
            plt.ylabel("Current CTC")
            plt.title("Experience vs. Current CTC")
            st.pyplot(plt)
            
            # Generate Bar Chart
            st.write("### Score Distribution of Candidates")
            plt.figure(figsize=(10, 5))
            plt.bar(scored_df.index, scored_df['score'], color='skyblue')
            plt.xlabel("Candidate Index")
            plt.ylabel("Score")
            plt.title("Scores of Candidates")
            st.pyplot(plt)
            
            # Generate Pie Chart for Location Distribution
            st.write("### Candidate Distribution by Location")
            location_counts = scored_df['location'].value_counts()
            plt.figure(figsize=(8, 8))
            plt.pie(location_counts, labels=location_counts.index, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
            plt.title("Distribution of Candidates by Location")
            st.pyplot(plt)
            
            # Generate Report by Experience Level
            st.write("### Candidates Categorized by Experience Level")
            experience_counts = scored_df['experience_level'].value_counts()
            st.write(experience_counts)
            
            plt.figure(figsize=(8, 6))
            plt.pie(experience_counts, labels=experience_counts.index, autopct='%1.1f%%', colors=plt.cm.Pastel1.colors)
            plt.title("Distribution of Candidates by Experience Level")
            st.pyplot(plt)
        else:
            st.warning("No candidates found.")