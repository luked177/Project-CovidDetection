#Import Scripts
import test
import train
import segment

#Import Needed Libraries
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox

#Class for CovidGUI
class CovidGUI:

	def __init__(self): # Initialise Tkinter window app
		self.root = tk.Tk()
		self.root.title("CovidGUI") #Name the window
		#self.root.geometry('500x200') #Size the window
		#self.root.overrideredirect(True)
		self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
		self._create_menubar() #Run create menubar function

	def _create_menubar(self):
		self.menubar = tk.Menu(self.root,foreground='white', activebackground='#0B3D54', activeforeground='white')
		self.root.configure(menu=self.menubar)

		predictCovid = tk.Menu(self.menubar,tearoff=0)
		self.menubar.add_cascade(label="Predict Covid", menu=predictCovid)
		predictCovid.add_command(label="Insert Image",command=test.prediction)

		showAccuracy = tk.Menu(self.menubar,tearoff=0)
		self.menubar.add_cascade(label="Show Accuracy", menu=showAccuracy)
		showAccuracy.add_command(label="Accuracy Graph",command=train.accuracy)
		showAccuracy.add_command(label="Loss Graph",command=train.loss)

		segmentLung = tk.Menu(self.menubar,tearoff=0)
		self.menubar.add_cascade(label="Segment Lung", menu=segmentLung)
		segmentLung.add_command(label="Segment",command=segment.originalImages)

		# Exit menu
		exitMenu = tk.Menu(self.menubar,tearoff=0) #Add exit to menubar
		self.menubar.add_cascade(label="Exit", menu=exitMenu)
		exitMenu.add_command(label="Exit", command=self.myExitApplication) #Run exit function created below

	def myExitApplication(self):
		MsgBox = messagebox.askquestion('Exit App', 'Are you sure?')#Ask if user wants to quit
		if MsgBox == 'yes': # If answer yes
			self.root.destroy() #Destroy Window