import py_trees
import time
import random

# =========================================================================
# 教学要点：
# 1. BatteryCheck: 这里的 Condition 节点，相当于 FSM 中的 Transition Guard。
# 2. Charger: 专属的充电动作，它与业务动作 (RobotAction) 完全解耦。
# 3. 这里的 Selector 就像一个实时巡检员，优先级左高右低。
# 4. 关键点：有running状态。因为robot action里面有running，所以有机会一直在tick中检查battery的状态，是这样子的么。在 FSM 中，当机器人处于某个状态时，它通常被“困”在那个函数里执行。但在行为树中，因为有了 RUNNING 状态，逻辑的控制权发生了微妙的流转
# 5. 感觉这个和plc的stl很像，没有sleep/delay函数，而是会一直循环。
# =========================================================================


class BatteryCheck(py_trees.behaviour.Behaviour):
    """【条件节点】仅负责监测电量，不执行动作"""

    def __init__(self, name="BatteryLow?"):
        super().__init__(name)
        self.triggered_once = False

    def update(self):
        # 模拟 20% 概率电量不足，且演示中只触发一次
        if not self.triggered_once and random.random() < 0.2:
            print("            🚨 [电量警报] BatteryOK 为 False！中断当前任务。")
            self.triggered_once = True
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class GoCharge(py_trees.behaviour.Behaviour):
    """【专项动作节点】专门负责充电逻辑"""

    def __init__(self, name="GoCharge"):
        super().__init__(name)
        self.progress = 0

    def initialise(self):
        self.progress = 0
        print("        🔋 [Enter] 进入 GoCharge：连接充电桩，开始充电...")

    def update(self):
        time.sleep(0.5)
        self.progress += 1
        if self.progress < 3:
            return py_trees.common.Status.RUNNING

        print("            ⚡ [反馈] 充电完成，电量已充满 (BatteryOK=True)。")
        return py_trees.common.Status.SUCCESS


class RobotAction(py_trees.behaviour.Behaviour):
    """【业务动作节点】模拟搬运任务"""

    def __init__(self, name, duration=3):
        super().__init__(name)
        self.duration = duration
        self.ticks = 0

    def initialise(self):
        self.ticks = 0
        print(f"        ⚙️ [Enter] 进入 {self.name}：正在执行...")

    def update(self):
        time.sleep(0.5)
        self.ticks += 1
        if self.ticks < self.duration:
            return py_trees.common.Status.RUNNING

        print(f"            ✅ [反馈] {self.name} 已顺利完成。")
        return py_trees.common.Status.SUCCESS

    def terminate(self, new_status):
        # 只有在 RUNNING 状态下被强制 INVALID（抢占）时才打印中断信号
        if (
            new_status == py_trees.common.Status.INVALID
            and self.status == py_trees.common.Status.RUNNING
        ):
            print(f"            🔌 [系统信号] {self.name} 动作被外部强制挂起/中断。")


def create_bt():
    # 根节点：反应式选择器（不记状态，每轮必从左往右扫）
    root = py_trees.composites.Selector(name="Root", memory=False)

    # 充电子树：由一个条件和一个专属动作组成
    charge_logic = py_trees.composites.Sequence(name="ChargeLogic", memory=False)
    charge_logic.add_children([BatteryCheck(), GoCharge()])  # 检查  # 执行

    # 业务子树：带记忆的序列（充电回来从断点继续）
    nominal_task = py_trees.composites.Sequence(name="Nominal", memory=True)
    nominal_task.add_children(
        [
            RobotAction("MoveToObj", duration=3),
            RobotAction("CloseGrip", duration=2),
            RobotAction("MoveHome", duration=3),
        ]
    )

    root.add_children([charge_logic, nominal_task])
    return root


def display_bt_structure():
    # 构造树
    root = py_trees.composites.Selector(name="Root", memory=False)

    charge_logic = py_trees.composites.Sequence(name="ChargeLogic", memory=False)
    charge_logic.add_children([BatteryCheck(), Charger()])

    nominal_task = py_trees.composites.Sequence(name="Nominal", memory=True)
    nominal_task.add_children(
        [RobotAction("MoveToObj"), RobotAction("CloseGrip"), RobotAction("MoveHome")]
    )

    root.add_children([charge_logic, nominal_task])

    # 使用 unicode_tree 打印
    print("\n" + "=" * 20 + " 行为树逻辑蓝图 " + "=" * 20)
    print(py_trees.display.unicode_tree(root=root))
    print("=" * 56)


if __name__ == "__main__":
    #
    # display_bt_structure()

    bt_root = create_bt()
    bt_root.setup_with_descendants()

    print(">>> 任务启动！当前状态: Idle")

    while True:
        bt_root.tick_once()
        if bt_root.status == py_trees.common.Status.SUCCESS:
            print("\n🎉 任务大获全胜！最终状态: Success")
            break
        time.sleep(0.1)
