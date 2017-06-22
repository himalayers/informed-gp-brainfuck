#make sm from BF corpus
import BFAST2, pickle, os, math
ngrams = {}

#normalize
def normaliseNgrams(curdict=ngrams):
    #if final dict, normalise
    if not isinstance(list(curdict.values())[0], dict):
        total = sum(curdict.values())
        
        #handle special case of all 0s!
        if total == 0:
            for key in curdict.keys():
                curdict[key] = 1
            total = len(curdict.keys())
            
        tempdict = {}
        for sequence, freq in curdict.items():
            tempdict[sequence] = freq/total
        return tempdict
    #else, append result
    tempdict = {}
    for key, keydict in curdict.items():
        tempdict[key] = normaliseNgrams(keydict)
    return tempdict

#checks args in exact order they appear.
def addNGram(args, curdict=ngrams, i=0):
    ni = i + 1
    #if ith arg in the dict, do for i+1th arg and dict
    if args[i] in curdict:
        if args[i]==args[-1]:
            curdict[args[i]] += 1
        else:
            newdict = curdict[args[i]]
            addNGram(args, newdict, ni)
    else:
        #else initialise all dicts from i to the end of args
        for j in range(i, len(args)-1):
            curdict[args[j]] = {}
            curdict = curdict[args[j]]
        #and add the final 1
        curdict[args[len(args)-1]] = 1

"""assumed first node given is a root node"""
def addNGrams(tree, model, N, depth=0):
    #make ngrams on the body
    types = [type(x) for x in tree.body]
    for i, item in enumerate(tree.body):
        addNGram([N, depth, tuple((['<s>']*N + types)[:i+N][-N:]), type(item)], curdict=model)
    #add a terminator
    addNGram([N, depth, tuple((['<s>']*N + types)[-N:]), '<e>'], curdict=model)

    #recurse on any LOOP nodes
    for item in tree.body:
        if isinstance(item, BFAST2.LOOP):
            ndepth = depth + 1
            addNGrams(item, model, N, ndepth)

def makeFromCorpus(corpusPath, N=3, leaveoneout=-1):
    model = {}
    for dirpath, dirnames, filenames in os.walk(os.getcwd() + corpusPath):
        for name in filenames:
            if leaveoneout==-1 or name!=leaveoneout:
                for i in range(1,N+1):
                    addNGrams(BFAST2.parseBF(open(os.path.join(dirpath, name)).read()), model, i)
    return normaliseNgrams(model)

def makeFromList(progs, N):
    model = {}
    for prog in progs:
        for i in range(1,N+1):
            if isinstance(prog, BFAST2.ROOT):
                addNGrams(prog, model, i)
            else:
                addNGrams(BFAST2.parseBF(prog), model, i)
    return normaliseNgrams(model)

def makeFromListInit(progs, N, startingpointmodel=-1):
    for prog in progs:
        addNGrams(BFAST2.parseBF(prog), startingpointmodel, N)
    return startingpointmodel

def addListToModel(model, progs, N, ALPHA=0.5): #alpha=0 gives no influence, 1 simply outputs the new model
    #compile ngrams for the prog list
    if len(progs)==0:
        print("why?")
        exit()
    addmodel = makeFromList(progs, N)
    #add this to the existing model
    #else add it as 1 prob mass
    for N in addmodel:
        if N in model:
            for depth in addmodel[N]:
                if depth in model[N]:
                    for sequence in addmodel[N][depth]:
                        if sequence in model[N][depth]:
                            #if it exists in model, redistribute the probability mass appropriately
                            #newprob = old + (new-old)*alpha
                            #synchronize them
                            for token in addmodel[N][depth][sequence]:
                                if token not in model[N][depth][sequence]:
                                    model[N][depth][sequence][token] = 0
                            for token in model[N][depth][sequence]:
                                if token not in addmodel[N][depth][sequence]:
                                    addmodel[N][depth][sequence][token] = 0

                            #change probs
                            probsum = 0
                            for token in model[N][depth][sequence]:
                                new, old = addmodel[N][depth][sequence][token], model[N][depth][sequence][token]
                                newprob = old + (new-old)*ALPHA
                                probsum += newprob
                                model[N][depth][sequence][token] = newprob
                                
                            #normalise...
                            for token in model[N][depth][sequence]:
                                model[N][depth][sequence][token] /= probsum
                        else:
                            model[N][depth][sequence] = addmodel[N][depth][sequence]
                else:
                    model[N][depth] = addmodel[N][depth]
        else:
            model[N] = addmodel[N]
