from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO
from threading import Event
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True, async_mode='gevent')
connected_clients = 0
thread_stop_event = Event()


def fetch_gold_prices():
    """Fetch gold prices using Selenium."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        url = 'https://dubaicityofgold.com/'
        driver.get(url)

        driver.implicitly_wait(5)

        gold_elements = driver.find_elements(By.CSS_SELECTOR, "ul.goldtable li")
        prices = {}
        for element in gold_elements:
            text = element.text.strip()
            if text:
                gold_type, price_value = text.split(" - AED ")
                prices[gold_type.strip()] = price_value.strip()

        driver.quit()
        return prices
    except Exception as e:
        print(f"Error fetching gold prices: {e}")
        return {"error": str(e)}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/gold-prices')
def api_gold_prices():
    """Flask route to get gold prices."""
    prices = fetch_gold_prices()
    if "error" in prices:
        return jsonify(prices), 500
    return jsonify(prices)


def background_scraping():
    """Background task to scrape gold prices and emit updates."""
    while connected_clients > 0:
        prices = fetch_gold_prices()
        if "error" not in prices:
            socketio.emit('gold_price_update', prices)
        else:
            print("Error in fetching prices for WebSocket clients:", prices["error"])
        socketio.sleep(600)  # Wait 10 minute before fetching again.


@socketio.on('connect')
def handle_connect():
    """Handle new client connections."""
    global connected_clients
    connected_clients += 1
    print(f"Client connected. Total clients: {connected_clients}")
    socketio.emit('welcome_message', {
        'message': 'Welcome to the gold price update WebSocket!',
        'status': 'success'
    }, to=request.sid)

    if connected_clients == 1:
        print("Starting background scraping task...")
        socketio.start_background_task(background_scraping)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    global connected_clients
    connected_clients -= 1
    print(f"Client disconnected. Total clients: {connected_clients}")


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

    # socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
