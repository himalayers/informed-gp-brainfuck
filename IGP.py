import BFAST2, copy, random, ModelAnalysis, saveloadmodels, sampleSMSmoothing, math, makeSMSmoothing
import numpy as np, fitfunctions

def printboxplot(fitnesses):
    NO = 50
    low, high = round(min(fitnesses)*NO), round(max(fitnesses)*NO)
    average = int(round(np.mean(fitnesses)*NO))
    anch1, anch2, anch3, anch4 = max(low-1, 0), average-low-1, high-average-1, NO-high-1
    print('|{}{}{}{}|'.format(' '*anch1 + 'L', ' '*anch2 + 'A', ' '*anch3 + 'H', ' '*anch4), "Average", average/NO)

def swapatpoint(prog1, prog2, cp):
    #swap the trees at this node
    body1, body2 = BFAST2.getbody(prog1, cp[:]), BFAST2.getbody(prog2, cp[:])
    temp = body1[cp[-1]]
    body1[cp[-1]] = body2[cp[-1]]
    body2[cp[-1]] = temp

def crossover(chosenprog1, chosenprog2, MODEL, N):
    prog1, prog2 = copy.deepcopy(chosenprog1), copy.deepcopy(chosenprog2)
    #find the common region - exclude roots
    commonregion = [node for node in BFAST2.nodedescrip(chosenprog1)[1:] if node in BFAST2.nodedescrip(chosenprog2)[1:]]
    #instead of choosing a random node from the common region, we find the node which results in the MOST LIKELY pair of children
    bestprob, bestcp = math.inf, [0]
    for cp in commonregion:
        #do the swap
        swapatpoint(prog1, prog2, cp)
        #find the probabilities
        probofchildren = -ModelAnalysis.sampprobSmoothing(prog1, MODEL, N) - ModelAnalysis.sampprobSmoothing(prog2, MODEL, N)
        #save cp no if good
        if probofchildren<bestprob:
            bestprob = probofchildren
            bestcp = cp
        #revert the swap (saves a bunch of deepcopies)
        swapatpoint(prog1, prog2, cp)
        
    #do the swap with the good cp
    swapatpoint(prog1, prog2, bestcp)
    return prog1, prog2

def mutation(chosenprog, XBOUNDS, YBOUND, MODEL, N):
    prog = copy.deepcopy(chosenprog)
    #choose a random body to mutate
    randbodynode = random.choice(BFAST2.nodedescrip(prog, onlyLoop=True))
    randbody = BFAST2.getbody(prog, randbodynode[:])
    #choose a random point in that body including the edge
    randpoint = random.randint(0, len(randbody))
    #append N<s>s onto start
    prevtoks = (['<s>']*N + [type(x) for x in randbody])[randpoint:randpoint+N]
    #use model to predict what token SHOULD be
    try:
        choice = sampleSMSmoothing.sampleNGrams(prevtoks, len(randbodynode)-1, MODEL)
    except:
        #if model can't say, choose at random
        choice = random.choice(BFAST2.classes)

    #if its advised to end right there, cut rand body short
    if choice=='<e>':
        randbody[:] = randbody[:randpoint]
        return prog
    newtoken = BFAST2.LOOP(BFAST2.create(XBOUNDS, YBOUND)) if choice==BFAST2.LOOP else choice(1)

    #add it if it was the end node
    if randpoint==len(randbody):
        randbody[:] = randbody + [newtoken]
    else:
        randbody[randpoint] = newtoken
    return prog

def mutationADV(chosenprog, XBOUNDS, YBOUND, MODEL, N):
    prog = copy.deepcopy(chosenprog)
    #choose a random body to mutate
    randbodynode = random.choice(BFAST2.nodedescrip(prog, onlyLoop=True))
    randbody = BFAST2.getbody(prog, randbodynode[:])
    #find the best node to mutate, that gives the highest gain in probability
    bestnode, bestmutate, bestprob = 0, BFAST2.leafconstructors[0], 10**1000
    for i, node in enumerate(randbody):
        prev = copy.deepcopy(node)
        for item in BFAST2.leafconstructors:
            randbody[i] = item
            probability = -ModelAnalysis.sampprobSmoothing(prog, MODEL, N)
            if probability<bestprob:
                bestnode, bestmutate, bestprob = i, item, probability
        randbody[i] = prev
    #perform the best node/mutation pair
    randbody[bestnode] = bestmutate
    return prog

def run(INPUTS, TARGETS, N, MODEL, POPSIZE=20, GENNO=100, MAXITERS=500, XBOUNDS=[2,10], YBOUND=1, MAXPROGSIZE=150, RATES=[0.33, 0.66], verbose=-1):
    #TRY INITTING WITH SAMPLE FROM MODEL
    programs = [sampleSMSmoothing.sample(MODEL, N, MAXPROGSIZE) for i in range(int(POPSIZE))]

    #readjust maxprogsize based on the sizes of the samples (they are not necessarily exactly maxprogsize)
    maxlen = max([len(BFAST2.unparseBF(prog)) for prog in programs])
    MAXPROGSIZE = max(maxlen, MAXPROGSIZE)
    
    best = (None, 0)
    for n in range(int(GENNO)):
        fitnesses = [(program, fitfunctions.fitness(program, INPUTS, TARGETS, MAXITERS)) for program in programs]
        #get best and see if we should terminate
        genbest = sorted(fitnesses, key=lambda x: x[1])[-1]
        if verbose==0:
            print("Generation:", n, "Best prog:", BFAST2.unparseBF(genbest[0]))
        if verbose in [0,1]:
            fitonly = [x[1] for x in fitnesses]
            printboxplot(fitonly)
        if genbest[1]>=best[1]:
            best = genbest
            if genbest[1]>=1:
                break
        #normalise fitnesses
        fitnesses = makeSMSmoothing.normaliseNgrams(dict(fitnesses))
        #generate new population
        newpop = []
        while len(newpop)<POPSIZE:
            #roulette wheel selection of one, or a pair
            goodpair = [sampleSMSmoothing.weightedChoice(dict(fitnesses))]
            roll = random.random()
            if roll<RATES[0]:
                #reproduction
                newpop.append(goodpair[0])
            elif roll<RATES[1]:
                #crossover
                goodpair.append(sampleSMSmoothing.weightedChoice(dict(fitnesses)))
                newmem1, newmem2 = crossover(goodpair[0], goodpair[1], MODEL, N)
                if len(BFAST2.unparseBF(newmem1))<=MAXPROGSIZE: #is this necessary?
                    newpop.append(newmem1)
                if len(BFAST2.unparseBF(newmem2))<=MAXPROGSIZE:
                    newpop.append(newmem2)
            else:
                #mutation
                mutate = mutation(goodpair[0], XBOUNDS, YBOUND, MODEL, N)
                if len(BFAST2.unparseBF(mutate))<=MAXPROGSIZE:
                    newpop.append(mutate)
        programs = newpop
        
    #get output of best program
    try:
        output = BFAST2.BFInterpreter(best[0], INPUTS[0])
    except BFAST2.TimedOutException as TOE:
        output = TOE.state.resStream[:len(TARGETS[0])]
    except BFAST2.StateException as SE:
        output = SE.state.resStream[:len(TARGETS[0])]
    if verbose in [0,1,2]:
        print('\nFINISHED===')
        print("Best prog:", BFAST2.unparseBF(best[0]), "of fitness:", best[1])
        print("output:", output)
    return best[1], best[0], output
