# -*- coding: utf-8 -*-

import numpy as np
#from Scheduling import Scheduling

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['vessel'] = {}
    data['helicopter'] = {}
    data['onshore'] = {}
    data['period'] = 5 # 天数
    data['tasks'] = np.array(range(3))
    data['generated power'] = np.array([[3,4,2,3,4],[4,5,3,4,5],[6,6,4,3,2]])
    data['demand'] = np.array([10,10,10,10,10])
    data['vessel']['cost_manpower'] = np.array([500,500,500,500,500])
    data['helicopter']['cost_manpower'] = np.array([1500,1500,1500,1500,1500])
    data['onshore']['cost_manpower'] = np.array([500,500,500,500,500])
    data['vessel']['manpower'] = np.array([7,5,6,3,4])
    data['helicopter']['manpower'] = np.array([4,5,5,4,3])
    data['onshore']['manpower'] = np.array([3,2,3,2,2])
    data['task manpower cost'] = np.array([[500,500,500,500,500],
        [500,500,500,500,500], [500,500,500,500,500]])
    data['equipment cost'] = np.array([[4000,5000,3000,2000,1000],
        [4000,5000,3000,2000,1000],[4000,5000,3000,2000,1000]])
    data['infrastructure cost'] = np.array([[3000,3000,3000,3000,3000],
        [3000,3000,3000,3000,3000],[3000,3000,3000,3000,3000]])
    data['vessel']['transport cost'] = np.array([[400,400,400,400,400],
        [400,400,400,400,400],[400,400,400,400,400]])
    data['helicopter']['transport cost'] = np.array([[1400,1400,1400,1400,1400],
        [1400,1400,1400,1400,1400],[1400,1400,1400,1400,1400]])
    data['vessel needed'] = np.array([3,2,2])
    data['helicopter needed'] = np.array([1,0,0])
    data['maintenance duration'] = np.array([1,2,2])
    data['vessel']['fixed cost'] = 200
    data['helicopter']['fixed cost'] = 400
    data['transport cost'] = np.array([[100,100,100,100,100],
        [100,100,100,100,100],[100,100,100,100,100]])
    data['unavailable periods'] = np.array([3])
    data['maintenance capacity'] = np.array([2,2,2,2,2])
    data['deadline'] = np.array([4,3,4])
    data['available manpower'] = np.array([12,12,12,12,12])
    data['available vessels'] = np.array([5,5,5,5,5])
    data['available helicopter'] = np.array([1,1,1,1,1])

    return data

def main():
    data = create_data_model()
    model = Scheduling(data)
    opt = model.create_model()

if __name__ == "__main__":
    main()