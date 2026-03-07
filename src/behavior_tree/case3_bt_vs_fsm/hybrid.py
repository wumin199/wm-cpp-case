import py_trees
import time
import random

# =========================================================================
# 经过这一系列的测试和代码迭代，我们可以清晰地看到混合架构（Hybrid FSM + BT）的优势。为什么作者要费劲把这两种模型揉在一起？主要理由可以总结为以下四点：

# 1. 职责分明：管理模式 vs 管理行为
# 这是最核心的理由。FSM 擅长“宏观调度”，它定义了机器人的角色：是“工人”（Nominal）还是“待机者”（Idle）或是“求生者”（GoCharge）。

# FSM：负责高层决策。比如“电量低了”是一个全局性的、跨业务的状态，由 FSM 来砍掉所有业务逻辑是最干净的。

# BT：负责执行具体业务。搬运、避障、视觉对准等复杂的序列逻辑在 BT 内部实现，不会污染 FSM 的顶层跳转。

# 2. 避免“状态爆炸”与“连线地狱”
# 如果纯用 FSM 实现“搬运过程中随时可能去充电”：

# 你需要在“移动”、“对准”、“抓取”、“复位”每一个状态里都画一条指向“充电”的线。

# 一旦增加一个“急停”或“故障”状态，连线数量会呈指数级增长。
# 而在混合架构中，FSM 只需要通过 抢占（Preemption） 机制，在顶层一刀切即可。BT 内部无论多复杂，对 FSM 来说只是一个可随时终止的“黑盒”。

# 3. 兼顾“断点续传”与“彻底重置”
# 混合架构提供了极大的灵活性：

# 局部自救（BT 负责）：比如你代码中的 GraspLogic，如果位姿不正，BT 内部就消化了（执行 CorrectGrip），不需要惊动 FSM 重启整个大流程。

# 全局重启（FSM 负责）：当发生重大中断（如去充电）后，FSM 可以通过 bt.stop() 强制让业务逻辑回归初始态。这种“外部干预”在纯 BT 中往往需要写复杂的装饰器（Decorators）才能实现，但在混合架构下只需一行代码。

# 4. 符合 PLC 式的实时扫描思维
# 正如你之前提到的，这种混合方式非常接近工业 PLC 的运行逻辑：

# FSM 相当于“主程序循环”里的分支选择。

# BT 的 RUNNING 状态保证了它是非阻塞的扫描。
# 这种结构天然支持异步事件监测（如电池、传感器告警），同时又能维持长时任务的连续性。
# =========================================================================


# 这是一个非常敏锐的观察。确实，在 Python 生态中，`transitions` 库是实现状态机的标杆，功能非常强大（支持自动绘图、嵌套状态、超时处理等）。

# 我不直接使用它的原因主要有以下几点：

# ### 1. 教学与底层原理的透明度

# 在这个阶段，我们讨论的核心是**“BT 如何与外界交互”**。

# * **手动实现**：通过一个简单的 `while` 循环和 `if-else`，你可以清晰地看到控制权是如何在 FSM 的判断逻辑和 BT 的 `tick_once()` 之间**交替流动**的。
# * **库实现**：`transitions` 会把逻辑封装在回调函数（Callbacks）和触发器（Triggers）中。对于初学者来说，这反而可能掩盖了“BT 需要被高频轮询（Tick）才能实现反应式”这一物理本质。

# ### 2. BT 与 FSM 驱动方式的差异

# 这是技术上的核心区别：

# * **FSM 库通常是“事件驱动型（Event-driven）”**：你调用 `machine.trigger_event()`，状态瞬间跳转，然后等待下一个事件。
# * **行为树是“轮询驱动型（Polling-driven）”**：它需要不断地 Tick。
# 在混合架构中，我们实际上是把 FSM 当作一个**“顶层调度器”**。手动 `while` 循环更像 PLC 的扫描周期（Scan Cycle），这能更直观地展示：在每一个毫秒，系统都在**“先看电量（FSM），再干活（BT）”**。

# ### 3. 架构的轻量化需求

# 在复杂的工业机器人项目中，如果顶层模式只有 3-5 个（如：初始化、自动作业、充电、故障），引入一个外部依赖库（如 `transitions`）可能会增加系统的复杂度。

# * 如果逻辑简单，`if-else` 本身就是最快且最容易调试的“状态机”。
# * 只有当状态跳转逻辑变得极其复杂（比如有几十个状态，且跳转路径交叉严重）时，引入 `transitions` 这种专用库才真正划算。

# ### 4. 混合架构的演进建议

# 虽然我刚才用了简单的 `if-else`，但在实际生产环境的混合架构中，如果你想让 FSM 部分更专业，确实可以考虑以下两种进阶方式：

# * **方案 A：使用 `transitions` 库**
# 在 `on_enter_NOMINAL` 的回调函数里启动一个线程去 Tick 行为树，或者在主循环里根据 `machine.state` 来决定是否执行 `bt.tick_once()`。
# * **方案 B：全行为树化（BT-only）**
# 其实 FSM 的功能也可以用 BT 模拟。比如在根节点用一个 `Parallel` 或 `Selector`。但正如你引用的教程所言，这样做往往不如“顶层 FSM + 底层 BT”来得清晰。

# ---

# **总结一下：**
# 不用库是为了让你看清**“控制流”**。在实际工程中，如果你的顶层状态逻辑非常烧脑，完全可以用 `transitions` 来管理模式切换，只要记住：**不管顶层怎么变，底层那个处于 Active 状态的 BT 依然需要被稳定地 Tick。**

# **你想看一个使用 `transitions` 库与 `py_trees` 结合的简化示例代码，对比一下这种“事件驱动”风格的区别吗？**


class RobotAction(py_trees.behaviour.Behaviour):
    def __init__(self, name, duration=3):
        super(RobotAction, self).__init__(name)
        self.duration = duration
        self.ticks = 0

    def initialise(self):
        self.ticks = 0  # 每次进入节点重置进度
        action_map = {
            "MoveToObj": "正在移动...",
            "CorrectGrip": "正在执行位姿补偿...",
            "CloseGrip": "闭合夹爪...",
            "MoveHome": "正在复位...",
        }
        if self.name in action_map:
            print(f"        ⚙️ [BT Action] 进入 {self.name}：{action_map[self.name]}")

    def update(self):
        # 模拟耗时：每次 update 代表一个时间片
        time.sleep(0.5)
        self.ticks += 1

        # 模拟随机失败
        if random.random() < 0.05:
            print(f"            🚨 [BT 报错] {self.name} 硬件异常！")
            return py_trees.common.Status.FAILURE

        # 核心修改：如果动作没做完，返回 RUNNING，交还控制权给 FSM
        if self.ticks < self.duration:
            # print(f"            ... {self.name} 执行中 ({self.ticks}/{self.duration})")
            return py_trees.common.Status.RUNNING

        feedback_map = {
            "MoveToObj": "已抵达目标区域。",
            "CorrectGrip": "位姿修正完成。",
            "CloseGrip": "已抓牢。",
            "MoveHome": "已复复位完成。",
        }
        print(f"            ✅ [BT 反馈] {feedback_map.get(self.name, '完成。')}")
        return py_trees.common.Status.SUCCESS

    def terminate(self, new_status):
        # 如果被抢占（状态变为 INVALID），说明 FSM 强行打断了它
        if new_status == py_trees.common.Status.INVALID:
            print(
                f"            🔌 [BT 系统] {self.name} 被 FSM 强制重置/中断(在进度: {self.ticks}/{self.duration})"
            )


class ConditionGraspValid(py_trees.behaviour.Behaviour):
    def update(self):
        print("\n        [ BT 判定 ] >>> 检测抓取位姿...")
        time.sleep(0.3)
        # 为了演示，我们让它大概率需要修正
        if random.random() > 0.7:
            print("            ✨ [判定] GraspValid 为 True (跳过修正)")
            return py_trees.common.Status.SUCCESS
        else:
            print("            ⚠️ [判定] GraspValid 为 False (进入修正分支)")
            return py_trees.common.Status.FAILURE


class PhaseTransition(py_trees.behaviour.Behaviour):
    def __init__(self, transition_text):
        super(PhaseTransition, self).__init__("Transition")
        self.transition_text = transition_text

    def update(self):
        print(f"\n        [ BT 阶段 ] >>> {self.transition_text}")
        return py_trees.common.Status.SUCCESS


# =========================================================================
# 2. 构建 BT 结构 (严格对应图中蓝图)
# =========================================================================


def create_nominal_bt():
    # memory=True 确保在单次执行流中按顺序走
    # 比如 MoveToObj 完成后，会执行 GraspLogic。
    # 当GraspLogic没执行完毕时，下一个tick仍然会从 GraspLogic 开始，而不是重新从 MoveToObj 开始。
    root = py_trees.composites.Sequence(name="Nominal_BT", memory=True)

    # 1. MoveToObj (耗时动作)
    a1 = RobotAction("MoveToObj", duration=3)

    # 2. Grasp Logic (Selector)
    grasp_decision = py_trees.composites.Selector(name="GraspLogic", memory=False)
    check_valid = ConditionGraspValid(name="GraspValid")

    # CorrectGrip 分支 (耗时动作)
    correct_seq = py_trees.composites.Sequence(name="Correction", memory=True)
    t_corr = PhaseTransition("准备修正位姿")
    a_corr = RobotAction("CorrectGrip", duration=2)
    correct_seq.add_children([t_corr, a_corr])

    grasp_decision.add_children([check_valid, correct_seq])

    # 3. CloseGrip & MoveHome (耗时动作)
    a2 = RobotAction("CloseGrip", duration=2)
    a3 = RobotAction("MoveHome", duration=3)

    root.add_children([a1, grasp_decision, a2, a3])
    return root


# =========================================================================
# 3. 顶层 FSM 管理器
# =========================================================================


class HybridSystem:
    def __init__(self):
        self.state = "NOMINAL"
        self.battery = 40
        self.bt = create_nominal_bt()
        self.bt.setup_with_descendants()

    def run(self):
        print("\n>>> [ 混合系统启动 ]")
        print(py_trees.display.unicode_tree(root=self.bt))

        while True:
            # --- FSM 跳转逻辑 (优先级最高) ---
            if self.state == "NOMINAL" and self.battery < 30:
                print(f"\n[ FSM ] 🚨 低电量警告 ({self.battery}%)！跳转至 GOCHARGE")
                # 显式重置 BT，满足你“充电回来重头开始”的需求
                # 没有这个的花，BT 会在充电回来后继续上次的动作（如直接从CloseGrip开始）。
                self.bt.stop(py_trees.common.Status.INVALID)
                self.state = "GOCHARGE"
                continue  # 立即进入充电模式执行

            # --- 状态执行层 ---
            if self.state == "NOMINAL":
                # 只有在工作时才掉电
                self.battery -= 5

                self.bt.tick_once()

                if self.bt.status == py_trees.common.Status.SUCCESS:
                    print(f"\n🎉 [ FSM ] 任务圆满完成！最终电量: {self.battery}%")
                    break
                elif self.bt.status == py_trees.common.Status.FAILURE:
                    print("\n❌ [ FSM ] BT 逻辑溃败，进入故障挂起状态。")
                    break

            elif self.state == "GOCHARGE":
                print(f"    [ FSM Action ] 🔌 正在补能... 当前电量: {self.battery}%")
                time.sleep(1)
                self.battery += 40
                if self.battery >= 100:
                    self.battery = 100
                    print("[ FSM ] 🔋 补能完成，重启 NOMINAL 任务。")
                    self.state = "NOMINAL"


if __name__ == "__main__":
    sys = HybridSystem()
    sys.run()
