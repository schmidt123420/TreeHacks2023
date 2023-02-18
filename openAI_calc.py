import json
import os

import openai
from flask import Flask, redirect, render_template, request, url_for

DESIRED_PERCENTAGE = 75 #Desired class average
DIFFERENCE_TO_CHANGE = 7.5 #if percentage difference between actual and desired class average >= than this value, make problem easier or harder
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = os.environ["OPENAI_API_KEY"]

#Processes an input JSON file with problems, solutions, and class averages of problems from a test
def process_file():
    #open JSON file and store the data
    file = open('problems.json')
    data = json.load(file)

    #print each problem
    for problem in data['problems']:
        diff_actual_desired = problem['class_average'] - DESIRED_PERCENTAGE
        #if difference between average and desired average lesss than threshold, do nothing
        if abs(diff_actual_desired) < DIFFERENCE_TO_CHANGE:
            print('do nothing')
        #if class average is too low, reduce difficulty of problem
        elif diff_actual_desired < 0:
            scale = diff_actual_desired/100 * (10 - 1)
            print(f"decreasing difficulty by factor of {scale}")
            print(f"Old problem: {problem['problem']}")
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=easier_problem_prompt(problem['problem'], scale),
                temperature=0.5,
                max_tokens=30
            )
            # print(f"Response: {response}")
            new_problem = response.choices[0].text.strip
            print(f"New problem: {new_problem}")

        #if class average is too high, increase difficulty of problem
        elif diff_actual_desired >= 0:
            scale = diff_actual_desired/100 * (10 - 1)
            print(f"increasing difficulty by factor of {scale}")
            print(f"Old problem: {problem['problem']}")
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=harder_problem_prompt(problem['problem'], scale),
                temperature=0.5,
                max_tokens=30
            )
            print(f"Response: {response}")
            print()
            # print(f"CHOICES TEXT: {response.choices[0].text}")
            new_problem = response.choices[0].text.strip()
            print(f"New problem: {new_problem}")
        else:
            print("something has gone wrong :(")

    #close file
    file.close()

def easier_problem_prompt(problem, scale):
    return f"Can you make this question: {problem}, easier by a factor of {scale}? Only respond with the easier question"


def harder_problem_prompt(problem, scale):
    return f"Can you make this question: {problem}, more difficult by a factor of {scale}? Only respond with the harder question"
#     return """Suggest three names for an animal that is a superhero.

# Animal: Cat
# Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
# Animal: Dog
# Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
# Animal: {}
# Names:""".format(
#         animal.capitalize()
#     )

process_file()



