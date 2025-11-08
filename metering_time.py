#!/usr/bin/env python3


import matplotlib.pyplot as plt
import time
import statistics
class Metric_time():
    def __init__(self):
        self.t=0
        self.data=[]
        self.count=0
    def add(self):
        self.data.append([])
    def mark(self,index=0):
        if index==self.count:
            self.t=time.time()
            self.count+=1
        else:
            self.data[index].append(time.time()-self.t)
            self.t=time.time()
    def view(self,labels=[],xlabel="Iterations",save=False):
        labels=range(len(self.data)) if labels==[] else labels
        plt.title("Time metric lines")
        plt.ylabel("Time,ms")
        plt.xlabel(xlabel)
        for y,label in zip(self.data,labels):
            plt.plot(range(len(y)),y,label=f'{label}, average: {round(statistics.mean(y),5)} ms')
        plt.legend()
        if save==True:
            plt.savefig('plot.png')