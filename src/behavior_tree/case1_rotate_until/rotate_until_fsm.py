import time


class RobotFSM:
    def __init__(self):
        # 定义状态
        self.STATE_IDLE_ROTATING = "IDLE_ROTATING"
        self.STATE_DETECT_1 = "DETECT_1"
        self.STATE_DETECT_2 = "DETECT_2"
        self.STATE_DETECT_3 = "DETECT_3"
        self.STATE_DETECT_4 = "DETECT_4"
        self.STATE_SUCCESS = "SUCCESS"

        self.current_state = self.STATE_IDLE_ROTATING
        self.tick_count = 0

    def get_sensor_data(self):
        """模拟传感器：第3次Tick开始看到人"""
        self.tick_count += 1
        found = True if self.tick_count >= 3 else False
        print(f"[传感器] Tick {self.tick_count}: {'看到人' if found else '没看到人'}")
        return found

    def execute_rotate(self):
        """动作：原地旋转"""
        print("[动作] 正在旋转底盘...")

    def tick(self):
        print(f"\n--- 第 {self.tick_count + 1} 次 Tick ---")

        # 1. 执行当前状态的基础动作（旋转在所有非成功状态都要执行）
        if self.current_state != self.STATE_SUCCESS:
            self.execute_rotate()

        # 2. 获取环境输入
        person_visible = self.get_sensor_data()

        # 3. 状态转移逻辑 (这就是 FSM 的“硬编码”跳转)
        if self.current_state == self.STATE_IDLE_ROTATING:
            if person_visible:
                self.current_state = self.STATE_DETECT_1

        elif self.current_state == self.STATE_DETECT_1:
            self.current_state = self.STATE_DETECT_2 if person_visible else self.STATE_IDLE_ROTATING

        elif self.current_state == self.STATE_DETECT_2:
            self.current_state = self.STATE_DETECT_3 if person_visible else self.STATE_IDLE_ROTATING

        elif self.current_state == self.STATE_DETECT_3:
            self.current_state = self.STATE_DETECT_4 if person_visible else self.STATE_IDLE_ROTATING

        elif self.current_state == self.STATE_DETECT_4:
            if person_visible:
                self.current_state = self.STATE_SUCCESS
            else:
                self.current_state = self.STATE_IDLE_ROTATING

        print(f"[状态机] 当前状态: {self.current_state}")

    def run(self):
        print(">>> FSM 版本机器人启动")
        while self.current_state != self.STATE_SUCCESS and self.tick_count < 15:
            self.tick()
            time.sleep(0.1)

        if self.current_state == self.STATE_SUCCESS:
            print("\n[结果] FSM 达到成功状态，任务完成！")


if __name__ == "__main__":
    fsm_robot = RobotFSM()
    fsm_robot.run()
