import tkinter as tk
from tkinter import messagebox #messagebox
from tkinter import simpledialog
from tkinter import filedialog
import datetime
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def originalImages():
    print("Read Nifti Images")
    # Take original images in
