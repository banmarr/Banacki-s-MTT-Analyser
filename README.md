# MTT Analyser
#### Description:
This is the MTT Analyser, a relatively simple code for automatition of the statistical analysis of the MTT assay, commonly used in molecular biology labs. It gives the mean, standard deviation and viability (relative to control) of each of the analysed groups on one plate. It can also analyse two plates and compare them against each other.


The code assumes:  
* The results are in a .csv table, which:  
    * Has the first cell in the A1 (that is, there is no header or index in the file)  
    * Uses the semicolon (;) as the separator  
    * Is formed of exactly 12 columns and 16 rows  
    * Has the “main” wavelength absorption values in every 2nd row, starting from the first row  
    * Has the “background” wavelength absorption values in every 2nd row, starting from the second row  
* If analysing two plates, one against each other, each one of them has the same number of treatments and each of the treatments has the same amount of repeats; moreover, each of the plates has the same number of series.  
*	The series (R) is the number of times each treatment is repeated on the plate.  
*	The treatments (T) is the number of groups on the plate.  
*	The repeats (N) is the number of wells (cells) each treatment in the series consists of.  
*	No well that is to be analysed has “0” as a value (unlikely to be returned by the machine).  
*	In each row, the results are shown starting from the left of the table, that is, there are no empty (non-result) cells to the left of the results in each row.  
*	The control group is the "treatment 0" on each analysed plate.  
*	There is the "project" folder in the "Users" folder on the C disk.  
*	The 2nd argument (aside from the name of the code) is the control plate.  
*	The 1st argument (aside from the name of the code) is the research plate.  


The code works like this: first, it asks how many plates (1 or 2) should be analysed. If the answer is other than the allowed or the wrong number of arguments has been put in, the code returns an Exception. The next step is the substraction of the background value (every 2nd row starting from the 2nd row) from the actual absorption value (every 2nd row starting from the 1st row) Then, it asks how many wells are empty, counting from right, in each of the rows on each plate. If the entire row is empty, it gets removed later for simplicity's sake.

Next is the statistical analysis: the code takes the given number of repeats and calculates means and standard deviations, putting them into each dictionary to the right treatment. Then, it is checked if there is the right number of inputs in the dictionaries (that is, if it equals the "R" stated at the beginning), and then, the "true mean" and "true SD" is calculated, by taking means of the previously put means and SDs.

Next, viability is calculated, by taking the mean of a given treatment, dividing it by the mean of the treatment0 (assumed to be a control), and multiplying by 100.

If analysing two plates, then the results are compared against each other: viability of each of the groups (treatments) of the research plate is divided by the viability of the control plate and multiplied by 100; the same thing happens with the means.

Finally, the code prints out the dataframes for analysed plates and, if two plates were analysed, a dataframe with joined results is shown. Moreover, the output .csv files with said dataframes are created, one for each analysed plate, and the one comparing the plates side-by-side is created too if 2 plates were analysed.
