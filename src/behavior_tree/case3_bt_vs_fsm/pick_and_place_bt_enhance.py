# pip install py_trees
import py_trees
import time
import random

# =========================================================================
# 保留你的核心笔记 (FSM vs BT 逻辑差异)
# =========================================================================


class RobotAction(py_trees.behaviour.Behaviour):
    def __init__(self, name, exit_msg=None):
        super(RobotAction, self).__init__(name)
        self.exit_msg = exit_msg

    def _log(self, level, msg):
        indent = "    " * level
        print(f"{indent}{msg}")

    def initialise(self):
        # 完全复刻 FSM 的 Enter 打印
        if self.name == "MoveToObj":
            self._log(2, "⚙️ [Enter] 进入 MoveToObj：正在移动...")
        elif self.name == "CloseGrip":
            self._log(2, "⚙️ [Enter] 进入 CloseGrip：闭合夹爪...")
        elif self.name == "MoveHome":
            self._log(2, "⚙️ [Enter] 进入 MoveHome：正在复位...")

    def update(self):
        time.sleep(0.5)
        if random.random() < 0.3:
            # 模拟 30% 失败率
            error_msg = (
                "路径被突然出现的障碍物阻挡！"
                if self.name == "MoveToObj"
                else "物体表面太滑，抓取失败！"
            )
            self._log(3, f"🚨 [报错] {error_msg}")
            return py_trees.common.Status.FAILURE

        # 成功反馈
        feedback = "已抵达目标。" if self.name == "MoveToObj" else "已抓牢。"
        if self.name == "MoveHome":
            feedback = "已复位。"
        self._log(3, f"✅ [反馈] {feedback}")
        return py_trees.common.Status.SUCCESS

    def terminate(self, new_status):
        # 只有在成功完成后才打印特定的 Exit 信息 (对应 FSM 的 on_exit)
        if new_status == py_trees.common.Status.SUCCESS and self.exit_msg:
            self._log(1, f"🔌 [Exit] {self.exit_msg}")


class PhaseTransition(py_trees.behaviour.Behaviour):
    """专门负责阶段转换提示和 Before 预检的节点"""

    def __init__(self, transition_text, before_text):
        super(PhaseTransition, self).__init__("Transition")
        self.transition_text = transition_text
        self.before_text = before_text

    def update(self):
        print(f"\n[ 阶段转换 ] >>> {self.transition_text}")
        print(f"    🔍 [Before] {self.before_text}")
        time.sleep(0.3)
        return py_trees.common.Status.SUCCESS


def create_bt():
    root = py_trees.composites.Sequence(name="PickPlace", memory=True)

    # 1. 第一阶段
    t1 = PhaseTransition("准备前往 MoveToObj", "机器人自检...")
    a1 = RobotAction("MoveToObj", exit_msg="离开 MoveToObj：切断底盘动力。")

    # 2. 第二阶段
    t2 = PhaseTransition("准备从 MoveToObj 切换到 CloseGrip", "环境预检...")
    a2 = RobotAction("CloseGrip")

    # 3. 第三阶段
    t3 = PhaseTransition(
        "准备前往 MoveHome", "复位准备..."
    )  # 这里的 before 文字你可以自定义
    a3 = RobotAction("MoveHome")

    root.add_children([t1, a1, t2, a2, t3, a3])
    return root


if __name__ == "__main__":
    bt_root = create_bt()
    bt_root.setup_with_descendants()

    print(">>> 任务启动！当前状态: Idle")

    # BT 的 Tick 模拟
    # 注意：Sequence 会依次执行子节点。当子节点返回 FAILURE，整棵树停止。
    result = bt_root.tick_once()

    if bt_root.status == py_trees.common.Status.SUCCESS:
        print(f"\n🎉 任务成功！最终状态: Success")
    else:
        # 模拟 FSM 的 error_occured 结果
        print(f"\n💥 运行时异常")
        print(f"❌ 任务失败跳转至: Failure (已进入终止状态)")
