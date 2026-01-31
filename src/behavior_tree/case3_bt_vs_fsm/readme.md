
先学习简单的案例：

![](./pick_place_example.png)

先看 fsm版本：

- pick_and_place_fsm_lifecycle.py
  - 基于 `from transitions import Machine`
- pick_and_place_fsm_pure.py
  - 手搓的fsm，用start(), success_step()来推动状态转移
  - 人形机器人统一用step()来当trigger,而且由于人形里面的状态是一直不停的，所以最外层是个step循环，放在来订阅的get_sytem_info()中