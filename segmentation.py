# Import Libraries
import os
import pathlib
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np  # linear algebra
import scipy.ndimage as ndimage
from nibabel.testing import data_path
from skimage import measure, morphology, segmentation

print("Libraries Imported")

def generate_markers(image):
	#Creation of the internal Marker
	marker_internal = image < -400 #Create a binary image where the only pixel bvalues are -400 or less then the original image.
	marker_internal = segmentation.clear_border(marker_internal)
	marker_internal_labels = measure.label(marker_internal)
	areas = [r.area for r in measure.regionprops(marker_internal_labels)]
	areas.sort()
	if len(areas) > 2:
		for region in measure.regionprops(marker_internal_labels):
			if region.area < areas[-2]:
				for coordinates in region.coords:                
					   marker_internal_labels[coordinates[0], coordinates[1]] = 0
	marker_internal = marker_internal_labels > 0
	#Creation of the external Marker
	external_a = ndimage.binary_dilation(marker_internal, iterations=10)
	external_b = ndimage.binary_dilation(marker_internal, iterations=55)
	marker_external = external_b ^ external_a
	#Creation of the Watershed Marker matrix
	marker_watershed = np.zeros((512, 512), dtype=np.int)
	marker_watershed += marker_internal * 255
	marker_watershed += marker_external * 128
	
	return marker_internal, marker_external, marker_watershed

def seperate_lungs(image):
	#Creation of the markers as shown above:
	marker_internal, marker_external, marker_watershed = generate_markers(image)
	
	#Creation of the Sobel-Gradient
	sobel_filtered_dx = ndimage.sobel(image, 1)
	sobel_filtered_dy = ndimage.sobel(image, 0)
	sobel_gradient = np.hypot(sobel_filtered_dx, sobel_filtered_dy)
	sobel_gradient *= 255.0 / np.max(sobel_gradient)
	
	#Watershed algorithm
	watershed = segmentation.watershed(sobel_gradient, marker_watershed)
	
	#Reducing the image created by the Watershed algorithm to its outline
	outline = ndimage.morphological_gradient(watershed, size=(3,3))
	outline = outline.astype(bool)
	
	#Performing Black-Tophat Morphology for reinclusion
	#Creation of the disk-kernel and increasing its size a bit
	blackhat_struct = [[0, 0, 1, 1, 1, 0, 0],
					   [0, 1, 1, 1, 1, 1, 0],
					   [1, 1, 1, 1, 1, 1, 1],
					   [1, 1, 1, 1, 1, 1, 1],
					   [1, 1, 1, 1, 1, 1, 1],
					   [0, 1, 1, 1, 1, 1, 0],
					   [0, 0, 1, 1, 1, 0, 0]]
	blackhat_struct = ndimage.iterate_structure(blackhat_struct, 8)
	#Perform the Black-Hat
	outline += ndimage.black_tophat(outline, structure=blackhat_struct)
	
	#Use the internal marker and the Outline that was just created to generate the lungfilter
	lungfilter = np.bitwise_or(marker_internal, outline)
	#Close holes in the lungfilter
	#fill_holes is not used here, since in some slices the heart would be reincluded by accident
	lungfilter = ndimage.morphology.binary_closing(lungfilter, structure=np.ones((5,5)), iterations=3)
	
	#Apply the lungfilter (note the filtered areas being assigned -2000 HU)
	segmented = np.where(lungfilter == 1, image, -2000*np.ones((512, 512)))
	
	return segmented, lungfilter, outline, watershed, sobel_gradient, marker_internal, marker_external, marker_watershed

def showSegmentation(sliceNum,testPatientImages,test_patient_internal,test_patient_external,test_patient_watershed,test_sobel_gradient,test_watershed,test_outline,test_lungfilter,test_segmented):
	fig, axs = plt.subplots(3,3)
	axs[0,0].axis('off')
	axs[0,0].grid(b=None)
	axs[0,0].imshow(testPatientImages, cmap='gray')
	axs[0,0].set_title("Original Slice")
	axs[0,1].axis('off')
	axs[0,1].grid(b=None)
	axs[0,1].imshow(test_patient_internal, cmap='gray')
	axs[0,1].set_title("Internal Marker")
	axs[0,2].axis('off')
	axs[0,2].grid(b=None)
	axs[0,2].imshow(test_patient_external, cmap='gray')
	axs[0,2].set_title("External Marker")
	axs[1,0].axis('off')
	axs[1,0].grid(b=None)
	axs[1,0].imshow(test_patient_watershed, cmap='gray')
	axs[1,0].set_title("Watershed Marker")
	axs[1,1].axis('off')
	axs[1,1].grid(b=None)
	axs[1,1].imshow(test_sobel_gradient, cmap='gray')
	axs[1,1].set_title("Sobel Gradient")
	axs[1,2].axis('off')
	axs[1,2].grid(b=None)
	axs[1,2].imshow(test_watershed, cmap='gray')
	axs[1,2].set_title("Watershed Image")
	axs[2,0].axis('off')
	axs[2,0].grid(b=None)
	axs[2,0].imshow(test_outline, cmap='gray')
	axs[2,0].set_title("Outline after reinclusion")
	axs[2,1].axis('off')
	axs[2,1].grid(b=None)
	axs[2,1].imshow(test_lungfilter, cmap='gray')
	axs[2,1].set_title("Lungfilter after closing")
	axs[2,2].axis('off')
	axs[2,2].grid(b=None)
	axs[2,2].imshow(test_segmented, cmap='gray')
	axs[2,2].set_title("Segmented Slice")
	fig.tight_layout()
	fig.canvas.set_window_title(f'Slice {sliceNum}') 
	fig.show()

def multipleSegmentation():
	path = filedialog.askdirectory() # Get user directory containing nifti files
	lungCTs = os.listdir(path)
	i = 0

	for filename in lungCTs:#Loop through every nifti file in directory
		try:
			lungCTScan = os.path.join(path, filename)
			img = nib.load(lungCTScan) # Load the scans
			# GET F DATA
			data = img.get_fdata()

			shape = data.shape
			lengthSlices = shape[2] # Get size of depth of nifti image

			x = list(range(0, lengthSlices)) #Create a list as long as the depth
			y = x[int(len(x) * .3) : int(len(x) * .7)] # Create a list getting only the middle 40 percent of the original list. (This stops segmenting slices where lungs are not visisble)
			yLength = len(y)

			niftiArray = []
			
			for j in range(yLength): # Loop for as many iterations as there are useful slices
				slice_0 = data[:,:,y[j]]

				image = np.stack([slice_0])
				image = image.astype(np.int16)

				image[image == -2000] = 30

				intercept = 1
				image += np.int16(intercept)

				testPatientImages = np.array(image, dtype=np.int16)

				testPatientImages = np.squeeze(testPatientImages)

				#Show some example markers from the middle        
				test_patient_internal, test_patient_external, test_patient_watershed = generate_markers(testPatientImages)

				#Some Testcode:
				test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, test_marker_external, test_marker_watershed = seperate_lungs(testPatientImages)

				niftiArray.append(test_segmented) #Add segmented nifti slice data to the nifti array. 

			affine = img.affine # Get Affine
			header = img.header # Get header
			path1 = f"SegmentedNiftiCovid\\segmentedNiftiCovid{i}" #Each iteration the name of saved slice will change to show what iteration it was performed on
			niftiArray = np.array(niftiArray)
			niftiArray = niftiArray.transpose((-1, 0, 1))
			niftiArray = niftiArray.transpose((-1, 0, 1))   #Transpose so height width and depth are in the right order
			savedFile = nib.Nifti1Image(niftiArray, affine, header) #Create a nifti image based on the nifti array
			savedFile.to_filename(path1 + '.nii.gz') #Save the file to the path the user specified
			print("Segmented Lung")
			i = i + 1 #Increase i
		except IndexError:
			print("Index Error")
			continue

def singleSegmentation():
	ori_img = filedialog.askopenfilename()

	img = nib.load(ori_img)
	# GET F DATA
	data = img.get_fdata()

	shape = data.shape
	lengthSlices = shape[2]

	x = list(range(0, lengthSlices))
	y = x[int(len(x) * .3) : int(len(x) * .7)]
	yLength = len(y)
	middleIndex = yLength // 2

	niftiArray = []

	for j in range(yLength):
		slice_0 = data[:,:,y[j]]

		image = np.stack([slice_0])
		image = image.astype(np.int16)

		image[image == -2000] = 30

		intercept = 1
		image += np.int16(intercept)

		testPatientImages = np.array(image, dtype=np.int16)

		testPatientImages = np.squeeze(testPatientImages)

		#Show some example markers from the middle        
		test_patient_internal, test_patient_external, test_patient_watershed = generate_markers(testPatientImages)

		#Some Testcode:
		test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, test_marker_external, test_marker_watershed = seperate_lungs(testPatientImages)

		if (j == middleIndex):{
			showSegmentation(y[j],testPatientImages,test_patient_internal,test_patient_external,test_patient_watershed,test_sobel_gradient,test_watershed,test_outline,test_lungfilter,test_segmented)
		}#Show user the segmentation stages

		niftiArray.append(test_segmented)

	msgBox = messagebox.askquestion(title="Save Segmented Nifti?",message="Would you like to save the segmented nifti file?")#Ask user with a question box if they would like to save the segmented slice
	if msgBox == 'yes':# If answer is yes, save the slice to a path and name of their choosing
			affine = img.affine
			header = img.header
			path1 = filedialog.askdirectory()
			fileName = simpledialog.askstring(title="File Name",prompt="Enter the file name: ")
			path1 = path1+ f"\\{fileName}"
			niftiArray = np.array(niftiArray)
			niftiArray = niftiArray.transpose((-1, 0, 1))
			niftiArray = niftiArray.transpose((-1, 0, 1))   
			savedFile = nib.Nifti1Image(niftiArray, affine, header)
			#savedFile.to_filename(path1 + 'saved.nii.gz')
			nib.save(savedFile, path1 + '.nii.gz')
			

	print("Segmented Lung")

def segmentationForPredict(ori_img):
	img = nib.load(ori_img)
	# GET F DATA
	data = img.get_fdata()

	shape = data.shape
	lengthSlices = shape[2]

	x = list(range(0, lengthSlices))
	y = x[int(len(x) * .3) : int(len(x) * .7)]
	yLength = len(y)

	niftiArray = []

	for j in range(yLength):
		slice_0 = data[:,:,y[j]]

		image = np.stack([slice_0])
		image = image.astype(np.int16)

		image[image == -2000] = 30

		intercept = 1
		image += np.int16(intercept)

		testPatientImages = np.array(image, dtype=np.int16)

		testPatientImages = np.squeeze(testPatientImages)

		#Show some example markers from the middle        
		test_patient_internal, test_patient_external, test_patient_watershed = generate_markers(testPatientImages)

		#Some Testcode:
		test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, test_marker_external, test_marker_watershed = seperate_lungs(testPatientImages)

		#showSegmentation(y[j],testPatientImages,test_patient_internal,test_patient_external,test_patient_watershed,test_sobel_gradient,test_watershed,test_outline,test_lungfilter,test_segmented)

		niftiArray.append(test_segmented)
	
	affine = img.affine
	header = img.header
	path1 = "segmentedSlice"
	niftiArray = np.array(niftiArray)
	niftiArray = niftiArray.transpose((-1, 0, 1))
	niftiArray = niftiArray.transpose((-1, 0, 1))   
	segmentedNifti = nib.Nifti1Image(niftiArray, affine, header)
	segmentedNifti.to_filename(path1 + '.nii.gz')
	print("Segmented Lung")
	return segmentedNifti