# pip install py_trees
import py_trees
import time
import random

# =========================================================================
# 保留核心笔记：
# SUCCESS 和 FAILURE 不是“一个地方”，而是“一个信号”。
# Selector (?) 节点：子节点只要有一个成功，它就成功（实现：有效则过，无效则修正）。
# =========================================================================


class RobotAction(py_trees.behaviour.Behaviour):
    def __init__(self, name, exit_msg=None):
        super(RobotAction, self).__init__(name)
        self.exit_msg = exit_msg

    def _log(self, level, msg):
        indent = "    " * level
        print(f"{indent}{msg}")

    def initialise(self):
        # 统一打印风格
        action_map = {
            "MoveToObj": "正在移动...",
            "CorrectGrip": "正在执行位姿补偿...",
            "CloseGrip": "闭合夹爪...",
            "MoveHome": "正在复位...",
        }
        if self.name in action_map:
            self._log(2, f"⚙️ [Enter] 进入 {self.name}：{action_map[self.name]}")

    def update(self):
        time.sleep(0.5)
        # 模拟失败率
        if random.random() < 0.2:
            self._log(3, f"🚨 [报错] {self.name} 执行异常！")
            return py_trees.common.Status.FAILURE

        # 成功反馈
        feedback_map = {
            "MoveToObj": "已抵达目标区域。",
            "CorrectGrip": "位姿修正完成。",
            "CloseGrip": "已抓牢。",
            "MoveHome": "已复位。",
        }
        self._log(3, f"✅ [反馈] {feedback_map.get(self.name, '完成。')}")
        return py_trees.common.Status.SUCCESS

    def terminate(self, new_status):
        if new_status == py_trees.common.Status.SUCCESS and self.exit_msg:
            self._log(1, f"🔌 [Exit] {self.exit_msg}")


class ConditionGraspValid(py_trees.behaviour.Behaviour):
    """对应图中红色的椭圆 GraspValid"""

    def update(self):
        print("\n[ 核心判定 ] >>> 正在检测抓取位姿是否有效...")
        time.sleep(0.3)
        if random.choice([True, False]):
            print("    ✨ [判定] GraspValid 为 True (位姿理想)")
            return py_trees.common.Status.SUCCESS
        else:
            print("    ⚠️ [判定] GraspValid 为 False (需要修正)")
            return py_trees.common.Status.FAILURE


class PhaseTransition(py_trees.behaviour.Behaviour):
    def __init__(self, transition_text, before_text):
        super(PhaseTransition, self).__init__("Transition")
        self.transition_text = transition_text
        self.before_text = before_text

    def update(self):
        print(f"\n[ 阶段转换 ] >>> {self.transition_text}")
        print(f"    🔍 [Before] {self.before_text}")
        time.sleep(0.3)
        return py_trees.common.Status.SUCCESS


def create_bt():
    # 根节点：顺序执行整个任务
    root = py_trees.composites.Sequence(name="PickPlaceV2", memory=True)

    # 1. 移动阶段
    t1 = PhaseTransition("准备前往 MoveToObj", "机器人自检...")
    a1 = RobotAction("MoveToObj", exit_msg="离开 MoveToObj：切断底盘动力。")

    # 2. 修正分支：对应图中红色的 Selector (?) 结构
    # 逻辑：如果 GraspValid 成功，则选择节点结束；如果失败，则运行 CorrectGrip
    grasp_decision = py_trees.composites.Selector(name="GraspLogic", memory=True)

    check_valid = ConditionGraspValid(name="GraspValid")

    # 将 CorrectGrip 包装在带有 Before 的 Sequence 中，以保持打印格式一致
    correct_seq = py_trees.composites.Sequence(name="CorrectionSequence", memory=True)
    t_corr = PhaseTransition("发现位姿偏差，准备前往 CorrectGrip", "环境重扫描...")
    a_corr = RobotAction("CorrectGrip")
    correct_seq.add_children([t_corr, a_corr])

    grasp_decision.add_children([check_valid, correct_seq])

    # 3. 抓取与返回阶段
    t2 = PhaseTransition("位姿就绪，准备前往 CloseGrip", "确认夹爪空间...")
    a2 = RobotAction("CloseGrip")

    t3 = PhaseTransition("准备前往 MoveHome", "复位准备...")
    a3 = RobotAction("MoveHome")

    # 组装整棵树
    root.add_children([t1, a1, grasp_decision, t2, a2, t3, a3])
    return root


if __name__ == "__main__":
    bt_root = create_bt()
    bt_root.setup_with_descendants()

    # 打印结构蓝图，方便你对比图示
    print("\n" + "=" * 20 + " 行为树 V2 结构蓝图 " + "=" * 20)
    print(py_trees.display.unicode_tree(root=bt_root))
    print("=" * 60 + "\n")

    print(">>> 任务启动！")
    bt_root.tick_once()

    if bt_root.status == py_trees.common.Status.SUCCESS:
        print("\n🎉 任务大获全胜！(Status.SUCCESS)")
    else:
        print(f"\n❌ 任务失败跳转至终止信号: {bt_root.status}")
