# informed-gp-brainfuck
Using n-grams to inform Genetic Programming search on a target BrainFuck programming problem

Please use the Test.py script as an example of how to use the modules in this collection. It runs all algorithms:
	EDA, MEDA, IEDA, MIEDA, GP, MGP, IGP, MIGP, RS, US
on a specific target word-program.

To view the DATA files that I collected, run datadefinition and choose the file to view. The format of the files is:
fitnessevaluations_ - number of fitness evaluations algs. were run for.
maxprogsize_ - maximum program size allowed in all algs.
sizerange_ - range of sizes of words in models
nrange_ - range of n values in models
algorithmsincluded_ - algorithms data was gathered for, 1=gathered, 0=not, for [mieda, migp, rs, meda, mgp, us]
seen/unseen - whether seen or unseen words by model were used

Please also note that some non-built-in imports may be required:
Matplotlib
Numpy
