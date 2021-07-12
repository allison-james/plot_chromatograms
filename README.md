# plot_chromatograms
This script plots Äkta chromatograms from the exported csv file. Note that the exported csv file only contains data for the curve that are shown when exporting, so ensure both the A280 and A260 are highlighted before exporting. This script can run without the A260, but the A280 is required.

This script also contains a peak calling function. The --peak_width argument allows for the adjustment of peak calling sensitivity, with lower values corresponding to increased sensitivity. Note that this function calls based on A280 height and will only call peaks that are >1.5 times the average A280.

To run the function, navigate to the appropriate directory and type "python plot_chrom.py" followed byt the file path for the csv file. All other arguments are optional.
