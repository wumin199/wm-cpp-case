import py_trees
import time


# =================================================================
# 1. 通用测试任务节点
# =================================================================
class TestTask(py_trees.behaviour.Behaviour):
    """
    一个灵活的测试节点：
    - 在达到 result_at_tick 之前返回 RUNNING
    - 达到后根据设置返回 SUCCESS 或 FAILURE
    """

    def __init__(
        self, name, result_at_tick=3, status_to_return=py_trees.common.Status.SUCCESS
    ):
        super().__init__(name)
        self.tick_count = 0
        self.result_at_tick = result_at_tick
        self.status_to_return = status_to_return

    def update(self):
        self.tick_count += 1
        if self.tick_count >= self.result_at_tick:
            print(f"  [节点 {self.name}] 触发终态判定 -> {self.status_to_return}")
            return self.status_to_return

        print(f"  [节点 {self.name}] 运行中... (当前第 {self.tick_count} Tick)")
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        # 当节点被停止（成功、失败或被并行节点强制打断）时触发
        print(f"  [节点 {self.name}] 已停止 (信号: {new_status})")


# =================================================================
# 2. 统一执行引擎
# =================================================================
def run_engine(root_node, max_ticks=6):
    """负责驱动树的运行并打印状态"""
    root_node.setup_with_descendants()

    for i in range(1, max_ticks + 1):
        print(f"\n--- 第 {i} 次 Tick ---")
        root_node.tick_once()

        # 打印树的可视化状态
        print(py_trees.display.unicode_tree(root=root_node, show_status=True))

        # 检查根节点是否已经结束
        if root_node.status != py_trees.common.Status.RUNNING:
            print(f"\n>>> 运行结束：最终状态为 {root_node.status}")
            break
        time.sleep(0.1)


# =================================================================
# 3. 封装测试案例
# =================================================================


def test_case_1_all_policy_failure():
    """
    案例 1：SuccessOnAll (全成才算成)
    场景：A 很快失败了，观察 B 是否会被立刻“连累”导致打断。
    """
    print(f"\n{'=' * 60}")
    print(" 执行案例 1：SuccessOnAll - 一人失败，全队出局")
    print(f"{'=' * 60}")

    # A 在第 2 步失败
    task_a = TestTask(
        "A_QuickFail", result_at_tick=2, status_to_return=py_trees.common.Status.FAILURE
    )
    # B 本来要 5 步才成功
    task_b = TestTask(
        "B_SlowWork", result_at_tick=5, status_to_return=py_trees.common.Status.SUCCESS
    )

    root = py_trees.composites.Parallel(
        name="AllPolicy_Root", policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )
    root.add_children([task_a, task_b])
    run_engine(root)


def test_case_2_one_policy_success():
    """
    案例 2：SuccessOnOne (一成就算成)
    场景：C 很快成功了，观察缓慢的 D 是否会被立刻“切断”。
    """
    print(f"\n{'=' * 60}")
    print(" 执行案例 2：SuccessOnOne - 一人成功，任务收工")
    print(f"{'=' * 60}")

    # C 在第 2 步成功
    task_c = TestTask(
        "C_FastSuccess",
        result_at_tick=2,
        status_to_return=py_trees.common.Status.SUCCESS,
    )
    # D 预计要运行很久
    task_d = TestTask("D_VerySlow", result_at_tick=10)

    root = py_trees.composites.Parallel(
        name="OnePolicy_Root", policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    root.add_children([task_c, task_d])
    run_engine(root)


# =================================================================
# 4. Main 调用入口
# =================================================================
if __name__ == "__main__":
    # 屏蔽内部日志，只看我们自定义的 print
    py_trees.logging.level = py_trees.logging.Level.WARN

    # --- 你可以通过注释下面其中一行来选择测试哪个案例 ---

    test_case_1_all_policy_failure()  # 测试连带失败

    # test_case_2_one_policy_success()  # 测试胜出机制
