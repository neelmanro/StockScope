from flask import Flask, render_template, request
import mysql.connector as connector
import yfinance as yf
import csv
import openai
import threading
import time


openai.api_key = "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"


app = Flask(__name__)

def get_db_connection():
    conn = connector.connect(
        host="localhost",
        user="root",
        password="Shukrana7*",
        database="StockScope",
    )
    cursor = conn.cursor(dictionary=True)
    return conn, cursor


def insert_stock_data():
    conn, cursor = get_db_connection()
    with open("top_50_stocks.csv", "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            ticker, sector, volatility = row[0], row[1], row[2]
            price = 0.0
            cursor.execute(
                """
                INSERT INTO stocks (ticker, sector, price, volatility)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    sector = VALUES(sector),
                    price = VALUES(price),
                    volatility = VALUES(volatility)
                """,
                (ticker, sector, price, volatility)
            )
    conn.commit()
    conn.close()
    print("✅ Stock data inserted successfully.")

def update_prices_from_api():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT ticker FROM stocks")
    tickers = cursor.fetchall()
    for stock in tickers:
        symbol = stock['ticker']
        try:
            data = yf.Ticker(symbol).history(period="1d")
            if not data.empty:
                latest_price = data["Close"].iloc[-1]
                cursor.execute(
                    "UPDATE stocks SET price = %s WHERE ticker = %s",
                    (round(latest_price, 2), symbol)
                )
        except Exception as e:
            print(f"Error updating {symbol}: {e}")
    conn.commit()
    conn.close()


def get_stock_summary(ticker, price, sector, volatility):
    prompt = (
        f"Provide a 50 to 100 word short analysis of the stock {ticker}. "
        f"Use the following data:\n"
        f"- Price: ${price}\n"
        f"- Sector: {sector}\n"
        f"- Volatility: {volatility}\n\n"
        f"Do not just restate the data. Instead, provide a short professional-sounding investment outlook. "
        f"Include any signals of performance (e.g., stability, risk, growth) based on this data. "
        f"Keep it beginner-friendly and easy to understand."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,   # bumped to 100 for longer summaries
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate summary: {e}"


@app.route("/", methods=["GET"])
def show_loading():
    return render_template("loading.html")


@app.route("/home", methods=["GET", "POST"])
def apply_filters():
    update_prices_from_api()

    threading.Thread(target=update_prices_from_api).start()
    time.sleep(0)  # Simulate wait


    conn, cursor = get_db_connection()
    query = "SELECT * FROM stocks WHERE 1=1"
    params = []

    if request.method == "POST":
        ticker = request.form.get("ticker")
        sector = request.form.get("sector")
        price_range = request.form.get("price_range")
        volatility = request.form.get("volatility")

        if ticker:
            query += " AND ticker = %s"
            params.append(ticker)
        if sector:
            query += " AND sector = %s"
            params.append(sector)
        if price_range:
            low, high = price_range.split("-")
            query += " AND price BETWEEN %s AND %s"
            params.extend([low, high])
        if volatility:
            query += " AND volatility = %s"
            params.append(volatility)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    summary = None
    if results:
        stock = results[0]
        summary = get_stock_summary(
            ticker=stock['ticker'],
            price=stock['price'],
            sector=stock['sector'],
            volatility=stock['volatility']
        )

    return render_template("home.html", stocks=results, summary=summary)

if __name__ == "__main__":
    
    app.run(debug=True)

