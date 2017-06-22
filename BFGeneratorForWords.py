#wordtoBF
import BFAST2
def nthroot(val, n):
    ret = int(val**(1./n))
    return ret + 1 if (ret + 1) ** n == val else ret

"""
consider only permutations
consider only factor groups that outweigh their loop cost / current global cost
"""
def getFactors(mp, fno):
    #we do this by trying each factor of mp to nth root, then finding factors for divided number
    factorpairs = []
    if fno==1: #if we're looking for only 1 factor, clearly itself
        return [[int(mp)]]
    for i in range(2, nthroot(mp, fno)+1):
        if mp % i == 0:
            nfno = fno - 1
            for pair in [[i] + x for x in getFactors(mp/i, nfno)]: #unpack returned factorpair list
                factorpairs.append(pair) 
    return factorpairs
            
def getBestFactors(mp, first=False):
    globalbestcost = mp
    factor = 1
    for i in range(2,4):
        factorgroups = getFactors(mp, i)
        if len(factorgroups)>0:
            distances = [abs(x[0] - x[1]) for x in factorgroups]
            bestfactorgroup = factorgroups[distances.index(min(distances))]
            if first:
                factorcost = sum(bestfactorgroup)+6*(i-1)
            else:
                factorcost = 2 + sum(bestfactorgroup) + 5*(i-1) + 2*(i-2) 
            #if the cost of this factor group is smaller than best global cost, assign!
            if factorcost<globalbestcost:
                globalbestcost = factorcost
                factor = bestfactorgroup
    return factor, globalbestcost

def getBestFactorsRange(mp, first=False):
    dist = min(mp, 10)
    #find closest, smallest number of factors of mp
    factors, num, gcost = [mp], mp, mp
    for i in range(-dist, dist+1): #search dist around the mp
        temp = mp + i
        factorgroup, cost = getBestFactors(temp, first)
        if cost+abs(i)<gcost: #factor in having to traverse to goal no. after making no.
            gcost, num, factors = cost+abs(i), mp + i, factorgroup
    return num, factors

def writeNumber(mp):
    line = ''
    num, factors = getBestFactorsRange(abs(mp))
    for i, factor in enumerate(factors):
        if i!=len(factors)-1:
            line += '>' + '+'*factor + '[-'
        else:
            line += '<'*(len(factors)-1) + ('+'*factor if mp>0 else '-'*factor) + '>'*(len(factors)-1) + ']<'*(len(factors)-1)
    if mp>0:
        line += '+'*abs(num-abs(mp)) if num-abs(mp)<0 else '-'*(num-abs(mp))
    else:
        line += '-'*abs(num-abs(mp)) if num-abs(mp)<0 else '+'*(num-abs(mp))
    return line

def wordToBF(word, verify=False):
    #convert all chars in word to ascii numbers
    prog = ''
    vals = [ord(char) for char in word]
    #find the average
    mp = round(sum(vals)/len(vals))
    #find best way of writing mp
    num, factors = getBestFactorsRange(mp, first=True)
    #now write mp
    for i, factor in enumerate(factors):
        if i!=len(factors)-1:
            prog += '+'*factor + '[->'
        else:
            prog += '+'*factor
    prog += ('<]'*(len(factors)-1) + '>'*(len(factors)-1))
    prog += '+'*abs(num-mp) if num-mp<0 else '-'*(num-mp)
    #reach each char from mp and output it
    for char in word:
        diff = ord(char)-mp
        prog += writeNumber(diff)
        prog += '.'
        mp += diff
    #verify output with interpreter
    if verify:
        assert(word==BFAST2.BFInterpreter(BFAST2.parseBF(prog)))
    return prog

def wordToBFNoFurtherLoops(word, verify=False):
    #convert all chars in word to ascii numbers
    prog = ''
    vals = [ord(char) for char in word]
    #find the average
    mp = round(sum(vals)/len(vals))
    #find best way of writing mp
    num, factors = getBestFactorsRange(mp, first=True)
    #now write mp
    for i, factor in enumerate(factors):
        if i!=len(factors)-1:
            prog += '+'*factor + '[->'
        else:
            prog += '+'*factor
    prog += ('<]'*(len(factors)-1) + '>'*(len(factors)-1))
    prog += '+'*abs(num-mp) if num-mp<0 else '-'*(num-mp)
    #reach each char from mp and output it
    for char in word:
        diff = ord(char)-mp
        prog += -diff*'-' if diff<0 else diff*'+'
        prog += '.'
        mp += diff
    #verify output with interpreter
    if verify:
        assert(word==BFAST2.BFInterpreter(BFAST2.parseBF(prog)))
    return prog

def wordToBFNoLoops(word, verify=False):
    #convert all chars in word to ascii numbers
    prog = ''
    mp = 0
    #reach each char from mp and output it
    for char in word:
        diff = ord(char)-mp
        prog += -diff*'-' if diff<0 else diff*'+'
        prog += '.'
        mp += diff
    #verify output with interpreter
    if verify:
        assert(word==BFAST2.BFInterpreter(BFAST2.parseBF(prog)))
    return prog
