"""
Optional GUI allowing for plotting of thermo data and global dump data

To use, call the launch method.
"""


# Import Packages
import tkinter.font as font
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import filedialog as fd

from PIL import ImageTk, Image
import PIL.Image

import ctypes

import math

from pathlib import Path

# Ensure compatible imports regardless of manner the file is loaded
if __name__ == "__main__":
    import thermo_reader
    import dump_reader
else:
    from . import thermo_reader
    from . import dump_reader


module_path = Path(__file__).parent

plot_image_path = module_path/"GUI_figures"/"PlottedGraph.png"

# Import Monitor Resolution
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1) # Obtain Width and Hight of Screen
window_W = math.floor(screensize[0]/1.75) # Screen Width
window_H = math.floor(screensize[1]/1.75) # Screen Height


def launch():
    """Launches interactive GUI"""
    
    # Define tkinter Window
    root = Tk() # Establish Tkinter Window
    root.geometry(str(window_W)+'x'+str(window_H)) # Define Window Width and Height
    root.minsize(window_W, window_H) # Define Minimize Window Size
    root.maxsize(window_W, window_H) # Define Maximum Window Size
    root.configure()
    
    # Define Button Parameters
    bFont = font.Font(family='MS Sans Serif', size = math.floor(window_W/50)) # Button Font
    bWidth = math.floor(window_W/70) # Button Width
    padding_x = math.floor(window_W)/75 # Widget Padding Value (x-direction)
    padding_y = math.floor(window_H)/35 # Widget Padding Value (y-direction)
    
    # Upload Original Background Image for Resizing
    BackgroundImage = PIL.Image.open(module_path/"GUI_figures"/"background.png") # Open Background File
    resize_image = BackgroundImage.resize((window_W, window_H)) # Resize Image to Fit Screen
    background_image= ImageTk.PhotoImage(resize_image) # Define Background Image (re-sized)
    background_label = Label(master = root, image=background_image) # Define Image widget
    background_label.place(x=0, y=0) # Position Background Image
    
    # Run LAMMPS .GIF
    frameCnt = 121 # Number of Frames in .GIF
    frames = [PhotoImage(file=module_path/'GUI_figures'/'logo.gif',format = 'gif -index %i' %(i)) \
              for i in range(frameCnt)] # Extract all frames
    
    def update(ind):
        """
        Function for updating frames in .GIF
        
        ind: index (for frames)
        """
        frame = frames[ind]
        ind += 1
        if ind == frameCnt:
            ind = 0
        gif.configure(image=frame)
        root.after(40, update, ind)
        
    gif = Label(root) # Establish .GIF Label
    gif.pack(pady=padding_y/4) # Fit .GIF Widget to Main Window
    root.after(0, update, 0) # Repeat .GIF Cycle Upon Completion
    
    # Holiday Spirit
    image_main = PhotoImage(file=module_path/"GUI_figures"/"HappyHolidays.png", master = root) # Upload Image File
    img_main = Label(root, image = image_main, relief = 'solid') # Define Image Widget
    img_main.pack(side="right", padx = (50, 50), pady = (15, 15)) # Fit Image to Main Window
    
          
    def resetBaseButtons():
        """
        Resets Home Screen Buttons
        """
    
        thermoButton.pack(padx=padding_x) # Fits 'Thermo. Plot' to Main Window
        dumpButton.pack(padx=padding_x) # Fits 'Dump Plot' to Main Window
        
        
    def clearMain():
        thermoButton.pack_forget() # Temporarily Removes Original thermo_reader button
        dumpButton.pack_forget() # Temporarily Removes Original dump_reader button
        fileError.forget() # Removes File Error, if present
        
        
        
    def thermo():
        """
        Command when 'Thermo. Plot' Button is Selected. Presents Options for plotting desired properties
        """
    
        clearMain() # Clears Home Screen Buttons
        
        # Select File From Local Directory
        filename = fd.askopenfilename() # Returns Selected File Directory as String
        
        #joblib.dump(filename, 'exported_GUI_files/log_file.pkl') # Exports file
        
        # Verifies if Correct File Type Has Been Selected
        if filename[-3:] != 'log':
            resetBaseButtons() # If Incorrect File Type, Reset Home Screen Buttons
            fileError.pack(side = "bottom", padx = 8) # Fit Error Message to Main Screen
            return
            
        # Import dataframes information from thermo_reader   
        dataframes = thermo_reader.parse_log_file(filename)
        runs = list(dataframes.keys())  # List of 'runs' (1-N)
        
        # Label For Selecting the Run Number
        thermoX = tk.Label(root, text="Select Run Number", relief = 'raised', width=bWidth, font = bFont, 
                           bg='blue', fg='white')
        thermoX.pack() # Fit Label To Current Screen
        
        # Dropdown Selector for Number of Runs
        OPTIONS = runs # Rename run variable for clarity
        default_runs = StringVar(root) # establish string list for 'runs' values
        default_runs.set(OPTIONS[0]) # Default Value
        thermoRuns = OptionMenu(root, default_runs, *OPTIONS) # Define Dropdown Widget
        thermoRuns.config(width=bWidth, font = bFont) # Define Button Parameters
        thermoRuns.pack() # Fit Dropdown to Current Screen
        
        def decide_runs():
            
            """
            Advances to Thermodynamic Property Selection once Run Number Has Been Selected
            """
            # Hide Unecessary Buttons/Labels
            thermoX.pack_forget() # Hides Label for Selecting Run Number
            thermoRuns.pack_forget() # Hides Dropdown Menu for Selecting Number of Runs
            okay_button.forget() # Hide 'Okay Button
            
            df = dataframes[int(default_runs.get())] # Extract Dataframe related to the selected run
            df_updated = df.loc[:, (df != 0).any(axis=0)] # Removes all columns with only zeros in them
            thermo = list(df_updated.columns)[1:] # List of Dataframe Columns Names i.e. thermodynamic properties
            
            # Label for selecting thermodyanmic Property (i.e. Y-axis of the plot)
            thermoY = tk.Label(root, text="Y: Thermo. Property", width=bWidth, font = bFont, bg='blue', 
                               fg='white')
            thermoY.pack() # Fit Label To the Curren Screen
             
            # Dropdown Button: Thermodynamic Properties
            properties_list = thermo # List of Thermodynamic Properties to be plotted
            default_thermo = StringVar(root) # establish string list for 'runs' values
            default_thermo.set(properties_list[0]) # Default Value
            thermoProp = OptionMenu(root, default_thermo, *properties_list) # Define Dropdown Widget
            thermoProp.config(width=bWidth, font = bFont) # Define Button Parameters
            thermoProp.pack() # Fit Dropdown to Current Screen
            
            def resetPlotButtons():
                """
                Reset Plotting Buttons After 'Plot' Has Been Selected
                """
                
                thermoX.pack() # Shows Label for Number of Runs
                thermoY.pack_forget() # Hides Label for 'Y: Thermo Property'
                thermoRuns.pack() # Shows Runs Dropdown Button
                thermoProp.pack_forget() # Hides Thermo Dropdown Button
                thermo_Cancel.pack_forget() # Hides 'Cancel' Button
                thermo_Plot.pack_forget() # Hides 'Plot' Button
                okay_button.pack() # Shows 'Okay' Button
    
            
            def resetAllButtons():
                """
                Reset All Buttons After 'Plot' Has Been Selected. Returns to Main Screen
                """
                
                thermoX.pack_forget() # Hides Label for Number of Runs
                thermoY.pack_forget() # Hides Label for 'Y: Thermo Property'
                thermoRuns.pack_forget() # Hides Runs Dropdown Button
                thermoProp.pack_forget() # Hides Thermo Dropdown Button
                thermo_Cancel.pack_forget() # Hides 'Cancel' Button
                thermo_Plot.pack_forget() # Hides 'Plot' Button
                thermoButton.pack(padx=padding_x) # Shows 'Thermo. Plot' Button
                dumpButton.pack(padx=padding_x) # Shows 'Dump Plot' Button
    
            def thermoPlot():
                """
                Plots Selected Property vs. Step Numbers by running thermo_reader
                
                * Note: A Web Browser with the plotly graph will open upon selecting ' Plot' Button
                """
                
                thermo_reader.plot_log_data(dataframes, int(default_runs.get()), y = default_thermo.get(),
                                             write_path = plot_image_path)
                
                
                NewGraph = PhotoImage(file = plot_image_path, master = root) # Uploads Image of Graph
    
                # Replace Main Image With Selected Plot
                img_main.configure(image=NewGraph) # Defines New Image
                img_main.image = NewGraph
                resetPlotButtons() # Resets Plotting Buttons
                
            def thermoCancel():
                """
                Resets all Buttons to return to Home Screen
                """
                resetAllButtons() # Resets Buttons
    
            # Plot Button - Plot Graph given selected parameters
            thermo_Plot = Button(root, text="Plot", borderwidth=5, width = bWidth, font = bFont, 
                                 bg='green', fg='white', command = thermoPlot)
            thermo_Plot.pack() # Fit Button to Current Screen
    
            # Cancel Button - Return To Home Screewn
            thermo_Cancel = Button(root, text="Cancel", borderwidth=5, width = bWidth, font = bFont, 
                                   bg='red', fg='white', command = thermoCancel)
            thermo_Cancel.pack() # Fit Button to Current Screen
            
        # Okay Button - Button For Confirming 'Number of Runs' Selection
        okay_button = Button(root, text="OKAY", borderwidth=5, width = bWidth, font = bFont, bg='green',
                             fg='white', command = decide_runs)
        okay_button.pack() # Fit Button to Current Screen
    
        
        
    def dump():
        
        """
        Command when 'Dump. Plot' Button is Selected. Presents Options for plotting desired properties
        """
        
        clearMain() # Clear Home Screen Buttons
    
        # Select .dump File From Local Directory
        file_path = fd.askopenfilename() # Returns Selected File Directory as String
    
        # Verifies if Correct File Type Has Been Selected
        if file_path[-4:] != 'dump':
            resetBaseButtons() # If Incorrect File Type, Reset Home Screen Buttons
            fileError.pack(side = "bottom", padx = 6) # Fit Error Message to Main Screen
            return()
    
        # Imports Packages related to task
        import numpy as np
        from dump_reader import Snapshots
        from thermo_reader import plot_data
        
        numeric_kinds = {"b", "i", "u", "f", "c"} # numeric data in dictionary
    
        snapshots = Snapshots.from_dump(file_path) # Exports Snapshots from .dump file
        
        # Dictionary containing numeric properties and data values
        prop_dict = {}
        
        # Filter out non-numeric and multi-dimensional data
        for prop, value in snapshots.items.items():
            if (value.dtype.kind in numeric_kinds) and value.ndim == 1:
                prop_dict[prop] = value
        
    
        # Add box properties to dictionary so they can be plotted
        prop_dict["lx"] = snapshots.boxes.lx
        prop_dict["ly"] = snapshots.boxes.ly
        prop_dict["lz"] = snapshots.boxes.lz
        prop_dict["xy"] = snapshots.boxes.xy
        prop_dict["xz"] = snapshots.boxes.xz
        prop_dict["yz"] = snapshots.boxes.yz
        
        del snapshots # Do Not need anymore
        
        timesteps = prop_dict["timestep"] # Time step values extracted from dictionary
        
        # Property list dropdown
        prop_list = list(prop_dict.keys())[1:]
        
        # Label For Property To Plot
        property_label = tk.Label(root, text="Property To Plot", relief = 'raised', width=bWidth, 
                                  font = bFont, bg='blue', fg='white')
        property_label.pack() # Fit Label To Current Screen
    
        # Dropdown Selector for Property To Plot
        property_option = prop_list # Rename list of properties variable for clarity
        default_property = StringVar(root) # establish string list for 'property' values
        default_property.set(property_option[0]) # Default Value
        property_drop = OptionMenu(root, default_property, *property_option) # Define Dropdown Widget
        property_drop.config(width=bWidth, font = bFont) # Define Button Parameters
        property_drop.pack() # Fit Dropdown to Current Screen
        
        
        def decide_property():
            """
            Plots data upon selecting property
            """
            # Plots Data to Web Browser via plotly
            plot_data(timesteps, prop_dict[default_property.get()], x_label = "Timestep (#)", 
                      y_label = default_property.get(), write_path = plot_image_path)
          
            
    #       Replace Main Image With Selected Plot
            DumpGraph = PhotoImage(file=plot_image_path, master = root) # Uploads Image of Graph
            img_main.configure(image=DumpGraph) # Defines New Image
            img_main.image = DumpGraph
        
            
        def dumpCancel():
            """
            Hides Buttons related to Dump_Plot and returns to home screen
            """
            
            dump_Plot.pack_forget() # Hides Dump Plot Button
            dump_Cancel.pack_forget() # Hides Cancel Button
            property_label.pack_forget() # Hides Property Label
            property_drop.pack_forget() # Hides Dropdown List of Properties
            resetBaseButtons() # Returns Home Screen Buttons
    
            
          # Plot Button - Plot Graph given selected parameters
        dump_Plot = Button(root, text="Plot", borderwidth=5, width = bWidth, font = bFont, bg='green', 
                           fg='white', command = decide_property)
        dump_Plot.pack() # Fit Button to Current Screen
        
        # Cancel Button - Return To Home Screewn
        dump_Cancel = Button(root, text="Cancel", borderwidth=5, width = bWidth, font = bFont, bg='red',
                             fg='white', command = dumpCancel)
        dump_Cancel.pack() # Fit Button to Current Screen
        
        
    # Thermo. Plot Button - Plots properties vs. Step number utilizing the 'thermo_reader' package
    thermoButton = Button(root, text="Thermo. Plot", borderwidth=15, width = bWidth, font = bFont, 
                          bg='green', fg='white', command=thermo)
    thermoButton.pack(padx = padding_x) # Fit Button to Main Screen
    
    # Dump Plot Buttons - Dump_Reader, Thermo_Reader, Quit
    dumpButton = Button(root, text="Dump Plot", borderwidth=15, width = bWidth, font = bFont, 
                        bg='green', fg='white', command = dump)
    dumpButton.pack(padx = padding_x)
    
    # File Error Label - Displayed if Wrong File Type is Selected
    fileError = Label(root, text = 'File Type Not Supported!', width=bWidth+5, 
                      font = ('MS Sans Serif',math.floor(window_W/50)), bg='#ED736C', fg='white')
    
    # Quit Button - Closes Tkinter Window, closes program
    quitButton = Button(root, text="Quit", borderwidth=15, width = bWidth, bg='#EC452E', font = bFont, 
                        fg='white', command=root.destroy)
    quitButton.pack(side = "bottom", padx=padding_x, pady=padding_y)
    
    # Closes tkinter Loop
    root.mainloop()



if __name__ == "__main__":
    launch()