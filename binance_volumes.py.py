from collections import deque
import json
import threading
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import websocket


MAX_POINTS = 50
buy_history = deque([0.0] * MAX_POINTS, maxlen=MAX_POINTS)
sell_history = deque([0.0] * MAX_POINTS, maxlen=MAX_POINTS)
delta_history = deque([0.0] * MAX_POINTS, maxlen=MAX_POINTS)


current_buy = 0.0
current_sell = 0.0


def on_message(ws, message):
    global current_buy, current_sell
    data = json.loads(message)

    quantity = float(data["q"])
    is_buyer_maker = data["m"]

    
    if is_buyer_maker:
        current_sell += quantity  
    else:
        current_buy += quantity  


def start_websocket(symbol="btcusdt"):
    socket_url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade"
    ws = websocket.WebSocketApp(socket_url, on_message=on_message)
    ws.run_forever()


def update_chart(frame):
    global current_buy, current_sell

   
    buy_history.append(current_buy)
    sell_history.append(current_sell)
    delta_history.append(current_buy - current_sell)

    
    current_buy = 0.0
    current_sell = 0.0

    
    plt.cla()

    
    plt.plot(buy_history, label="Buy Volume", color="green", linewidth=1.5)
    plt.plot(sell_history, label="Sell Volume", color="red", linewidth=1.5)
    plt.plot(
        delta_history,
        label="Net Delta (Buy - Sell)",
        color="orange",
        linewidth=2.5,
    )

   
    plt.axhline(0, color="black", linestyle="--", alpha=0.6)

    # Chart Styling
    plt.title("Live Volume Delta Oscillator (Binance)")
    plt.xlabel("Ticks")
    plt.ylabel("Volume")
    plt.legend(loc="upper left")
    plt.grid(True, linestyle=":", alpha=0.5)


if __name__ == "__main__":
    symbol_input = (
        input("Enter symbol (default BTCUSDT): ").strip() or "BTCUSDT"
    )

    
    ws_thread = threading.Thread(
        target=start_websocket, args=(symbol_input,), daemon=True
    )
    ws_thread.start()

    
    fig = plt.figure(figsize=(10, 5))
    ani = animation.FuncAnimation(
        fig, update_chart, interval=1000
    )  

    plt.show()