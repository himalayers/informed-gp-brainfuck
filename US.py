import BFAST2, fitfunctions

def uniformsample(horizlimit):
    return BFAST2.randomTree([2,10], 4)

def sampleWord(word, limit=1, maxiters=500, exclimit=10000, horizlimit=150):
    besttree, bestfit, iters = BFAST2.ROOT([]), 0, 0
    while True:
        tree = uniformsample(horizlimit)
        fitness = fitfunctions.fitness(tree, [''], [word], maxiters)
        if fitness>bestfit:
            bestfit, besttree = fitness, tree
        if bestfit >= limit or iters > exclimit:
            try:
                output = BFAST2.BFInterpreter(besttree, maxiters=maxiters)
            except BFAST2.TimedOutException as TOE:
                output = TOE.state.resStream[:len(word)]
            except:
                output = "FAILED ON RUN"
            return bestfit, BFAST2.unparseBF(besttree), output
        iters += 1
