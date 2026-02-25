# /opt/wm-vcpkg/installed/x64-linux/tools/python3/pip install transitions
# pick_place_battery_check.png

from transitions import Machine
import time
import random


class RobotFSM:
    # =========================================================================
    # 保留你的核心笔记：
    #
    # 长方形 (MoveToObj, CloseGrip, MoveHome)：过程状态 (Action State)。
    # 圆形 (SUCCESS, FAILURE)：终止状态。
    #
    # 图 2 升级：加入了 GoCharge 状态。
    # 任何时候 !BatteryOK 都要从当前状态连一根线到 GoCharge。
    # GoCharge 成功后回到 MoveToObj。
    # =========================================================================

    states = [
        "Idle",
        "MoveToObj",
        "CloseGrip",
        "MoveHome",
        "GoCharge",
        "Success",
        "Failure",
    ]

    def __init__(self):
        # 初始状态设为 Idle
        self.machine = Machine(model=self, states=RobotFSM.states, initial="Idle")

        # --- 1. 定义转换逻辑 ---

        # 正常路径
        self.machine.add_transition("start", "Idle", "MoveToObj")
        self.machine.add_transition("success_step", "MoveToObj", "CloseGrip")
        self.machine.add_transition("success_step", "CloseGrip", "MoveHome")
        self.machine.add_transition("success_step", "MoveHome", "Success")

        # 电池逻辑 (对应图 2 中那些发散的灰色箭头)
        # wildcard '*' 表示从任何状态检测到 low_battery 都要去 GoCharge
        self.machine.add_transition("low_battery", "*", "GoCharge")
        # 充电完成回到起点
        self.machine.add_transition("charge_done", "GoCharge", "MoveToObj")

        # 故障逻辑
        self.machine.add_transition("error_occured", "*", "Failure")

        # --- 2. 绑定钩子 (修正后的写法) ---
        # 这种写法是 transitions 库推荐的动态属性绑定
        self.machine.on_enter_MoveToObj("simulate_move_to_obj")
        self.machine.on_enter_CloseGrip("simulate_close_grip")
        self.machine.on_enter_MoveHome("simulate_move_home")
        self.machine.on_enter_GoCharge("simulate_charging")

        # 终态通知
        self.machine.on_enter_Success("on_task_finished")
        self.machine.on_enter_Failure("on_task_aborted")

    def _log(self, level, msg):
        indent = "    " * level
        print(f"{indent}{msg}")

    # --- 核心业务/仿真逻辑 ---

    def simulate_move_to_obj(self):
        self._log(2, "⚙️ [Enter] 进入 MoveToObj：正在移动...")
        if self._check_battery():
            time.sleep(0.5)
            self._log(3, "✅ [反馈] 已抵达目标。")
            self.success_step()

    def simulate_close_grip(self):
        self._log(2, "⚙️ [Enter] 进入 CloseGrip：闭合夹爪...")
        if self._check_battery():
            time.sleep(0.5)
            self._log(3, "✅ [反馈] 已抓牢。")
            self.success_step()

    def simulate_move_home(self):
        self._log(2, "⚙️ [Enter] 进入 MoveHome：正在复位...")
        if self._check_battery():
            time.sleep(0.5)
            self._log(3, "✅ [反馈] 已复位。")
            self.success_step()

    def simulate_charging(self):
        self._log(2, "🔋 [Enter] 进入 GoCharge：正在充电...")
        time.sleep(1.0)
        self._log(3, "⚡ [反馈] 电池已充满，BatteryOK 为 True。")
        self.charge_done()

    def _check_battery(self):
        """模拟工业级电量监控：如果在执行前发现没电，立刻跳转"""
        if random.random() < 0.2:  # 20% 概率没电
            self._log(3, "🚨 [电量警报] BatteryOK 为 False！中断当前任务。")
            self.low_battery()
            return False
        return True

    def on_task_finished(self):
        print(f"\n🎉 任务大获全胜！最终状态: {self.state}")

    def on_task_aborted(self):
        print(f"\n💀 任务遭遇致命故障，最终状态: {self.state}")

    def run_task(self):
        print(f">>> 任务启动！当前状态: {self.state}")
        self.start()


if __name__ == "__main__":
    robot = RobotFSM()
    robot.run_task()
