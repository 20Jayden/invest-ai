import os
from dotenv import load_dotenv

load_dotenv()

def ai_trading():
    # 1. 업비트 차트 데이터 가져오기 ( 30일 일봉 )
    import pyupbit

    df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")

    # 2. A.I에게 데이터 제공하고 판단 받기
    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "You are an expert in Bitcoin investing. Tell me whether I should buy, sell, or hold at the moment based on the chart data provided. response in json format.\n\nResponse Example:\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"}\n{\"decision\": \"sell\", \"reason\": \"some technical reason\"}\n{\"decision\": \"hold\", \"reason\": \"some technical reason\"}"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": df.to_json()
            }
        ]
        }
    ],
    response_format={
        "type": "json_object"
    },
    )

    result = response.choices[0].message.content


    # 3. A.I의 판단에 따라 실제로 자동매매 진행하기
    import json
    result = json.loads(result)

    import pyupbit
    access = os.getenv("UPBIT_ACCESS")
    secret = os.getenv("UPBIT_SECRET")
    upbit = pyupbit.Upbit(access, secret)

    print("### AI Decision: ", result["decision"].upper(), "###")
    print("### Reason: ", result["reason"], "###")

    if result["decision"] == "buy":
        my_krw = upbit.get_balance("KRW") # 내 잔고 조회
        if my_krw * 0.9995 > 5000: # 내가 가진 돈의 수수료를 제외했을 때, 5000원이 넘으면 매수
            print("### Buy Order Executed ###")
            print(upbit.buy_market_order("KRW-BTC", my_krw * 0.9995)) # 시장가의 비트코인을 잔고를 모두 사용하여 매수
        else:
            print("### Buy Order Failed: Insufficient KRW (less than 5000 KRW) ###")
    elif result["decision"] == "sell":
        my_btc = upbit.get_balance("KRW-BTC")
        current_price = pyupbit.get_orderbook(ticker="KRW-BTC")["orderbook_units"][0]["ask_price"]
        if my_btc * current_price > 5000: # 내가 가진 비트코인의 현재 가격이 5000원이 넘으면 매도
            print("### Sell Order Executed ###")
            print(upbit.sell_market_order("KRW-BTC", my_btc))
        else:
            print("### Sell Order Failed: Insufficient BTC (less than 5000 KRW worth) ###")
    elif result["decision"] == "hold":
        print("### Hold Position ###")

    print(result)
    print(type(result))
    print(result['decision'])

while True:
    import time
    time.sleep(10)
    ai_trading()
