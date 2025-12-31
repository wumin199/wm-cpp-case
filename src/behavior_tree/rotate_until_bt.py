# /opt/wm-vcpkg/installed/x64-linux/tools/python3/pip install py_trees
# /opt/wm-vcpkg/installed/x64-linux/tools/python3/python xx.py

import py_trees
import time

# =================================================================
# 1. 传感器节点 (生产者) - 必须返回 RUNNING 才能保证每 Tick 都执行
# =================================================================


class SensorToBlackboard(py_trees.behaviour.Behaviour):
    def __init__(self, name="Sensor"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        # 逻辑：第 3 次 Tick 开始看到人
        found = True if self.tick_count >= 3 else False

        # 写入黑板
        self.blackboard.set("person_visible", found)

        # 这里的打印是证明节点在运行的关键
        print(f"[传感器] Tick {self.tick_count}: {'看到人' if found else '没看到人'}")

        # 关键修正：返回 RUNNING。
        # 这样 Parallel 节点每一轮都会重新进入这个 update
        return py_trees.common.Status.RUNNING

# =================================================================
# 2. 连续计数触发器 (消费者)
# =================================================================


class ContinuousSuccessTrigger(py_trees.behaviour.Behaviour):
    def __init__(self, name="Trigger", limit=5):
        super().__init__(name)
        self.limit = limit
        self.count = 0
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        person_visible = self.blackboard.get("person_visible")

        if person_visible is True:
            self.count += 1
            print(f"  [逻辑计数] 匹配成功! 进度: {self.count}/{self.limit}")
            if self.count >= self.limit:
                return py_trees.common.Status.SUCCESS
        else:
            if self.count > 0:
                print("  [逻辑计数] 目标丢失，重置计数")
            self.count = 0

        return py_trees.common.Status.RUNNING

# =================================================================
# 3. 运行逻辑
# =================================================================


def create_robot_tree():
    sensor = SensorToBlackboard()
    rotate = py_trees.behaviours.Running(name="Rotate")
    trigger = ContinuousSuccessTrigger(limit=5)

    confirm_seq = py_trees.composites.Sequence(name="ConfirmLogic", memory=False)
    confirm_seq.add_child(trigger)

    # 根节点：监控 confirm_seq
    root = py_trees.composites.Parallel(
        name="Root",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected([confirm_seq])
    )

    root.add_children([sensor, rotate, confirm_seq])
    return root


if __name__ == "__main__":
    # 强制设置打印级别
    py_trees.logging.level = py_trees.logging.Level.WARN

    tree = create_robot_tree()
    tree.setup_with_descendants()

    print(">>> 行为树 Demo V7.0 (解决逻辑停滞问题) 启动")
    for i in range(1, 10):
        print(f"\n--- 第 {i} 次 Tick ---")

        # 执行 Tick
        tree.tick_once()

        # 每一 Tick 显式打印树结构，确保“友好”的界面回来
        print(py_trees.display.unicode_tree(root=tree, show_status=True))

        if tree.status == py_trees.common.Status.SUCCESS:
            print("\n[结果] 任务成功完成！")
            break
        time.sleep(0.1)
