import py_trees
import time
import random

# =================================================================
# 1. 核心节点类
# =================================================================


class GetLoc(py_trees.behaviour.Behaviour):
    def __init__(self, name="GetLoc"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        queue = self.blackboard.get("location_queue")
        if not queue:
            return py_trees.common.Status.FAILURE
        target = queue.pop(0)
        self.blackboard.set("current_location", target)
        self.blackboard.set("at_destination", False)
        self.blackboard.set("wheel_error", False)
        print(f"\n[任务系统] >>> 新目标: {target}")
        return py_trees.common.Status.SUCCESS


class CheckWheelError(py_trees.behaviour.Behaviour):
    def __init__(self, name="CheckWheelError"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        # 只要黑板显示有错，就返回 SUCCESS 激活恢复逻辑
        if self.blackboard.get("wheel_error"):
            print("  [监控] !!! 警报：检测到故障 !!!")
            # 整个 Sequence 继续执行恢复步骤，才能决定是 SUCCESS 还是 FAILURE 或 RUNNING
            return py_trees.common.Status.SUCCESS
        # 正常，无报错，整个Sequecence返回 FAILURE
        return py_trees.common.Status.FAILURE


class WaitManualReset(py_trees.behaviour.Behaviour):
    def __init__(self, name="WaitManualReset"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        print("\n" + "!" * 50)
        print(f"  [故障中] 目标 {self.blackboard.get('current_location')} 挂起。")
        user_input = input("  [输入 'r' 排除故障并继续导航]: ")

        if user_input.lower() == "r":
            print("  [恢复] 故障已清除，正在切换回导航动作...")
            self.blackboard.set("wheel_error", False)
            # --- 关键点：返回 FAILURE ---
            # 这会让父节点 Selector 意识到“恢复分支不再需要运行了”
            # 从而在同一个 Tick 立即执行后面的 GoToLoc
            return py_trees.common.Status.FAILURE

        return py_trees.common.Status.RUNNING


class AtLoc(py_trees.behaviour.Behaviour):
    def __init__(self, name="AtLoc"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        if self.blackboard.get("at_destination"):
            print("  [判断] 已到达目的地，准备开始业务")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class GoToLoc(py_trees.behaviour.Behaviour):
    def __init__(self, name="GoToLoc"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.move_time = 0

    def update(self):
        error_chance = self.blackboard.get("config_error_chance") or 0.0
        move_limit = self.blackboard.get("config_move_speed") or 3

        # 模拟随机故障
        if random.random() < error_chance:
            print("  [动作] 糟糕！轮子卡住了！")
            self.blackboard.set("wheel_error", True)
            return py_trees.common.Status.RUNNING

        self.move_time += 1
        if self.move_time >= move_limit:
            print(f"  [动作] 到达目的地！: {self.move_time}/{move_limit}")
            self.blackboard.set("at_destination", True)
            self.move_time = 0
            return py_trees.common.Status.SUCCESS

        print(f"  [动作] 移动中: ({self.move_time}/{move_limit})")

        # 这是一个非常精妙的工程设计问题。在 GoToLoc 报错时返回 RUNNING 而不是 FAILURE，
        # 是为了**“保护”**整棵行为树不被这个临时错误搞崩溃，同时为下一秒的“抢占”留下空间。

        # 如果这里返回了 FAILURE，根据行为树的逻辑，会产生以下连锁反应：

        # 1. 为什么不能返回 FAILURE (失败)？
        # 如果 GoToLoc 返回 FAILURE：

        # 其父节点 LocSelector 会收到 FAILURE，由于它已经没有其他孩子可以尝试了，它也会报 FAILURE。

        # 外层的 MainLogic (这是一个 Sequence) 收到 FAILURE 后会认为：“整个导航任务彻底搞砸了”。

        # Sequence 会立即中断并向上传递 FAILURE，导致整棵树停止运行。

        # 结果： 机器人还没来得及进入“恢复模式”，程序就直接退出了。这就好比车轮打滑了一下，司机不是去踩刹车尝试脱困，而是直接把车报废了。

        # 在 py_trees 开发中，如果你希望一个动作在出故障后能被“抢占”并进入恢复流程，
        # RUNNING 是你最好的朋友。它能让逻辑流停留在当前任务点，既不向后推进，也不向前溃退，直到环境状态（黑板变量）发生变化，将控制权交给优先级更高的分支。
        return py_trees.common.Status.RUNNING


class FoundApple(py_trees.behaviour.Behaviour):
    def __init__(self, name="FoundApple"):
        super().__init__(name)

    def update(self):
        print("    [业务] 识别到：🍎")
        return py_trees.common.Status.SUCCESS


class FoundOrange(py_trees.behaviour.Behaviour):
    def __init__(self, name="FoundOrange"):
        super().__init__(name)

    def update(self):
        print("    [业务] 识别到：🍊")
        return py_trees.common.Status.SUCCESS


# =================================================================
# 2. 组装函数 (解决“修完继续走”的 Bug)
# =================================================================


def create_full_robot_tree():
    get_loc = GetLoc(name="GetLoc")

    # 1. 恢复分支
    recovery_process = py_trees.composites.Sequence(name="Recovery", memory=True)
    recovery_process.add_children([CheckWheelError(), WaitManualReset()])

    # 2. 导航判断：已经到了吗？
    at_loc = AtLoc(name="AtLoc")

    # 3. 导航动作：去走吧
    go_to_loc = GoToLoc(name="GoToLoc")

    # 核心选择器：优先级 恢复 > 判定 > 动作
    # memory=False 非常重要，确保每一秒都在重新评估优先级
    # 因为最外层套着一个 Repeat，所以每一秒都会重新评估这个 Selector 的孩子状态，确保一旦恢复分支完成了它的任务（用户输入 'r'），就能立刻切换回导航动作。
    nav_logic = py_trees.composites.Selector(name="NavLogic", memory=False)
    nav_logic.add_children([recovery_process, at_loc, go_to_loc])

    # 4. 业务并行
    work_parallel = py_trees.composites.Parallel(
        name="WorkParallel", policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )
    work_parallel.add_children([FoundApple(name="Apple"), FoundOrange(name="Orange")])

    # 5. 主流程
    main_logic = py_trees.composites.Sequence(name="MainLogic", memory=True)
    main_logic.add_children([get_loc, nav_logic, work_parallel])

    return py_trees.decorators.Repeat(child=main_logic, name="Root", num_success=-1)


# =================================================================
# 3. 执行入口
# =================================================================
if __name__ == "__main__":
    bb = py_trees.blackboard.Blackboard()

    # --- 调试配置 ---
    bb.set("config_error_chance", 0.4)  # 40%概率报错
    bb.set("config_move_speed", 3)
    bb.set("location_queue", ["地点A"])

    tree = create_full_robot_tree()
    tree.setup_with_descendants()

    print(">>> 行为树 V11.6 (修完继续移动版) 启动")

    for i in range(1, 50):
        print(f"\n--- Tick {i} ---")
        tree.tick_once()
        print(py_trees.display.unicode_tree(root=tree, show_status=True))

        # 所以在我们的设计中，只能在GetLoc中返回failer,其他的selector和parallel只能返回running或success对吧

        # 简单来说：是的，在“主干”流程上，我们要极力避免动作节点抛出 FAILURE，除非那是真的不可挽回的灾难

        # 你的理解完全正确。在构建稳健的机器人行为时：

        # 用 FAILURE 来控制流程的终点。

        # 用 RUNNING 来处理过程中的波折。

        # 用 SUCCESS 来推动阶段的交接。

        if tree.status == py_trees.common.Status.FAILURE:
            # 这里只能由第一个Actions节点GetLoc返回FAILURE触发，表示任务执行结束
            print("\n[结果] 任务队列已完成。")
            break

        if not bb.get("wheel_error"):
            time.sleep(0.1)
