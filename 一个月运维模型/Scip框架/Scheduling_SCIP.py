import numpy as np
from pyscipopt import Model, quicksum

class Scheduling():
    def __init__(self, data):
        # length of periods in time horizon
        self.periods = list(range(data['period']))
        # tasks needed maintenance service
        self.tasks = data['tasks']
        self.p = data['generated power']
        self.d = data['demand']
        self.C_MV = data['vessel']['cost_manpower']
        self.C_MH = data['helicopter']['cost_manpower']
        self.C_ML = data['onshore']['cost_manpower']
        self.MV = data['vessel']['manpower']
        self.MH = data['helicopter']['manpower']
        self.ML = data['onshore']['manpower']
        self.C_M = data['task manpower cost']
        self.C_EQ = data['equipment cost']
        self.C_I = data['infrastructure cost']
        self.C_SV = data['vessel']['transport cost']
        self.C_SH = data['helicopter']['transport cost']
        self.V = data['vessel needed']
        self.H = data['helicopter needed']
        self.LP = data['maintenance duration']
        self.C_FV = data['vessel']['fixed cost']
        self.C_FH = data['helicopter']['fixed cost']
        self.C_T = data['transport cost']
        self.U = data['unavailable periods']
        self.LT = data['maintenance capacity']
        self.L = data['deadline']
        self.AM = data['available manpower']
        self.AV = data['available vessels']
        self.AH = data['available helicopter']


    def create_model(self):
        model = Model()
        x, b = {}, {}
        _A = [(i,t) for i in self.tasks for t in self.periods]
        for (i,t) in _A:
            x[i,t] = model.addVar(vtype = "B", name = "x(%s,%s)" % (i,t)) # create decision variables
            b[i,t] = model.addVar(vtype = "B", name = "b(%s,%s)" % (i,t)) # create decision variables

        # create constraints
        for t in self.periods:
            model.addCons(quicksum(self.p[i,t] * (1 - x[i,t]) for i in self.tasks) - self.d[t] >= 0) # 1
            model.addCons(quicksum(x[i,t] for i in self.tasks) <= self.LT[t]) # 6
            model.addCons(quicksum((self.MV[i] + self.MH[i] + self.ML[i]) * x[i,t] for i in self.tasks) <= self.AM[t]) # 11
            model.addCons(quicksum(self.V[i] * x[i,t] for i in self.tasks) <= self.AV[t]) # 12
            model.addCons(quicksum(self.H[i] * x[i,t] for i in self.tasks) <= self.AH[t]) # 13

        for i in self.tasks:
            model.addCons(quicksum(b[i,t] for t in self.periods) == 1) # 2
            model.addCons(quicksum(x[i,t] for t in self.periods) == self.LP[i]) # 5
            model.addCons(quicksum(b[i,t] for t in self.periods[:self.L[i]-self.LP[i]+2]) == 1) # 9
            for t in self.periods:
                model.addCons(x[i,t] >= b[i,t]) # 3
            
            for t in self.periods[1:]:
                model.addCons(x[i,t] - x[i,t-1] <= b[i,t] ) # 3, t >= 2
                model.addCons(x[i,t] + x[i,t-1] + b[i,t] <= 1+self.LP[i]) # 4
            
            for j in self.tasks:
                if j != i:
                    model.addCons(x[i,t] + x[j,t] <= 1 ) # 8
                    for t in self.periods:
                        model.addCons(quicksum(b[i,k] for k in self.periods) - b[j,t] >= 0) # 7
            
            for t in self.U:
                model.addCons(x[i,t] == 0) # 10

        # create costs
        C_M, C_T = {}, {}
        for i in self.tasks:
            for t in self.periods:
                C_M[i,t] = self.C_MV[t] * self.MV[i] + self.C_MH[t] * self.MH[i] + \
                    self.C_ML[t] * self.ML[i]
                C_T[i,t] = (self.C_FV * self.V[i] + self.C_FH * self.H[i])/self.LP[i] + \
                    self.C_SV[i,t] * self.V[i] + self.C_SH[i,t] * self.H[i]

        # create ojective function
        model.setObjective(quicksum((C_M[i,t] + self.C_EQ[i,t] + self.C_I[i,t] + \
            C_T[i,t]) * x[i,t] for t in self.periods for i in self.tasks), "minimize")
        model.hideOutput() # silent mode
        model.optimize()
        if model.getStatus() != 'optimal':
            print('Model is not feasible!')
        else:
            c_total = model.getObjVal()
            print ("Total cost is: ", c_total)
            for (i,t) in _A:
                if model.getVal(x[i,t]) == 1.0:
                    print (x[i,t], " = 1")
                if model.getVal(b[i,t]) == 1.0:
                    print (b[i,t], " = 1")
        return


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['vessel'] = {}
    data['helicopter'] = {}
    data['onshore'] = {}
    data['period'] = 30  # 天数
    data['tasks'] = np.array(range(3))
    data['generated power'] = np.array([[10,10,10,10,10,6,6,6,6,6,
                                         0,0,0,0,0,10,10,10,10,10,
                                         10,10,10,10,10,10,10,10,10,10],
                                        [11,11,11,10,10,0,0,0,0,0,
                                         10,10,10,10,10,6,6,6,6,6,
                                        6,6,6,6,6,6,6,6,6,6],
                                        [11,12,10,13,10,3,3,3,3,3,
                                         6,6,6,6,6,0,0,0,0,0,
                                         10,10,10,10,10,7,7,7,7,7]])
    data['demand'] = np.array([4,3,8,3,5,6,6,6,6,6,
                               6,6,6,6,6,6,6,6,6,6,
                               6,6,6,6,4,4,4,4,4,4])
    data['vessel']['cost_manpower'] = np.array([500,300,800,500,500,
                                                1000,800,1000,700,500,
                                                600,600,600,600,600,
                                                500,300, 800,500,500,
                                                1000,800,1000,700,500,
                                                600,600,600,600,600])
    data['helicopter']['cost_manpower'] = np.array([1200,1500,1000,800,1100,
                                                    1200,1500,1000,800,1100,
                                                    1200,1500,1000,800,1100,
                                                    1200,1500,1000,800,1100,
                                                    1200,1500,1000,800,1100,
                                                    1200,1500,1000,800,1100,])
    data['onshore']['cost_manpower'] = np.array([300,500,700,500,500,
                                                 300,500,700,500,500,
                                                 300,500,700,500,500,
                                                 300,500,700,500,500,
                                                 300,500,700,500,500,
                                                 300,500,700,500,500])
    data['vessel']['manpower'] = np.array([4,4,2,3,4,
                                           4,4,2,3,4,
                                           4,4,2,3,4,
                                           4,4,2,3,4,
                                           4,4,2,3,4,
                                           4,4,2,3,4])
    data['helicopter']['manpower'] = np.array([2,2,2,2,2,
                                               2,2,2,2,2,
                                               2,2,2,2,2,
                                               2,2,2,2,2,
                                               2,2,2,2,2,
                                               2,2,2,2,2])
    data['onshore']['manpower'] = np.array([1,2,1,2,2,
                                            1,2,1,2,2,
                                            1,2,1,2,2,
                                            1,2,1,2,2,
                                            1,2,1,2,2,
                                            1,2,1,2,2])
    data['task manpower cost'] = np.array([[100,300,500,700,500,100,300,500,700,500,
                                            100,300,500,700,500,100,300,500,700,500,
                                            100,300,500,700,500,100,300,500,700,500],
                                           [500,500,300,200,500,500,500,300,200,500,
                                            500,500,300,200,500,500,500,300,200,500,
                                            500,500,300,200,500,500,500,300,200,500],
                                           [500,500,500,500,500,500,500,300,200,500,
                                            500,500,300,200,500,500,500,300,200,500,
                                            500,500,300,200,500,500,500,300,200,500]])
    data['equipment cost'] = np.array([[4000,5000,3000,2000,1000,4000,5000,3000,2000,1000,
                                        4000,5000,4000,5000,3000,2000,1000,3000,2000,1000,
                                        4000,5000,3000,2000,1000,4000,5000,3000,2000,1000],
                                       [4000,5000,3000,2000,1000,4000,5000,3000,2000,1000,
                                        4000,5000,3000,2000,1000,4000,5000,3000,2000,1000,
                                        4000,5000,3000,2000,1000,4000,5000,3000,2000,1000],
                                       [4000,5000,3000,2000,1000,4000,5000,3000,2000,1000,
                                        4000,5000,3000,2000,1000,4000,5000,3000,2000,1000,
                                        4000,5000,3000,2000,1000,4000,5000,3000,2000,1000]])
    data['infrastructure cost'] = np.array([[3000,3000,3000,3000,3000,3000,3000,3000,3000,3000,
                                             3000,3000,3000,3000,3000,3000,3000,3000,3000,3000,
                                             3000,3000,3000,3000,3000,3000,3000,3000,3000,3000],
                                            [3000,3000,3000,3000,3000,3000,3000,3000,3000,3000,
                                             3000,3000,3000,3000,3000,3000,3000,3000,3000,3000,
                                             3000,3000,3000,3000,3000,3000,3000,3000,3000,3000],
                                            [3000,3000,3000,3000,3000,3000,3000,3000,3000,3000,
                                             3000,3000,3000,3000,3000,3000,3000,3000,3000,3000,
                                             3000,3000,3000,3000,3000,3000,3000,3000,3000,3000]])
    data['vessel']['transport cost'] = np.array([[400,400,400,400,400,400,400,400,400,400,
                                                  400,400,400,400,400,400,400,400,400,400,
                                                  400,400,400,400,400,400,400,400,400,400],
                                                 [400,400,400,400,400,400,400,400,400,400,
                                                  400,400,400,400,400,400,400,400,400,400,
                                                  400,400,400,400,400,400,400,400,400,400],
                                                 [400,400,400,400,400,400,400,400,400,400,
                                                  400,400,400,400,400,400,400,400,400,400,
                                                  400,400,400,400,400,400,400,400,400,400]])
    data['helicopter']['transport cost'] = np.array([[1400,1400,1400,1400,1400,1400,1400,1400,1400,1400,
                                                      1400,1400,1400,1400,1400,1400,1400,1400,1400,1400,
                                                      1400,1400,1400,1400,1400,1400,1400,1400,1400,1400],
                                                     [1400,1400,1400,1400,1400,1400,1400,1400,1400,1400,
                                                      1400,1400,1400,1400,1400,1400,1400,1400,1400,1400,
                                                      1400,1400,1400,1400,1400,1400,1400,1400,1400,1400],
                                                     [1400,1400,1400,1400,1400,1400,1400,1400,1400,1400,
                                                      1400,1400,1400,1400,1400,1400,1400,1400,1400,1400,
                                                      1400,1400,1400,1400,1400,1400,1400,1400,1400,1400]])
    data['vessel needed'] = np.array([2,3,1])
    data['helicopter needed'] = np.array([1,0,1])
    data['maintenance duration'] = np.array([1,1,1])
    data['vessel']['fixed cost'] = 200
    data['helicopter']['fixed cost'] = 400
    data['transport cost'] = np.array([[200,100,80,70,100,200,100,80,70,100,
                                        200,100,80,70,100,200,100,80,70,100,
                                        200,100,80,70,100,200,100,80,70,100],
                                       [100,100,80,100,90,100,100,80,100,90,
                                        100,100,80,100,90,100,100,80,100,90,
                                        100,100,80,100,90,100,100,80,100,90],
                                       [90,100,100,70,100,100,100,80,100,90,
                                        100,100,80,100,90,100,100,80,100,90,
                                        100,100,80,100,90,100,100,80,100,90]])
    data['unavailable periods'] = np.array([3])
    data['maintenance capacity'] = np.array([2,2,2,2,2,2,2,2,2,2,
                                             2,2,2,2,2,2,2,2,2,2,
                                             2,2,2,2,2,2,2,2,2,2])
    data['deadline'] = np.array([5,3,4])
    data['available manpower'] = np.array([12,12,12,12,12,12,12,12,12,12,
                                           12,12,12,12,12,12,12,12,12,12,
                                           12,12,12,12,12,12,12,12,12,12])
    data['available vessels'] = np.array([5,5,5,5,5,5,5,5,5,5,
                                          5,5,5,5,5,5,5,5,5,5,
                                          5,5,5,5,5,5,5,5,5,5])
    data['available helicopter'] = np.array([1,1,1,1,1,1,1,1,1,1,
                                             1,1,1,1,1,1,1,1,1,1,
                                             1,1,1,1,1,1,1,1,1,1])

    return data

def main():
    data = create_data_model()
    model = Scheduling(data)
    opt = model.create_model()

if __name__ == "__main__":
    main()