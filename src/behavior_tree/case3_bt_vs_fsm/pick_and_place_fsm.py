# /opt/wm-vcpkg/installed/x64-linux/tools/python3/pip install transitions

# pick_place_example.png

from transitions import Machine
import time


class RobotFSM:
    # 定义状态 (对应图中的长方形)

    # 长方形 (MoveToObj, CloseGrip, MoveHome)：代表过程状态 (Intermediate States)。机器人正处于“做某事”的过程中。
    # 圆形 (SUCCESS, FAILURE)：代表终止状态 (Terminal States)。一旦进入这个状态，状态机就停止运行，任务结束。

    # 长方形,执行状态 (Action State),列表中的普通字符串,任务正在进行中
    # 双线圆形,终态 (Final/Exit State),列表中的普通字符串,任务彻底完成（成功或失败）
    # 实心黑圆点,初始态 (Initial State),initial='Idle',程序的启动起点

    # 在左图的行为树（BT）中，你会发现没有专门代表 SUCCESS 或 FAILURE 的长方形或圆圈。

    # 这是因为 BT 的设计更模块化：

    # SUCCESS 和 FAILURE 不是“一个地方”（状态），而是**“一个信号” (Status/Signal)**。

    # 每个动作节点（如 MoveToObj）在运行完后，会向上汇报一个信号。

    # 根节点的箭头（Sequence）根据这些信号决定是继续往右走，还是直接宣告全树失败。

    # 这就是为什么说 BT 更容易组合和修改：你不需要像 FSM 那样画一根长长的线连到最后的圆圈上，你只需要关注节点本身返回什么信号即可。

    # 定义所有逻辑状态
    # 包含图中的长方形（过程态）和圆形（终止态）
    states = [
        "Idle",  # 初始点 (黑圆点)
        "MoveToObj",  # 执行中 (长方形)
        "CloseGrip",  # 执行中 (长方形)
        "MoveHome",  # 执行中 (长方形)
        "Success",  # 终态 (双线圆圈 SUCCESS)
        "Failure",  # 终态 (双线圆圈 FAILURE)
    ]

    def __init__(self):
        # 初始化状态机
        self.machine = Machine(model=self, states=RobotFSM.states, initial="Idle")

        # 定义转换逻辑 (对应图中的箭头)
        # trigger: 触发动作名, source: 起点, dest: 终点
        self.machine.add_transition(trigger="start", source="Idle", dest="MoveToObj")
        self.machine.add_transition(
            trigger="success_step", source="MoveToObj", dest="CloseGrip"
        )
        self.machine.add_transition(
            trigger="success_step", source="CloseGrip", dest="MoveHome"
        )
        self.machine.add_transition(
            trigger="success_step", source="MoveHome", dest="Success"
        )
        self.machine.add_transition(trigger="error_occured", source="*", dest="Failure")

    def run_task(self):
        try:
            print(f">>> FSM 当前状态: {self.state}")
            self.start()

            for step in ["MoveToObj", "CloseGrip", "MoveHome"]:
                print(f"  [FSM] 正在状态 {self.state} 执行业务...")
                time.sleep(0.5)
                self.success_step()

            print(f">>> FSM 最终状态: {self.state}")
        except Exception:
            self.error_occured()


# 运行
if __name__ == "__main__":
    fsm = RobotFSM()
    fsm.run_task()
