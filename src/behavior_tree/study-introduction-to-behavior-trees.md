
- [Introduction to behavior trees](https://robohub.org/introduction-to-behavior-trees/)


## Note

1. FallBack：只要一个达到条件就行

一般用于查询后执行：
- One very common design principle you should know is defined in the book as **explicit success conditions**. In simpler terms, you should almost always check before you act. For example, if you’re already at a specific location, why not check if you’re already there before starting a navigation action?
![](https://robohub.org/wp-content/uploads/2021/08/bt_mobile_robot_02.png)
   (到达A或者没到A的话就GoToA)

- We can also use Fallback nodes to define reactive behaviors; that is, if one behavior does not work, try the next one, and so on.

2. Parallel nodes allows multiple actions and/or conditions to be considered within a single tick
  
  并行节点可以同时获取几个 multiple actions and/or conditions，然后自己对这些状态进行or and运算

3. 原地旋转，直到连续 5 次 tick 都检测到人为止

```mermaid
graph TD
 Root[Parallel 节点: 查找人类] --> Rotate[Action: 原地旋转]
 Root --> CheckPerson[Sequence: 检测确认]
 CheckPerson --> Detect[Condition: 视野中有人?]
 CheckPerson --> Count[Decorator: 连续5次Tick]
```


4. 节点返回状态

我们要先理清一个核心概念：在行为树中，任何一个节点在被 Tick（执行）之后，必须返回且只能返回以下三种状态之一：

SUCCESS（成功）

FAILURE（失败）

RUNNING（运行中）


```mermaid
graph TD
    Root[Parallel: 原地查找人类任务] --> Sensor[Sensor: 视觉检测更新]
    Root --> Rotate[Action: 原地旋转底盘]
    Root --> ConfirmSeq[Sequence: 确认逻辑 - 无记忆模式]
    
    ConfirmSeq --> Guard[Condition: 黑板检查-视野中有人?]
    ConfirmSeq --> Counter[Decorator: 连续计数器-5次]
    Counter --> CheckBB[Condition: 黑板检查-确认数据源]

    style Sensor fill:#f9f,stroke:#333
    style Rotate fill:#bbf,stroke:#333
    style Guard fill:#dfd,stroke:#333
    style Root fill:#ff9,stroke:#333
```