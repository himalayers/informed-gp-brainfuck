#make model on BF programs
import math, random

class Node(object):
    def __init__(self, number):
        self.number = number
class LT(Node):
    name = "LT"
class GT(Node):
    name = "GT"
class DOT(Node):
    name = "DOT"
class COM(Node):
    name = "COMMA"
class PLUS(Node):
    name = "PLUS"
class MINUS(Node):
    name = "MINUS"
class LOOP(object):
    def __init__(self, body):
        self.body = body
class ROOT(object):
    def __init__(self, body):
        self.body = body
    def contains(self, node):
        for thing in self.body:
            if isinstance(thing, node):
                return True
        return False
    
class StateException(Exception):
    def __init__(self, state):
        self.state = state
class UnexpectedTokenException(StateException):
    def __init__(self, token):
        self.token = token
class MismatchingBracketsException(StateException):
    pass
class UnexpectedNodeException(StateException):
    def __init__(self, node):
        self.node = node
class NeedMoreInputException(StateException):
    pass
class TimedOutException(StateException):
    pass
class CharOfNegativeException(StateException):
    pass
class OutOfBoundsException(StateException):
    pass
class NotBodyException(StateException):
    pass

leafset = ['<','>','.',',','+','-']
leafconstructors = [LT(1), GT(1), DOT(1), COM(1), PLUS(1), MINUS(1)]
leaftypes = [LT, GT, DOT, COM, PLUS, MINUS]
classes = [LT, GT, DOT, COM, PLUS, MINUS, LOOP]



def traversedescrip(tree, poses=[], pos=0, noLoops=False, onlyLoops=False):
    if isinstance(tree, (ROOT, LOOP)):
        descrips = []
        for i, item in enumerate(tree.body):
            descrip = traversedescrip(item, poses + [i], i, noLoops, onlyLoops)
            if isinstance(descrip, type(None)):
                pass
            elif isinstance(descrip[0], list):
                descrips.extend(descrip)
            else:
                descrips.append(descrip)
        if noLoops or isinstance(tree, ROOT):
            return descrips
        return [poses[:-1] + [pos]] + descrips
    elif not onlyLoops:
        return poses

def getbody(tree, poslist):
    if len(poslist)==1:
        return tree.body
    if not isinstance(tree, (ROOT, LOOP)):
        raise NotBodyException()
    temp = poslist[0]
    poslist.pop(0)
    return getbody(tree.body[temp], poslist)

'''returns the indices of all nodes in an AST'''
def nodedescrip(tree, noLoop=False, onlyLoop=False):
    if not noLoop: #add root node as loop
        return [[-1]] + traversedescrip(tree, noLoops=noLoop, onlyLoops=onlyLoop)
    return traversedescrip(tree, noLoops=noLoop, onlyLoops=onlyLoop)

def getsubloopstring(BFstring):
    stack = 0
    for i, char in enumerate(BFstring):
        if char=='[':
            stack+=1
        elif char==']':
            stack-=1
        if stack==0:
            return BFstring[1:i] #return dots in [...]
    raise MismatchingBracketsException()

def parse(BFsource):
    #return leaves as themselves constructed
    if len(BFsource)==1:
        return [leafconstructors[leafset.index(BFsource)]]
    
    temp = []
    i = 0
    while i<len(BFsource):
        if BFsource[i] in leafset:
            temp.append(leafconstructors[leafset.index(BFsource[i])]) #return just this without [] if just this
            i += 1
        elif BFsource[i]=='[':
            #find the subtree string
            subloop = getsubloopstring(BFsource[i:])
            #recurse on it if not empty
            if subloop!='':
                temp.append(LOOP(parse(subloop)))
            #skip ahead to past this loop
            i += len(subloop) + 2 #+2 accounts for brackets
        elif BFsource[i]==']':
            raise MismatchingBracketsException()
        else:
            raise UnexpectedTokenException(BFsource[i])
    return temp

'''
collapse a BF AST into single instructions by collating all same instructions into one with property = how many instructions in that chain
e.g. +++++ goes to +(5)
'''
def condenseBFTree(tree):
    if isinstance(tree, (LOOP, ROOT)):
        if len(tree.body)>1:
            prev = type(tree.body[0]) if type(tree.body[0])!=LOOP else type(None)
            chain = 1
            newbody = []
            for i, item in enumerate(tree.body[1:]):
                if isinstance(item, LOOP):
                    if prev!=type(None):
                        newbody.append(prev(chain)) #instantiate prev type with no chain
                    newbody.append(LOOP(condenseBFTree(item)))
                    prev, chain = type(None), 0
                elif isinstance(item, prev) and item!=None:
                    chain += 1
                else:
                    if prev!=type(None):
                        newbody.append(prev(chain)) #instantiate prev type with no chain
                    prev, chain = type(item), 1
            if chain>0:
                newbody.append(prev(chain)) #instantiate prev type with no chain
            return newbody
        elif isinstance(tree, LOOP):
            return condenseBFTree(tree.body[0])
        elif isinstance(tree, ROOT):
            temp = condenseBFTree(tree.body[0])
            return [LOOP(temp)]
    else:
        return [tree]

'''parse a BF program string into a BF AST'''
def parseBF(BFsource, condense=False):
    tree = ROOT(parse(BFsource))
    if condense:
        return ROOT(condenseBFTree(tree))
    return tree

'''unparse a BF AST into a BF program string'''
def unparseBF(tree):
    source = ''
    if isinstance(tree, (LT, GT, DOT, COM, PLUS, MINUS)):
        for i in range(tree.number):
            source += leafset[leaftypes.index(type(tree))]
    elif isinstance(tree, LOOP):
        source += '['
        for item in tree.body:
            source += unparseBF(item)
        source += ']'
    elif isinstance(tree, ROOT):
        for item in tree.body:
            source += unparseBF(item)
    else:
        raise UnexpectedNodeException(type(tree))
    return source

'''pretty print a BF AST'''
def pprint(tree, depth=0, indentLevel=4):
    indent = (' '*indentLevel)*depth
    if isinstance(tree, ROOT):
        print("ROOT")
        for item in tree.body:
            ndepth = depth + 1
            pprint(item, ndepth)
    elif isinstance(tree, LOOP):
        print(indent + "LOOP")
        for item in tree.body:
            ndepth = depth + 1
            pprint(item, ndepth)
    elif isinstance(tree, (PLUS, MINUS, COM, DOT, LT, GT)):
        print(indent + tree.name)
    else:
        raise UnexpectedNodeException(tree)

def create(xbounds, ybound, depth=0):
    body = []
    for i in range(random.randint(xbounds[0], xbounds[1])):
        #choose random thing
        nodechoice = random.choice(classes)
        if nodechoice==LOOP:
            if depth<=ybound:
                ndepth = depth + 1
                body.append(LOOP(create(xbounds, ybound, ndepth)))
            else:
                temp = random.choice(leafconstructors)
                body.append(temp)
        else:
            body.append(nodechoice(1))
    for x in body:
        if isinstance(x, list):
            print(body)
            exit()
    return body

'''create a random BF AST where loops and root sizes are within xbounds and maximum depth ybound'''
def randomTree(xbounds, ybound):
    return ROOT(create(xbounds, ybound))

class programState(object):
    def __init__(self, inputStream, maxiters):
        self.pool = [0]*30000
        self.p, self.inpi = 0,0
        self.resStream = ''
        self.iters, self.maxiters = 0, maxiters
        self.inputStream = inputStream
    def dump(self):
        print(' '.join([str(x) for x in self.pool][:30]))
        print(self.p)
        print(self.inputStream, self.resStream)
        print(' '*self.inpi + '^')
        print(self.iters, self.maxiters)

'''
run a BF AST, or BF program string, and return the output it gives
inputstream is the input characters passed to the BF program
maxiters is the number of iterations it runs for until it is terminated
'''
def BFInterpreter(tree, inputStream='', maxiters=1000):
    if isinstance(tree, str):
        tree = parseBF(tree)
    state = programState(inputStream, maxiters)
    execute(tree, state)
    return state.resStream

def execute(tree, state):
    for item in tree.body:
        if isinstance(item, PLUS):
            state.pool[state.p] += 1
        elif isinstance(item, MINUS):
            state.pool[state.p] -= 1
        elif isinstance(item, GT):
            if state.p>=len(state.pool):
                raise OutOfBoundsException(state)
            state.p += 1
        elif isinstance(item, LT):
            if state.p<-len(state.pool):
                raise OutOfBoundsException(state)
            state.p -= 1
        elif isinstance(item, COM):
            if state.inpi==len(state.inputStream):
                state.pool[state.p] = -1 #standards: -1, 0, 10 or repeating
            elif state.inpi>len(state.inputStream):
                raise NeedMoreInputException(state)
            else:
                state.pool[state.p] = ord(state.inputStream[state.inpi])
            state.inpi += 1
        elif isinstance(item, DOT):
            if state.pool[state.p]<0:
                raise CharOfNegativeException(state)
            state.resStream += chr(state.pool[state.p])
        elif isinstance(item, LOOP):
            while state.pool[state.p]!=0:
                execute(item, state)
        else:
            raise UnexpectedNodeException(item)
        if state.iters>=state.maxiters:
            raise TimedOutException(state)
        state.iters += 1
    
