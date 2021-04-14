# -*- coding: utf-8 -*-

import numpy as np
from gurobipy import Model, GRB, quicksum

class Scheduling():
    def __init__(self, data):
        # length of periods in time horizon
        self.periods = list(range(data['period']))
        # tasks needed maintenance service
        self.tasks = data['tasks']
        # self.days = data['tasks required days']
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
        _A = [(i,t) for i in self.tasks for t in self.periods]
        x = model.addVars(_A, vtype = GRB.BINARY) # create decision variables
        b = model.addVars(_A, vtype = GRB.BINARY) # create decision variables

        # create constraints
        model.addConstrs(quicksum(self.p[i,t] * (1 - x[i,t]) for i in self.tasks) - \
            self.d[t] >= 0 for t in self.periods) # 1
        model.addConstrs(quicksum(b[i,t] for t in self.periods) == 1 \
            for i in self.tasks) # 2
        model.addConstrs(x[i,t] >= b[i,t] for i in self.tasks for t in self.periods) # 3
        model.addConstrs(x[i,t] - x[i,t-1] <= b[i,t] for i in self.tasks \
            for t in self.periods[1:]) # 3, t >= 2
        _tmp =  self.periods[1:]
        # model.addConstrs(x[i,t] <= b[i,t] for t in _tmp \
        #     for i in self.tasks) # 4
        model.addConstrs(x[i,t] + x[i,t-1] + b[i,t] <= 1+self.LP[i] for t in self.periods[1:] \
            for i in self.tasks) # 4
        model.addConstrs(quicksum(x[i,t] for t in self.periods) == self.LP[i] \
            for i in self.tasks) # 5
        model.addConstrs(quicksum(x[i,t] for i in self.tasks) <= self.LT[t] \
            for t in self.periods) # 6
        model.addConstrs(quicksum(b[i,k] for k in self.periods) - b[j,t] >= 0 \
            for t in self.periods for i in self.tasks for j in self.tasks if j!=i) # 7
        model.addConstrs(x[i,t] + x[j,t] <= 1 for t in self.periods \
            for i in self.tasks for j in self.tasks if j!=i) # 8
        model.addConstrs(quicksum(b[i,t] for t in self.periods[:self.L[i]-self.LP[i]+2]) == 1 \
            for i in self.tasks) # 9
        # model.addConstrs(quicksum(x[i,t] == 0 for t in self.U) for i in self.tasks) # 10
        model.addConstrs(x[i,t] == 0 for t in self.U for i in self.tasks) # 10
        model.addConstrs(quicksum((self.MV[i] + self.MH[i] + self.ML[i]) * x[i,t] \
            for i in self.tasks) <= self.AM[t] for t in self.periods) # 11
        model.addConstrs(quicksum(self.V[i] * x[i,t] for i in self.tasks) \
            <= self.AV[t] for t in self.periods) # 12
        model.addConstrs(quicksum(self.H[i] * x[i,t] for i in self.tasks) <= \
            self.AH[t] for t in self.periods) # 13

        # create costs
        C_M, C_T = {}, {}
        for i in self.tasks:
            for t in self.periods:
                C_M[i,t] = self.C_MV[t] * self.MV[i] + self.C_MH[t] * self.MH[i] + \
                    self.C_ML[t] * self.ML[i]
                C_T[i,t] = (self.C_FV * self.V[i] + self.C_FH * self.H[i])/self.LP[i] + \
                    self.C_SV[i,t] * self.V[i] + self.C_SH[i,t] * self.H[i]

        model.modelSense = GRB.MINIMIZE
        # create ojective function
        model.setObjective(quicksum((C_M[i,t] + self.C_EQ[i,t] + self.C_I[i,t] + \
            C_T[i,t]) * x[i,t] for t in self.periods for i in self.tasks))
        # model.setParam('OutputFlag', 0)
        model.optimize()
        return
