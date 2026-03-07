# pick_place_example.png

import py_trees
import time


# --- 1. 定义叶子节点 (Leaf Nodes) ---
class RobotAction(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(RobotAction, self).__init__(name)

    def update(self):
        # 模拟动作执行
        print(f"  [BT] 执行动作: {self.name}...")
        time.sleep(0.5)
        # 默认返回成功，实际开发中根据传感器判断
        return py_trees.common.Status.SUCCESS


# --- 2. 组装行为树 ---
def create_bt():
    # 创建顺序节点 (图中带箭头的方框)
    root = py_trees.composites.Sequence(name="PickAndMove", memory=True)

    # 添加子节点
    move_to_obj = RobotAction(name="MoveToObj")
    close_grip = RobotAction(name="CloseGrip")
    move_home = RobotAction(name="MoveHome")

    root.add_children([move_to_obj, close_grip, move_home])
    return root


# 运行
if __name__ == "__main__":
    bt_root = create_bt()
    bt_root.setup_with_descendants()
    print(">>> 开始运行行为树任务")
    bt_root.tick_once()
    print(f">>> 行为树最终状态: {bt_root.status}")
