import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        num_problems = request.form["num_problems"]
        problems = request.form["problems"]
        class_avg = request.form["class_avg"]
        desired_avg = request.form["desired_avg"]
        threshold = request.form["threshold"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(problems),
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(problems):
    return """Can you make this question easier by a factor of 4? Only respond with the easier question"

    

Question: {}
Answer:""".format(
        problems.capitalize()
    )
