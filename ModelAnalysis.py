import BFAST2
import os, random, math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
            
'''find progs prob of being sampled w.r.t a model'''
def sampprob(prog, ngrams, N, depth=0):
    #look at each token in the prog
    prev = ['<s>']*N
    prob = 0
    for i, token in enumerate(prog.body):
        #find the previous things in ngram model
        if tuple(prev) in ngrams[depth]:
            nextdict = ngrams[depth][tuple(prev)]
            #using that dict, find the prob of hitting the next token
            if type(token) in nextdict:
                prob += math.log(nextdict[type(token)], 10) #use log addition to avoid tiny numbers = 0
            else:
                #give it the average prob it would've had
                prob += -math.inf #math.log(0.1) #0.000000001
        else:
            prob += -math.inf #math.log(0.1)
        
        #update prev
        prev = prev[1:] + [type(token)]
        
        #recurse
        if isinstance(token, BFAST2.LOOP):
            ndepth = depth + 1
            prob += sampprob(token, ngrams, N, ndepth)
    return prob

'''find progs prob of being sampled w.r.t a model that implements back-off smoothing'''
def sampprobSmoothing(prog, ngrams, N, depth=0):
    prev = ['<s>']*N
    prob = 0
    for i, token in enumerate(prog.body):
        if depth in ngrams[N]:
            if tuple(prev) in ngrams[N][depth] and type(token) in ngrams[N][depth][tuple(prev)]:
                prob += math.log(ngrams[N][depth][tuple(prev)][type(token)], 10)
            else:
                #find the prob in back-off
                n = N-1
                while True:
                    if n==0:
                        #Back-off counter-measure
                        prob += math.log((1/7)**N, 10)
                        break
                    else:
                        if tuple(prev[-n:]) in ngrams[n][depth] and type(token) in ngrams[n][depth][tuple(prev[-n:])]:
                            prob += math.log(ngrams[n][depth][tuple(prev[-n:])][type(token)] * (1/7)**(N-n), 10) #add uniform distribution chance to access the backed-off ngram
                            break
                        n -= 1
                        
        else:
            prob += -math.inf

        #update prev
        prev = prev[1:] + [type(token)]

        #recurse
        if isinstance(token, BFAST2.LOOP):
            ndepth = depth + 1
            prob += sampprobSmoothing(token, ngrams, N, ndepth)
    return prob
