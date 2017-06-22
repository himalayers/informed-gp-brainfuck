import BFAST2, copy, random#, makeSM, sampleSM
import makeSMSmoothing, sampleSMSmoothing, ModelAnalysis, BFGeneratorForWords
import numpy as np, sys, fitfunctions

def printboxplot(fitnesses):
    NO = 50
    low, high = round(min(fitnesses)*NO), round(max(fitnesses)*NO)
    average = int(round(np.mean(fitnesses)*NO))
    anch1, anch2, anch3, anch4 = max(low-1, 0), average-low-1, high-average-1, NO-high-1
    print('|{}{}{}{}|'.format(' '*anch1 + 'L', ' '*anch2 + 'A', ' '*anch3 + 'H', ' '*anch4), "Average", average/NO, "Best:", high/NO)

def run(INPUTS, TARGETS, N=5, INITPOP=[], model={}, ALPHA=0.9, PROGRATIO=0.9, POPSIZE=100, GENNO=200, MAXITERS=500, XBOUNDS=[2,10], YBOUND=1, MAXPROGSIZE=150, verbose=-1):
    TERMINATEFIT = 1
    targetprog = BFAST2.parseBF(BFGeneratorForWords.wordToBF(TARGETS[0]))
    if verbose in [0,1]:
        print("target prog:", BFAST2.unparseBF(targetprog))

    #initialise population with model unless given an init pop
    programs = INITPOP
    if programs==[]:
        if model!={}:
            #sample new population
            while len(programs)<POPSIZE:
                programs.append(sampleSMSmoothing.sample(model, N, horizlimit=MAXPROGSIZE))
        else:
            programs = [BFAST2.randomTree(XBOUNDS, YBOUND) for i in range(int(POPSIZE))]
            model = makeSMSmoothing.makeFromList(programs, N)

    best = (None, 0)
    for n in range(int(GENNO)):
        #find the probability of the word being sampled with the model
        if verbose in [0,1]:
            print("Prob of word being sampled as prog:", -ModelAnalysis.sampprobSmoothing(targetprog, model, N))
        
        fitnesses = [(program, fitfunctions.fitness(program, INPUTS, TARGETS, MAXITERS)) for program in programs]
        fitonly = [x[1] for x in fitnesses]
        #get best and see if we should terminate
        genbest = sorted(fitnesses, key=lambda x: x[1])[-1]
        if verbose==0:
            print("Generation:", n, "Best prog:", BFAST2.unparseBF(genbest[0]))
        if verbose in [0,1]:
            printboxplot(fitonly)
        if genbest[1]>=best[1]:
            best = genbest
            if genbest[1]>=TERMINATEFIT:
                break

        #normalise fitnesses
        fitnesses = makeSMSmoothing.normaliseNgrams(dict(fitnesses))

        #add the good part of the population to the model
        programs = sorted(programs, key=lambda x: fitfunctions.fitness(x, INPUTS, TARGETS, MAXITERS))[::-1]
        makeSMSmoothing.addListToModel(model, programs[:max(1,round(PROGRATIO*len(programs)))], N, ALPHA)

        #sample new pop
        newpop = []
        while len(newpop)<POPSIZE:
            newpop.append(sampleSMSmoothing.sample(model, N, horizlimit=MAXPROGSIZE))
        programs = newpop

    #get output of best program
    try:
        output = BFAST2.BFInterpreter(best[0], INPUTS[0])
    except BFAST2.TimedOutException as TOE:
        output = TOE.state.resStream[:len(TARGETS[0])]
    except BFAST2.StateException as SE:
        output = SE.state.resStream[:len(TARGETS[0])]
    except:
        output = ''
    if verbose in [0,1,2]:
        print('\nFINISHED===')
        print("Best prog:", BFAST2.unparseBF(best[0]), "of fitness:", best[1])
        print("output:", output)
    return best[1], best[0], output
