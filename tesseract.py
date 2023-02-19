import os
import json

import openai
from flask import Flask, redirect, render_template, request, url_for
from fpdf import FPDF
from PIL import Image
import pytesseract
import cv2

def preprocess_image(filename):
    image = cv2.imread(filename) #read original image
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #convert to grayscale
    # cv2.imshow('Grayscale', grayscale)
    return grayscale



# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg']) #allowed file types for OCR

# #Check if the user provided file is a valid type (png, jpg, or jpeg)
# def check_valid_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def process_image(file):
#     if file and check_valid_file(file.filename):
#         extracted_text = ocr_core(file)
#         print(extracted_text)

def ocr_core(filename):
    text = pytesseract.image_to_string(Image.open(filename))
    return text

# print(ocr_core('IMG_0633.JPG'))
gray_image = preprocess_image('IMG_0635.JPG')
print(pytesseract.image_to_string(gray_image, lang='eng'))