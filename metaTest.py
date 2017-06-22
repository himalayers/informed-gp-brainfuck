import saveloadmodels, BFAST2, random, BFGeneratorForWords, copy, MIEDAfixed, EDAfixed
import EDA, GP, MGP, MIEDA, IGP, MIGP, sampleSMSmoothing, US

# constants
N, fitevals, mps = 5, 50, 150
# determining a pop size / gen no split for the fit eval no
fitevalsplit = BFGeneratorForWords.getFactors(fitevals,2)[0]
psize, gno = fitevalsplit[0], fitevalsplit[1]
#loading a test model
trw, tew, MODEL = saveloadmodels.load(5,N)
word = BFAST2.BFInterpreter(random.choice(tew))
INPUTS, TARGETS = [''], [word]
print("TARGET WORD:", word)

tno = 10
#run RS with it
av = 0
for i in range(tno):
    fit, best, out = sampleSMSmoothing.sampleWord(TARGETS[0], copy.deepcopy(MODEL), N, exclimit=fitevals, horizlimit=mps)
    av += fit
print("\nRS", av/tno)

av = 0
av2 = 0
diff = 0
for i in range(tno):
    #fixed init pop
    programs = []
    while len(programs)<psize:
        programs.append(sampleSMSmoothing.sample(MODEL, N, horizlimit=mps))
        
    #run MIEDA on the fixed initial population to get HPs
    fit1, HPs, out = MIEDAfixed.run(INPUTS, TARGETS, N, copy.deepcopy(MODEL), FITNESSEVALS=fitevals, MAXPROGSIZE=mps, INITPOP=copy.deepcopy(programs))
    av2 += fit1

    #run IEDA with those HPs
    fit2, best, out = EDAfixed.run(INPUTS, TARGETS, N, copy.deepcopy(programs), copy.deepcopy(MODEL), *HPs)
    av += fit2
    diff += (fit1-fit2)

print("\nMIEDA", av2/tno)
print("\nIEDA", av/tno)
print("diff", diff/tno)
