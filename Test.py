import saveloadmodels, BFAST2, random, BFGeneratorForWords, copy
import EDA, GP, MGP, MIEDA, IGP, MIGP, sampleSMSmoothing, US

# constants
N, fitevals, mps = 5, 100, 150
# determining a pop size / gen no split for the fit eval no
fitevalsplit = BFGeneratorForWords.getFactors(fitevals,2)[0]
psize, gno = fitevalsplit[0], fitevalsplit[1]
#loading a test model
trw, tew, MODEL = saveloadmodels.load(5,N)
word = BFAST2.BFInterpreter(random.choice(tew))
INPUTS, TARGETS = [''], [word]
print("TARGET WORD:", word)

fit, best, out = EDA.run(INPUTS, TARGETS, N, {}, POPSIZE=psize, GENNO=gno, MAXPROGSIZE=mps)
print("EDA", fit, out)

fit, best, out = MIEDA.run(INPUTS, TARGETS, N, {}, FITNESSEVALS=fitevals, MAXPROGSIZE=mps)
print("MEDA", fit, out)

fit, best, out = EDA.run(INPUTS, TARGETS, N, copy.deepcopy(MODEL), POPSIZE=psize, GENNO=gno, MAXPROGSIZE=mps)
print("IEDA", fit, out)

fit, best, out = MIEDA.run(INPUTS, TARGETS, N, copy.deepcopy(MODEL), FITNESSEVALS=fitevals, MAXPROGSIZE=mps)
print("MIEDA", fit, out)

fit, best, out = GP.run(INPUTS, TARGETS, POPSIZE=psize, GENNO=gno, MAXPROGSIZE=mps)
print("\nGP", fit, out)

fit, best, out = MGP.run(INPUTS, TARGETS, FITNESSEVALS=fitevals, MAXPROGSIZE=mps)
print("MGP", fit, out)

fit, best, out = IGP.run(INPUTS, TARGETS, N, copy.deepcopy(MODEL), POPSIZE=psize, GENNO=gno, MAXPROGSIZE=mps)
print("IGP", fit, out)

fit, best, out = MIGP.run(INPUTS, TARGETS, N, copy.deepcopy(MODEL), FITNESSEVALS=fitevals, MAXPROGSIZE=mps)
print("MIGP", fit, out)

fit, best, out = sampleSMSmoothing.sampleWord(TARGETS[0], copy.deepcopy(MODEL), N, exclimit=fitevals, horizlimit=mps)
print("\nRS", fit, out)

fit, best, out = US.sampleWord(TARGETS[0], exclimit=fitevals, horizlimit=mps)
print("US", fit, out)
