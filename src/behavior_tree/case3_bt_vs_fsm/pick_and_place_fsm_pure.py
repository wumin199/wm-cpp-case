import time
import random


class ManualRobotFSM:
    def __init__(self):
        # 初始状态 (实心黑圆点)
        self.state = "Idle"

        # 定义转换逻辑 (Transitions)
        # 结构：{ "当前状态": { "触发器": "目标状态" } }
        # 人形机器人这边，触发器都是step()
        self._transitions = {
            "Idle": {"start": "MoveToObj"},
            "MoveToObj": {"success_step": "CloseGrip"},
            "CloseGrip": {"success_step": "MoveHome"},
            "MoveHome": {"success_step": "Success"},
        }

    # --- 核心引擎逻辑 (模仿 transitions 库内部实现) ---

    def _execute_trigger(self, trigger_name):
        """核心跳转引擎：负责 Before -> Exit -> Change -> Enter 生命周期"""

        # 0. 确定目标状态
        # 特殊处理 error_occured，它允许从任意状态跳到 Failure
        if trigger_name == "error_occured":
            dest = "Failure"
        else:
            dest = self._transitions.get(self.state, {}).get(trigger_name)

        if not dest:
            return

        # 1. Step 2: Before (准入检查)
        # 模拟 transitions 的 before 机制：查找 pre_check_xxx 方法
        before_func = self._get_before_hook(trigger_name, dest)
        if before_func:
            before_func()

        # 2. Step 3: On_Exit (源状态告别)
        exit_func = getattr(self, f"on_exit_{self.state}", None)
        if exit_func:
            exit_func()

        # 3. Step 4: 状态变更 (State Change)
        old_state = self.state
        self.state = dest
        # print(f"\n[ 系统 ] 状态变更: {old_state} -> {self.state}")

        # 4. Step 5: On_Enter (新状态欢迎/核心业务执行)
        enter_func = getattr(self, f"on_enter_{self.state}", None)
        if enter_func:
            enter_func()

    def _get_before_hook(self, trigger, dest):
        """手动映射转换时的 before 钩子"""
        if trigger == "start" and dest == "MoveToObj":
            return self.pre_check_robot
        if trigger == "success_step" and dest == "CloseGrip":
            return self.pre_check_environment
        return None

    # --- 模拟触发器函数 ---
    def start(self):
        self._execute_trigger("start")

    def success_step(self):
        self._execute_trigger("success_step")

    def error_occured(self):
        self._execute_trigger("error_occured")

    # --- 生命周期钩子 (Lifecycle Hooks) ---
    def pre_check_robot(self):
        print("\n[ 阶段转换 ] >>> 准备前往 MoveToObj")
        self._log(1, "🔍 [Before] 机器人自检...")

    def pre_check_environment(self):
        print("\n[ 阶段转换 ] >>> 准备从 MoveToObj 切换到 CloseGrip")
        self._log(1, "🔍 [Before] 环境预检...")

    def on_exit_MoveToObj(self):
        self._log(1, "🔌 [Exit] 离开 MoveToObj：切断底盘动力。")

    def on_enter_MoveToObj(self):
        self.simulate_move_to_obj()

    def on_enter_CloseGrip(self):
        self.simulate_close_grip()

    def on_enter_MoveHome(self):
        self.simulate_move_home()

    # --- 业务仿真逻辑 ---
    def _log(self, level, msg):
        print(f"{'    ' * level}{msg}")

    def simulate_move_to_obj(self):
        self._log(2, "⚙️ [Enter] 进入 MoveToObj：正在移动...")
        time.sleep(0.5)
        if random.random() < 0.3:
            self._log(3, "🚨 [报错] 路径被阻挡！")
            raise RuntimeError("Navigation Blocked")
        self._log(3, "✅ [反馈] 已抵达目标。")

    def simulate_close_grip(self):
        self._log(2, "⚙️ [Enter] 进入 CloseGrip：闭合夹爪...")
        time.sleep(0.5)
        if random.random() < 0.3:
            self._log(3, "🚨 [报错] 抓取失败！")
            raise RuntimeError("Grip Slip")
        self._log(3, "✅ [反馈] 已抓牢。")

    def simulate_move_home(self):
        print("\n[ 阶段转换 ] >>> 准备前往 MoveHome")
        self._log(2, "⚙️ [Enter] 进入 MoveHome：正在复位...")
        time.sleep(0.5)
        self._log(3, "✅ [反馈] 已复位。")

    def run_task(self):
        try:
            print(f">>> 任务启动！当前状态: {self.state}")
            self.start()  # Idle -> MoveToObj
            self.success_step()  # MoveToObj -> CloseGrip
            self.success_step()  # CloseGrip -> MoveHome
            self.success_step()  # MoveHome -> Success
            print(f"\n🎉 任务成功！最终状态: {self.state}")
        except Exception as e:
            print(f"\n💥 运行时异常: {e}")
            self.error_occured()
            print(f"❌ 任务失败跳转至: {self.state} (已进入终止状态)")


if __name__ == "__main__":
    robot = ManualRobotFSM()
    robot.run_task()
