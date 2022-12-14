"""
This module implements functions for parsing YAML thermo tables from LAMMPS log files and plotting
them interactively with plotly. See methods below
"""

import re
import yaml
import pandas as pd

import plotly.express as px
import plotly.io as pio

from pathlib import Path
from warnings import warn


# Boilerplate for yaml loader
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader


# Flag to disable writing images to file (for debugging use)
_DEBUG_DISABLE_WRITE_FILE = False

# Enable browser mode for plotly
pio.renderers.default = 'browser'


# Get module absolute path (used for accessing companion files)
module_path = Path(__file__).parent

# units_info.yaml contains info for auto-detecting units from log data

with open(module_path/"units_info.yaml", 'r') as f:
    units_info = yaml.load(f.read(), Loader=Loader)


# unit_styles contains units of varies quantities (press, temp, ...) for each style (metal, si, etc)
unit_styles = units_info["unit_styles"]

# prop_types maps thermo log properties to their unit style (e.g. Pxy -> pressure)
prop_types = units_info["prop_types"]


# string pattern to match to runs in LAMMPS
# The first line attempts to match to a unit style line, which is written to stdout (but no in log files)
# The second line attempts to match to a timestep line, which is written to stdout for dynamics runs
# The third line matches the YAML table for the thermo data

pattern_str = \
    "(Unit style" "\s*:\s*" "(?P<unit_style>.*)" "\s*" "\n" "(?s:.*?))?" \
    "(Time step" "\s*:\s*" "(?P<timestep>.*)" "\s*" "\n" "(?s:.*?))?" \
    "(?P<yaml>" "---" "\n" "\s*" "keywords:.+" "\n" "\s*" "data:.*" "\n" "(?:\s*-\s*\[.*\n)*" "\.\.\." ")"

pattern = re.compile(pattern_str)


def get_axis_label(dataframe, col):
    """
    Get axis label with units, if it is available in units_info.yaml
    
    Args:
        dataframe (DataFrame): dataframe originating from parse_log_file
        col (str): col from that dataframe whose label is desired
    
    Returns:
        label (str): If units are found, they are appended to the col.
            Otherwise, only the col is returned
    """
    
    unit_style = dataframe.attrs.get("unit_style")
    
    if unit_style is None: # Unit style isn't available
        return col
    
    name = col.lower()
    
    prop_type = prop_types.get(name)
    units_map = unit_styles.get(unit_style)

    if prop_type is None or units_map is None: # prop_type or units_map is unavailable
        return col
    
    units = units_map.get(prop_type)
    
    if units is None: # Unit isn't stored in unit_style
        return col
    
        
    return f"{col} ({units})"
    

def parse_log_file(path):
    """
    Reads YAML-style thermo tables from lammps output file.
    
    It is recommended that you use the LAMMPS stdout file, as it contains information necessary
    to auto-detect units. A LAMMPS log file will also work, but unit auto-detection will be
    unavailable
    
    Args:
        path (Path or str): location of log file
        
    Returns:
        dataframes (dict of dataframes): Keys are numbered from 1, ..., N with the corresponding
            dataframe as the value
    """
    
    with open(path, "r") as f:
        file_string = f.read()
    
    
    # Dataframes are stored in dictionary with one-based indexing, as it is more intuitive to users
    dataframes = {}
    
    units_warned = False
    
    # Find all YAML tables and convert to dataframes
    for count, match in enumerate(pattern.finditer(file_string), start = 1):
        yaml_table = yaml.load(match["yaml"], Loader=Loader)
        
        dataframe = pd.DataFrame(data = yaml_table["data"], columns = yaml_table["keywords"])
        
        dataframes[count] = dataframe
        
        if match["unit_style"] is None:
            if not units_warned:
                # Only give warning once
                warn("Cannot auto-detect unit style, try stdout file if you want units detection")
                units_warned = True
                
            continue
        
        timestep = match["timestep"]
        if timestep is not None:
            timestep = float(timestep)
            dataframe.attrs["timestep"] = timestep
        
            if ("Time" not in dataframe.columns) and "Step" in dataframe.columns:
                # Automatically calculate time for user if it is missing
                dataframe["Time"] = dataframe["Step"]*timestep
    
        dataframe.attrs["type"] = "dynamics" if (timestep is not None) else "minimization"
        dataframe.attrs["unit_style"] = match["unit_style"]
        
    return dataframes



def plot(*args, write_path = None, **kwargs):
    """
    Simple wrapper to plotly plotter
    
    Args:
        path (Path or str): location of log file
        write_path (Path, str, or None): Optional path to write figure to (default None)
            
    Returns: Plotly fig
    """
    
    fig = px.scatter(*args, **kwargs)
    
    if write_path is not None:
        if _DEBUG_DISABLE_WRITE_FILE:
            warn("Write file is currently disabled, " + write_path)
        else:
            fig.write_image(write_path)
        
        
    fig.show()


    return fig
    

def plot_data(x, y, x_label = '', y_label = '', title = '', write_path = None):
    """Create plotly figure with x and y data series, see plot"""
    return plot(x = x, y = y, labels = {"x": x_label, "y": y_label}, title = title, write_path = write_path)


def plot_log_data(dataframes, index, y, x = None, write_path = None):
    """
    Plot requested log data entry using plotly
    
    Args:
        dataframe (DataFrame): dataframe originating from parse_log_file
        index (int): Which run to plot
        y (str): Column of data to plot in y
        x (str): Column of data to plot in x. If not given, Time or Step will be used
        write_path (Path, str, or None): Optional path to write figure to (default None)
        
    Returns: Plotly fig
    """
    
    dataframe = dataframes[index]
    attrs = dataframe.attrs
    
    if x is None:
        if "type" in attrs and attrs["type"] == "dynamics":
            x = "Time"
        else:
            x = "Step"    
    
    labels = {}
    labels[x] = get_axis_label(dataframe, x)
    labels[y] = get_axis_label(dataframe, y)
    
    
    title = f"Run {index}/{len(dataframes)}"
    
    if "type" in attrs:
        title = attrs["type"].capitalize() + ' ' + title
    
    return plot(dataframes[index], x = x, y = y, title = title, labels = labels, write_path = write_path)




if __name__ == "__main__":
    # Arbitary test code
    dataframes = parse_log_file("../dislocation2.log")
    
    plot_log_data(dataframes, 6, "Temp", write_path = 'hello.png')
        