import py_trees
import time

# bt_mobile_robot_blackboard.png


# =================================================================
# 1. 任务管理节点：从队列获取下一个地点 (对应图中的 GetLoc)
# =================================================================
class GetNextTask(py_trees.behaviour.Behaviour):
    def __init__(self, name="GetNextTask"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        queue = self.blackboard.get("location_queue")
        if not queue:
            print("[系统] 所有任务已完成，队列为空")
            return py_trees.common.Status.FAILURE

        # 弹出下一个目标
        current_target = queue.pop(0)
        self.blackboard.set("current_location", current_target)
        self.blackboard.set("person_visible", False)  # 重置识别状态
        print(f"\n[任务切换] >>> 当前目标地点: {current_target}")
        return py_trees.common.Status.SUCCESS


# =================================================================
# 2. 传感器节点 (保持数据驱动)
# =================================================================
class SensorToBlackboard(py_trees.behaviour.Behaviour):
    def __init__(self, name="Sensor"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.internal_tick = 0

    def update(self):
        self.internal_tick += 1
        # 模拟：偶数次 Tick 才能看到人，增加任务难度
        found = True if self.internal_tick % 2 == 0 else False
        self.blackboard.set("person_visible", found)

        loc = self.blackboard.get("current_location")
        print(f"[传感器] 在 {loc} 监测中: {'看到人' if found else '没看到人'}")
        return py_trees.common.Status.RUNNING


# =================================================================
# 3. 连续计数触发器 (重构：任务完成后重置计数)
# =================================================================
class ContinuousSuccessTrigger(py_trees.behaviour.Behaviour):
    def __init__(self, name="Trigger"):
        super().__init__(name)
        self.count = 0
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        limit = self.blackboard.get("target_limit") or 3
        visible = self.blackboard.get("person_visible")

        if visible:
            self.count += 1
            print(f"  [逻辑] 匹配成功! 进度: {self.count}/{limit}")
            if self.count >= limit:
                self.count = 0  # 重要：完成后重置自己，为下一个任务做准备
                return py_trees.common.Status.SUCCESS
        else:
            self.count = 0
        return py_trees.common.Status.RUNNING


# =================================================================
# 4. 组装：实现图 2 的架构
# =================================================================
def create_robot_tree():
    # A. 核心业务子树 (对应图中的中间部分)
    # 包含：传感器、动作、确认逻辑
    sensor = SensorToBlackboard()
    rotate = py_trees.behaviours.Running(name="Rotate")
    trigger = ContinuousSuccessTrigger(name="Trigger")

    confirm_seq = py_trees.composites.Sequence(name="ConfirmLogic", memory=False)
    confirm_seq.add_child(trigger)

    # 业务并行层
    task_parallel = py_trees.composites.Parallel(
        name="TaskParallel",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected([confirm_seq]),
    )
    task_parallel.add_children([sensor, rotate, confirm_seq])

    # B. 任务流序列 (对应图中的横向 Sequence)
    # 步骤：1. 获取目标 -> 2. 执行任务并行层
    main_logic = py_trees.composites.Sequence(name="MainLogic", memory=True)
    main_logic.add_children([GetNextTask(), task_parallel])

    # C. 装饰器 (对应图顶部的 Repeat/delta 符号)
    # 只要 main_logic 成功完成一个地点，就重新开始寻找下一个地点

    # 关键修复点：增加 num_success=-1
    # 这意味着：只要子节点成功，就一直重复；直到子节点失败（队列空）才停止
    root = py_trees.decorators.Repeat(
        child=main_logic, name="RepeatUntilQueueEmpty", num_success=-1
    )
    return root


if __name__ == "__main__":
    bb = py_trees.blackboard.Blackboard()

    # 初始化任务队列 (对应图中的 LocationQueue)
    bb.set("location_queue", ["Kitchen", "Bedroom", "Balcony"])
    bb.set("target_limit", 2)  # 每个地点确认 2 次即成功

    tree = create_robot_tree()
    tree.setup_with_descendants()

    print(">>> 行为树 V9.0 工业级任务流引擎 启动")

    # 运行足够多的 Tick 以完成所有任务
    for i in range(1, 30):
        print(f"\n--- Tick {i} ---")
        tree.tick_once()

        # 打印树结构
        print(py_trees.display.unicode_tree(root=tree, show_status=True))

        # 如果 Repeat 装饰器返回了 FAILURE，说明 GetNextTask 发现队列空了
        if tree.status == py_trees.common.Status.FAILURE:
            print("\n[最终结果] 队列全部处理完毕，机器人关机。")
            break
        time.sleep(0.05)
