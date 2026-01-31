import time
import random


class PureRobotFSM:
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
    # =========================================================================

    def __init__(self):
        # 初始态 (Initial State): 实心黑圆点
        self.state = "Idle"

        # 定义转移映射 (State Transition Map)
        # 模拟 transitions 库的 trigger 机制
        self.transitions = {
            "Idle": {"success": "MoveToObj"},
            "MoveToObj": {"success": "CloseGrip"},
            "CloseGrip": {"success": "MoveHome"},
            "MoveHome": {"success": "Success"},
        }

    # --- 模拟 transitions 库的跳转触发器 ---

    def trigger(self, event):
        """裸写跳转引擎：根据当前状态和事件查找下一状态"""
        print(f"\n[FSM Event] 触发事件: '{event}'")

        if event == "error":
            self._transition_to("Failure")
            return

        next_state = self.transitions.get(self.state, {}).get(event)

        if next_state:
            self._transition_to(next_state)
        else:
            print(f"⚠️ 警告: 状态 {self.state} 无法响应事件 {event}")

    def _transition_to(self, next_state):
        """核心跳转逻辑：包含 exit -> transition -> enter 的完整生命周期"""

        # 1. 执行旧状态的 EXIT 钩子
        exit_hook = f"on_exit_{self.state}"
        if hasattr(self, exit_hook):
            getattr(self, exit_hook)()

        # 2. 执行跳转前的 BEFORE 钩子
        before_hook = f"before_to_{next_state}"
        if hasattr(self, before_hook):
            getattr(self, before_hook)()

        # 3. 更新状态
        print(f"--- 状态转换: {self.state} >> {next_state} ---")
        self.state = next_state

        # 4. 执行新状态的 ENTER 钩子 (开始仿真动作)
        enter_hook = f"on_enter_{self.state}"
        if hasattr(self, enter_hook):
            getattr(self, enter_hook)()

    # --- 生命周期钩子 (Lifecycle Hooks) ---

    def before_to_MoveToObj(self):
        print("[Hook - BEFORE] 正在检查机器人自检状态：电池、电机正常。")

    def before_to_CloseGrip(self):
        print("[Hook - BEFORE] 正在通过相机确认物体位置。")

    def on_exit_MoveToObj(self):
        print("[Hook - EXIT] 机器人已就位，切断底盘动力。")

    # --- 动作执行 (ENTER 触发) ---

    def on_enter_MoveToObj(self):
        print("  [Action] 正在执行 MoveToObj：驱动底盘移动...")
        time.sleep(0.8)
        if random.random() < 0.3:  # 30% 失败率
            raise RuntimeError("Navigation Error")
        print("  [反馈] 已抵达物体。")

    def on_enter_CloseGrip(self):
        print("  [Action] 正在执行 CloseGrip：闭合夹爪...")
        time.sleep(0.8)
        if random.random() < 0.3:
            raise RuntimeError("Grip Error")
        print("  [反馈] 已抓牢物体。")

    def on_enter_MoveHome(self):
        print("  [Action] 正在执行 MoveHome：返回起始点...")
        time.sleep(0.8)
        print("  [反馈] 机器人已复位。")

    # --- 任务主循环 ---

    def run_task(self):
        try:
            print(f">>> 任务启动！当前状态: {self.state}")

            # 手动步进，模拟 success_step 触发
            self.trigger("success")  # Idle -> MoveToObj
            self.trigger("success")  # MoveToObj -> CloseGrip
            self.trigger("success")  # CloseGrip -> MoveHome
            self.trigger("success")  # MoveHome -> Success

            print(f"\n任务结束，最终状态: {self.state} (SUCCESS 🏆)")

        except Exception as e:
            print(f"\n！捕获异常: {e}")
            self.trigger("error")  # 强制跳转到 Failure
            print(f"任务中断，最终状态: {self.state} (FAILURE ❌)")


if __name__ == "__main__":
    robot = PureRobotFSM()
    robot.run_task()
