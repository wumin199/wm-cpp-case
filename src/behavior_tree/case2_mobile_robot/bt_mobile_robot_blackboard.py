import py_trees
import time


# =================================================================
# 1. 任务管理层 (对应图中的 GetLoc)
# =================================================================
class GetLoc(py_trees.behaviour.Behaviour):
    def __init__(self, name="GetLoc"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        queue = self.blackboard.get("location_queue")
        if not queue:
            return py_trees.common.Status.FAILURE

        # 从队列 Pop 一个地点并写入黑板
        target = queue.pop(0)
        self.blackboard.set("current_location", target)
        self.blackboard.set("at_destination", False)  # 初始状态不在目的地
        print(f"\n[任务系统] 目标更新为: {target}")
        return py_trees.common.Status.SUCCESS


# =================================================================
# 2. 导航判断层 (对应图中的 AtLoc 和 GoToLoc)
# =================================================================
class AtLoc(py_trees.behaviour.Behaviour):
    def __init__(self, name="AtLoc"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self):
        # 检查黑板数据判断是否到达
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
        self.move_time += 1
        # print(f"  [动作] 正在前往 {self.blackboard.get('current_location')}...")
        if self.move_time >= 3:  # 模拟移动耗时
            print(f"  [动作] 已到达 {self.blackboard.get('current_location')}")
            self.blackboard.set("at_destination", True)
            self.move_time = 0
            return py_trees.common.Status.SUCCESS
        else:
            print(f"  [动作] 正在前往 {self.blackboard.get('current_location')}...")
        return py_trees.common.Status.RUNNING


# =================================================================
# 3. 业务执行层 (对应图中的 FoundApple 和 FoundOrange)
# =================================================================
class FoundApple(py_trees.behaviour.Behaviour):
    def update(self):
        # 这里的实现可以共享视觉资源
        print("    [业务] 识别到：🍎 苹果")
        return py_trees.common.Status.SUCCESS


class FoundOrange(py_trees.behaviour.Behaviour):
    def update(self):
        print("    [业务] 识别到：🍊 橙子")
        return py_trees.common.Status.SUCCESS


# =================================================================
# 4. 组装完整架构
# =================================================================
def create_full_robot_tree():
    # --- 1. 获取任务 ---
    get_loc = GetLoc(name="GetLoc")

    # --- 2. 导航选择逻辑 (Selector ?) ---
    loc_selector = py_trees.composites.Selector(name="LocSelector", memory=False)
    loc_selector.add_children([AtLoc(), GoToLoc()])

    # --- 3. 业务并行逻辑 (Parallel ⇉) ---
    # 按照图中所示，苹果和橙子是并行寻找的

    # SuccessOnAll 对 FAILURE 敏感（遇到就崩）。
    # SuccessOnOne 对 SUCCESS 敏感（遇到就成）。
    # RUNNING 状态就是“维持现状”的信号，继续tick(执行update)

    work_parallel = py_trees.composites.Parallel(
        name="WorkParallel", policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )
    work_parallel.add_children(
        [FoundApple(name="FoundApple"), FoundOrange(name="FoundOrange")]
    )

    # --- 4. 主任务序列 (Sequence →) ---
    # 对应图中：GetLoc -> LocSelector -> WorkParallel
    main_logic = py_trees.composites.Sequence(name="MainLogic", memory=True)
    main_logic.add_children([get_loc, loc_selector, work_parallel])

    # --- 5. 装饰器循环 (Repeat δ) ---
    # 直到队列空，GetLoc 返回 Failure 为止
    root = py_trees.decorators.Repeat(
        child=main_logic,
        name="RepeatUntilQueueEmpty",
        num_success=-1,  # 无限重复直到子树失败
    )
    return root


if __name__ == "__main__":
    # 初始化黑板数据
    bb = py_trees.blackboard.Blackboard()
    bb.set("location_queue", ["地点A", "地点B"])  # 任务清单

    tree = create_full_robot_tree()
    tree.setup_with_descendants()

    print(">>> 行为树 V10.0 (图片完整还原版) 启动")
    for i in range(1, 20):
        print(f"\n--- Tick {i} ---")
        tree.tick_once()
        print(py_trees.display.unicode_tree(root=tree, show_status=True))

        if tree.status == py_trees.common.Status.FAILURE:
            print("\n[结果] 任务队列已清空，系统停止。")
            break
        time.sleep(0.1)
