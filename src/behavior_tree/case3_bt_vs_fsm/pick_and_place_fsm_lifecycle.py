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

    states = ["Idle", "MoveToObj", "CloseGrip", "MoveHome", "Success", "Failure"]

    def __init__(self):
        self.machine = Machine(model=self, states=RobotFSM.states, initial="Idle")

        # 定义转换
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
        # 错误跳转逻辑：从任何状态 (*) 都可以跳向 Failure (对应图中所有向右转的 failure 线)
        self.machine.add_transition(trigger="error_occured", source="*", dest="Failure")

        # 绑定钩子
        self.machine.on_enter_MoveToObj("simulate_move_to_obj")
        self.machine.on_exit_MoveToObj(
            "stop_chassis_motors"
        )  # 只有在准备跳出 MoveToObj 时触发
        self.machine.on_enter_CloseGrip("simulate_close_grip")
        self.machine.on_enter_MoveHome("simulate_move_home")

    def _log(self, level, msg):
        indent = "    " * level
        print(f"{indent}{msg}")

    # --- 生命周期钩子 ---
    def pre_check_robot(self):
        print("\n[ 阶段转换 ] >>> 准备前往 MoveToObj")
        self._log(1, "🔍 [Before] 机器人自检...")

    def pre_check_environment(self):
        print("\n[ 阶段转换 ] >>> 准备从 MoveToObj 切换到 CloseGrip")
        self._log(1, "🔍 [Before] 环境预检...")

    def stop_chassis_motors(self):
        self._log(1, "🔌 [Exit] 离开 MoveToObj：切断底盘动力。")

    def simulate_move_to_obj(self):
        self._log(2, "⚙️ [Enter] 进入 MoveToObj：正在移动...")
        time.sleep(0.5)
        # 模拟 30% 的导航失败概率
        if random.random() < 0.3:
            self._log(3, "🚨 [报错] 路径被突然出现的障碍物阻挡！")
            raise RuntimeError("Navigation Blocked")
        self._log(3, "✅ [反馈] 已抵达目标。")

    def simulate_close_grip(self):
        self._log(2, "⚙️ [Enter] 进入 CloseGrip：闭合夹爪...")
        time.sleep(0.5)
        # 模拟 30% 的抓取失败概率
        if random.random() < 0.3:
            self._log(3, "🚨 [报错] 物体表面太滑，抓取失败！")
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
            self.start()
            self.success_step()
            self.success_step()
            self.success_step()
            print(f"\n🎉 任务成功！最终状态: {self.state}")
        except Exception as e:
            # 当底层动作触发 raise 时，这里捕获异常并执行 FSM 的错误跳转
            print(f"\n💥 运行时异常: {e}")
            self.error_occured()
            print(f"❌ 任务失败跳转至: {self.state} (已进入终止状态)")


if __name__ == "__main__":
    robot = RobotFSM()
    robot.run_task()

"""输出示例：
>>> 任务启动！当前状态: Idle

[ 阶段转换 ] >>> 准备前往 MoveToObj
    🔍 [Before] 机器人自检...
        ⚙️ [Enter] 进入 MoveToObj：正在移动...
            ✅ [反馈] 已抵达目标。

[ 阶段转换 ] >>> 准备从 MoveToObj 切换到 CloseGrip
    🔍 [Before] 环境预检...
    🔌 [Exit] 离开 MoveToObj：切断底盘动力。
        ⚙️ [Enter] 进入 CloseGrip：闭合夹爪...
            ✅ [反馈] 已抓牢。

[ 阶段转换 ] >>> 准备前往 MoveHome
        ⚙️ [Enter] 进入 MoveHome：正在复位...
            ✅ [反馈] 已复位。

🎉 任务成功！最终状态: Success


"""

"""笔记1：
这就是为什么 "[Exit] 离开 MoveToObj：切断底盘动力。"
出现在“[ 阶段转换 ] >>> 准备从 MoveToObj 切换到 CloseGrip”区域内：因为你只有决定要去“新地方”时，才会触发“离开旧地方”的动作。
"""

"""笔记2：

🔍 [Before] 环境预检...
    🔌 [Exit] 离开 MoveToObj：切断底盘动力。

为什么是先before在exit


简单来说，在 FSM 的逻辑中，Before 是针对“跳转（Transition）”这个动作的，而 Exit 是针对“状态（State）”的。

1. 为什么逻辑上必须先 Before？
请想象一个现实场景：你正坐在房间（MoveToObj）里，准备去阳台（CloseGrip）。

Before (跳转预检)：你先看一眼阳台门是不是锁着的（环境预检）。如果门锁了，你根本不应该起身（不触发跳转）。

Exit (离开状态)：确认门可以打开后，你站起来，关掉房间的灯（切断底盘动力，离开 MoveToObj）。

Enter (进入状态)：你跨步走进阳台（进入 CloseGrip），开始收衣服（执行仿真函数）。

结论： Before 是决策阶段，决定“能不能走”；而 Exit 是执行阶段，代表“确定要走，开始收尾”。如果先 Exit 后 Before，
万一 Before 检查失败（比如门锁了），你已经把房间的灯关了且动力切断了，机器人就会卡在一个尴尬的中间地带。

2. 状态机转换的完整生命周期 (Transitions 库标准)
按照你使用的 transitions 库，当你调用 success_step() 时，内部执行链条严格遵循以下顺序：

Step 1: prepare (准备阶段，极少使用)。

Step 2: before：转换前的准入检查。只有通过了，才正式开启转换。

Step 3: on_exit：源状态的告别动作。代表逻辑正式离开旧状态。

Step 4: 状态变更：此时 self.state 正式从 MoveToObj 变为 CloseGrip。

Step 5: on_enter：新状态的欢迎动作。开始执行核心业务逻辑。

Step 6: after：转换彻底完成后的清理。
"""
