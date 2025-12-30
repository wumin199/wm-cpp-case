import py_trees
import time

# =================================================================
# 1. 传感器节点 (生产者)
# =================================================================


class SensorToBlackboard(py_trees.behaviour.Behaviour):
    def __init__(self, name="Sensor"):
        super().__init__(name)
        # 最新版推荐用法：通过 Client 挂载黑板
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="person_visible", access=py_trees.common.Access.WRITE)
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        # 模拟：第 3 次 Tick 看到人，第 8 次人消失
        found = True if 3 <= self.tick_count <= 7 or self.tick_count >= 10 else False
        self.blackboard.person_visible = found
        print(f"[传感器] Tick {self.tick_count}: {'看到人' if found else '没看到人'}")
        return py_trees.common.Status.SUCCESS

# =================================================================
# 2. 连续计数触发器 (核心逻辑消费者)
# =================================================================


class ContinuousSuccessTrigger(py_trees.behaviour.Behaviour):
    def __init__(self, name="Trigger", limit=5):
        super().__init__(name)
        self.limit = limit
        self.count = 0
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="person_visible", access=py_trees.common.Access.READ)

    def update(self):
        # 从黑板读取数据
        if self.blackboard.person_visible:
            self.count += 1
            print(f"  [逻辑] 连续计数: {self.count}/{self.limit}")
            if self.count >= self.limit:
                return py_trees.common.Status.SUCCESS
        else:
            if self.count > 0:
                print("  [逻辑] 目标丢失，计数重置！")
            self.count = 0
        # 只要还没成功，就报 RUNNING，保持 Parallel 节点不退出
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        # 如果分支被重置，计数也要归零
        if new_status == py_trees.common.Status.INVALID:
            self.count = 0

# =================================================================
# 3. 组装函数 (避开所有 API 陷阱)
# =================================================================


def create_robot_tree():
    # A. 实例化所有节点
    sensor = SensorToBlackboard()
    rotate = py_trees.behaviours.Running(name="RotateAction")
    trigger = ContinuousSuccessTrigger(limit=5)

    # B. 组装检测分支 (Sequence 默认 memory=False，符合反应性要求)
    confirm_seq = py_trees.composites.Sequence(name="ConfirmLogic", memory=False)
    confirm_seq.add_child(trigger)

    # C. 创建 Parallel 节点
    # 注意：最新版 SuccessOnSelected 只接收一个列表作为位置参数
    # 里面放你希望“达成成功条件”的节点实例
    root = py_trees.composites.Parallel(
        name="Root",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            [confirm_seq]
        )
    )

    # D. 添加孩子，顺序很重要：Sensor 必须在最前面
    root.add_children([sensor, rotate, confirm_seq])

    return root

# =================================================================
# 4. 运行模拟
# =================================================================


if __name__ == "__main__":
    # 抑制调试日志，只看我们的 print
    py_trees.logging.level = py_trees.logging.Level.WARN

    tree_root = create_robot_tree()
    tree_root.setup_with_descendants()

    print(">>> 行为树工业级 Demo 启动 (最新版 API 适配)")
    for i in range(1, 15):
        print(f"\n--- 第 {i} 次 Tick ---")
        tree_root.tick_once()

        # 打印树状态
        print(py_trees.display.unicode_tree(root=tree_root, show_status=True))

        if tree_root.status == py_trees.common.Status.SUCCESS:
            print("\n[结果] 任务成功完成！")
            break
        elif tree_root.status == py_trees.common.Status.FAILURE:
            print("\n[结果] 任务失败！")
            break
        time.sleep(0.1)
