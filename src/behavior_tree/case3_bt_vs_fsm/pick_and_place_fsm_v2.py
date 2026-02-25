# /opt/wm-vcpkg/installed/x64-linux/tools/python3/pip install transitions
# pick_place_example_v2.png (Grasp Correction Update)

from transitions import Machine
import time
import random


class RobotFSM:
    # =========================================================================
    # 保留你的核心笔记：
    #
    # 定义状态 (对应图中的长方形)
    #
    # 长方形 (MoveToObj, CorrectGrip, CloseGrip, MoveHome)：过程状态。
    # 圆形 (SUCCESS, FAILURE)：终止状态。
    #
    # 在左图的行为树（BT）中，你会发现没有专门代表 SUCCESS 或 FAILURE 的长方形。
    # 新增的红框在 BT 中体现为 Selector (?) 节点，而在 FSM 中体现为更复杂的跳转线。
    # =========================================================================

    # 新增了 "CorrectGrip" 状态
    states = [
        "Idle",
        "MoveToObj",
        "CorrectGrip",
        "CloseGrip",
        "MoveHome",
        "Success",
        "Failure",
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=RobotFSM.states, initial="Idle")

        # --- 定义转换逻辑 ---

        # 1. 起点
        self.machine.add_transition(
            trigger="start", source="Idle", dest="MoveToObj", before="pre_check_robot"
        )

        # 2. MoveToObj 的分支跳转 (对应图中的 success 判定)
        # 路径 A: 姿态有效 -> 直接抓取 (success && GraspValid)
        self.machine.add_transition(
            trigger="grasp_valid", source="MoveToObj", dest="CloseGrip"
        )
        # 路径 B: 姿态无效 -> 需要修正 (success && !GraspValid)
        self.machine.add_transition(
            trigger="grasp_invalid",
            source="MoveToObj",
            dest="CorrectGrip",
            before="pre_check_environment",
        )

        # 3. CorrectGrip 修正成功后前往 CloseGrip
        self.machine.add_transition(
            trigger="success_step", source="CorrectGrip", dest="CloseGrip"
        )

        # 4. 后续常规路径
        self.machine.add_transition(
            trigger="success_step", source="CloseGrip", dest="MoveHome"
        )
        self.machine.add_transition(
            trigger="success_step", source="MoveHome", dest="Success"
        )

        # 5. 全局错误处理
        self.machine.add_transition(trigger="error_occured", source="*", dest="Failure")

        # --- 绑定钩子 ---
        self.machine.on_enter_MoveToObj("simulate_move_to_obj")
        self.machine.on_exit_MoveToObj("stop_chassis_motors")

        self.machine.on_enter_CorrectGrip("simulate_correct_grip")  # 新增
        self.machine.on_enter_CloseGrip("simulate_close_grip")
        self.machine.on_enter_MoveHome("simulate_move_home")

        self.machine.on_enter_Success("on_task_finished")
        self.machine.on_enter_Failure("on_task_aborted")

    def _log(self, level, msg):
        indent = "    " * level
        print(f"{indent}{msg}")

    # --- 生命周期钩子 ---
    def pre_check_robot(self):
        print("\n[ 阶段转换 ] >>> 准备前往 MoveToObj")
        self._log(1, "🔍 [Before] 机器人自检...")

    def pre_check_environment(self):
        print("\n[ 阶段转换 ] >>> 发现位姿偏差，准备前往 CorrectGrip")
        self._log(1, "🔍 [Before] 环境重扫描...")

    def stop_chassis_motors(self):
        self._log(1, "🔌 [Exit] 离开 MoveToObj：切断底盘动力。")

    # --- 核心业务逻辑 ---

    def simulate_move_to_obj(self):
        self._log(2, "⚙️ [Enter] 进入 MoveToObj：正在移动...")
        time.sleep(0.5)
        if random.random() > 0.2:  # 80% 成功率
            self._log(3, "✅ [反馈] 已抵达目标区域。")

            # --- 核心逻辑升级：判定位姿是否有效 ---
            if random.choice([True, False]):  # 随机模拟位姿是否需要修正
                self._log(3, "✨ [判定] GraspValid 为 True，准备直接抓取。")
                self.grasp_valid()
            else:
                self._log(3, "⚠️ [判定] GraspValid 为 False，需要修正位姿。")
                self.grasp_invalid()
        else:
            self._log(3, "🚨 [报错] 移动失败。")
            self.error_occured()

    def simulate_correct_grip(self):
        self._log(2, "⚙️ [Enter] 进入 CorrectGrip：正在微调机械臂末端位姿...")
        time.sleep(0.5)
        if random.random() > 0.1:
            self._log(3, "✅ [反馈] 位姿修正完成。")
            self.success_step()
        else:
            self._log(3, "🚨 [报错] 修正失败。")
            self.error_occured()

    def simulate_close_grip(self):
        self._log(2, "⚙️ [Enter] 进入 CloseGrip：闭合夹爪...")
        time.sleep(0.5)
        if random.random() > 0.2:
            self._log(3, "✅ [反馈] 已抓牢。")
            self.success_step()
        else:
            self._log(3, "🚨 [报错] 抓取失败。")
            self.error_occured()

    def simulate_move_home(self):
        print("\n[ 阶段转换 ] >>> 准备前往 MoveHome")
        self._log(2, "⚙️ [Enter] 进入 MoveHome：正在复位...")
        time.sleep(0.5)
        self._log(3, "✅ [反馈] 已复位。")
        self.success_step()

    def on_task_finished(self):
        print(f"\n🎉 任务大获全胜！最终状态: {self.state}")

    def on_task_aborted(self):
        print(f"\n❌ 任务在中途崩溃，最终状态: {self.state}")

    def run_task(self):
        print(f">>> 任务启动！当前状态: {self.state}")
        self.start()


if __name__ == "__main__":
    robot = RobotFSM()
    robot.run_task()
