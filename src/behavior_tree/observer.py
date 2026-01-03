# 观察者模式（Observer Pattern）是行为树底层逻辑的灵魂。在机器人开发中，它被广泛用于处理“当传感器数据变化时，多个功能模块需要同时做出反应”的情况。

# 为了让你更容易理解，我们用一个**“机器人警报系统”**作为例子：当“电池传感器”发现电量低时，它会通知“语音报警器”和“LED灯”。

# 虽然它们很像，但有一个关键的工程区别：
# 观察者模式是“推（Push）”逻辑：数据一变，被观察者主动去“推”通知。如果观察者很多，或者 update 逻辑很耗时，主线程会卡住。
# 行为树（BT）是“拉（Pull）”逻辑：黑板只管存数据，节点在每一秒（Tick）主动去黑板“拉”最新数据。
# 优势：这种“拉”的机制（轮询）在机器人系统中更稳定，因为它可以严格控制逻辑频率，不会因为某个模块的瞬间变化导致整个系统产生不可控的突发计算。
# 总结： 观察者模式是**“事件驱动”，而行为树是“周期驱动”**。行为树通过“周期性地观察黑板”，实现了类似观察者模式的解耦效果，但又比单纯的事件监听更适合复杂的硬件控制。
# 你会发现，你对 MVVM、共享内存、单例的直觉，最后都指向了同一个终点：如何优雅地让“数据”和“动作”分家。


# =================================================================
# 1. 被观察者 (Subject) - 电池传感器
# =================================================================
class BatterySensor:
    def __init__(self):
        self._observers = []  # 存放所有的观察者
        self._level = 100  # 初始电量

    def attach(self, observer):
        """注册/订阅：把想要观察我的对象加进来"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """注销/取消订阅"""
        self._observers.remove(observer)

    def notify(self):
        """广播：告诉所有人我的状态变了"""
        for observer in self._observers:
            observer.update(self._level)

    def set_level(self, level):
        """模拟电量变化"""
        print(f"\n[传感器] 电量变化为: {level}%")
        self._level = level
        self.notify()  # 只要数据变了，就立刻通知所有人


# =================================================================
# 2. 观察者 (Observers) - 具体的反应模块
# =================================================================
class VoiceAlarm:
    """语音报警模块"""

    def update(self, level):
        if level < 20:
            print(f"  [语音] 警告：电量仅剩 {level}%，请及时充电！")


class LEDLight:
    """LED 灯控模块"""

    def update(self, level):
        if level < 20:
            print("  [LED] 开启红色闪烁模式")
        else:
            print("  [LED] 保持绿色常亮")


# =================================================================
# 3. 运行测试
# =================================================================
if __name__ == "__main__":
    # 创建“被观察者”
    battery = BatterySensor()

    # 创建并注册“观察者”
    voice = VoiceAlarm()
    led = LEDLight()

    battery.attach(voice)
    battery.attach(led)

    # 模拟电量下降
    battery.set_level(50)  # 还没到警报线，LED 绿灯，语音不响
    battery.set_level(15)  # 触发警报线，语音和 LED 同时反应
