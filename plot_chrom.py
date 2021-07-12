import pandas as pd
import matplotlib.pyplot as plt
plt.rc('font', family='Helvetica')
import math
import numpy as np
import argparse

#shift value by injection point value
def shift_df(input_file, injection_point):
    input_df = pd.read_csv(input_file, sep = "\t", encoding="utf-16", header=[1,2])
    input_df = input_df.rename(columns = {f"Unnamed: {input_df.columns.get_loc(('UV 1_280', 'ml'))+1}_level_0": "UV 280", f"Unnamed: {input_df.columns.get_loc(('Cond', 'ml'))+1}_level_0": "Conductivity", f"Unnamed: {input_df.columns.get_loc(('Conc B', 'ml'))+1}_level_0": "Conc B"})
    if ('UV 2_260', 'ml') in list(input_df):
        input_df = input_df.rename(columns={f"Unnamed: {input_df.columns.get_loc(('UV 2_260', 'ml'))+1}_level_0": "UV 260"})
    if ('Fraction', 'ml') in list(input_df):
        input_df = input_df.rename(columns={list(input_df.loc[:, pd.IndexSlice[:, 'Fraction']])[0][0]: "Fraction name"})
    shifted_df = input_df.copy()
    shifted_df.loc[:, ("UV 1_280", "ml")]= input_df.loc[:, ("UV 1_280", "ml")]- input_df["Injection"]["ml"][injection_point-1]
    if ('UV 2_260', 'ml') in list(input_df):
        shifted_df.loc[:, ("UV 2_260", "ml")]= input_df.loc[:, ("UV 2_260", "ml")]- input_df["Injection"]["ml"][injection_point-1]
    return(shifted_df)

#creates tuple of fraction names and values
def get_fractions(shifted_df):
    fraction_list = list(shifted_df["Fraction"]["ml"])
    fraction_vals = [x for x in fraction_list if math.isnan(x) == False]
    fraction_name_list = list(shifted_df["Fraction name"]["Fraction"])
    fraction_names = [y for y in fraction_name_list if isinstance(y, str)]
    return (fraction_names, fraction_vals)

#finds peak values. Adjust width to adjust sensitivity.
def find_peaks(shifted_df, width):
    min_width = width*1000
    peak_x_vals = []
    peak_y_vals = []
    for row in np.arange(len(shifted_df)):
        if (row-min_width)>=0:
            min_pos = row-min_width
        else:
            min_pos=0
        if (row+min_width)<=len(shifted_df):
            max_pos = row+min_width
        else: max_pos = len(shifted_df)
        if shifted_df.loc[row,("UV 280", "mAU")]==max(shifted_df.loc[(min_pos):(max_pos),("UV 280", "mAU")]) and shifted_df.loc[row,("UV 280", "mAU")]>(np.average(shifted_df.loc[:,("UV 280", "mAU")])*1.5):
            peak_x_vals= np.append(peak_x_vals, shifted_df.loc[row,("UV 1_280", "ml")])
            peak_y_vals = np.append(peak_y_vals, shifted_df.loc[row,("UV 280", "mAU")])
    return (peak_x_vals, peak_y_vals)
                                     

#creates a plot of the chromatogram
def plot_csv_file(input_file, title = "", plot_fractions=True, output="png", injection_point=2, y_min=None, y_max =None, x_min=None, x_max=None, peaks=True, peak_width=1):
    shifted_df = shift_df(input_file, injection_point)
    shifted_df.head(3)
    if title == "":
        title = input_file.split("/")[-1][0:-4]
    output_path = f'{input_file[0:-3]}{output}'
    fig = plt.figure(figsize=(15, 10), dpi=80)
    ax = fig.add_subplot(1, 1, 1)
    plt.plot("UV 1_280", "UV 280", data=shifted_df, color = "blue")
    if ('UV 2_260', 'ml') in list(shifted_df):
        plt.plot("UV 2_260", "UV 260", data=shifted_df, color="red")
    if y_min == None:
        y_min= min(shifted_df["UV 280"]["mAU"])-0.2
    if y_max == None:
        if ('UV 2_260', 'ml') in list(shifted_df):
            y_max = max(shifted_df["UV 260"]["mAU"])+10
        else:
            plt.ylim(-1, max(shifted_df["UV 280"]["mAU"])+10)
    plt.ylim(y_min, y_max)
    if x_min == None:
        x_min = 0
    if x_max == None:
        x_max = max(shifted_df.loc[:, ("UV 1_280", "ml")])
    plt.xlim(x_min, x_max)
    plt.xlabel("Elution volume (mL)", fontsize=17)
    plt.ylabel("Absorbance (mAu)", fontsize=17)
    plt.legend(fontsize=14)
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    ax.minorticks_on()
    plt.title(title, fontsize=20)
    if plot_fractions:
        (fraction_names, fraction_vals) = get_fractions(shifted_df)
        fractions = ax.secondary_xaxis("bottom")
        fractions.set_axisbelow(False)
        fractions.set_xticks(ticks = fraction_vals)
        fractions.set_xticklabels(fraction_names, ha="left")
        fractions.tick_params(axis="x", direction="in", length=15, colors = "black", pad=-46, labelrotation=90)
        fractions.minorticks_off()
    if peaks==True:
        (peak_x_vals, peak_y_vals) = find_peaks(shifted_df, peak_width)
        for val in np.arange(len(peak_x_vals)):
            ax.annotate(np.around(peak_x_vals[val], decimals=2), (peak_x_vals[val]-0.035, peak_y_vals[val]+1), fontsize=13)
     
    plt.savefig(output_path, dpi=300)
 
# Argument parser
parser = argparse.ArgumentParser(description='Plots chromatograms from a CSV file')
parser.add_argument('file_path', type=str,
                    help='Path to CSV file')
parser.add_argument("--title", "-t", type=str, required=False, default="", help="Displayed title for graph")
parser.add_argument("--hide_fractions", "-f", required=False, default=True, action="store_false", help="Flag to hide fractions")
parser.add_argument("--output", "-o", type=str, required=False, default = "png", help="Output file type for the chromatogram")
parser.add_argument("--injection_point", "-i", type=float, required=False, default = 2, help="injection value")
parser.add_argument("--y_min", type=float, required=False, default=None, help = "Y-axis minimum")
parser.add_argument("--y_max", type=float, required=False, default=None, help = "Y-axis maximum")
parser.add_argument("--x_min", type=float, required=False, default=None, help = "X-axis minimum")
parser.add_argument("--x_max", type=float, required=False, default=None, help = "X-axis maximum")
parser.add_argument("--label_peaks", "-p", required=False, default=True, help="Show peak labels")
parser.add_argument("--peak_width", "-w", required=False, type=float, default=1, help="Adjusts sensitivity of peak finder")

args = parser.parse_args()

def main():
    # paste input file
    plot_csv_file(args.file_path, title = args.title, plot_fractions=args.hide_fractions, output=args.output, injection_point=args.injection_point, y_min=args.y_min, y_max=args.y_max, x_min=args.x_min, x_max=args.x_max, peaks=args.label_peaks, peak_width=args.peak_width)


if __name__ == "__main__":
    main()
