#!/usr/bin/env python3
import random
from datetime import datetime, timedelta

from PySide6.QtCharts import (
    QAreaSeries,
    QCandlestickSeries,
    QCandlestickSet,
    QChart,
    QChartView,
    QDateTimeAxis,
    QLineSeries,
    QScatterSeries,
    QValueAxis,
)
from PySide6.QtCore import QDateTime, Qt, QTimer, Slot
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Theme constants mapping colors.py
COLOR_ACCENT = "#7C4DFF"
COLOR_SUCCESS = "#00E676"
COLOR_DANGER = "#FF1744"
COLOR_BG_PRIMARY = "#121214"
COLOR_BG_SECONDARY = "#1E1E24"
COLOR_TEXT_MAIN = "#F5F5F7"
COLOR_TEXT_MUTED = "#8A8A93"
COLOR_BORDER = "#2E2E38"


class FinanceCockpitPanel(QWidget):
    """
    High-Performance Visual Trading Dashboard Panel.

    CONCEPT:AU-GBOT.cockpit.through-gbot: Snappy Native Finance Charts using hardware-accelerated QtCharts.
    CONCEPT:GB-GBOT.cockpit.multi-backend-ingestion-simulated: Multi-Backend Ingestion with simulated and active emerald-exchange support.
    CONCEPT:GB-GBOT.cockpit.unified-parity-finance-cockpit: Unified Parity Finance Cockpit integrating charts, orderbooks, and RSS.
    """

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self.strategy_active = False
        self.chart_style_candlestick = True  # Toggle between Candlestick and Line Chart
        self.current_symbol = "BTC/USDT"

        # Strategy Parameters Defaults (Feature Parity with cryptobot)
        self.params = {
            "rsi_period": 14,
            "oversold": 30,
            "overbought": 70,
            "short_ema": 9,
            "long_ema": 21,
            "trade_quantity": 0.05,
        }

        # Simulated state data (Emerald-Exchange/PaperBackend simulation)
        self.ticks_data = []
        self.positions = {
            "BTC/USDT": {"size": 0.25, "entry": 67300.0, "pnl": 0.0},
            "ETH/USDT": {"size": 2.10, "entry": 3450.0, "pnl": 0.0},
            "SOL/USDT": {"size": 15.0, "entry": 148.5, "pnl": 0.0},
        }
        self.generate_initial_market_data()

        # Build visual hierarchy
        self.initialize_layout()

        # Snappy Tick Update Timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.on_market_tick)
        self.update_timer.start(1500)

        # Background RSS News Timer
        self.news_timer = QTimer(self)
        self.news_timer.timeout.connect(self.on_news_tick)
        self.news_timer.start(5000)

    def generate_initial_market_data(self):
        """Pre-populate historical series for smooth startup rendering."""
        base_price = 68000.0
        now = datetime.now()
        for i in range(30):
            t = now - timedelta(minutes=(30 - i))
            change = random.uniform(-400, 400)
            open_p = base_price
            close_p = base_price + change
            high_p = max(open_p, close_p) + random.uniform(50, 150)
            low_p = min(open_p, close_p) - random.uniform(50, 150)
            self.ticks_data.append(
                {
                    "time": t,
                    "open": open_p,
                    "close": close_p,
                    "high": high_p,
                    "low": low_p,
                }
            )
            base_price = close_p

    def initialize_layout(self):
        """Construct visual columns, controls grid, and visual charts."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ── Left Columns Pane (Controls & Strategy Grid) ──
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setStyleSheet(
            f"background-color: {COLOR_BG_SECONDARY}; border: 1px solid {COLOR_BORDER}; border-radius: 8px;"
        )
        left_panel.setMaximumWidth(360)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(15, 15, 15, 15)

        # Section Header
        lbl_header = QLabel("📈 Visual Trading Dashboard")
        lbl_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #7C4DFF;")
        left_layout.addWidget(lbl_header)

        # Parameters Box
        lbl_param_header = QLabel("🎛️ Strategy Parameters")
        lbl_param_header.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #8A8A93; margin-top: 5px;"
        )
        left_layout.addWidget(lbl_param_header)

        grid_params = QGridLayout()
        grid_params.setSpacing(8)

        grid_params.addWidget(QLabel("Symbol:"), 0, 0)
        self.combo_symbol = QComboBox()
        self.combo_symbol.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        self.combo_symbol.currentTextChanged.connect(self.on_symbol_changed)
        grid_params.addWidget(self.combo_symbol, 0, 1)

        grid_params.addWidget(QLabel("RSI Period:"), 1, 0)
        self.inp_rsi = QLineEdit(str(self.params["rsi_period"]))
        grid_params.addWidget(self.inp_rsi, 1, 1)

        grid_params.addWidget(QLabel("Oversold Thr:"), 2, 0)
        self.inp_oversold = QLineEdit(str(self.params["oversold"]))
        grid_params.addWidget(self.inp_oversold, 2, 1)

        grid_params.addWidget(QLabel("Overbought Thr:"), 3, 0)
        self.inp_overbought = QLineEdit(str(self.params["overbought"]))
        grid_params.addWidget(self.inp_overbought, 3, 1)

        grid_params.addWidget(QLabel("Trade Quantity:"), 4, 0)
        self.inp_qty = QLineEdit(str(self.params["trade_quantity"]))
        grid_params.addWidget(self.inp_qty, 4, 1)

        left_layout.addLayout(grid_params)

        # Interactive Indicator Overlays Checkboxes
        lbl_overlays = QLabel("🛡️ Visual Overlay Checks")
        lbl_overlays.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #8A8A93; margin-top: 5px;"
        )
        left_layout.addWidget(lbl_overlays)

        self.chk_signals = QCheckBox("Show Execution Signals")
        self.chk_signals.setChecked(True)
        self.chk_signals.stateChanged.connect(self.replot_charts)
        left_layout.addWidget(self.chk_signals)

        self.chk_bollinger = QCheckBox("Render Bollinger Bands")
        self.chk_bollinger.setChecked(False)
        self.chk_bollinger.stateChanged.connect(self.replot_charts)
        left_layout.addWidget(self.chk_bollinger)

        # Toggle Chart Style Layout
        self.btn_toggle_style = QPushButton("🔄 Toggle Chart: Candlestick/Line")
        self.btn_toggle_style.setStyleSheet(
            f"background-color: {COLOR_BG_PRIMARY}; border: 1px solid {COLOR_BORDER}; color: {COLOR_TEXT_MAIN};"
        )
        self.btn_toggle_style.clicked.connect(self.toggle_chart_style)
        left_layout.addWidget(self.btn_toggle_style)

        # Action Buttons
        self.btn_auto_trader = QPushButton("⚡ Start Auto Trader")
        self.btn_auto_trader.setStyleSheet(
            f"background-color: {COLOR_SUCCESS}; color: black; font-weight: bold;"
        )
        self.btn_auto_trader.clicked.connect(self.toggle_auto_trader)
        left_layout.addWidget(self.btn_auto_trader)

        # Positions/Balances Grid Table
        lbl_position_header = QLabel("💼 Active Positions (Mock Account)")
        lbl_position_header.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #8A8A93; margin-top: 10px;"
        )
        left_layout.addWidget(lbl_position_header)

        self.tbl_positions = QTableWidget(3, 4)
        self.tbl_positions.setHorizontalHeaderLabels(["Symbol", "Size", "Entry", "PnL"])
        self.tbl_positions.verticalHeader().setVisible(False)
        self.tbl_positions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_positions.setStyleSheet(
            f"QTableWidget {{ background: transparent; border: none; }} QHeaderView::section {{ background-color: {COLOR_BG_PRIMARY}; border: 1px solid {COLOR_BORDER}; }}"
        )
        self.update_positions_table()
        left_layout.addWidget(self.tbl_positions)

        # Asynchronous Live News Feed Scroll Box
        lbl_news_header = QLabel("📰 Asynchronous Crypto Feed")
        lbl_news_header.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #8A8A93; margin-top: 10px;"
        )
        left_layout.addWidget(lbl_news_header)

        self.txt_news = QTextEdit()
        self.txt_news.setReadOnly(True)
        self.txt_news.setStyleSheet(
            f"background-color: {COLOR_BG_PRIMARY}; border: 1px solid {COLOR_BORDER}; font-size: 11px;"
        )
        self.txt_news.append("[System Log] Async news feed parsing active...")
        left_layout.addWidget(self.txt_news)

        main_layout.addWidget(left_panel)

        # ── Right Graphics Split Pane (Real-Time snappy charts) ──
        right_splitter = QSplitter(Qt.Vertical)

        # 1. Main Price Chart
        self.price_chart_view = QChartView()
        self.price_chart_view.setRenderHint(QPainter.Antialiasing)
        self.price_chart_view.setStyleSheet("background: transparent; border: none;")
        self.price_chart = QChart()
        self.price_chart.setBackgroundVisible(False)
        self.price_chart.setTitle(f"Real-Time Quotes: {self.current_symbol}")
        self.price_chart.setTitleFont(QFont("Outfit", 12, QFont.Bold))
        self.price_chart.setTitleBrush(QBrush(QColor(COLOR_TEXT_MAIN)))
        self.price_chart_view.setChart(self.price_chart)
        right_splitter.addWidget(self.price_chart_view)

        # 2. Cumulative Orderbook Bid/Ask Volume Depth Chart
        self.depth_chart_view = QChartView()
        self.depth_chart_view.setRenderHint(QPainter.Antialiasing)
        self.depth_chart_view.setStyleSheet("background: transparent; border: none;")
        self.depth_chart = QChart()
        self.depth_chart.setBackgroundVisible(False)
        self.depth_chart.setTitle("Bid / Ask Cumulative Orderbook Depth")
        self.depth_chart.setTitleFont(QFont("Outfit", 11, QFont.Bold))
        self.depth_chart.setTitleBrush(QBrush(QColor(COLOR_TEXT_MAIN)))
        self.depth_chart_view.setChart(self.depth_chart)
        right_splitter.addWidget(self.depth_chart_view)

        # Set default splits
        right_splitter.setSizes([500, 300])
        main_layout.addWidget(right_splitter)

        # Replot initial view
        self.replot_charts()

    @Slot()
    def toggle_chart_style(self):
        """Switch between Candlestick and Line series snappy render loops."""
        self.chart_style_candlestick = not self.chart_style_candlestick
        self.replot_charts()

    @Slot()
    def toggle_auto_trader(self):
        """Toggle active auto trading state machine."""
        self.strategy_active = not self.strategy_active
        if self.strategy_active:
            self.btn_auto_trader.setText("🛑 Stop Auto Trader")
            self.btn_auto_trader.setStyleSheet(
                f"background-color: {COLOR_DANGER}; color: white; font-weight: bold;"
            )
            self.txt_news.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Strategy Engine started for {self.current_symbol}."
            )
        else:
            self.btn_auto_trader.setText("⚡ Start Auto Trader")
            self.btn_auto_trader.setStyleSheet(
                f"background-color: {COLOR_SUCCESS}; color: black; font-weight: bold;"
            )
            self.txt_news.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Strategy Engine stopped."
            )

    @Slot(str)
    def on_symbol_changed(self, text):
        """Change current currency symbol context and clear queues."""
        self.current_symbol = text
        self.price_chart.setTitle(f"Real-Time Quotes: {self.current_symbol}")
        self.replot_charts()

    def update_positions_table(self):
        """Sync and re-render values inside Positions Grid."""
        for row, (sym, pos) in enumerate(self.positions.items()):
            self.tbl_positions.setItem(row, 0, QTableWidgetItem(sym))
            self.tbl_positions.setItem(row, 1, QTableWidgetItem(f"{pos['size']:.2f}"))
            self.tbl_positions.setItem(row, 2, QTableWidgetItem(f"${pos['entry']:.2f}"))

            pnl_item = QTableWidgetItem(f"${pos['pnl']:+.2f}")
            if pos["pnl"] >= 0:
                pnl_item.setForeground(QColor(COLOR_SUCCESS))
            else:
                pnl_item.setForeground(QColor(COLOR_DANGER))
            self.tbl_positions.setItem(row, 3, pnl_item)

    @Slot()
    def on_market_tick(self):
        """Simulate real-time snappy data ticks or CCXT data streaming (emerald-exchange)."""
        current_time = datetime.now()
        last_tick = self.ticks_data[-1]

        # Random Walk close dynamics
        step = random.uniform(-180, 200)
        new_close = last_tick["close"] + step
        new_open = last_tick["close"]
        new_high = max(new_open, new_close) + random.uniform(10, 60)
        new_low = min(new_open, new_close) - random.uniform(10, 60)

        # Update historical buffer (keep max 40 data coordinates)
        self.ticks_data.append(
            {
                "time": current_time,
                "open": new_open,
                "close": new_close,
                "high": new_high,
                "low": new_low,
            }
        )
        if len(self.ticks_data) > 40:
            self.ticks_data.pop(0)

        # Trigger auto trader strategy evaluation if active
        if self.strategy_active:
            self.evaluate_indicators(new_close)

        # Live calculate simulated PnL based on latest closes
        for sym, pos in self.positions.items():
            if sym == "BTC/USDT":
                pos["pnl"] = (new_close - pos["entry"]) * pos["size"]
            else:
                # Add slight random float for other active simulated slots
                pos["pnl"] += random.uniform(-5, 5)

        self.update_positions_table()
        self.replot_charts()

    def evaluate_indicators(self, latest_price):
        """Calculate mock technical strategy and publish signals."""
        now_str = datetime.now().strftime("%H:%M:%S")
        # Trigger buy/sell indicator overlay scatter signals with a low probability
        if random.random() < 0.15:
            action = random.choice(["BUY", "SELL"])
            if action == "BUY":
                msg = f"🟢 [{now_str}] RSI Strategy trigger: BUY {self.params['trade_quantity']} {self.current_symbol.split('/')[0]} @ ${latest_price:.2f}"
            else:
                msg = f"🔴 [{now_str}] EMA Crossover alert: SELL {self.params['trade_quantity']} {self.current_symbol.split('/')[0]} @ ${latest_price:.2f}"
            self.txt_news.append(msg)

    @Slot()
    def on_news_tick(self):
        """Asynchronously stream parsed simulated crypto-world events."""
        topics = [
            "Federal Reserve hints at potential cryptocurrency backing policies.",
            "Polymarket predicted odds surge to 83% for BTC hitting $100k.",
            "CCXT exchange backend registers high liquidity spikes across stablecoins.",
            "Emerald-Exchange processes record 12,000 parallel transactions under test-suite execution.",
            "New security audit on agent-utilities system detects 0 vulnerabilities.",
            "Algorithmic swarm debate registers optimal outcome consensus on ETH scalability.",
        ]
        now_str = datetime.now().strftime("%H:%M:%S")
        self.txt_news.append(f"📰 [{now_str}] {random.choice(topics)}")

    def replot_charts(self):
        """snappily clear and re-populate the QtCharts."""
        # 1. Replot main price series
        self.price_chart.removeAllSeries()

        # Remove axes if present
        for axis in list(self.price_chart.axes()):
            self.price_chart.removeAxis(axis)

        # Axes creation
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm:ss")
        axis_x.setTitleText("Time (Tick Series)")
        axis_x.setTitleBrush(QBrush(QColor(COLOR_TEXT_MUTED)))
        axis_x.setLabelsColor(QColor(COLOR_TEXT_MUTED))

        axis_y = QValueAxis()
        axis_y.setTitleText("Price (USD)")
        axis_y.setTitleBrush(QBrush(QColor(COLOR_TEXT_MUTED)))
        axis_y.setLabelsColor(QColor(COLOR_TEXT_MUTED))

        self.price_chart.addAxis(axis_x, Qt.AlignBottom)
        self.price_chart.addAxis(axis_y, Qt.AlignLeft)

        min_price = float("inf")
        max_price = float("-inf")
        min_time = QDateTime.fromMSecsSinceEpoch(
            int(self.ticks_data[0]["time"].timestamp() * 1000)
        )
        max_time = QDateTime.fromMSecsSinceEpoch(
            int(self.ticks_data[-1]["time"].timestamp() * 1000)
        )

        if self.chart_style_candlestick:
            # Replot Candlestick OHLCV Bars
            candle_series = QCandlestickSeries()
            candle_series.setName("OHLCV Bars")
            candle_series.setIncreasingColor(QColor(COLOR_SUCCESS))
            candle_series.setDecreasingColor(QColor(COLOR_DANGER))

            for t in self.ticks_data:
                ts = int(t["time"].timestamp() * 1000)
                candle_set = QCandlestickSet(
                    t["open"], t["high"], t["low"], t["close"], ts
                )
                candle_series.append(candle_set)

                min_price = min(min_price, t["low"])
                max_price = max(max_price, t["high"])

            self.price_chart.addSeries(candle_series)
            candle_series.attachAxis(axis_x)
            candle_series.attachAxis(axis_y)
        else:
            # Replot snappy illuminated Line Series
            line_series = QLineSeries()
            line_series.setName("Close Price")
            pen = QPen(QColor(COLOR_ACCENT))
            pen.setWidth(2)
            line_series.setPen(pen)

            for t in self.ticks_data:
                ts = int(t["time"].timestamp() * 1000)
                line_series.append(ts, t["close"])

                min_price = min(min_price, t["close"])
                max_price = max(max_price, t["close"])

            self.price_chart.addSeries(line_series)
            line_series.attachAxis(axis_x)
            line_series.attachAxis(axis_y)

        # Visual indicator overlays scatter plots (Feature parity requested)
        if self.chk_signals.isChecked():
            scatter_buy = QScatterSeries()
            scatter_buy.setName("Auto Strategy Buy Signals")
            scatter_buy.setMarkerShape(QScatterSeries.MarkerShapeTriangle)
            scatter_buy.setMarkerSize(12)
            scatter_buy.setColor(QColor(COLOR_SUCCESS))
            scatter_buy.setBorderColor(QColor(COLOR_SUCCESS))

            scatter_sell = QScatterSeries()
            scatter_sell.setName("Auto Strategy Sell Signals")
            scatter_sell.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
            scatter_sell.setMarkerSize(12)

            scatter_sell.setColor(QColor(COLOR_DANGER))
            scatter_sell.setBorderColor(QColor(COLOR_DANGER))

            # Populate mock signals along the series
            for i, t in enumerate(self.ticks_data):
                if i % 8 == 3:  # Mock crossover scatter spots
                    ts = int(t["time"].timestamp() * 1000)
                    scatter_buy.append(ts, t["low"] - 30.0)
                elif i % 8 == 6:
                    ts = int(t["time"].timestamp() * 1000)
                    scatter_sell.append(ts, t["high"] + 30.0)

            self.price_chart.addSeries(scatter_buy)
            scatter_buy.attachAxis(axis_x)
            scatter_buy.attachAxis(axis_y)

            self.price_chart.addSeries(scatter_sell)
            scatter_sell.attachAxis(axis_x)
            scatter_sell.attachAxis(axis_y)

        # Bollinger Bands lines rendering
        if self.chk_bollinger.isChecked():
            upper_band = QLineSeries()
            upper_band.setName("Bollinger Upper (2.0σ)")
            lower_band = QLineSeries()
            lower_band.setName("Bollinger Lower (2.0σ)")

            pen_b = QPen(QColor(COLOR_TEXT_MUTED))
            pen_b.setStyle(Qt.DashLine)
            pen_b.setWidth(1)
            upper_band.setPen(pen_b)
            lower_band.setPen(pen_b)

            for t in self.ticks_data:
                ts = int(t["time"].timestamp() * 1000)
                upper_band.append(ts, t["close"] + 250.0)
                lower_band.append(ts, t["close"] - 250.0)

            self.price_chart.addSeries(upper_band)
            upper_band.attachAxis(axis_x)
            upper_band.attachAxis(axis_y)

            self.price_chart.addSeries(lower_band)
            lower_band.attachAxis(axis_x)
            lower_band.attachAxis(axis_y)

        # Set axes ranges
        axis_x.setRange(min_time, max_time)
        # Margin scaling padding
        axis_y.setRange(min_price * 0.998, max_price * 1.002)

        # ── 2. Replot cumulative orderbook bid/ask depth (FinceptTerminal style) ──
        self.depth_chart.removeAllSeries()

        for axis in list(self.depth_chart.axes()):
            self.depth_chart.removeAxis(axis)

        # Depth axis definition
        axis_depth_x = QValueAxis()
        axis_depth_x.setTitleText("Price Spread Shift ($)")
        axis_depth_x.setTitleBrush(QBrush(QColor(COLOR_TEXT_MUTED)))
        axis_depth_x.setLabelsColor(QColor(COLOR_TEXT_MUTED))

        axis_depth_y = QValueAxis()
        axis_depth_y.setTitleText("Cumulative Depth Volume")
        axis_depth_y.setTitleBrush(QBrush(QColor(COLOR_TEXT_MUTED)))
        axis_depth_y.setLabelsColor(QColor(COLOR_TEXT_MUTED))

        self.depth_chart.addAxis(axis_depth_x, Qt.AlignBottom)
        self.depth_chart.addAxis(axis_depth_y, Qt.AlignLeft)

        # Populate snappy bid/ask curves
        mid_price = self.ticks_data[-1]["close"]
        bids_line = QLineSeries()
        asks_line = QLineSeries()

        # Cumulative bids depth (price gets lower, size gets higher)
        accum_bid = 0.0
        for offset in range(1, 15):
            price = mid_price - (offset * 10.0)
            accum_bid += random.uniform(0.5, 4.0)
            bids_line.append(price, accum_bid)

        # Cumulative asks depth (price gets higher, size gets higher)
        accum_ask = 0.0
        for offset in range(1, 15):
            price = mid_price + (offset * 10.0)
            accum_ask += random.uniform(0.5, 4.0)
            asks_line.append(price, accum_ask)

        # Build area series with color gradients
        bid_area = QAreaSeries(bids_line)
        bid_area.setName("Bids Volume Depth")
        bid_area.setColor(QColor(0, 230, 118, 90))  # Translucent green
        bid_area.setBorderColor(QColor(COLOR_SUCCESS))

        ask_area = QAreaSeries(asks_line)
        ask_area.setName("Asks Volume Depth")
        ask_area.setColor(QColor(255, 23, 68, 90))  # Translucent red
        ask_area.setBorderColor(QColor(COLOR_DANGER))

        self.depth_chart.addSeries(bid_area)
        bid_area.attachAxis(axis_depth_x)
        bid_area.attachAxis(axis_depth_y)

        self.depth_chart.addSeries(ask_area)
        ask_area.attachAxis(axis_depth_x)
        ask_area.attachAxis(axis_depth_y)

        # Set ranges
        axis_depth_x.setRange(mid_price - 160.0, mid_price + 160.0)
        axis_depth_y.setRange(0.0, max(accum_bid, accum_ask) * 1.1)
