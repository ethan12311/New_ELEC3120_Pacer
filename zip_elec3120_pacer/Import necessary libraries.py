# Import necessary libraries
import PyPDF2
import io
import re
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output, Markdown
import json

# For progress tracking
from datetime import datetime