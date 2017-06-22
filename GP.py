import BFAST2, copy, random, makeSMSmoothing, sampleSMSmoothing
import numpy as np, fitfunctions

def printboxplot(fitnesses):
    NO = 50
    low, high = round(min(fitnesses)*NO), round(max(fitnesses)*NO)
    average = int(round(np.mean(fitnesses)*NO))
    anch1, anch2, anch3, anch4 = max(low-1, 0), average-low-1, high-average-1, NO-high-1
    print('|{}{}{}{}|'.format(' '*anch1 + 'L', ' '*anch2 + 'A', ' '*anch3 + 'H', ' '*anch4), "Average", average/NO)

def crossover(chosenprog1, chosenprog2):
    prog1 = copy.deepcopy(chosenprog1)
    prog2 = copy.deepcopy(chosenprog2)
    #find the common region - exclude roots
    commonregion = [node for node in BFAST2.nodedescrip(prog1)[1:] if node in BFAST2.nodedescrip(prog2)[1:]]
    #choose a random node in this common region
    cp = random.choice(commonregion)
    #swap the trees at this node
    body1, body2 = BFAST2.getbody(prog1, cp[:]), BFAST2.getbody(prog2, cp[:])
    temp = body1[cp[-1]]
    body1[cp[-1]] = body2[cp[-1]]
    body2[cp[-1]] = temp
    return prog1, prog2

def mutation(chosenprog, XBOUNDS, YBOUND):
    prog = copy.deepcopy(chosenprog)
    #choose a random node to mutate
    randnode = random.choice(BFAST2.nodedescrip(prog))
    #choose a node to replace it
    choice = random.choice(BFAST2.classes)
    if choice==BFAST2.LOOP:
        mutationnode = BFAST2.LOOP(BFAST2.create(XBOUNDS, YBOUND))
    else:
        mutationnode = choice(1)
    BFAST2.getbody(prog, randnode)[randnode[-1]] = mutationnode
    return prog

def run(INPUTS, TARGETS, POPSIZE=100, GENNO=200, MAXITERS=500, XBOUNDS=[2,10], YBOUND=1, MAXPROGSIZE=150, RATES=[0.33, 0.66], verbose=-1):
    #initialise population randomly
    programs = [BFAST2.randomTree(XBOUNDS, YBOUND) for i in range(int(POPSIZE))]

    #readjust maxprogsize based on the sizes of the programs (they are not necessarily exactly maxprogsize)
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
                newmem1, newmem2 = crossover(goodpair[0], goodpair[1])
                if len(BFAST2.unparseBF(newmem1))<MAXPROGSIZE: #is this necessary?
                    newpop.append(newmem1)
                if len(BFAST2.unparseBF(newmem2))<MAXPROGSIZE:
                    newpop.append(newmem2)
            else:
                #mutation
                mutate = mutation(goodpair[0], XBOUNDS, YBOUND)
                if len(BFAST2.unparseBF(mutate))<MAXPROGSIZE:
                    newpop.append(mutate)
        programs = newpop

    #get output of best program
    try:
        output = BFAST2.BFInterpreter(best[0], INPUTS[0])
    except BFAST2.TimedOutException as TOE:
        output = TOE.state.resStream[:len(TARGETS[0])]
    except BFAST2.StateException as SE:
        output = SE.state.resStream[:len(TARGETS[0])]
    if verbose in [3]:
        print('\nFINISHED===')
        print("Best prog:", BFAST2.unparseBF(best[0]), "of fitness:", best[1])
        print("output:", output)
    if output==None:
        print(best[1], best[0])
        exit()
    return best[1], best[0], output
