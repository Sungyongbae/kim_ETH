import time
import pyupbit
import datetime
import requests
import telegram

access = "MrylCV4hQ2NcpLxziYAd7JhBnlXqivGj1sujAxEL"
secret = "dkkEdfFmyKF02NGNVvn5vKvRvktxog4YtOlg63cX"

TOKEN = '1919980133:AAG845Pwz1i4WCJvaaamRT-_QE0uezlvA9A'
ID = '-548871861'
bot = telegram.Bot(TOKEN)


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma10(ticker):
    """10일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=10)
    ma15 = df['close'].rolling(10).mean().iloc[-1]
    return ma15

def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("kiyoon_autotrade start")
# 시작 메세지 텔레그램 전송
bot.sendMessage(ID, "kiyoon_autotrade start")

check_buy = False
check_inform = False
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            check_inform = False
            target_price = get_target_price("KRW-ETH", 0.1)
            ma10 = get_ma10("KRW-ETH")
            current_price = get_current_price("KRW-ETH")
            if check_buy == False and target_price < current_price and ma10 < current_price:   
                krw = get_balance("KRW")
                real_target = round(target_price,-3)
                total = (krw*0.9995)/real_target
                if krw > 5000:
                    buy_result = upbit.buy_limit_order("KRW-ETH", real_target, total)
                    bot.sendMessage(ID, "kiyoon_buy :"+str(buy_result))
                    check_buy = True

        else:
            btc = get_balance("ETH")
            if check_inform == False:
                if btc > 0.0016:
                    sell_result = upbit.sell_market_order("KRW-ETH", btc*0.9995)
                    bot.sendMessage(ID, "kiyoon_sell :"+str(sell_result))
                    check_buy = False
                    check_inform = True
                else:
                    uuid = buy_result['uuid']
                    cancel_result = upbit.cancel_order(uuid)
                    bot.sendMessage(ID, "kiyoon_cancel :"+str(cancel_result))
                    check_buy = False
                    check_inform = True
            else:
                print("인폼 끝")
        time.sleep(1)
    except Exception as e:
        print(e)
        bot.sendMessage(ID, e)
        time.sleep(1)
