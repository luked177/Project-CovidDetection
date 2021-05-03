import tkinter as tk

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


def loss():
    print("Loss")
    lossPath = 'ModelImages\ModelLoss.png'
    img = mpimg.imread(lossPath)
    plt.imshow(img)
    plt.grid(False)
    plt.show()

def accuracy():
    print("Accuracy")
    accPath = 'ModelImages\ModelAcc.png'
    img = mpimg.imread(accPath)
    plt.imshow(img)
    plt.grid(False)
    plt.show()

def summary():
    print("Summary")
    accPath = 'ModelImages\ModelSummary.png'
    img = mpimg.imread(accPath)
    plt.imshow(img)
    plt.grid(False)
    plt.show()
