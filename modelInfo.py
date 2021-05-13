import tkinter as tk

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


def loss():
    print("Loss")
    lossPath = 'ModelImages\ModelLoss.png'#Get the path of Loss graph
    img = mpimg.imread(lossPath)#Load the graph
    plt.imshow(img)#Show the graph
    plt.grid(False)
    plt.show()

def accuracy():
    print("Accuracy")
    accPath = 'ModelImages\ModelAcc.png'#Get the path of loss graph
    img = mpimg.imread(accPath)#Load the graph
    plt.imshow(img)#Show the graph
    plt.grid(False)
    plt.show()

def summary():
    print("Summary")
    accPath = 'ModelImages\ModelSummary.png'#Get path of the png of model summary
    img = mpimg.imread(accPath)#Load the summary
    plt.imshow(img)#Show the summary
    plt.grid(False)
    plt.show()
