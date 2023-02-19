import os
import json

import openai
from flask import Flask, redirect, render_template, request, url_for
from fpdf import FPDF

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        # num_problems = request.form["num_problems"]
        problems = request.form["problems"]
        desired_avg = int(request.form["desired_avg"])
        threshold = int(request.form["threshold"])
        response = generate_prompt(problems, desired_avg, threshold),
        pdf = output_file(response)
        
        # return redirect(url_for("index", result=response.choices[0].text))
        return redirect(url_for("index"))


    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(problems, desired_avg, threshold):
    file = open('problems.json')
    data = json.load(file)
    problems = [] #list to hold new problems and old problems not modified

    def easier_problem_prompt(problem, scale):
        return f"Can you make this question: {problem}, easier by a factor of {scale}? Only respond with the easier question"

    def harder_problem_prompt(problem, scale):
        return f"Can you make this question: {problem}, more difficult by a factor of {scale}? Only respond with the harder question"
    #     return """Suggest three names for an animal that is a superhero.


    for problem in data['problems']:
        diff_actual_desired = problem['question_average'] - desired_avg
        #if difference between average and desired average lesss than threshold, do nothing
        if abs(diff_actual_desired) < threshold:
            # print('do nothing')
            problems.append(problem['problem'])
        #if class average is too low, reduce difficulty of problem
        elif diff_actual_desired < 0:
            scale = diff_actual_desired/100 * (10 - 1)
            # print(f"decreasing difficulty by factor of {scale}")
            # print(f"Old problem: {problem['problem']}")
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=easier_problem_prompt(problem['problem'], scale),
                temperature=0.5,
                max_tokens=30
            )
            # print(f"Response: {response}")
            new_problem = response.choices[0].text.strip()
            # print(f"New problem: {new_problem}")
            problems.append(new_problem)

        #if class average is too high, increase difficulty of problem
        elif diff_actual_desired >= 0:
            scale = diff_actual_desired/100 * (10 - 1)
            # print(f"increasing difficulty by factor of {scale}")
            # print(f"Old problem: {problem['problem']}")
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=harder_problem_prompt(problem['problem'], scale),
                temperature=0.5,
                max_tokens=30
            )
            # print(f"Response: {response}")
            # print(f"CHOICES TEXT: {response.choices[0].text}")
            new_problem = response.choices[0].text.strip()
            # print(f"New problem: {new_problem}")
            problems.append(new_problem)
        else:
            print("something has gone wrong :(")
        
        file.close()
    return problems

def output_file(problem_list):
    pdf = FPDF()
    # Add a page
    pdf.add_page()
    
    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size = 15)
    
    # create a cell
    pdf.cell(200, 10, txt = "Output File",
            ln = 1, align = 'C')
    
    # add another cell
    pdf.cell(200, 10, txt = "Whatever Title You Want",
            ln = 2, align = 'C')
    
    # save the pdf with name .pdf
    pdf.output("GFG.pdf") 
