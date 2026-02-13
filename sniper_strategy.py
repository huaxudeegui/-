# -*- coding: utf-8 -*-
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
from hummingbot.core.data_type.common import OrderType
from decimal import Decimal

class SniperStrategy(ScriptStrategyBase):
    """
    PIPPIN 狙击策略 (测试网专用版)
    核心逻辑:
    1. 监听 15分钟 K线，计算 EMA(14)。
    2. 当价格向上偏离 EMA 超过阈值 (deviation_threshold) 时，锁定最高价。
    3. 当价格从最高价回调超过比例 (callback_rate) 时，市价开空。
    """
    # ================= 策略配置 =================
    trading_pair = "PIPPIN-USDT"
    exchange = "binance_perpetual_testnet" # 注意：实盘请改为 binance_perpetual
    
    # ================= 核心参数 =================
    ema_length = 14
    deviation_threshold = Decimal("0.001")  # 触发锁定的偏离度 (0.1%)
    callback_rate = Decimal("0.0005")       # 触发交易的回调幅度 (0.05%)
    order_amount_usdt = Decimal("20")       # 单笔下单金额 (USDT)
    
    # ================= 内部变量 (勿动) =================
    markets = {exchange: {trading_pair}}
    is_locked = False
    highest_price = Decimal("0")

    def on_tick(self):
        # 1. 获取价格与K线数据
        current_price = self.connectors[self.exchange].get_mid_price(self.trading_pair)
        if current_price is None: return

        candles = self.connectors[self.exchange].get_candles(self.trading_pair, "15m", self.ema_length + 5)
        if len(candles) < self.ema_length: return
        
        # 2. 计算指标
        close_prices = [Decimal(str(c.close)) for c in candles]
        ema = self.calculate_ema(close_prices, self.ema_length)
        deviation = (current_price - ema) / ema
        
        # 3. 打印实时状态
        self.logger().info(f"P: {current_price:.4f} | EMA: {ema:.4f} | Dev: {deviation*100:.2f}% | Locked: {self.is_locked}")

        # 4. 交易逻辑
        if not self.is_locked:
            # 检查是否满足锁定条件
            if deviation >= self.deviation_threshold:
                self.is_locked = True
                self.highest_price = current_price
                self.logger().info(f"🔒 价格偏离过大，进入锁定状态! 当前最高: {current_price}")
        else:
            # 更新最高价
            if current_price > self.highest_price:
                self.highest_price = current_price
            
            # 检查回调触发
            trigger_price = self.highest_price * (1 - self.callback_rate)
            if current_price <= trigger_price:
                self.logger().info(f"🚀 确认回调! 执行开空! 触发价: {trigger_price}")
                self.place_order(current_price)
                self.is_locked = False # 重置状态

    def place_order(self, price):
        amount = self.order_amount_usdt / price
        self.sell(connector_name=self.exchange, trading_pair=self.trading_pair, amount=amount, order_type=OrderType.MARKET)

    def calculate_ema(self, prices, period):
        alpha = Decimal(2) / (Decimal(period) + Decimal(1))
        ema = prices[0]
        for p in prices[1:]:
            ema = (p * alpha) + (ema * (Decimal(1) - alpha))
        return ema
