import websocket
import json
import threading
import time

# Dictionary lưu giá ban đầu và giá hiện tại của các đồng coin
coins_data = {}

# Danh sách các đồng coin cần theo dõi
coins = ["btcusdt", "ethusdt", "bnbusdt", "adausdt", "solusdt"]

# Tính phần trăm thay đổi
def calculate_percentage_change(initial_price, current_price):
    return ((current_price - initial_price) / initial_price) * 100

# Hàm xử lý khi nhận dữ liệu từ WebSocket
def on_message(ws, message):
    data = json.loads(message)
    symbol = data['s'].lower()  # Lấy tên coin (vd: btcusdt)
    current_price = float(data['p'])  # Giá hiện tại

    if symbol not in coins_data:
        # Lưu giá ban đầu nếu chưa có
        coins_data[symbol] = {"initial_price": current_price, "current_price": current_price}
    else:
        # Cập nhật giá hiện tại
        coins_data[symbol]["current_price"] = current_price

    # Tính phần trăm thay đổi
    initial_price = coins_data[symbol]["initial_price"]
    percentage_change = calculate_percentage_change(initial_price, current_price)

    print(f"{symbol.upper()}: {current_price:.2f} USD ({percentage_change:+.2f}%)")

# Hàm xử lý lỗi
def on_error(ws, error):
    print(f"Error: {error}")

# Hàm xử lý khi kết nối đóng
def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

# Hàm mở kết nối WebSocket
def on_open(ws):
    print("WebSocket connection opened")
    params = {
        "method": "SUBSCRIBE",
        "params": [f"{coin}@trade" for coin in coins],
        "id": 1
    }
    ws.send(json.dumps(params))

# Chạy WebSocket trong một luồng riêng
def run_websocket():
    ws_url = "wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(ws_url,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

# Khởi chạy WebSocket
thread = threading.Thread(target=run_websocket)
thread.start()

# Hiển thị dữ liệu theo chu kỳ
try:
    while True:
        print("\n=== Real-Time Prices ===")
        for coin, data in coins_data.items():
            initial_price = data["initial_price"]
            current_price = data["current_price"]
            percentage_change = calculate_percentage_change(initial_price, current_price)
            print(f"{coin.upper()}: {current_price:.2f} USD ({percentage_change:+.2f}%)")
        time.sleep(5)  # Cập nhật mỗi 5 giây
except KeyboardInterrupt:
    print("Exiting...")
