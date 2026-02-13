docker exec -i hummingbot-instance bash -c "cat << 'EOF' > /home/hummingbot/scripts/sniper_strategy.py
# -*- coding: utf-8 -*-
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
from hummingbot.core.data_type.common import OrderType
from decimal import Decimal

class SniperStrategy(ScriptStrategyBase):
    trading_pair = 'PIPPIN-USDT'
    exchange = 'binance_perpetual_testnet'
    
    ema_length = 14
    deviation_threshold = Decimal('0.001')
    callback_rate = Decimal('0.0005')
    order_amount_usdt = Decimal('20')
    
    markets = {exchange: {trading_pair}}
    is_locked = False
    highest_price = Decimal('0')

    def on_tick(self):
        try:
            connector = self.connectors[self.exchange]
            # 增加检查：如果连接器没准备好或 K 线没加载完，就直接跳过
            if not connector.ready:
                return

            current_price = connector.get_mid_price(self.trading_pair)
            if current_price is None or current_price.is_nan():
                return

            candles = connector.get_candles(self.trading_pair, '15m', self.ema_length + 5)
            if len(candles) < self.ema_length:
                self.logger().info(f'数据收集中心: 已获取 {len(candles)} 根 K 线...')
                return

            close_prices = [Decimal(str(c.close)) for c in candles]
            ema = self.calculate_ema(close_prices, self.ema_length)
            deviation = (current_price - ema) / ema
            
            # 实时输出，确认逻辑在跑
            self.logger().info(f'价格: {current_price:.4f} | EMA: {ema:.4f} | 偏离: {deviation*100:.2f}%')

            if not self.is_locked:
                if deviation >= self.deviation_threshold:
                    self.is_locked = True
                    self.highest_price = current_price
                    self.logger().info(f'🔒 偏离触发，进入锁定模式! 最高价: {current_price}')
            else:
                if current_price > self.highest_price:
                    self.highest_price = current_price
                if current_price <= self.highest_price * (1 - self.callback_rate):
                    self.logger().info(f'🚀 回调确认，执行开空!')
                    self.place_order(current_price)
                    self.is_locked = False
        except Exception as e:
            # 捕获异常并打印，防止整个机器人日志刷屏红字
            self.logger().error(f'脚本运行异常: {str(e)}')

    def place_order(self, price):
        amount = self.order_amount_usdt / price
        self.sell(self.exchange, self.trading_pair, amount, OrderType.MARKET)

    def calculate_ema(self, prices, period):
        alpha = Decimal(2) / (Decimal(period) + Decimal(1))
        ema = prices[0]
        for p in prices[1:]:
            ema = (p * alpha) + (ema * (Decimal(1) - alpha))
        return ema
EOF"
            ema = (p * alpha) + (ema * (Decimal(1) - alpha))
        return ema
