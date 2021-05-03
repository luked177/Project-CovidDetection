#Import Libraries
import os
import tkinter as tk
from tkinter import filedialog

import nibabel as nib
import numpy as np
import tensorflow as tf
from scipy import ndimage
from tensorflow import keras

import segmentOne


def read_nifti_file(filepath):
    """Read and load volume"""
    # Read file
    scan = nib.load(filepath)
    # Get raw data
    scan = scan.get_fdata()
    return scan


def normalize(volume):
    """Normalize the volume"""
    min = -1000
    max = 400
    volume[volume < min] = min
    volume[volume > max] = max
    volume = (volume - min) / (max - min)
    volume = volume.astype("float32")
    return volume


def resize_volume(img):
    """Resize across z-axis"""
    # Set the desired depth
    desired_depth = 64
    desired_width = 128
    desired_height = 128
    # Get current depth
    current_depth = img.shape[-1]
    current_width = img.shape[0]
    current_height = img.shape[1]
    # Compute depth factor
    depth = current_depth / desired_depth
    width = current_width / desired_width
    height = current_height / desired_height
    depth_factor = 1 / depth
    width_factor = 1 / width
    height_factor = 1 / height
    # Rotate
    img = ndimage.rotate(img, 90, reshape=False)
    # Resize across z-axis
    img = ndimage.zoom(img, (width_factor, height_factor, depth_factor), order=1)
    return img


def process_scan(path):
    """Read and resize volume"""
    # Read scan
    volume = read_nifti_file(path)
    # Normalize
    volume = normalize(volume)
    # Resize width, height and depth
    volume = resize_volume(volume)
    return volume

def userFile():
    print("User Inserts File")
    #	file = filedialog.askopenfilename() #Ask for a file
	#	print(file)
    # Allow user to insert a Nifti Image

#Segment the userFile

def prediction():
    print("Prediction")
    model = tf.keras.models.load_model('ModelSaved')
    model.load_weights("ModelWeights\\CovidWeights.h5")

    predictScan = filedialog.askopenfilename()
    segmentOne.segmentationForPredict(predictScan)
    path = 'segmentedSlice.nii.gz'
    predictScan = process_scan(path)

    prediction = model.predict(np.expand_dims(predictScan, axis=0))
    scores = [1 - prediction[0], prediction[0]]

    class_names = ["normal", "abnormal"]
    for score, name in zip(scores, class_names):
        print(
            "This model is %.2f percent confident that CT scan is %s"
            % ((100 * score), name)
        )

def predictionSegmented():
    print("PredictionSegmentation")
    model = tf.keras.models.load_model('ModelSaved')
    model.load_weights("ModelWeights\\CovidWeights.h5")

    predictScan = filedialog.askopenfilename()
    predictScan = process_scan(predictScan)

    prediction = model.predict(np.expand_dims(predictScan, axis=0))
    scores = [1 - prediction[0], prediction[0]]

    class_names = ["normal", "abnormal"]
    for score, name in zip(scores, class_names):
        print(
            "This model is %.2f percent confident that CT scan is %s"
            % ((100 * score), name)
        )

