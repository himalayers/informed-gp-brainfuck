#meta GPEDA - evolve the right constants
import random, BFGeneratorForWords, BFAST2, EDA, pprint, copy, IGP
import saveloadmodels

def randomparamset(fitnessevals, MAXPROGSIZE):
    new = []
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
    new.append(round(random.random()*(MAXPROGSIZE/10))*9 + round(MAXPROGSIZE/10)) #MAXPROGSIZE
    #get rates to add to 1
    rate1 = round(random.random()*20)/20
    rate2 = round(random.random()*(1-rate1)*20)/20
    new.append([rate1, rate1+rate2]) #RATES
    return new

def printparamset(set1):
    print("POPSIZE     :", set1[0])
    print("GENNO       :", set1[1])
    print("MAXITERS    :", set1[2])
    print("MAXPROGSIZE :", set1[5])
    print("RATES       :", set1[6])

def crossover(set1, set2):
    cp = random.randint(2, len(set1)-2)
    return set1[:cp] + set2[cp:], set2[:cp] + set1[cp:]
    
def mutation(set1, FITNESSEVALS, MAXPROGSIZE):
    while True:
        mp = random.randint(0, len(set1)-1)
        if mp not in [3,4]:
            newset = randomparamset(FITNESSEVALS, MAXPROGSIZE)
            if mp == 0: #popsize
                return set1[:mp] + [newset[mp]] + [FITNESSEVALS/newset[mp]] + set1[mp+2:]
            elif mp == 1:
                return set1[:mp-1] + [FITNESSEVALS/newset[mp]] + [newset[mp]] + set1[mp+1:]
            else:
                return set1[:mp] + [newset[mp]] + set1[mp+1:]

def weightedChoice(fits):
   offset = random.random() #dict is normalized so no need to sum values
   for item, weight in fits:
      if offset < weight:
         return item
      offset -= weight

def run(INPUTS, TARGETS, N, MODEL, FITNESSEVALS, MAXPROGSIZE, verbose=-1):
    POPSIZE, GENNO, REPRATE, CROSSRATE = 10, 10, 0.33, 0.33
    base = [INPUTS, TARGETS, N, MODEL]
    #init pop
    population = [randomparamset(FITNESSEVALS, MAXPROGSIZE) for i in range(POPSIZE)]
    best = (None, (0,0))
    for n in range(GENNO):
        outputs = [(popset, IGP.run(*base[:4], *popset, verbose=-1)) for popset in population]
        #get best and see if we should terminate
        sortedoutputs = sorted(outputs, key=lambda x: x[1][0])
        #sortedfits = sorted(fits, key=lambda x: x[1])
        genbest = sortedoutputs[-1]
        if verbose==0:
            print("Generation:", n, "Best set:", genbest[0], "fit", genbest[1][0])
        if verbose in [0,1]:
            fitonly = [x[1][0] for x in outputs]
            EDA.printboxplot(fitonly)
        if genbest[1][0]>best[1][0]:
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
