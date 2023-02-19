import os
import json
import re

import openai
from flask import Flask, redirect, render_template, request, url_for
from flask import send_file
from fpdf import FPDF
from PIL import Image
import pytesseract
import cv2
import re

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        # num_problems = request.form["num_problems"]
        problems = request.form["problems"]
        desired_avg = int(request.form["desired_avg"])
        num_questions = (request.form["num-questions"])
        question_averages = (request.form.getlist("question_averages")) #in a list format [avg_1, avg_2]
        question_averages = [eval(i) for i in question_averages]
        threshold = int(request.form["threshold"])

        # response = generate_prompt(problems, desired_avg, threshold)
        # Handle the input image
        gray_image = preprocess_image(problems)
        image_text = pytesseract.image_to_string(gray_image, lang='eng')
        print("IMAGE TEXT")
        print(image_text)
        response = generate_prompt(image_text, desired_avg, threshold, question_averages)
        output_file(response)
        
        return redirect(url_for("index", result = True))


    result = request.args.get("result")
    return render_template("index.html", result=result)

def preprocess_image(filename):
    image = cv2.imread(filename) #read original image
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #convert to grayscale
    return grayscale

# Returns a message to be sent to ChatGPT to make problem easier
def easier_problem_prompt(problem, scale):
    return f"Can you make this question: {problem}, easier by a factor of {scale}? Only respond with the easier question"

# Returns a message to be sent to ChatGPT to make problem harder
def harder_problem_prompt(problem, scale):
    return f"Can you make this question: {problem}, more difficult by a factor of {scale}? Only respond with the harder question"

# Updates a single problem if meets criteria
def update_problem(problem, question_avg, desired_avg, threshold, problems):
    diff_actual_desired = question_avg - desired_avg
    #if difference between average and desired average lesss than threshold, do nothing
    if abs(diff_actual_desired) < threshold:
        # print('do nothing')
        problems.append(problem)
    #if class average is too low, reduce difficulty of problem
    elif diff_actual_desired < 0:
        scale = diff_actual_desired/100 * (10 - 1)
        # print(f"decreasing difficulty by factor of {scale}")
        # print(f"Old problem: {problem['problem']}")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=easier_problem_prompt(problem, scale),
            temperature=0.5,
            max_tokens=1000
        )
        # print(f"Response: {response}")
        new_problem = response.choices[0].text.strip()
        print(f"New problem: {new_problem}")
        problems.append(new_problem)

    #if class average is too high, increase difficulty of problem
    elif diff_actual_desired >= 0:
        scale = diff_actual_desired/100 * (10 - 1)
        # print(f"increasing difficulty by factor of {scale}")
        # print(f"Old problem: {problem['problem']}")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=harder_problem_prompt(problem, scale),
            temperature=0.5,
            max_tokens=1000
        )
        # print(f"Response: {response}")
        # print(f"CHOICES TEXT: {response.choices[0].text}")
        new_problem = response.choices[0].text.strip()
        print(f"New problem: {new_problem}")
        problems.append(new_problem)
    else:
        print("something has gone wrong :(")


# Parses text from input image and if problem is farther than the threshold
# from the desired average, asks ChatGPT to create an easier/harder problem
def generate_prompt(image_text, desired_avg, threshold, class_avgs):
    new_problems = [] #list to hold new problems and old problems not modified
    old_problems = parse_problems(image_text)
    answers = parse_answers(image_text)

    for problem in old_problems:
        question_avg = class_avgs.pop()
        update_problem(problem, question_avg, desired_avg, threshold, new_problems)
        
    # return problems
    return new_problems

# Parses all the problems from the image text
def parse_problems(image_text):
    problems = re.findall(r'Problem \d+\)(.*?)Answer:', image_text, re.DOTALL)
    print(problems)
    return problems

def parse_answers(image_text):
    answers = re.findall(r'Answer: (.*)', image_text)
    print(answers)
    return answers

def output_file(problem_list):
    pdf = FPDF()
    # Add a page
    pdf.add_page()
    
    # set style and size of font
    # that you want in the pdf
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 15)
    
    # create a cell
    pdf.cell(200, 10, txt = "Output File",
            ln = 1, align = 'C')
    
    # add another cell
    pdf.cell(200, 10, txt = "Math Exam!",
            ln = 2, align = 'C')

    pdf.set_font("DejaVu", size = 10)

    for question in problem_list:
        pdf.multi_cell(180, 10, txt = question, align = 'L')

        pdf.cell(180, 40, txt = "",
        ln = 1, align = 'L')

    
    # save the pdf with name .pdf
    pdf.output("static/GFG.pdf") 
