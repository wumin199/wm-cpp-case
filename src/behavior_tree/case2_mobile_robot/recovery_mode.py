import py_trees
import time
import random


# =================================================================
# 1. 任务管理层
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
        self.blackboard.set("wheel_error", False)  # 初始任务无错误
        print(f"\n[任务系统] 目标更新为: {target}")
        return py_trees.common.Status.SUCCESS


# =================================================================
# 2. 异常处理层 (新增)
# =================================================================
class CheckWheelError(py_trees.behaviour.Behaviour):
    def __init__(self, name="CheckWheelError"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        error = self.blackboard.get("wheel_error")
        if error:
            print("  [监控] !!! 警报：检测到轮子卡住或异常 !!!")
            return py_trees.common.Status.SUCCESS
        # 没有错误时返回 FAILURE，以便 Selector 切换到下一个正常的分支
        return py_trees.common.Status.FAILURE


class WaitManualReset(py_trees.behaviour.Behaviour):
    def __init__(self, name="WaitManualReset"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        print("\n" + "!" * 50)
        print("  [恢复模式] 机器人已停止。请手动排除障碍并输入 'r' 恢复任务...")
        user_input = input("  >> 等待输入: ")

        if user_input.lower() == "r":
            print("  [恢复模式] 故障已排除，重置错误标志。")
            self.blackboard.set("wheel_error", False)
            return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.RUNNING


# =================================================================
# 3. 导航执行层
# =================================================================
class AtLoc(py_trees.behaviour.Behaviour):
    def __init__(self, name="AtLoc"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        is_at = self.blackboard.get("at_destination")
        if is_at:
            print(f"  [判断] 已在 {self.blackboard.get('current_location')}，无需移动")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class GoToLoc(py_trees.behaviour.Behaviour):
    def __init__(self, name="GoToLoc"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.move_time = 0

    def update(self):
        # 模拟 15% 的概率发生故障
        if random.random() < 0.15:
            print("  [动作] 糟糕！轮子突然卡住了！")
            self.blackboard.set("wheel_error", True)
            return py_trees.common.Status.FAILURE

        self.move_time += 1
        if self.move_time >= 3:
            print(f"  [动作] 已到达目的地: {self.blackboard.get('current_location')}")
            self.blackboard.set("at_destination", True)
            self.move_time = 0
            return py_trees.common.Status.SUCCESS
        else:
            print(
                f"  [动作] 正在前往 {self.blackboard.get('current_location')}... ({self.move_time}/3)"
            )

        return py_trees.common.Status.RUNNING


# =================================================================
# 4. 业务执行层
# =================================================================
class FoundApple(py_trees.behaviour.Behaviour):
    def update(self):
        print("    [业务] 识别到：🍎 苹果")
        return py_trees.common.Status.SUCCESS


class FoundOrange(py_trees.behaviour.Behaviour):
    def update(self):
        print("    [业务] 识别到：🍊 橙子")
        return py_trees.common.Status.SUCCESS


# =================================================================
# 5. 组装行为树
# =================================================================
def create_full_robot_tree():
    # 1. 任务获取
    get_loc = GetLoc(name="GetLoc")

    # 2. 故障恢复分支 (Sequence)
    # 逻辑：检查是否有错 -> 若有错则进入等待重置逻辑
    recovery_seq = py_trees.composites.Sequence(name="RecoveryProcess", memory=True)
    recovery_seq.add_children([CheckWheelError(), WaitManualReset()])

    # 3. 正常导航分支 (Selector)
    loc_selector = py_trees.composites.Selector(name="LocSelector", memory=False)
    loc_selector.add_children([AtLoc(name="AtLoc"), GoToLoc(name="GoToLoc")])

    # 4. 导航总控 (Selector)
    # 优先级：RecoveryProcess > LocSelector
    nav_with_recovery = py_trees.composites.Selector(
        name="NavWithRecovery", memory=False
    )
    nav_with_recovery.add_children([recovery_seq, loc_selector])

    # 5. 业务并行逻辑
    work_parallel = py_trees.composites.Parallel(
        name="WorkParallel", policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )
    work_parallel.add_children(
        [FoundApple(name="FoundApple"), FoundOrange(name="FoundOrange")]
    )

    # 6. 主逻辑序列
    main_logic = py_trees.composites.Sequence(name="MainLogic", memory=True)
    main_logic.add_children([get_loc, nav_with_recovery, work_parallel])

    # 7. 根节点装饰器
    root = py_trees.decorators.Repeat(
        child=main_logic, name="RepeatUntilQueueEmpty", num_success=-1
    )
    return root


# =================================================================
# 6. 执行循环
# =================================================================
if __name__ == "__main__":
    py_trees.logging.level = py_trees.logging.Level.WARN

    bb = py_trees.blackboard.Blackboard()
    bb.set("location_queue", ["地点A", "地点B"])

    tree = create_full_robot_tree()
    tree.setup_with_descendants()

    print(">>> 行为树 V11.0 (故障恢复增强版) 启动")
    print(">>> 运行提示：当看到'轮子卡住'警报时，请在提示处输入 'r' 并回车。")

    for i in range(1, 40):  # 增加循环次数以应对恢复等待
        print(f"\n--- Tick {i} ---")
        tree.tick_once()
        print(py_trees.display.unicode_tree(root=tree, show_status=True))

        if tree.status == py_trees.common.Status.FAILURE:
            print("\n[结果] 任务队列已清空，系统停止。")
            break

        # 只有在不需要等待用户输入时才短暂休眠
        if not bb.get("wheel_error"):
            time.sleep(0.1)
