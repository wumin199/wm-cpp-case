# /opt/wm-vcpkg/installed/x64-linux/tools/python3/pip install transitions
# pick_place_example.png

from transitions import Machine
import time
import random


class RobotFSM:

    states = ["Idle", "MoveToObj", "CloseGrip", "MoveHome", "Success", "Failure"]

    def __init__(self):
        self.machine = Machine(model=self, states=RobotFSM.states, initial="Idle")

        # 定义转换逻辑 - 完整保留 before 检查
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
        self.machine.add_transition(trigger="error_occured", source="*", dest="Failure")

        # 绑定钩子 - 完整保留 Enter 和 Exit
        self.machine.on_enter_MoveToObj("simulate_move_to_obj")
        self.machine.on_exit_MoveToObj("stop_chassis_motors")

        self.machine.on_enter_CloseGrip("simulate_close_grip")

        self.machine.on_enter_MoveHome("simulate_move_home")

        # 终态处理
        self.machine.on_enter_Success("on_task_finished")
        self.machine.on_enter_Failure("on_task_aborted")

    def _log(self, level, msg):
        indent = "    " * level
        print(f"{indent}{msg}")

    # --- 生命周期钩子 (完全保留你的原有逻辑) ---
    def pre_check_robot(self):
        print("\n[ 阶段转换 ] >>> 准备前往 MoveToObj")
        self._log(1, "🔍 [Before] 机器人自检...")

    def pre_check_environment(self):
        print("\n[ 阶段转换 ] >>> 准备从 MoveToObj 切换到 CloseGrip")
        self._log(1, "🔍 [Before] 环境预检...")

    def stop_chassis_motors(self):
        self._log(1, "🔌 [Exit] 离开 MoveToObj：切断底盘动力。")

    # --- 核心业务逻辑 (内部消化跳转，消灭外部 try-except) ---

    def simulate_move_to_obj(self):
        self._log(2, "⚙️ [Enter] 进入 MoveToObj：正在移动...")
        time.sleep(0.5)
        if random.random() > 0.3:  # 70% 成功率
            self._log(3, "✅ [反馈] 已抵达目标。")
            self.success_step()  # 成功则驱动自己跳入下一步
        else:
            self._log(3, "🚨 [报错] 路径被突然出现的障碍物阻挡！")
            self.error_occured()  # 失败则驱动自己跳入 Failure

    def simulate_close_grip(self):
        self._log(2, "⚙️ [Enter] 进入 CloseGrip：闭合夹爪...")
        time.sleep(0.5)
        if random.random() > 0.3:
            self._log(3, "✅ [反馈] 已抓牢。")
            self.success_step()
        else:
            self._log(3, "🚨 [报错] 物体表面太滑，抓取失败！")
            self.error_occured()

    def simulate_move_home(self):
        print("\n[ 阶段转换 ] >>> 准备前往 MoveHome")
        self._log(2, "⚙️ [Enter] 进入 MoveHome：正在复位...")
        time.sleep(0.5)
        self._log(3, "✅ [反馈] 已复位。")
        self.success_step()  # 成功复位，前往最终 Success 状态

    # --- 终态处理 ---
    def on_task_finished(self):
        print(f"\n🎉 任务成功！最终状态: {self.state}")

    def on_task_aborted(self):
        print(f"\n❌ 任务失败并已跳转至最终状态: {self.state}")

    def run_task(self):
        # 此时 run_task 没有任何 try...except。
        # 它只负责“点火”第一步，后续就像多米诺骨牌一样自动流转。
        print(f">>> 任务启动！当前状态: {self.state}")
        self.start()


if __name__ == "__main__":
    robot = RobotFSM()
    robot.run_task()
