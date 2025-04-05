#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from translate.crew import Translate

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
            'filePath': "C:/Users/gafer/Downloads/babel-japanese-sample.pdf",
            'outputPath': "C:/Coding/CrewAI/Translate/output/translated.pdf",
            'sourceLang': 'es',
            'targetLang': 'en',
            'instructions': "Translate the text content at {filePath} that is in source language {sourceLang} to the target language {targetLang} using the tools provided while following all instructions provided by the user in {instructions}"
        }
    
    try:
        Translate().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")