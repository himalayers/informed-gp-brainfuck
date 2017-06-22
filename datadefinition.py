import pickle, os, pprint
import matplotlib as mpl, numpy as np, matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class data(object):
    def __init__(self, datasets, fitevals, MPS, accuracies, nrange, sizerange, descrip=''):
        #mieda, migp, rs, meda, mgp
        self.mieda = datasets[0]
        self.migp = datasets[1]
        self.rs = datasets[2]
        self.meda = datasets[3]
        self.mgp = datasets[4]
        self.us = datasets[5]
        self.fitevals = fitevals
        self.MPS = MPS
        self.accuracies = accuracies
        self.nrange = nrange
        self.sizerange = sizerange
        self.sets = [self.mieda, self.migp, self.rs, self.meda, self.mgp, self.us]
        self.descrip = '_' + descrip
    def save(self):
        nrange = str(self.nrange[0]) + 'to' + str(self.nrange[-1])
        sizerange = str(self.sizerange[0]) + 'to' + str(self.sizerange[-1])
        sets = ''.join(['0' if x==0 else '1' for x in self.sets])
        with open('DATA_' + str(self.fitevals) + '_' + str(self.MPS) + '_' + nrange + '_' + sizerange + '_' + sets + self.descrip + '.pkl', 'wb') as f:
            pickle.dump(self, f)
    @staticmethod
    def loaddata():
        files, i = [], 0
        for file in os.listdir():
            if file[:5]=='DATA_':
                files.append(file)
                print(i, file)
                i += 1
        toload = input("Select file to load.\n")
        with open(files[int(toload)], 'rb') as f:
            return pickle.load(f)
    def addData(self, newsets):
        for i, dataset in enumerate(newsets):
            if dataset!=0 and self.sets[i]==0:
                self.sets[i] = dataset

    '''
    x,y,zticks all decide the range of the graph that is plotted i.e. xticks=[2,3,4] would plot sizes=2,3,4
    zslice decides what slice of z the graph is plotted for. anything outside is cut off
    draw determines which datasets are to be plotted, 1=plot, 0=don't plot
    '''
    def plot(self, xticks=None, yticks=None, zticks=None, zslice=[0,1], draw=[1,1,1,1,1,1]):
        xticks, yticks = self.sizerange if xticks==None else xticks, self.nrange if yticks==None else yticks
        x,y = np.meshgrid(self.sizerange, self.nrange)
        fig = plt.figure()
        ax = plt.subplot(projection='3d')
        names = ['MIEDA', 'RS', 'MIGP', 'MEDA', 'MGP', 'US']
        colours = ['steelblue', 'darkorange', 'green', 'purple', 'red', 'brown']
        legends, j = [], 0
        for i, dataset in enumerate(self.sets):
            if dataset!=0 and draw[i]!=0:
                
                z = dataset
                #remove all ns sets from the data corresponding to the slice being looked at
                if len(xticks)<len(self.sizerange):
                    xtemp = xticks
                    delxrange = self.sizerange[:]
                    for m in xticks:
                        if m in self.sizerange:
                            delxrange.remove(m)
                    delxrange = [a-1 for a in delxrange]
                    for m in delxrange[::-1]:
                        del z[m]
                else:
                    xtemp = self.sizerange
                if len(yticks)<len(self.nrange):
                    ytemp = yticks
                    delyrange = self.nrange[:]
                    for m in yticks:
                        if m in self.nrange:
                            delyrange.remove(m)
                    delyrange = [a-1 for a in delyrange]
                    for m in delyrange[::-1]:
                        for k in z:
                            del k[m]
                else:
                    ytemp = self.nrange
                x,y = np.meshgrid(xtemp, ytemp)
                for m in range(len(z)):
                    for k in range(len(z[m])):
                        if z[m][k]<zslice[0]:
                            z[m][k] = np.nan
                a = ax.plot_surface(x,y,np.array(z).T, color=colours[j])
                legends.append([mpl.lines.Line2D([0],[0], linestyle="none", c=colours[j], marker = 'o'), names[i]])
                j += 1

        ax.legend([x[0] for x in legends], [x[1] for x in legends], numpoints=1)
        ax.view_init(elev=18, azim=-40)
        ax.set_xlabel('Size of target word')
        ax.set_ylabel('N')
        ax.set_zlabel('Fitness')
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        ax.set_xbound(xticks[0], xticks[-1])
        ax.set_ybound(yticks[0], yticks[-1])
        if zticks!=None:
            ax.set_zbound(zticks[0], zticks[-1])
        plt.show()
        
if __name__=='__main__':
    d1 = data.loaddata()
    d1.plot()
