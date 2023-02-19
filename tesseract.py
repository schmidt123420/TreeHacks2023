import os
import json

import openai
from flask import Flask, redirect, render_template, request, url_for
from fpdf import FPDF
from PIL import Image
import pytesseract
import cv2
import re

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

    # for problem in data['problems']:
    for problem in old_problems:
        question_avg = class_avgs.pop()
        update_problem(problem, question_avg, desired_avg, threshold, new_problems)
        
    # return problems
    return new_problems

# Parses all the problems from the image text
def parse_problems(image_text):
    problems = re.findall(r'Problem \d+\)(.*?)Answer:', image_text, re.DOTALL)
    print(problems)

def parse_answers(image_text):
    answers = re.findall(r'Answer: (.*)', image_text)
    print(answers)
    

gray_image = preprocess_image('Trigonometry Test Exam Key1024_1.jpg')
image_text = pytesseract.image_to_string(gray_image, lang='eng')
print(image_text)
parse_problems(image_text)
parse_answers(image_text)