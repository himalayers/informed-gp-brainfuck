#meta GPEDA - evolve the right constants
import random, BFGeneratorForWords, BFAST2, EDA, pprint, copy, EDAfixed

def randomparamset(fitnessevals, MAXPROGSIZE):
    new = []
    new.append(random.random()) #ALPHA
    new.append(random.random()) #PROGRATIO
    #get factor pairs for popsize and genno and choose one
    factorpairs = BFGeneratorForWords.getFactors(fitnessevals,2)
    choice = random.choice(factorpairs)
    if random.random()<0.5:
        choice = choice[::-1]
    new.append(choice[0]) #POPSIZE
    new.append(choice[1]) #GENNO
    new.append(round(random.random()*10)*100) #MAXITERS
    new.append(tuple([2,10])) #XBOUNDS
    new.append(1) #YBOUND
    
    new.append(round(random.random()*(MAXPROGSIZE/10))*10) #MAXPROGSIZE
    return new

def printparamset(set1):
    print("ALPHA      :", set1[0])
    print("PROGRATIO  :", set1[1])
    print("POPSIZE    :", set1[2])
    print("GENNO      :", set1[3])
    print("MAXITERS   :", set1[4])
    print("MAXPROGSIZE:", set1[7])

def crossover(set1, set2):
    cp = random.randint(2, len(set1)-2)
    return set1[:cp] + set2[cp:], set2[:cp] + set1[cp:]
    
def mutation(set1, FITNESSEVALS, MAXPROGSIZE):
    while True:
        mp = random.randint(0, len(set1)-1)
        if mp not in [5,6]:
            newset = randomparamset(FITNESSEVALS, MAXPROGSIZE)
            if mp == 2: #popsize
                return set1[:mp] + [newset[mp]] + [FITNESSEVALS/newset[mp]] + set1[mp+2:]
            elif mp == 3:
                return set1[:mp-1] + [FITNESSEVALS/newset[mp]] + [newset[mp]] + set1[mp+1:]
            else:
                return set1[:mp] + [newset[mp]] + set1[mp+1:]

def weightedChoice(fits):
   offset = random.random() #dict is normalized so no need to sum values
   for item, weight in fits:
      if offset < weight:
         return item
      offset -= weight

def run(INPUTS, TARGETS, N, MODEL, FITNESSEVALS, MAXPROGSIZE, INITPOP, verbose=-1):
    POPSIZE, GENNO, REPRATE, CROSSRATE = 10, 10, 0.33, 0.33
    base = [INPUTS, TARGETS, N, INITPOP, MODEL]
    #init pop
    population = [randomparamset(FITNESSEVALS, MAXPROGSIZE) for i in range(POPSIZE)]
    best = (None, (0,0))
    for n in range(GENNO):
        outputs = [(popset, EDAfixed.run(*base[:3], copy.deepcopy(INITPOP), copy.deepcopy(MODEL), *popset)) for popset in population]
        #get best and see if we should terminate
        sortedoutputs = sorted(outputs, key=lambda x: x[1][0])
        #sortedfits = sorted(fits, key=lambda x: x[1])
        genbest = sortedoutputs[-1]
        if verbose==0:
            print("Generation:", n, "Best set:", genbest[0], "fit", genbest[1][0])
        if verbose in [0,1]:
            fitonly = [x[1][0] for x in outputs]
            EDA.printboxplot(fitonly)
        if genbest[1][0]>=best[1][0]:
            best = genbest
            if genbest[1][0]>=1:
                break
        #normalise fitnesses
        fits = [(popset, x[0]) for popset, x in outputs]
        total = sum([x[1] for x in fits])
        if total==0:
            break
        fits = [(x[0], x[1]/total) for x in fits]
        #generate new population
        newpop = []
        while len(newpop)<POPSIZE:
            #roulette wheel selection of one, or a pair
            goodpair = [weightedChoice(fits)]
            roll = random.random()
            if roll<REPRATE:
                #reproduction
                newpop.append(goodpair[0])
            elif roll<CROSSRATE:
                #crossover
                goodpair.append(weightedChoice(fits))
                newmem1, newmem2 = crossover(goodpair[0], goodpair[1])
                newpop.append(newmem1)
                newpop.append(newmem2)
            else:
                #mutation
                mutate = mutation(goodpair[0], FITNESSEVALS, MAXPROGSIZE)
                newpop.append(mutate)
        population = newpop #do we need to deepcopy here?

    if verbose in [0,1,2]:
        print('\nFINISHED===')
        print("Best set:")
        printparamset(best[0])
        print("of fit:", best[1][0])
        print("best prog using set:", best[1][1], "of output", best[1][2])
    return best[1][0], best[0], best[1][2] #fitness, set, output

