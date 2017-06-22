#sample SM with BF
import BFAST2, pickle, os, random, sys, BFGeneratorForWords, fitfunctions

class TokenNotInModelException(Exception):
    pass

def weightedChoice(d):
   offset = random.random() #dict is normalized so no need to sum values
   for k, v in d.items():
      if offset < v:
         return k
      offset -= v

def sampleNGrams(prevtoks, depth, ngrams):
    # backoff smoothing
    chosenN = min(max(ngrams.keys()), len(prevtoks)) #chosen=max(ngrams.keys())
    assert chosenN>=0 #avoid infinite loops
    assert len(prevtoks)==chosenN #ensure prevtoks is sufficient size
    while True:
        if depth in ngrams[chosenN]:
            modprevtoks = tuple(prevtoks[-chosenN:])
            if modprevtoks in ngrams[chosenN][depth]:
                return weightedChoice(ngrams[chosenN][depth][modprevtoks])
        #otherwise backoff to N-1
        chosenN -= 1
        if chosenN==0:
            #chance of this should be very, very, very, very low
            #i.e. token would have to not exist in corpus anywhere
            raise TokenNotInModelException()

def construct(ngrams, N, horizlimit, depth=0):
    #we start sampling with N <s>s
    prevTokens = ['<s>']*N
    children = []
    #we continue until <e> recommended
    while True:
        global horiznow
        nexttoken = sampleNGrams(prevTokens[-N:], depth, ngrams)
        if nexttoken=='<e>' or (horiznow>horizlimit and len(children)>=1):
            break
        horiznow += 1
        #if its a leaf, instantiate and append, else instantiate LOOP recursively
        if nexttoken==BFAST2.LOOP:
            ndepth = depth + 1
            children.append(BFAST2.LOOP(construct(ngrams, N, horizlimit, depth=ndepth)))
            prevTokens.append(BFAST2.LOOP)
        else:
            children.append(nexttoken(1))
            prevTokens.append(nexttoken)
    return children

def sample(ngrams, N, horizlimit):
    global horiznow
    horiznow = 0
    return BFAST2.ROOT(construct(ngrams, N, horizlimit))

def sampleWord(word, model, N, limit=1, maxiters=500, exclimit=10000, horizlimit=150):
    besttree, bestfit, iters = BFAST2.ROOT([]), 0, 0
    while True:
        tree = sample(model, N, horizlimit)
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
