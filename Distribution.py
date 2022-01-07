import numpy as np
from random import randint

class Distribution:
    def __init__(self, tasks, devkoef, M, N, population = 500, fixedsize = 50, mutchance = 0.15):
        self.mutchance = mutchance * 100
        self.population = population
        self.fixedsize = fixedsize
        self.tasksNum = N
        self.devNum = M
        self.tasks = tasks
        self.devkoef = devkoef
        self.distrn = np.array([[randint(0, self.devNum-1) for i in range(self.tasksNum)] for i in range(self.population)])

    def checksus(self, fitness, start):
        F = np.sum(fitness, axis = 0)[0]
        Distance = F/self.fixedsize
        pointers = [start + i*Distance for i in range(self.fixedsize)]
        keep = []
        ind = 0
        for p in pointers:
            while np.sum(fitness[:ind+1], axis = 0)[0] < p:
                ind += 1
            keep.append(int(fitness[ind][1]))
        return keep

    def countFit(self):
        fitness = []
        for indivindx in range(len(self.distrn)):
            fit = [0 for i in range(self.devNum)]
            for indx in range(self.tasksNum):
                taskhard = self.tasks[indx][0]
                devind = self.distrn[indivindx][indx]
                timekoef = self.devkoef[devind][int(taskhard-1)]
                fit[devind] += self.tasks[indx][1] * timekoef
            fitness.append([max(fit), indivindx])
        fitness.sort()
        fitness = [[1/i[0], i[1]] for i in fitness]        
        return fitness

    def mutation(self, individ):
        indexes = list(set([randint(0, self.tasksNum - 1) for i in range(2)]))
        if len(indexes) == 2:
            c = individ[indexes[0]]
            individ[indexes[0]] = individ[indexes[1]]
            individ[indexes[1]] = c
        indexes = list(set([randint(0, self.tasksNum - 1) for i in range(1)]))
        for i in indexes:
            individ[i] = self.devNum - individ[i] - 1
        return individ
    
    def k_point_crossover(self, a: np.ndarray, b: np.ndarray, points: np.ndarray):
        lenth = len(b)
        points = np.append(points, [lenth])
        firstChild = a[:points[0]+1]
        secondChild = b[:points[0]+1]
        for i in range(len(points)-1):
            if i % 2 == 0:
                firstChild = np.append(firstChild, b[points[i]+1: points[i+1]])
                secondChild = np.append(secondChild, a[points[i]+1: points[i+1]])
            else:
                firstChild = np.append(firstChild, a[points[i]: points[i+1]+1])
                secondChild = np.append(secondChild, b[points[i]: points[i+1]+1])
        return [firstChild, secondChild]

    def createNewGeneration(self, iter = 100):
        prevBestFit = 0
        frozenMutChance = self.mutchance
        for j in range(iter):
            print(j)
            fitness = np.array(self.countFit()) 
            indexlist = self.checksus(fitness, np.min(fitness)/2) 
            if fitness[0][0] == prevBestFit:
                self.mutchance = self.mutchance * 1.05
            else:
                self.mutchance = frozenMutChance
            newDistrn = []
            points = list(set([randint(0, self.tasksNum-1) for i in range(int(self.tasksNum/2) + 1)]))
            points.sort()
            points = np.array(points)
            newGenLen = self.population - self.fixedsize//10
            while len(newDistrn) < newGenLen:
                parent1 = randint(0,int(self.fixedsize * 0.4) - 1)
                parent2 = randint(max(0, parent1 - int(self.fixedsize/3)), min(self.fixedsize - 1, parent1 + int(self.fixedsize/3)))
                childs = self.k_point_crossover(np.array(self.distrn[indexlist[parent1]]),np.array(self.distrn[indexlist[parent2]]), points)
                newDistrn.append(childs[0])
                newDistrn.append(childs[1])
            for i in newDistrn:
                if randint(0, 100) < self.mutchance:
                    i = self.mutation(i)
            for i in indexlist[:self.fixedsize//10]:
                 newDistrn.append(self.distrn[i])
            self.distrn = np.array(newDistrn)
            prevBestFit = fitness[0][0]          
        fitness = self.countFit()
        return self.distrn[fitness[0][1]]

fileToRead = 'textfiles/input.txt'
fread = open(fileToRead, 'r')
N = int(fread.readline()) # количество задач
taskHard = fread.readline().split()
taskTime = fread.readline().split()
tasks = []
for i in range(len(taskHard)):
    tasks.append([int(taskHard[i]), float(taskTime[i])])
M = int(fread.readline()) # количество разработчиков
devkoef = []
for i in range(M):
    dev = fread.readline().split()
    dev = [float(i) for i in dev]
    devkoef.append(dev)
dstr = Distribution(np.array(tasks), np.array(devkoef), M, N, population = 300, fixedsize = 100, mutchance = 0.1)
best = dstr.createNewGeneration(iter = 150)
time = [0 for i in range(M)]
for i in range(len(best)):
    devind = int(best[i])
    taskind = i
    taskhard = int(tasks[i][0]) - 1
    tasktime = tasks[i][1]
    devk = devkoef[devind][taskhard]
    time[best[i]] += devk * tasktime
print(time)
print(max(time))
best += 1
fwr= open('textfiles/output.txt', 'w')
fwr.write(" ".join(str(i) for i in best))
fwr.close()