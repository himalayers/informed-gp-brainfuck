import BFAST2
#fitness functions
def ordinal(output, target):
    #ensure same length
    diff = len(output)-len(target)
    if diff>0:
        output = output[:-diff]
    elif diff<0:
        output += chr(0)*abs(diff)
    #ordinal distance
    ordindist = [abs(ord(x)-ord(y)) for x,y in zip(output, target)]
    return max(1-(sum(ordindist)/sum([ord(x) for x in target])), 0) #cap at 0
    
def hamming(output, target):
    #ensure same length
    diff = len(output)-len(target)
    if diff<0:
        output += ' '*(-diff)
    elif diff>0:
        output = output[:-diff]
    #hamming distance
    hamdist = [1 if x==y else 0 for x,y in zip(output, target)]
    return sum(hamdist)/len(target)

def ordinalandhamming(output, target):
    return (ordinal(output, target) + hamming(output, target)) / 2

def fitness(prog, INPUTS, TARGETS, MAXITERS):
    fitfunction = ordinal
    #for each input target pair
    fitnesses = 0
    for i in range(len(INPUTS)):
        try:
            output = BFAST2.BFInterpreter(prog, INPUTS[i], MAXITERS)
            fitnesses += fitfunction(output, TARGETS[i])
        except BFAST2.TimedOutException as TOE:
            fitnesses += fitfunction(TOE.state.resStream, TARGETS[i]) #ensure loops stay in gene pool
        except:
            pass
    #average
    fitnesses /= len(INPUTS)
    return fitnesses
