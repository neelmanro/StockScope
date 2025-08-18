# StockScope

Simple and fast stock filtering with an AI summary. Built with Flask and MySQL. Pulls live prices with yfinance. Generates a short beginner friendly outlook for any selected ticker using OpenAI

Live app at https://stockscope.xyz

## What this project does

* Filter a curated list of tickers by symbol sector price band and volatility
* View a clean table of results that updates with fresh prices
* Click into a result and see a short AI summary that explains stability risk and growth signals in plain language
* Smooth loading view that sends you straight to Home once data is ready

## Why this exists

Finding a clear signal inside basic stock data can feel hard for new investors. StockScope keeps the UI minimal. It gives one simple AI paragraph that reads like a quick nudge in the right direction

## Tech stack

* Flask for the web app
* MySQL for data storage
* yfinance for price updates
* OpenAI for the AI summary
* HTML CSS and a little vanilla JS for the front end

## App structure

* app.py holds routes data access helpers price updater and AI summary helper
* templates folder contains loading.html and home.html
* top_50_stocks.csv is the seed list used for the first insert

## Key flow

* loading page posts an empty form to the Home route
* Home route fetches prices then applies filters then renders the table
* The first matching row powers the AI summary with a short OpenAI call

## Local setup

Requirements
* Python 3.10 or newer
* MySQL 8 or newer
* A working OpenAI API key
* top_50_stocks.csv in the project root

Create and activate a virtual environment

macOS or Linux
python3 -m venv .venv
source .venv/bin/activate

Windows PowerShell
py -m venv .venv
.venv\Scripts\Activate.ps1

Install packages

pip install flask mysql-connector-python yfinance openai

Set your OpenAI key in the environment

macOS or Linux
export OPENAI_API_KEY=your_key_here

Windows PowerShell
setx OPENAI_API_KEY your_key_here

Create the database and table in MySQL

CREATE DATABASE IF NOT EXISTS StockScope;
USE StockScope;

CREATE TABLE IF NOT EXISTS stocks (
  ticker VARCHAR(16) PRIMARY KEY,
  sector VARCHAR(64),
  price DECIMAL(10,2) DEFAULT 0.00,
  volatility VARCHAR(16)
);

Seed the tickers from CSV. This step is baked into app.py through insert_stock_data which you can run once in a Python shell if you need it. Prices will be filled by the updater

Optional one time seed using Python REPL

from app import insert_stock_data
insert_stock_data()

Run the app

python app.py

Open http local host 5000 in your browser

## How to use the filters

* Enter a ticker or leave blank
* Choose a sector or leave blank
* Pick a price band or leave blank
* Choose a volatility level or leave blank
* Submit to see a table of matching rows
* The page shows one AI summary for the first matching stock

## Configuration notes

* OpenAI summary uses a short friendly prompt with a target of fifty to one hundred words
* Model string in code is gpt 3.5 turbo which still works for a quick paragraph. You can switch to a newer light model if you prefer
* yfinance pulls the most recent Close and rounds to two decimals

## Deployment overview

The live site runs on AWS EC2. A simple production setup looks like this

* Ubuntu on EC2
* System Python or a dedicated virtualenv
* MySQL on the instance or an external RDS
* A process manager such as systemd or tmux that keeps the Flask app alive
* Optional Nginx in front for TLS and clean routing

Example systemd service snippet

[Unit]
Description=StockScope
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/stockscope
Environment=OPENAI_API_KEY=your_key_here
ExecStart=/home/ubuntu/stockscope/.venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target

If you use Nginx you can proxy pass to localhost port 5000 and add a Lets Encrypt certificate

## Security and reliability

* Store secrets in environment variables not in code
* Wrap the OpenAI call with a short timeout and simple error text which is already handled in get_stock_summary
* yfinance calls can fail during network hiccups so the updater runs inside a try block per ticker
* The app spawns a background thread in the Home route. For heavier traffic consider moving the updater to a scheduled job or a worker process

## Database model

stocks
* ticker text primary key
* sector text
* price decimal
* volatility text

## Project status

First public version is live. Core filters and AI summary are stable. Next up you can add pagination watchlists export to CSV and sparkline charts

## Contributing

Issues and pull requests are welcome. Keep the tone beginner friendly and keep the UI simple

## License

MIT. Use it learn from it share it

## Acknowledgements

Thanks to the yfinance project and the OpenAI API which make quick experiments like this possible

## Quick FAQ

Why do I sometimes see zero prices
* That means the row has been seeded but a price update did not arrive yet. Try reloading or let the updater run again

Can I point this at a bigger universe
* Yes. Replace top_50_stocks.csv and reseed. Make sure tickers exist on Yahoo Finance

Can I run this without OpenAI
* Yes. Comment out the summary call and hide the summary box in the template

## Contact

If you have ideas or find bugs open an issue or reach out on the repo. Live app is at stockscope dot xyz
