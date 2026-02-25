# 安装指令: pip install transitions
from transitions.extensions import HierarchicalMachine as Machine
import time
import random


class RobotHFSM:
    # 定义子状态（Nominal 内部的小框）
    # 在 HFSM 中，子状态通常表示为 '父状态_子状态'
    nominal_substates = ["MoveToObj", "CloseGrip", "MoveHome"]

    # 定义顶级状态
    states = [
        {"name": "Nominal", "children": nominal_substates, "initial": "MoveToObj"},
        "GoCharge",
        "Success",
        "Failure",
    ]

    def __init__(self):
        # 初始化分层状态机
        self.machine = Machine(model=self, states=RobotHFSM.states, initial="Nominal")

        # --- 1. Nominal 内部的局部跳转 (图 3 灰色框内部) ---
        self.machine.add_transition(
            "success_step", "Nominal_MoveToObj", "Nominal_CloseGrip"
        )
        self.machine.add_transition(
            "success_step", "Nominal_CloseGrip", "Nominal_MoveHome"
        )
        # 内部全部成功则跳向全局 Success
        self.machine.add_transition("success_all", "Nominal_MoveHome", "Success")

        # --- 2. 全局层级的跳转 (处理超级状态) ---
        # 只要在 Nominal 状态及其任何子状态下，!BatteryOK 都会跳向 GoCharge
        self.machine.add_transition("low_battery", "Nominal", "GoCharge")

        # 充电成功后返回 Nominal (会自动进入其 initial 状态: MoveToObj)
        self.machine.add_transition("charge_done", "GoCharge", "Nominal")

        # 任何层级的 failure 都指向全局 Failure
        self.machine.add_transition("error_occured", "*", "Failure")

        # 绑定日志打印
        self.machine.on_enter_Nominal(
            lambda: print("\n>>> 进入 [Nominal] 常规作业模式")
        )
        self.machine.on_enter_GoCharge(self.simulate_charging)

    def _log(self, msg):
        print(f"    [HFSM Log] {msg} ({self.state})")

    def simulate_charging(self):
        print("     🔋 [执行] 正在充电...")
        time.sleep(1)
        self.charge_done()

    def run_step(self):
        """模拟一个作业步骤"""
        if self.state.startswith("Nominal"):
            self._log("执行任务...")
            # 模拟随机电量低 (图 3 中的 !BatteryOK 箭头)
            if random.random() < 0.2:
                print("     ⚠️ [低电量] 触发超级状态跳转！")
                self.low_battery()
            else:
                # 正常推进
                if self.state == "Nominal_MoveHome":
                    self.success_all()
                else:
                    self.success_step()

    def run_full_task(self):
        print("开始任务")
        while self.state not in ["Success", "Failure"]:
            self.run_step()
            time.sleep(0.5)
        print(f"\n任务终点: {self.state}")


if __name__ == "__main__":
    robot = RobotHFSM()
    robot.run_full_task()
