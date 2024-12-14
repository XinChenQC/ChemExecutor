import json
import os
import subprocess
import re
import matplotlib.pyplot as plt



def load_data(file_path: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def process_returnData(DataReturns: dict, data: dict) -> dict:
    print( 'ss')