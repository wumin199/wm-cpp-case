

状态机：适合事件驱动状态跃迁，如：
- 任何状态下报错，就停止运动
- 从A到B到C到D的过程中，底盘没电就去充电
  Adding a battery check and charging action to a BT is easy, but note that this check is not reactive — it only occurs at the start of the sequence.
- 游戏中，任何情况下发现玩家，就去追击玩家

状态机结构：状态集合+转移条件(Q->∑->σ)
状态机执行逻辑：线性跳转，当前状态唯一
状态机复杂度：容易状态转移爆炸（随着状态数量上升，转移条件指数级别曾长Nx(N-1)
  
行为树：条件驱动节点执行（树状分层决策），如：
- 先做A，再同时做BC
- 需要A和B,再做C,然后某些情况下做D,某些情况下做E
- 简单说是需要一大堆if/else/until/repeated/while等构成的类似树状的固定的逻辑

行为树结构：节点组合：控制节点/装饰节点/任务节点
行为树复杂度：节点服用性质强，子树模块化，适合复杂逻辑，容易扩展
行为树执行逻辑：自顶向下遍历，节点返回Success/Failure/Running



✅状态机实现
	
▶️常用方法：枚举+switch-case、状态类（IState接口+OnEnter/Update/Exit）。人形的hey,run,bye。有个step()一直在循环。
▶️优化点：避免频繁状态切换；使用字典注册状态减少GC
▶️性能：执行效率高（直接跳转），内存占用低
	
✅行为树实现
	
▶️节点类型：Selector（或逻辑）、Sequence（与逻辑）、Decorator（条件修饰）、Action（具体行为）
▶️工具支持：       插件：Behavior Designer（可视化编辑）、NodeCanvas       自定义：通过BehaviorNode基类派生节点
▶️性能瓶颈：高频Tick遍历可能消耗CPU，需优化（如降低非实时节点更新频率）


> 状态少用状态机，状态多了行为树。实际应用可以结合，用状态机做大状态的切换，里面用行为树控制具体状态的行为逻辑

> 状态少，行为简单，预期以后需求更改不频繁，就用状态机。状态多，行为复杂，需求多变，就用行为树。另外思想都是相通的，行为树本质上是一种可视化的编程脚本，用来实现复杂 AI 时也需要按状态机的思路来进行管理，不然就完全不具备可维护性


