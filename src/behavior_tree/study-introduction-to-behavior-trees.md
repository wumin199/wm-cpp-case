
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




### 原地旋转，直到连续 5 次 tick 都检测到人为止

我们要先理清一个核心概念：在行为树中，任何一个节点在被 Tick（执行）之后，必须返回且只能返回以下三种状态之一：

SUCCESS（成功）
FAILURE（失败）
RUNNING（运行中）

`rotate_until_bt.py`

```mermaid
graph TD
    Root((Parallel)) --- Sensor[Sensor]
    Root --- Rotate[Rotate]
    Root --- Sequence[Sequence]
    Sequence --- Trigger[Trigger]
```


```mermaid
graph TD
    %% 根节点定义
    Root{{"Parallel (SuccessOnSelected)"}} 
    
    %% 子节点定义
    Sensor["Sensor (生产者)"]
    Rotate["Rotate (动作)"]
    ConfirmSeq["ConfirmLogic (Sequence: memory=False)"]
    Trigger["Trigger (消费者/触发器)"]

    %% 树结构连接
    Root --> Sensor
    Root --> Rotate
    Root --> ConfirmSeq
    ConfirmSeq --> Trigger

    %% 数据流（黑板）展示
    subgraph Blackboard ["共享内存 (Blackboard)"]
        Data(person_visible: bool)
    end

    Sensor -.->|"1. 写入 (set)"| Data
    Data -.->|"2. 读取 (get)"| Trigger

    %% 状态说明
    classDef producer fill:#f9f,stroke:#333,stroke-width:2px;
    classDef action fill:#bbf,stroke:#333,stroke-width:2px;
    classDef logic fill:#dfd,stroke:#333,stroke-width:2px;
    classDef rootNode fill:#ff9,stroke:#333,stroke-width:4px;

    class Sensor producer;
    class Rotate action;
    class ConfirmSeq,Trigger logic;
    class Root rootNode;

    %% 备注说明
    note1[注释：并行策略: 仅监控 ConfirmLogic]
    note2[反应性: memory=False 保证连续性]
    Root --- note1
    ConfirmSeq --- note2
```


fsm版本

`rotate_until_fsm.py`


```mermaid
stateDiagram-v2
    [*] --> Rotating_Idle: 启动

    state Rotating_Idle {
        direction lr
        Id: 仅旋转，不计数
    }

    Rotating_Idle --> Detect_1: 发现人 (第1次)
    
    state Detect_1 {
        direction lr
        D1: 旋转 + 计数=1
    }
    Detect_1 --> Rotating_Idle: 人消失 (重置)
    Detect_1 --> Detect_2: 发现人 (第2次)

    state Detect_2 {
        D2: 旋转 + 计数=2
    }
    Detect_2 --> Rotating_Idle: 人消失 (重置)
    Detect_2 --> Detect_3: 发现人 (第3次)

    state Detect_3 {
        D3: 旋转 + 计数=3
    }
    Detect_3 --> Rotating_Idle: 人消失 (重置)
    Detect_3 --> Detect_4: 发现人 (第4次)

    state Detect_4 {
        D4: 旋转 + 计数=4
    }
    Detect_4 --> Rotating_Idle: 人消失 (重置)
    Detect_4 --> Success_Stop: 发现人 (第5次)

    Success_Stop --> [*]: 停止所有动作
```


看了这段代码，你应该能明显感觉到它和 BT 版本的巨大区别：

状态爆炸（State Explosion）：为了数 5 个数，我不得不手动写了 DETECT_1 到 DETECT_4 四个状态。如果你要求连续检测 100 次，这个 if-elif 逻辑将变成几百行，根本无法维护。

逻辑重复：在每个状态里，我都得判断 if person_visible ... else ... self.STATE_IDLE_ROTATING。这种“如果失败就回退到初始状态”的逻辑在 FSM 里需要每一行都写，而在 BT 里只需要一个 memory=False 的 Sequence 就能自动搞定。

动作与逻辑耦合：在 FSM 里，我必须在 tick 函数里显式调用 execute_rotate()。如果以后我想把“旋转”改成“原地跳舞”，我得修改状态机内部的所有逻辑。而在 BT 里，你只需要把 Rotate 节点换成 Dance 节点，不需要动任何逻辑代码。

总结： FSM 在处理简单的、无回退的顺序流程时很好用；但在处理这种**带有计数确认、需要随时反应环境变化（Reactiveness）**的机器人任务时，BT 的优势是压倒性的。


- 总结

FSM 是“跳转驱动”的：它的核心是“如果发生 A，就切换到状态 B”。在处理简单的顺序流程时很清晰，但在处理“边做 A 边看 B”且带有“计数确认”这种复合逻辑时，会变得非常臃肿。

BT 是“决策驱动”的：它的核心是“每一秒我都重新评估所有可能性”。正如我们在 V7.0 代码中看到的，Trigger 节点每一秒都在确认计数，而 Parallel 节点每一秒都在确认任务是否完成。
