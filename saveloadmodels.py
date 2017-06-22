import BFAST2, pickle, os, makeSMSmoothing

def load(size, N):
    if os.path.isfile(os.getcwd() + '/MODELS/' + str(size) + " " + str(N) + '.pkl'):
        with open(os.getcwd() + '/MODELS/' + str(size) + " " + str(N) + '.pkl', 'rb') as f:
            model = pickle.load(f)
            trw = pickle.load(f)
            tew = pickle.load(f)
            return trw, tew, model
    else:
        return save(size, N)

def save(size, N):
    #make a corpus of N small words using words.txt
    words = []
    with open(os.getcwd() + '/words.txt', 'r') as f:
        for word in f.readlines():
            wordstripped = word.strip('\n')
            if len(wordstripped)==size:
                words.append(wordstripped)
    print("Gathered words:", len(words))

    progs = []
    #find program versions in corpus
    for word in words:
        progs.append(open(os.getcwd() + '/WORDCORPUS/' + word + '.b','r').read())
    print("Got progs:", len(progs))

    #split into training and test data
    trw = progs[::2]
    tew = progs[1::2]
    print("Split:", len(trw), len(tew))

    #MAKE A MODEL
    MODEL = makeSMSmoothing.makeFromList(trw, N)

    #save model and training/test sets
    with open(os.getcwd() + '/MODELS/' + str(size) + " " + str(N) + '.pkl', 'wb') as f:
        pickle.dump(MODEL, f)
        pickle.dump(trw, f)
        pickle.dump(tew, f)
    return trw, tew, MODEL
