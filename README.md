# 海上风电场运维调度项目

针对当前国内海上风电面临的运维能力弱、成本高这一关键问题，研究海上风电场区域运维策略，构建区域级海上风电大数据平台，基于大数据平台海量数据的存储和挖掘，形成适应特定环境条件下的海上风电场智能施工、运维作业调度，实现集约化运维模式和运维资源配置与运维策略的智能优化，统筹区域内海上风电运维資源，有效降低运维成本提升效益，为相关运维单位提供决策建议。

## 算法部分
研究相关论文，基于多码头多风电场情况，在python环境下使用Gurobi框架复现论文的优化模型，针对子问题每一个可行的计划规划出最间步长t为每个船v选择一个可行的路线，得到该计划时间周期内风机的维护时间安排表，其中还包含船和运维人员的时间安排，最终完善MILP和ILP结合的周运维模型。


'''
文件说明：
    外部直接通过from O_S_model import one2seven_model调用即可
    
注意：O_S_model.py不修改,直接调用

输入:
    json数据
    
输出格式：

"route":{
    "initial":[
        {
            "vessel":1.0,
            "turbine":[0.0]
        },
        {
            "vessel":2.0,
            "turbine":[6.0,2.0,5.0]
        },
        {
            "vessel":3.0,
            "turbine":[0.0]
        }],
    "firstday":[
            ...
        ],
    ...
    }
'''



研究相关论文，基于可靠性最高和妻用最低的目标函数，在python环境下使用Gurobi和Scip框架建立了海上风电场PM调度问题的多目标规划模型，完成月运维非支配排序遗传算法模型。

Gurobi框架运行结果展示

![image](https://user-images.githubusercontent.com/60246446/114642318-5072d680-9d06-11eb-98c2-5be0a5239ee2.png)

Scip框架运行结果展示

![image](https://user-images.githubusercontent.com/60246446/114642432-7dbf8480-9d06-11eb-98ec-7731bd8352cf.png)



## 服务器部署和运维
将测试好的算法部署到Linux服务器中运行，为海上风电大数据平台提供建模算法支持。

部署结果展示

![image](https://user-images.githubusercontent.com/60246446/114642509-a47dbb00-9d06-11eb-85cb-78be33335bde.png)

### 接通前后端

编写Flask web框架来请求服务，实现前端输入数据存储到数据库，算法从数据库调用并计算出结果输出到前端大数据平台页面。
文件请见 https://github.com/LJL-6666/Operation-and-maintenance-scheduling-project---Offshore-Wind-Farm/blob/main/all.py


### 运维

**启动前端**

nohup java -jar data-admin.jar & tail -f nohup.out

**关闭前端**

ps aux

netstat -anp|grep 8083

kill -9 +端口号

Kill + PID

**启动后端**

conda activate auto

python all.py

conda deactivate
