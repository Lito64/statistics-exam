import streamlit as st
import random
import time
from datetime import datetime
import requests
import json

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Final Scenarios - Statistics Exam",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CONFIGURATION - CHANGE THESE VALUES
# ============================================================

# Google Apps Script URL (you'll get this after setup)
GOOGLE_SCRIPT_URL = "YOUR_GOOGLE_SCRIPT_URL_HERE"

# Exam settings
EXAM_NAME = "Final Scenarios"
EXAM_ID = "STATS_FINAL_001"
TOTAL_QUESTIONS = 16

# ============================================================
# CUSTOM CSS STYLING
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary-color: #4a6fa5;
        --secondary-color: #6c9bcf;
        --accent-color: #87ceeb;
        --success-color: #4caf50;
        --danger-color: #f44336;
        --warning-color: #ff9800;
    }
    
    .main-header {
        background-color: #4a6fa5;
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 28px;
    }
    
    .main-header p {
        margin: 8px 0 0 0;
        opacity: 0.9;
    }
    
    .question-box {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        border-left: 4px solid #4a6fa5;
        min-height: 100px;
        font-size: 16px;
        line-height: 1.8;
    }
    
    .progress-box {
        background-color: #f0f0f0;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: 600;
        color: #4a6fa5;
        margin-bottom: 20px;
    }
    
    .score-display {
        background-color: #4a6fa5;
        color: white;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }
    
    .score-display h2 {
        margin: 0 0 15px 0;
        font-size: 24px;
    }
    
    .score-percentage {
        font-size: 64px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .result-item {
        background-color: #f9f9f9;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 8px;
        border-left: 4px solid #4a6fa5;
    }
    
    .result-correct {
        border-left-color: #4caf50 !important;
    }
    
    .result-incorrect {
        border-left-color: #f44336 !important;
    }
    
    .answer-correct {
        color: #4caf50;
        font-weight: 600;
    }
    
    .answer-incorrect {
        color: #f44336;
        font-weight: 600;
    }
    
    .submission-success {
        background-color: rgba(76, 175, 80, 0.1);
        border: 2px solid #4caf50;
        color: #4caf50;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 15px 0;
    }
    
    .submission-error {
        background-color: rgba(244, 67, 54, 0.1);
        border: 2px solid #f44336;
        color: #f44336;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 15px 0;
    }
    
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        color: #e65100;
        font-weight: 500;
    }
    
    .stats-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    
    .stats-table th {
        background-color: #4a6fa5;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }
    
    .stats-table td {
        padding: 12px;
        border-bottom: 1px solid #ddd;
    }
    
    .stats-table tr:nth-child(even) {
        background-color: #f5f5f5;
    }
    
    .stats-table tr:hover {
        background-color: #e3f2fd;
    }
    
    .start-container {
        text-align: center;
        padding: 40px 20px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .timer-display {
        background-color: #e3f2fd;
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: 600;
        color: #4a6fa5;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA - STATISTICAL TESTS AND SCENARIOS
# ============================================================

STATISTICAL_TESTS = [
    {"name": "Confidence Interval - Single Proportion", "variables": "One categorical variable (binary)", "whenToUse": "Estimate a population proportion with uncertainty"},
    {"name": "Confidence Interval - Single Mean", "variables": "One numerical variable", "whenToUse": "Estimate a population mean with uncertainty"},
    {"name": "Confidence Interval - Two Proportions (Independent)", "variables": "One categorical variable (binary) + one grouping variable", "whenToUse": "Estimate the difference between two population proportions with uncertainty"},
    {"name": "Confidence Interval - Two Means (Independent)", "variables": "One numerical variable + one grouping variable", "whenToUse": "Estimate the difference between two population means with uncertainty"},
    {"name": "Confidence Interval - Two Means (Paired)", "variables": "One numerical variable measured twice (paired/dependent)", "whenToUse": "Estimate the mean difference between paired observations with uncertainty"},
    {"name": "Hypothesis Test - One-Sample Proportion", "variables": "One categorical variable (binary)", "whenToUse": "Test if a population proportion differs from a specific value"},
    {"name": "Hypothesis Test - One-Sample Mean (t-Test)", "variables": "One numerical variable", "whenToUse": "Test if a population mean differs from a specific value"},
    {"name": "Hypothesis Test - Two-Sample Proportions (Independent)", "variables": "One categorical variable (binary) + one grouping variable", "whenToUse": "Test if two population proportions are significantly different"},
    {"name": "Hypothesis Test - Two-Sample Means (Independent t-Test)", "variables": "One numerical variable + one grouping variable", "whenToUse": "Test if two population means are significantly different"},
    {"name": "Hypothesis Test - Paired t-Test", "variables": "One numerical variable measured twice (paired/dependent)", "whenToUse": "Test if the mean difference between paired observations is significantly different from zero"},
    {"name": "Chi-Square Test of Independence", "variables": "Two categorical variables", "whenToUse": "Test if two categorical variables are independent"},
    {"name": "Chi-Square Test of Homogeneity", "variables": "One categorical variable + one grouping variable", "whenToUse": "Test if the distribution of a categorical variable is the same across multiple groups"},
    {"name": "Chi-Square Goodness-of-Fit Test", "variables": "One categorical variable (multiple categories)", "whenToUse": "Test if observed frequencies match expected frequencies (equal or unequal)"},
    {"name": "One-Way ANOVA", "variables": "One numerical variable + one categorical grouping variable (3+ groups)", "whenToUse": "Test if means are equal across three or more independent groups"},
    {"name": "Pearson Correlation", "variables": "Two numerical variables", "whenToUse": "Measure the strength and direction of the linear relationship between two numerical variables"},
    {"name": "Simple Linear Regression", "variables": "Two numerical variables (one predictor, one response)", "whenToUse": "Predict one numerical variable from another numerical variable"}
]

NUMERICAL_VARIABLES = [
    "blood pressure (mmHg)", "body weight (kg)", "height (cm)", "age (years)",
    "income (dollars)", "test score (points)", "reaction time (ms)", "heart rate (bpm)",
    "temperature (°F)", "distance (miles)", "sleep duration (hours)", "exercise time (minutes)",
    "sales revenue (dollars)", "customer satisfaction (1-10 scale)", "productivity score (points)"
]

CATEGORICAL_VARIABLES = [
    "gender (male, female)", "treatment group (treatment, control)", "smoking status (smoker, non-smoker)",
    "education level (high school, college, graduate)", "political affiliation (Democrat, Republican, Independent)",
    "employment status (employed, unemployed)", "marital status (married, single, divorced)",
    "product preference (Product A, Product B)", "disease status (diseased, healthy)",
    "age group (young, middle-aged, elderly)"
]

SCENARIO_TEMPLATES = [
    # CONFIDENCE INTERVALS
    {
        "test": "Confidence Interval - Single Proportion",
        "scenarios": [
            "A health organization surveys [SAMPLE_SIZE] adults and wants to estimate the proportion of people who [BINARY_CATEGORICAL] in the population with a measure of uncertainty. What statistical method should be used?",
            "A company surveys [SAMPLE_SIZE] customers and wants to estimate the percentage who are satisfied with their service, including a margin of error. What statistical approach is appropriate?",
            "A political pollster surveys [SAMPLE_SIZE] voters and wants to estimate the proportion who support a particular candidate, with a confidence interval. What method should they use?",
            "A researcher samples [SAMPLE_SIZE] students and wants to estimate the proportion who prefer online learning, including uncertainty bounds. What statistical technique is appropriate?",
            "A quality control manager inspects [SAMPLE_SIZE] products and wants to estimate the defect rate with a confidence interval. What method should be used?"
        ]
    },
    {
        "test": "Confidence Interval - Single Mean",
        "scenarios": [
            "A nutritionist measures the [NUMERICAL] of [SAMPLE_SIZE] individuals and wants to estimate the average for the population with uncertainty. What statistical method should be used?",
            "A researcher collects [NUMERICAL] data from [SAMPLE_SIZE] participants and wants to create an interval estimate for the population mean. What approach is appropriate?",
            "A company measures [NUMERICAL] for [SAMPLE_SIZE] employees and wants to estimate the average with a margin of error. What statistical technique should they use?",
            "An environmental scientist measures [NUMERICAL] at [SAMPLE_SIZE] locations and wants to estimate the overall average with confidence bounds. What method is appropriate?",
            "A medical researcher measures [NUMERICAL] in [SAMPLE_SIZE] patients and wants to estimate the population mean with uncertainty. What statistical approach should be used?"
        ]
    },
    {
        "test": "Confidence Interval - Two Proportions (Independent)",
        "scenarios": [
            "A researcher wants to estimate the difference in the proportion of people who [BINARY_CATEGORICAL] between two cities, with [SAMPLE_SIZE1] surveyed in city 1 and [SAMPLE_SIZE2] in city 2. They want an interval estimate for the difference. What statistical method should be used?",
            "A company wants to estimate the difference in customer satisfaction rates between two store locations with uncertainty. They survey [SAMPLE_SIZE1] customers at location 1 and [SAMPLE_SIZE2] at location 2. What approach is appropriate?",
            "A medical researcher wants to estimate the difference in recovery rates between a treatment group ([SAMPLE_SIZE1] patients) and a control group ([SAMPLE_SIZE2] patients) with a confidence interval. What statistical method should be used?",
            "An educator wants to estimate the difference in pass rates between two different teaching methods with uncertainty. They have [SAMPLE_SIZE1] students in method 1 and [SAMPLE_SIZE2] in method 2. What statistical technique is appropriate?",
            "A political analyst wants to estimate the difference in support rates for a policy between two regions with confidence bounds. They sample [SAMPLE_SIZE1] voters in region 1 and [SAMPLE_SIZE2] in region 2. What method should they use?"
        ]
    },
    {
        "test": "Confidence Interval - Two Means (Independent)",
        "scenarios": [
            "A researcher wants to estimate the difference in average [NUMERICAL] between two independent groups with [SAMPLE_SIZE1] in group 1 and [SAMPLE_SIZE2] in group 2, including uncertainty. What statistical method should be used?",
            "A company wants to estimate the difference in average [NUMERICAL] between two departments with a confidence interval. They have [SAMPLE_SIZE1] employees in department 1 and [SAMPLE_SIZE2] in department 2. What approach is appropriate?",
            "An agricultural scientist wants to estimate the difference in average crop yield between two fertilizer types with uncertainty. They have [SAMPLE_SIZE1] plots with fertilizer 1 and [SAMPLE_SIZE2] with fertilizer 2. What method should they use?",
            "A medical researcher wants to estimate the difference in average [NUMERICAL] between a treatment group ([SAMPLE_SIZE1] patients) and a control group ([SAMPLE_SIZE2] patients) with confidence bounds. What statistical technique should be used?",
            "A sports scientist wants to estimate the difference in average performance between two training programs with a margin of error. They have [SAMPLE_SIZE1] athletes in program 1 and [SAMPLE_SIZE2] in program 2. What method is appropriate?"
        ]
    },
    {
        "test": "Confidence Interval - Two Means (Paired)",
        "scenarios": [
            "A researcher measures [NUMERICAL] in [SAMPLE_SIZE] individuals before and after an intervention and wants to estimate the average change with uncertainty. What statistical method should be used?",
            "A fitness trainer measures [NUMERICAL] in [SAMPLE_SIZE] clients at the beginning and end of a program and wants to create a confidence interval for the mean difference. What method is appropriate?",
            "A teacher measures [NUMERICAL] in [SAMPLE_SIZE] students before and after a training session and wants to estimate the average improvement with confidence bounds. What statistical technique should be used?",
            "A medical researcher measures [NUMERICAL] in [SAMPLE_SIZE] patients before and after treatment and wants to estimate the mean change with uncertainty. What method should be used?",
            "A psychologist measures [NUMERICAL] in [SAMPLE_SIZE] participants at two time points and wants to estimate the average difference with a confidence interval. What statistical approach is appropriate?"
        ]
    },
    # HYPOTHESIS TESTS
    {
        "test": "Hypothesis Test - One-Sample Proportion",
        "scenarios": [
            "A researcher wants to test if the proportion of people who [BINARY_CATEGORICAL] differs from [PERCENTAGE]%. They survey [SAMPLE_SIZE] individuals. What statistical test should be used?",
            "A quality control manager claims that the defect rate is [PERCENTAGE]%. They inspect [SAMPLE_SIZE] products to test this claim. What test is appropriate?",
            "A company wants to test if customer satisfaction exceeds [PERCENTAGE]%. They survey [SAMPLE_SIZE] customers. What statistical test should they use?",
            "A health official wants to determine if vaccination rates differ from the national average of [PERCENTAGE]%. They sample [SAMPLE_SIZE] individuals. What test should be conducted?",
            "A teacher wants to test if the pass rate in their class differs from [PERCENTAGE]%. They have data from [SAMPLE_SIZE] students. What statistical test is appropriate?"
        ]
    },
    {
        "test": "Hypothesis Test - One-Sample Mean (t-Test)",
        "scenarios": [
            "A researcher wants to determine if the average [NUMERICAL] in a sample of [SAMPLE_SIZE] individuals differs significantly from [VALUE]. What statistical test should be used?",
            "A company wants to test if their average [NUMERICAL] differs from the industry standard of [VALUE]. They have data from [SAMPLE_SIZE] observations. What test is appropriate?",
            "A nutritionist wants to determine if the average [NUMERICAL] of [SAMPLE_SIZE] participants differs from the recommended value of [VALUE]. What statistical test should be conducted?",
            "A quality control manager wants to test if the average [NUMERICAL] differs from the target value of [VALUE]. They have [SAMPLE_SIZE] measurements. What test should they use?",
            "A medical researcher wants to determine if the average [NUMERICAL] in [SAMPLE_SIZE] patients differs significantly from the normal value of [VALUE]. What statistical test is appropriate?"
        ]
    },
    {
        "test": "Hypothesis Test - Two-Sample Proportions (Independent)",
        "scenarios": [
            "A researcher wants to test if the proportion of people who [BINARY_CATEGORICAL] differs between two cities. They survey [SAMPLE_SIZE1] in city 1 and [SAMPLE_SIZE2] in city 2. What statistical test should be used?",
            "A company wants to determine if customer satisfaction rates differ between two store locations. They survey [SAMPLE_SIZE1] customers at location 1 and [SAMPLE_SIZE2] at location 2. What test is appropriate?",
            "A medical researcher wants to test if recovery rates differ between a treatment group ([SAMPLE_SIZE1] patients) and a control group ([SAMPLE_SIZE2] patients). What statistical test should be used?",
            "An educator wants to test if pass rates differ between two teaching methods with [SAMPLE_SIZE1] students in method 1 and [SAMPLE_SIZE2] in method 2. What test is appropriate?",
            "A political analyst wants to test if support rates for a policy differ between two regions with [SAMPLE_SIZE1] voters in region 1 and [SAMPLE_SIZE2] in region 2. What statistical test should they use?"
        ]
    },
    {
        "test": "Hypothesis Test - Two-Sample Means (Independent t-Test)",
        "scenarios": [
            "A researcher wants to test if the average [NUMERICAL] differs between two independent groups with [SAMPLE_SIZE1] in group 1 and [SAMPLE_SIZE2] in group 2. What statistical test should be used?",
            "A company wants to determine if average [NUMERICAL] differs between two departments with [SAMPLE_SIZE1] employees in department 1 and [SAMPLE_SIZE2] in department 2. What test is appropriate?",
            "An agricultural scientist wants to test if average crop yield differs between two fertilizer types with [SAMPLE_SIZE1] plots using fertilizer 1 and [SAMPLE_SIZE2] using fertilizer 2. What statistical test should be used?",
            "A medical researcher wants to test if average [NUMERICAL] differs between a treatment group ([SAMPLE_SIZE1] patients) and a control group ([SAMPLE_SIZE2] patients). What test is appropriate?",
            "A sports scientist wants to test if average performance differs between two training programs with [SAMPLE_SIZE1] athletes in program 1 and [SAMPLE_SIZE2] in program 2. What statistical test should they use?"
        ]
    },
    {
        "test": "Hypothesis Test - Paired t-Test",
        "scenarios": [
            "A researcher measures [NUMERICAL] in [SAMPLE_SIZE] individuals before and after an intervention and wants to test if there is a significant change. What statistical test should be used?",
            "A fitness trainer measures [NUMERICAL] in [SAMPLE_SIZE] clients at the beginning and end of a program and wants to test if there is significant improvement. What test is appropriate?",
            "A teacher measures [NUMERICAL] in [SAMPLE_SIZE] students before and after a training session and wants to determine if the training had a significant effect. What statistical test should be used?",
            "A medical researcher measures [NUMERICAL] in [SAMPLE_SIZE] patients before and after treatment and wants to test if the treatment caused a significant change. What test should be conducted?",
            "A psychologist measures [NUMERICAL] in [SAMPLE_SIZE] participants at two time points and wants to test if there is a significant difference. What statistical test is appropriate?"
        ]
    },
    # CHI-SQUARE TESTS
    {
        "test": "Chi-Square Test of Independence",
        "scenarios": [
            "A researcher wants to determine if there is a relationship between [CATEGORICAL] and [CATEGORICAL2] in a sample of [SAMPLE_SIZE] individuals. What statistical test should be used?",
            "A marketing analyst wants to test if product preference is related to age group among [SAMPLE_SIZE] customers. What test is appropriate?",
            "A health researcher wants to determine if smoking status is associated with disease status in [SAMPLE_SIZE] patients. What statistical test should be used?",
            "A sociologist wants to test if political affiliation is related to education level among [SAMPLE_SIZE] voters. What test should be conducted?",
            "A company wants to determine if customer satisfaction level is associated with region among [SAMPLE_SIZE] customers. What statistical test is appropriate?"
        ]
    },
    {
        "test": "Chi-Square Test of Homogeneity",
        "scenarios": [
            "A researcher wants to test if the distribution of [CATEGORICAL] is the same across three different cities. They sample [SAMPLE_SIZE1] from city 1, [SAMPLE_SIZE2] from city 2, and [SAMPLE_SIZE3] from city 3. What statistical test should be used?",
            "A company wants to determine if customer satisfaction distribution is the same across four store locations. They survey customers at each location. What test is appropriate?",
            "A health official wants to test if the distribution of vaccination status is the same across three age groups. What statistical test should be used?",
            "An educator wants to determine if the distribution of grades is the same across three different schools. What test should be conducted?",
            "A political analyst wants to test if the distribution of political preferences is the same across four regions. What statistical test is appropriate?"
        ]
    },
    {
        "test": "Chi-Square Goodness-of-Fit Test",
        "scenarios": [
            "A researcher wants to test if the observed distribution of [CATEGORICAL] matches an expected distribution in a sample of [SAMPLE_SIZE] individuals. What statistical test should be used?",
            "A quality control manager wants to test if defects are equally distributed across five production lines. They inspect [SAMPLE_SIZE] products. What test is appropriate?",
            "A geneticist wants to test if the observed phenotype ratios match the expected Mendelian ratios in [SAMPLE_SIZE] offspring. What statistical test should be used?",
            "A marketing analyst wants to test if customer visits are equally distributed across the seven days of the week based on [SAMPLE_SIZE] observations. What test should be conducted?",
            "A researcher wants to test if responses follow a uniform distribution across four categories among [SAMPLE_SIZE] participants. What statistical test is appropriate?"
        ]
    },
    # ANOVA
    {
        "test": "One-Way ANOVA",
        "scenarios": [
            "A researcher wants to test if the average [NUMERICAL] differs among four independent groups with different sample sizes. What statistical test should be used?",
            "A company wants to determine if average [NUMERICAL] differs among employees from five different departments. What test is appropriate?",
            "An agricultural scientist wants to test if average crop yield differs among three fertilizer types. What statistical test should be used?",
            "A medical researcher wants to test if average [NUMERICAL] differs among patients receiving four different treatments. What test should be conducted?",
            "An educator wants to determine if average test scores differ among students from three different schools. What statistical test is appropriate?"
        ]
    },
    # CORRELATION
    {
        "test": "Pearson Correlation",
        "scenarios": [
            "A researcher wants to measure the strength and direction of the linear relationship between [NUMERICAL] and [NUMERICAL2] in [SAMPLE_SIZE] individuals. What statistical method should be used?",
            "A health researcher wants to determine how strongly [NUMERICAL] is linearly related to [NUMERICAL2] among [SAMPLE_SIZE] patients. What method is appropriate?",
            "An economist wants to measure the linear association between income and spending among [SAMPLE_SIZE] households. What statistical technique should be used?",
            "A psychologist wants to quantify the linear relationship between stress levels and sleep quality in [SAMPLE_SIZE] participants. What method should be used?",
            "An environmental scientist wants to measure how strongly temperature is linearly related to pollution levels across [SAMPLE_SIZE] cities. What statistical approach is appropriate?"
        ]
    },
    # REGRESSION
    {
        "test": "Simple Linear Regression",
        "scenarios": [
            "A researcher wants to predict [NUMERICAL] based on [NUMERICAL2] using data from [SAMPLE_SIZE] individuals. What statistical method should be used?",
            "A company wants to create a model to predict sales based on advertising spending. They have [SAMPLE_SIZE] data points. What technique should they use?",
            "A medical researcher wants to predict patient recovery time based on age. They have measurements from [SAMPLE_SIZE] patients. What method should be used?",
            "An environmental scientist wants to create a predictive model for pollution levels based on traffic volume using [SAMPLE_SIZE] observations. What statistical approach is appropriate?",
            "An educator wants to predict final exam scores based on homework completion rates for [SAMPLE_SIZE] students. What method should they use?"
        ]
    }
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def replace_placeholders(text):
    """Replace placeholders in scenario text with random values."""
    
    # Binary categorical
    while '[BINARY_CATEGORICAL]' in text:
        cat_var = random.choice(CATEGORICAL_VARIABLES)
        parts = cat_var.split('(')[1].split(')')[0].split(', ')
        replacement = f"prefer {parts[0]} over {parts[1]}"
        text = text.replace('[BINARY_CATEGORICAL]', replacement, 1)
    
    # Categorical
    while '[CATEGORICAL]' in text:
        cat_var = random.choice(CATEGORICAL_VARIABLES).split(' (')[0]
        text = text.replace('[CATEGORICAL]', cat_var, 1)
    
    while '[CATEGORICAL2]' in text:
        cat_var = random.choice(CATEGORICAL_VARIABLES).split(' (')[0]
        text = text.replace('[CATEGORICAL2]', cat_var, 1)
    
    # Numerical
    while '[NUMERICAL]' in text:
        num_var = random.choice(NUMERICAL_VARIABLES)
        text = text.replace('[NUMERICAL]', num_var, 1)
    
    while '[NUMERICAL2]' in text:
        num_var = random.choice(NUMERICAL_VARIABLES)
        text = text.replace('[NUMERICAL2]', num_var, 1)
    
    # Sample sizes
    while '[SAMPLE_SIZE]' in text:
        text = text.replace('[SAMPLE_SIZE]', str(random.randint(30, 500)), 1)
    
    while '[SAMPLE_SIZE1]' in text:
        text = text.replace('[SAMPLE_SIZE1]', str(random.randint(30, 300)), 1)
    
    while '[SAMPLE_SIZE2]' in text:
        text = text.replace('[SAMPLE_SIZE2]', str(random.randint(30, 300)), 1)
    
    while '[SAMPLE_SIZE3]' in text:
        text = text.replace('[SAMPLE_SIZE3]', str(random.randint(30, 300)), 1)
    
    # Percentage and value
    while '[PERCENTAGE]' in text:
        text = text.replace('[PERCENTAGE]', str(random.randint(10, 90)), 1)
    
    while '[VALUE]' in text:
        text = text.replace('[VALUE]', str(random.randint(10, 100)), 1)
    
    return text

def generate_quiz_questions():
    """Generate 16 random questions, one from each test type."""
    questions = []
    
    for template in SCENARIO_TEMPLATES:
        # Pick random scenario from this test's templates
        scenario_text = random.choice(template['scenarios'])
        scenario_text = replace_placeholders(scenario_text)
        correct_answer = template['test']
        
        # Generate 3 incorrect options
        incorrect_tests = [t['name'] for t in STATISTICAL_TESTS if t['name'] != correct_answer]
        incorrect_options = random.sample(incorrect_tests, 3)
        
        # Combine and shuffle options
        all_options = [correct_answer] + incorrect_options
        random.shuffle(all_options)
        
        questions.append({
            'scenario': scenario_text,
            'options': all_options,
            'correct_answer': correct_answer,
            'student_answer': None
        })
    
    # Shuffle questions
    random.shuffle(questions)
    return questions

def submit_to_google_sheets(data):
    """Submit exam results to Google Sheets."""
    try:
        response = requests.post(
            GOOGLE_SCRIPT_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        return True
    except Exception as e:
        st.error(f"Submission error: {str(e)}")
        return False

def format_time(seconds):
    """Format seconds into mm:ss format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if 'exam_started' not in st.session_state:
    st.session_state.exam_started = False
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# ============================================================
# MAIN HEADER
# ============================================================

st.markdown("""
<div class="main-header">
    <h1>📝 Final Scenarios</h1>
    <p>Statistical Test Identification Exam</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MAIN APPLICATION
# ============================================================

# Create tabs
tab_quiz, tab_reference = st.tabs(["📝 Exam", "📊 Reference Table"])

# ============================================================
# REFERENCE TABLE TAB
# ============================================================

with tab_reference:
    st.markdown("### Statistical Tests Reference Table")
    
    table_html = """
    <table class="stats-table">
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Variables</th>
                <th>When to Use</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for test in STATISTICAL_TESTS:
        table_html += f"""
        <tr>
            <td><strong>{test['name']}</strong></td>
            <td>{test['variables']}</td>
            <td>{test['whenToUse']}</td>
        </tr>
        """
    
    table_html += "</tbody></table>"
    
    st.markdown(table_html, unsafe_allow_html=True)

# ============================================================
# EXAM TAB
# ============================================================

with tab_quiz:
    
    # ----- START SCREEN -----
    if not st.session_state.exam_started and not st.session_state.exam_submitted:
        st.markdown("""
        <div class="start-container">
            <h2>📝 Final Scenarios Exam</h2>
            <p style="font-size: 18px; margin: 20px 0;">This exam contains <strong>16 questions</strong>, one from each statistical test.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Important:</strong> You only get ONE attempt at this exam! Make sure you're ready before starting.
        </div>
        """, unsafe_allow_html=True)
        
        student_name = st.text_input("Enter your full name:", placeholder="John Smith", key="name_input")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Exam", type="primary", use_container_width=True):
                if student_name.strip():
                    st.session_state.student_name = student_name.strip()
                    st.session_state.questions = generate_quiz_questions()
                    st.session_state.exam_started = True
                    st.session_state.start_time = time.time()
                    st.session_state.current_question = 0
                    st.session_state.answers = {}
                    st.rerun()
                else:
                    st.error("Please enter your name to start the exam.")
    
    # ----- EXAM IN PROGRESS -----
    elif st.session_state.exam_started and not st.session_state.exam_submitted:
        
        # Progress indicator
        current_q = st.session_state.current_question
        total_q = len(st.session_state.questions)
        
        # Timer
        elapsed = time.time() - st.session_state.start_time
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<div class="progress-box">Question {current_q + 1} of {total_q}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="timer-display">⏱️ {format_time(elapsed)}</div>', unsafe_allow_html=True)
        
        # Progress bar
        st.progress((current_q + 1) / total_q)
        
        # Current question
        question = st.session_state.questions[current_q]
        
        st.markdown(f'<div class="question-box">{question["scenario"]}</div>', unsafe_allow_html=True)
        
        # Answer options
        st.markdown("**Select the appropriate statistical method:**")
        
        # Get previously selected answer for this question
        previous_answer = st.session_state.answers.get(current_q, None)
        
        # Radio buttons for options
        selected = st.radio(
            "Options:",
            question['options'],
            index=question['options'].index(previous_answer) if previous_answer in question['options'] else None,
            key=f"q_{current_q}",
            label_visibility="collapsed"
        )
        
        # Save answer
        if selected:
            st.session_state.answers[current_q] = selected
        
        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_q > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            # Show answered count
            answered = len(st.session_state.answers)
            st.markdown(f"<center>Answered: {answered}/{total_q}</center>", unsafe_allow_html=True)
        
        with col3:
            if current_q < total_q - 1:
                if st.button("Next ➡️", use_container_width=True):
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("📤 Submit Exam", type="primary", use_container_width=True):
                    # Check if all questions answered
                    if len(st.session_state.answers) < total_q:
                        unanswered = [i+1 for i in range(total_q) if i not in st.session_state.answers]
                        st.error(f"Please answer all questions. Unanswered: {unanswered}")
                    else:
                        st.session_state.exam_submitted = True
                        st.session_state.end_time = time.time()
                        st.rerun()
        
        # Question navigator
        st.markdown("---")
        st.markdown("**Question Navigator:** (click to jump)")
        
        nav_cols = st.columns(16)
        for i in range(total_q):
            with nav_cols[i]:
                is_answered = i in st.session_state.answers
                is_current = i == current_q
                
                btn_type = "primary" if is_current else ("secondary" if is_answered else "secondary")
                label = f"{'✓' if is_answered else ''}{i+1}"
                
                if st.button(label, key=f"nav_{i}", use_container_width=True):
                    st.session_state.current_question = i
                    st.rerun()
    
    # ----- RESULTS SCREEN -----
    elif st.session_state.exam_submitted:
        
        # Calculate score
        correct_count = 0
        right_answers = []
        wrong_answers = []
        
        for i, question in enumerate(st.session_state.questions):
            student_answer = st.session_state.answers.get(i, "")
            correct_answer = question['correct_answer']
            
            if student_answer == correct_answer:
                correct_count += 1
                right_answers.append(f"Q{i+1}")
            else:
                wrong_answers.append(f"Q{i+1}: Selected \"{student_answer}\" instead of \"{correct_answer}\"")
        
        percentage = round((correct_count / TOTAL_QUESTIONS) * 100)
        time_taken = st.session_state.end_time - st.session_state.start_time
        
        # Display score
        st.markdown(f"""
        <div class="score-display">
            <h2>Your Score</h2>
            <p style="font-size: 18px;">Student: {st.session_state.student_name}</p>
            <div class="score-percentage">{correct_count}/{TOTAL_QUESTIONS}</div>
            <p style="font-size: 28px; margin: 10px 0;">{percentage}%</p>
            <p style="font-size: 16px;">Time: {format_time(time_taken)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Submit to Google Sheets
        submission_data = {
            'studentName': st.session_state.student_name,
            'examName': EXAM_NAME,
            'examId': EXAM_ID,
            'score': correct_count,
            'totalQuestions': TOTAL_QUESTIONS,
            'percentage': percentage,
            'timeTaken': int(time_taken),
            'rightAnswers': ', '.join(right_answers),
            'wrongAnswers': '; '.join(wrong_answers),
            'timestamp': datetime.now().isoformat()
        }
        
        # Try to submit
        if GOOGLE_SCRIPT_URL != "YOUR_GOOGLE_SCRIPT_URL_HERE":
            with st.spinner("Submitting results..."):
                success = submit_to_google_sheets(submission_data)
            
            if success:
                st.markdown("""
                <div class="submission-success">
                    ✓ Your exam has been submitted successfully!
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="submission-error">
                    ⚠️ There was an issue submitting your exam. Please take a screenshot of your results.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="submission-error">
                ⚠️ Google Sheets not configured. Please take a screenshot of your results.
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed results
        st.markdown("---")
        st.markdown("### 📋 Detailed Results")
        
        for i, question in enumerate(st.session_state.questions):
            student_answer = st.session_state.answers.get(i, "No answer")
            correct_answer = question['correct_answer']
            is_correct = student_answer == correct_answer
            
            result_class = "result-correct" if is_correct else "result-incorrect"
            icon = "✓" if is_correct else "✗"
            
            st.markdown(f"""
            <div class="result-item {result_class}">
                <h4>Question {i+1} {icon}</h4>
                <p style="margin: 10px 0; line-height: 1.8;">{question['scenario']}</p>
                <p class="{'answer-correct' if is_correct else 'answer-incorrect'}">
                    Your Answer: {student_answer}
                </p>
                {'<p class="answer-correct">Correct Answer: ' + correct_answer + '</p>' if not is_correct else ''}
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 13px;">
    📝 Statistics Exam | Built with Streamlit
</div>
""", unsafe_allow_html=True)
