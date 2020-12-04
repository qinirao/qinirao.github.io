from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import multiprocessing

def dist(df):
    res = pd.DataFrame(index=np.arange(df.shape[1]), columns = np.arange(df.shape[1]))
    for i in range(df.shape[1]):
        res.iloc[i,i] = 0
        for j in range(i + 1, df.shape[1]):
            #d,p = fastdtw(df[i].dropna(),df[j].dropna(), dist = euclidean)
            d,p = fastdtw(df[i].dropna().values, df[j].dropna().values, dist = euclidean)
            res.iloc[i,j] = d
            res.iloc[j,i] = d
    return res

def cal(x):
    i = x[0]
    j = x[1]
    df = x[2]
    d,p = fastdtw(df[i].dropna().values, df[j].dropna().values, dist = euclidean)
#    res.iloc[i,j] = d
#    res.iloc[j,i] = d
    return [i, j , d]

class mdist(object):
    df = None
    res = None
    pool = None
    xs = []

    def __init__(self,df):
        self.df = df
        self.res = pd.DataFrame(index=np.arange(df.shape[1]), columns = np.arange(df.shape[1]))
        for i in range(df.shape[1]):
            self.res.iloc[i,i] = 0
            for j in range(i + 1, df.shape[1]):
                self.xs.append([i,j, self.df])

    def work(self):
        df = self.df
        res = self.res
        cores = multiprocessing.cpu_count()
        self.pool = multiprocessing.Pool(processes=cores)
        try:
            ret = self.pool.map(cal, self.xs)
            for x in ret:
                i = x[0]
                j = x[1]
                res.iloc[i,j] = x[2]
                res.iloc[j,i] = x[2]
        except Exception as e:
            print(e)
        self.pool.terminate()
        self.pool.join()
        return res




class qu(object):
    id=[]
    count=0
    df = None

    def __init__(self,df):
        self.df = df
        self.count = df.shape[1]

    def reset(self):
        self.id.clear()
        self.count = self.df.shape[1]
        i=0
        while i< self.count:
            self.id.append(int(i))
            i+=1

    def connected(self,p,q):
        if self.find(p) == self.find(q):
            return True
        else:
            return False

    def find(self,p):
        while (p != self.id[p]):
            p = self.id[p]
        return p

    def union(self,p,q):
        idq = self.find(q)
        idp = self.find(p)
        if not self.connected(p,q):
            self.id[idp]=idq
            self.count -=1
    def out(self, val):
        self.reset()
        df = self.df
        pas = []
        pmap = {}
        for i in range(df.shape[1]):
            for j in range(i + 1, df.shape[1]):
                if (df.iloc[i, j] < val):
                    self.union(i, j)
        for i in range(df.shape[1]):
            p = self.find(i)
            if p not in pas:
                pas.append(p)
        for p in pas:
            pmap[p] = []
        for i in range(df.shape[1]):
            p = self.find(i)
            pmap[p].append(int(i))
        return pd.DataFrame.from_dict(pmap, orient='index')
