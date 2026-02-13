# -*- coding: utf-8 -*-
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
from hummingbot.core.data_type.common import OrderType
from hummingbot.data_feed.candles_feed.candles_factory import CandlesFactory
from decimal import Decimal
import pandas as pd

class SniperStrategy(ScriptStrategyBase):
    trading_pair = "PIPPIN-USDT"
    exchange = "binance_perpetual_testnet"
    
    # 参数设置
    ema_length = 14
    deviation_threshold = Decimal("0.001")
    callback_rate = Decimal("0.0005")
    order_amount_usdt = Decimal("20")
    
    # 初始化市场和 K 线订阅
    markets = {exchange: {trading_pair}}
    # 创建 15 分钟 K 线喂价
    candles = CandlesFactory.get_candle(connector=exchange, trading_pair=trading_pair, interval="15m", max_records=50)
    
    def __init__(self, connectors):
        super().__init__(connectors)
        self.is_locked = False
        self.highest_price = Decimal("0")
        # 启动 K 线数据推送
        self.candles.start()

    def on_stop(self):
        self.candles.stop()

    def on_tick(self):
        try:
            connector = self.connectors[self.exchange]
            if not connector.ready or not self.candles.ready:
                return

            current_price = connector.get_mid_price(self.trading_pair)
            
            # 获取 K 线 DataFrame 并计算 EMA
            df = self.candles.candles_df
            if len(df) < self.ema_length:
                return

            # 计算 EMA (使用 pandas 效率更高且准确)
            close_series = df['close'].astype(float)
            ema_value = close_series.ewm(span=self.ema_length, adjust=False).mean().iloc[-1]
            ema = Decimal(str(ema_value))

            deviation = (current_price - ema) / ema
            
            # 日志输出
            self.logger().info(f"Price: {current_price:.6f} | EMA: {ema:.6f} | Dev: {deviation*100:.3f}%")

            if not self.is_locked:
                if deviation >= self.deviation_threshold:
                    self.is_locked = True
                    self.highest_price = current_price
                    self.logger().info(f"🔒 偏离触发，进入监测模式! 当前价: {current_price}")
            else:
                # 更新最高价
                if current_price > self.highest_price:
                    self.highest_price = current_price
                
                # 回调逻辑
                if current_price <= self.highest_price * (1 - self.callback_rate):
                    self.logger().info(f"🚀 回调确认: {current_price} <= {self.highest_price} * (1-{self.callback_rate})")
                    self.execute_sell(current_price)
                    self.is_locked = False # 交易后解锁
                    
        except Exception as e:
            self.logger().error(f"脚本异常: {str(e)}")

    def execute_sell(self, price):
        connector = self.connectors[self.exchange]
        # 计算下单量并进行精度校正 (Quantize)
        raw_amount = self.order_amount_usdt / price
        quantized_amount = connector.quantize_order_amount(self.trading_pair, raw_amount)
        
        if quantized_amount > 0:
            self.sell(
                self.exchange,
                self.trading_pair,
                quantized_amount,
                OrderType.MARKET
            )
            self.logger().info(f"✅ 已投单: {quantized_amount} {self.trading_pair}")
