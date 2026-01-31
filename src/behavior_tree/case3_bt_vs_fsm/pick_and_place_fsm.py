# /opt/wm-vcpkg/installed/x64-linux/tools/python3/pip install transitions
# pick_place_example.png

from transitions import Machine
import time
import random


class RobotFSM:
    # =========================================================================
    # 保留你的核心笔记：
    #
    # 定义状态 (对应图中的长方形)
    #
    # 长方形 (MoveToObj, CloseGrip, MoveHome)：代表过程状态 (Intermediate States)。
    # 机器人正处于“做某事”的过程中。
    # 圆形 (SUCCESS, FAILURE)：代表终止状态 (Terminal States)。一旦进入这个状态，状态机就停止运行，任务结束。
    #
    # 长方形, 执行状态 (Action State), 列表中的普通字符串, 任务正在进行中
    # 双线圆形, 终态 (Final/Exit State), 列表中的普通字符串, 任务彻底完成（成功或失败）
    # 实心黑圆点, 初始态 (Initial State), initial='Idle', 程序的启动起点
    #
    # 在左图的行为树（BT）中，你会发现没有专门代表 SUCCESS 或 FAILURE 的长方形或圆圈。
    #
    # 这是因为 BT 的设计更模块化：
    #
    # SUCCESS 和 FAILURE 不是“一个地方”（状态），而是**“一个信号” (Status/Signal)**。
    #
    # 每个动作节点（如 MoveToObj）在运行完后，会向上汇报一个信号。
    #
    # 根节点的箭头（Sequence）根据这些信号决定是继续往右走，还是直接宣告全树失败。
    #
    # 这就是为什么说 BT 更容易组合和修改：你不需要像 FSM 那样画一根长长的线连到最后的圆圈上，
    # 你只需要关注节点本身返回什么信号即可。
    #
    # 定义所有逻辑状态
    # 包含图中的长方形（过程态）和圆形（终止态）
    # =========================================================================

    states = [
        "Idle",  # 初始点 (实心黑圆点)
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

        # 错误跳转逻辑：从任何状态 (*) 都可以跳向 Failure (对应图中所有向右转的 failure 线)
        self.machine.add_transition(trigger="error_occured", source="*", dest="Failure")

        # 绑定仿真函数：当进入某个状态时，执行对应的 simulate 方法
        self.machine.on_enter_MoveToObj("simulate_move_to_obj")
        self.machine.on_enter_CloseGrip("simulate_close_grip")
        self.machine.on_enter_MoveHome("simulate_move_home")

    # --- 仿真函数区域 ---

    def simulate_move_to_obj(self):
        print("  [仿真] 正在规划路径并驱动底盘向物体移动...")
        time.sleep(0.8)
        if random.random() > 0.1:  # 90% 成功率
            print("  [反馈] 传感器显示：已抵达物体。")
        else:
            print("  [报错] 路径受阻或电机超时！")
            raise RuntimeError("Navigation Error")

    def simulate_close_grip(self):
        print("  [仿真] 驱动夹爪执行器：闭合...")
        time.sleep(0.8)
        if random.random() > 0.1:
            print("  [反馈] 压力传感器：已抓牢物体。")
        else:
            print("  [报错] 抓取失败，物体滑落！")
            raise RuntimeError("Grip Error")

    def simulate_move_home(self):
        print("  [仿真] 驱动底盘返回 Home 点...")
        time.sleep(0.8)
        print("  [反馈] 机器人已复位。")

    def run_task(self):
        try:
            print(f">>> FSM 当前状态: {self.state}")
            self.start()  # Idle -> MoveToObj

            # 驱动状态机向前步进
            # 由于绑定了 on_enter 回调，每次跳转都会自动运行对应的仿真逻辑
            self.success_step()  # MoveToObj -> CloseGrip
            self.success_step()  # CloseGrip -> MoveHome
            self.success_step()  # MoveHome -> Success

            print(f"\n任务结束，FSM 最终状态: {self.state} (SUCCESS 🏆)")

        except Exception as e:
            print(f"\n！捕获异常: {e}")
            self.error_occured()  # 跳转到 Failure 状态
            print(f"任务中断，FSM 已跳转至最终状态: {self.state} (FAILURE ❌)")


if __name__ == "__main__":
    robot = RobotFSM()
    robot.run_task()
