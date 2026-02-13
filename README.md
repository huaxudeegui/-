更新说明文档 (README.md)
为了防止你以后忘记怎么用，建议更新一下说明书。

点击列表里的 README.md 文件，点击右上角的 铅笔图标（Edit）。

清空内容，粘贴以下备忘录：

Markdown
# 🎯 Hummingbot PIPPIN 狙击策略

## 📊 策略逻辑
该策略用于捕捉 **PIPPIN-USDT** 的急速拉升后的回调机会（插针做空）。
* **锁定条件**: 价格偏离 15m EMA(14) 超过 **0.1%**。
* **开单条件**: 从锁定后的最高价回调 **0.05%**。

## 🚀 如何在服务器上一键安装
1. 进入机器人容器内部：
   ```bash
   docker exec -it hummingbot-instance bash
进入脚本目录：

Bash
cd /home/hummingbot/scripts
下载脚本 (请将下面的 URL 替换为你仓库文件的 Raw 链接)：

Bash
curl -O [https://raw.githubusercontent.com/你的用户名/hummingbot-pippin-sniper/main/sniper_strategy.py](https://raw.githubusercontent.com/你的用户名/hummingbot-pippin-sniper/main/sniper_strategy.py)
退出并启动：

Bash
exit
# 回到机器人界面
start --script sniper_strategy.py
⚠️ 风险提示
当前配置为 Testnet (测试网)。

实盘前请务必修改 exchange 参数。

建议单笔金额不超过总仓位的 5%。

3. 点击 **Commit changes** 保存。

---

### 🎁 如何获取那个“一键下载”链接？ (关键！)

当你把文件传好后，要在服务器上下载，必须使用 **Raw** 链接（否则会下载成 HTML 网页导致报错）：

1.  在你的仓库里点击 `sniper_strategy.py` 文件。
2.  找到文件右上角的 **Raw** 按钮，点击它。
3.  浏览器地址栏里的那个链接（以 `raw.githubusercontent.com` 开头），就是你要在 AWS 服务器上 `curl` 的地址。

**快去试试吧！建好后，以后你哪怕换了一百台服务器，也只需要一条命令就能部署你的赚钱机器了。**
