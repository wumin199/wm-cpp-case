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

        # --- 1. 定义带有 before/after 钩子的转换逻辑 ---
        # before: 在状态跳转动作开始“之前”执行（类似于预检）
        # after: 在状态跳转彻底完成“之后”执行（类似于日志记录）

        self.machine.add_transition(
            trigger="start", source="Idle", dest="MoveToObj", before="pre_check_robot"
        )

        self.machine.add_transition(
            trigger="success_step",
            source="MoveToObj",
            dest="CloseGrip",
            before="pre_check_environment",
        )

        self.machine.add_transition(
            trigger="success_step", source="CloseGrip", dest="MoveHome"
        )

        self.machine.add_transition(
            trigger="success_step", source="MoveHome", dest="Success"
        )

        # 错误跳转逻辑
        self.machine.add_transition(trigger="error_occured", source="*", dest="Failure")

        # --- 2. 绑定 enter/exit 钩子 ---
        # on_enter: 进入该状态的瞬间触发（通常用于启动仿真/实际动作）
        # on_exit: 离开该状态的瞬间触发（通常用于清理现场/关闭电机）

        # 移动到物体
        self.machine.on_enter_MoveToObj("simulate_move_to_obj")
        self.machine.on_exit_MoveToObj("stop_chassis_motors")

        # 闭合夹爪
        self.machine.on_enter_CloseGrip("simulate_close_grip")

        # 返回原地
        self.machine.on_enter_MoveHome("simulate_move_home")

    # --- 生命周期钩子函数 (Lifecycle Hooks) ---

    def pre_check_robot(self):
        print("\n[Hook - BEFORE] 正在检查机器人自检状态：电池、电机、传感器正常。")

    def pre_check_environment(self):
        print("\n[Hook - BEFORE] 正在通过相机确认物体位置未发生偏移。")

    def stop_chassis_motors(self):
        print("[Hook - EXIT] 机器人已就位，正在切断底盘动力以保持稳定。")

    # --- 仿真函数区域 ---

    def simulate_move_to_obj(self):
        print("  [Action - ENTER] 正在执行 MoveToObj：驱动底盘向物体移动...")
        time.sleep(0.8)
        if random.random() > 0.3:
            print("  [反馈] 传感器显示：已抵达物体。")
        else:
            print("  [报错] 路径受阻！")
            raise RuntimeError("Navigation Error")

    def simulate_close_grip(self):
        print("  [Action - ENTER] 正在执行 CloseGrip：驱动夹爪闭合...")
        time.sleep(0.8)
        if random.random() > 0.3:
            print("  [反馈] 压力传感器：已抓牢物体。")
        else:
            print("  [报错] 物体掉落！")
            raise RuntimeError("Grip Error")

    def simulate_move_home(self):
        print("  [Action - ENTER] 正在执行 MoveHome：返回 Home 点...")
        time.sleep(0.8)
        print("  [反馈] 机器人已复位。")

    def run_task(self):
        try:
            print(f">>> 任务启动！当前状态: {self.state}")
            self.start()  # Idle -> MoveToObj

            self.success_step()  # MoveToObj -> CloseGrip
            self.success_step()  # CloseGrip -> MoveHome
            self.success_step()  # MoveHome -> Success

            print(f"\n任务结束，FSM 最终状态: {self.state} (SUCCESS 🏆)")

        except Exception as e:
            print(f"\n！捕获异常: {e}")
            self.error_occured()
            print(f"任务中断，FSM 已跳转至最终状态: {self.state} (FAILURE ❌)")


if __name__ == "__main__":
    robot = RobotFSM()
    robot.run_task()
