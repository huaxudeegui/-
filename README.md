# # 🎯 Hummingbot PIPPIN 狙击策略

## 📊 策略逻辑
该策略用于捕捉 **PIPPIN-USDT** 的急速拉升后的回调机会（插针做空）。
* **锁定条件**: 价格偏离 15m EMA(14) 超过 **0.1%**。
* **开单条件**: 从锁定后的最高价回调 **0.05%**。

## 🚀 如何在服务器上一键安装
1. 进入机器人容器内部：
   ```bash
   docker exec -it hummingbot-instance bash-
