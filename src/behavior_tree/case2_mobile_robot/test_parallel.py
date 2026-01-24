import py_trees
import time


"""
如何理解运行结果？
连带失败 (Case 1)：在第 2 次 Tick，你会看到 A_QuickFail 返回 FAILURE。
即便 B_SlowWork 还在 RUNNING 状态，整个 AllPolicy_Root 也会瞬间变成 FAILURE。这就像是串联电路，一个灯泡坏了，全线断电。

胜出机制 (Case 2)：在第 2 次 Tick，当 C_FastSuccess 返回 SUCCESS 时，
你会发现 D_VerySlow 的状态从 [*] (Running) 变成了 [-] (Invalid)。
这证明了 SuccessOnOne 只要拿到一个满意的答案，就会立刻杀死其他正在运行的冗余任务。

核心结论
顺序轮询：你会发现 A 永远在 B 之前打印，C 永远在 D 之前。这说明并行节点是单线程按顺序遍历孩子的。

短路逻辑：

SuccessOnAll 对 FAILURE 敏感（遇到就崩）。

SuccessOnOne 对 SUCCESS 敏感（遇到就成）。

RUNNING 状态就是“维持现状”的信号，继续tick(执行update)

这两个实验做完后，你觉得这种“短路”机制在机器人安全（比如：一边移动，一边监控紧急停止按钮）中应该怎么应用？
"""

import py_trees
import time


# =================================================================
# 1. 通用测试任务节点 (移植自你的代码)
# =================================================================
class TestTask(py_trees.behaviour.Behaviour):
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
            print(
                f"  [节点 {self.name}] 触发终态判定 -> {self.status_to_return} (Tick: {self.tick_count})"
            )
            return self.status_to_return

        print(f"  [节点 {self.name}] 运行中... (Tick: {self.tick_count})")
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        print(f"  [节点 {self.name}] 已停止 (信号: {new_status})")


# =================================================================
# 2. 统一执行引擎
# =================================================================
def run_engine(root_node, max_ticks=8):
    root_node.setup_with_descendants()
    for i in range(1, max_ticks + 1):
        print(f"\n--- 第 {i} 次 Tick ---")
        root_node.tick_once()
        print(py_trees.display.unicode_tree(root=root_node, show_status=True))
        if root_node.status != py_trees.common.Status.RUNNING:
            print(f"\n>>> 运行结束：最终状态为 {root_node.status}")
            break
        time.sleep(0.1)


# =================================================================
# 3. 测试案例集
# =================================================================


def test_case_1_all_policy_failure():
    """验证：SuccessOnAll 模式下，一人失败，全队立刻出局"""
    print(f"\n{'=' * 60}\n 执行案例 1：一人失败导致整体失败 \n{'=' * 60}")
    task_a = TestTask(
        "A_QuickFail", result_at_tick=2, status_to_return=py_trees.common.Status.FAILURE
    )
    task_b = TestTask("B_SlowWork", result_at_tick=5)
    root = py_trees.composites.Parallel(
        name="Failure_Test", policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )
    root.add_children([task_a, task_b])
    run_engine(root)


def test_case_2_one_policy_success():
    """验证：SuccessOnOne 模式下，一人成功，任务立刻收工"""
    print(f"\n{'=' * 60}\n 执行案例 2：一人成功导致整体成功 \n{'=' * 60}")
    task_c = TestTask("C_FastSuccess", result_at_tick=2)
    task_d = TestTask("D_VerySlow", result_at_tick=10)
    root = py_trees.composites.Parallel(
        name="SuccessOne_Test", policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    root.add_children([task_c, task_d])
    run_engine(root)


def test_case_3_persistence_check():
    """
    验证：SuccessOnAll 模式下，先成功的节点是否在后续 Tick 中持续运行？
    预期：即使 A 成功了，只要 B 还在跑，每一轮依然会进入 A 的 update。
    """
    print(f"\n{'=' * 60}\n 执行案例 3：验证已成功节点是否被持续 Tick \n{'=' * 60}")
    # A 在第 2 步就成功
    task_a = TestTask("A_PersistentSuccess", result_at_tick=2)
    # B 要在第 5 步才成功
    task_b = TestTask("B_Waiting", result_at_tick=5)

    root = py_trees.composites.Parallel(
        name="Persistence_Check", policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )
    root.add_children([task_a, task_b])
    run_engine(root)


# =================================================================
# 4. 调用入口
# =================================================================
if __name__ == "__main__":
    py_trees.logging.level = py_trees.logging.Level.WARN

    # 你可以通过注释来选择你想观察的案例
    # test_case_1_all_policy_failure()
    # test_case_2_one_policy_success()
    test_case_3_persistence_check()
