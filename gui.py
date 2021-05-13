#Import Scripts
import test
#Import Needed Libraries
import tkinter as tk
from tkinter import messagebox, simpledialog

from PIL import Image, ImageTk

import modelInfo
import segmentation


#Class for CovidGUI
class CovidGUI:

	def __init__(self): # Initialise Tkinter window app
		self.root = tk.Tk()
		self.root.title("CovidGUI") #Name the window
		self.root.geometry('500x200') #Size the window
		self._create_menubar() #Run create menubar function
		self.image_bck() #Run image background function

	def image_bck(self): #Create background image
		image1 = Image.open("background.png") #Import image
		image1 = image1.resize((500,200), Image.ANTIALIAS) #Resize image to match window size
		bck = ImageTk.PhotoImage(image1) #Create a photo image

		label1 = tk.Label(image=bck) #Add image to a label
		label1.image = bck

		label1.grid(column=0,row=0) # Position label


	def _create_menubar(self): # Create menu bar
		self.menubar = tk.Menu(self.root)
		self.root.configure(menu=self.menubar) # Initialise menu bar

		predictCovid = tk.Menu(self.menubar,tearoff=0) # Add the predict covid tab to menu bar
		self.menubar.add_cascade(label="Predict Covid", menu=predictCovid)
		predictCovid.add_command(label="Insert Raw Image",command=test.prediction) #Add ability to segment a lung image before making a prediction
		predictCovid.add_command(label="Insert Segmented Image",command=test.predictionSegmented) # Make a prediction on an already segmented lung

		showAccuracy = tk.Menu(self.menubar,tearoff=0) 
		self.menubar.add_cascade(label="Model Info", menu=showAccuracy) #Add the model info tab
		showAccuracy.add_command(label="Model Summary",command=modelInfo.summary) # Show a model summary
		showAccuracy.add_command(label="Accuracy Graph",command=modelInfo.accuracy)# Show an accuracy graph
		showAccuracy.add_command(label="Loss Graph",command=modelInfo.loss) # Show a loss graph

		segmentLung = tk.Menu(self.menubar,tearoff=0)
		self.menubar.add_cascade(label="Segment Lung", menu=segmentLung) # Add segmentation tab
		segmentLung.add_command(label="Segment One",command=segmentation.singleSegmentation) # Segment one image
		segmentLung.add_command(label="Segment Directory & Save",command=segmentation.multipleSegmentation) # Segment multiple images

		# Exit menu
		exitMenu = tk.Menu(self.menubar,tearoff=0) #Add exit to menubar
		self.menubar.add_cascade(label="Exit", menu=exitMenu)
		exitMenu.add_command(label="Exit", command=self.myExitApplication) #Run exit function created below

	def myExitApplication(self):
		MsgBox = messagebox.askquestion('Exit App', 'Are you sure?')#Ask if user wants to quit
		if MsgBox == 'yes': # If answer yes
			self.root.destroy() #Destroy Window
