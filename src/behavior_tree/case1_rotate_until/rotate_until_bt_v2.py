import py_trees
import time


# =================================================================
# 1. 传感器节点 (保持不变)
# =================================================================
class SensorToBlackboard(py_trees.behaviour.Behaviour):
    def __init__(self, name="Sensor"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        found = True if self.tick_count >= 3 else False
        self.blackboard.set("person_visible", found)
        print(f"[传感器] Tick {self.tick_count}: {'看到人' if found else '没看到人'}")
        return py_trees.common.Status.RUNNING


# =================================================================
# 2. 连续计数触发器 (重构：完全数据驱动)
# =================================================================
class ContinuousSuccessTrigger(py_trees.behaviour.Behaviour):
    def __init__(self, name="Trigger"):
        super().__init__(name)
        self.count = 0
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        # 【关键改动】不再使用 self.limit，而是从黑板动态获取任务指标
        # 如果黑板没设置，默认给个 5
        current_limit = self.blackboard.get("target_limit") or 5
        person_visible = self.blackboard.get("person_visible")

        if person_visible is True:
            self.count += 1
            print(f"  [逻辑计数] 匹配成功! 进度: {self.count}/{current_limit}")
            if self.count >= current_limit:
                return py_trees.common.Status.SUCCESS
        else:
            if self.count > 0:
                print("  [逻辑计数] 目标丢失，重置计数")
            self.count = 0

        return py_trees.common.Status.RUNNING


# =================================================================
# 3. 运行逻辑 (重构：逻辑模具化)
# =================================================================
def create_robot_tree():
    sensor = SensorToBlackboard()
    rotate = py_trees.behaviours.Running(name="Rotate")

    # 【关键改动】实例化时不再传入 limit=5
    trigger = ContinuousSuccessTrigger(name="Trigger")

    confirm_seq = py_trees.composites.Sequence(name="ConfirmLogic", memory=False)
    confirm_seq.add_child(trigger)

    root = py_trees.composites.Parallel(
        name="Root",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected([confirm_seq]),
    )
    root.add_children([sensor, rotate, confirm_seq])
    return root


if __name__ == "__main__":
    py_trees.logging.level = py_trees.logging.Level.WARN

    # 【数据驱动的核心】在启动树之前，统一在黑板里下达“任务指标”
    # 你可以试着把这里的 3 改成 2 或者 5，代码逻辑完全不用动
    bb = py_trees.blackboard.Blackboard()
    bb.set("target_limit", 3)

    tree = create_robot_tree()
    tree.setup_with_descendants()

    print(
        f">>> 行为树 Demo V8.0 (数据驱动版) 启动，当前任务指标: {bb.get('target_limit')}次"
    )

    for i in range(1, 12):
        print(f"\n--- 第 {i} 次 Tick ---")
        tree.tick_once()
        print(py_trees.display.unicode_tree(root=tree, show_status=True))

        if tree.status == py_trees.common.Status.SUCCESS:
            print(f"\n[结果] 连续检测满 {bb.get('target_limit')} 次，任务成功完成！")
            break
        time.sleep(0.1)
