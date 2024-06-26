# from orderly_evm_connector.websocket.websocket_api import WebsocketAPIClient as WebsocketClients
import json

from utils.config import get_account_info
import time, logging
from orderly_evm_connector.websocket.websocket_api import WebsocketPublicAPIClient
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

(
    orderly_key,
    orderly_secret,
    orderly_account_id,
    wallet_secret,
    orderly_testnet,
    wss_id,
) = get_account_info()


def on_close(_):
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    now = datetime.now()
    # 获取当前时间戳（毫秒）
    current_timestamp_ms = int(now.timestamp() * 1000) + now.microsecond // 1000

    # logging.info(f"thread={threading.current_thread().name} {message}")

    try:
        response = json.loads(message)
        #if 'event' in response and response['event'] == 'ping':
        #    return
        if 'ts' in response:
            ts = response['ts']
            logging.info(f"thread={threading.current_thread().name} ts={ts} now={current_timestamp_ms}, {message} "
                         f"Time difference: {current_timestamp_ms - ts}")
    except ValueError:
        return


# Public websocket does not need to pass orderly_key and orderly_secret arguments


def websocket_task(no):
    wss_client = WebsocketPublicAPIClient(
        orderly_testnet=orderly_testnet,
        orderly_account_id=orderly_account_id,
        wss_id=wss_id + str(no),
        on_message=message_handler,
        on_close=on_close,
        debug=True,
    )
    logging.info(f"Starting websocket task: thread={threading.current_thread().name} clientId={wss_client.wss_id}")

    # #Request orderbook data
    wss_client.request_orderbook('orderbook','PERP_BTC_USDC')
    #orderbook depth 100 push every 1s
    wss_client.get_orderbook('PERP_NEAR_USDC@orderbook')
    # orderbookupdate updated orderbook push every 200ms
    wss_client.get_orderbookupdate('PERP_NEAR_USDC@orderbookupdate')
    wss_client.get_trade('PERP_NEAR_USDC@trade')
    wss_client.get_24h_ticker('PERP_NEAR_USDC@ticker')
    wss_client.get_24h_tickers()
    wss_client.get_bbo('PERP_NEAR_USDC@bbo')
    wss_client.get_bbos()
    wss_client.get_kline("PERP_NEAR_USDC@kline_1m")
    wss_client.get_index_price('PERP_ETH_USDC@indexprice')
    wss_client.get_index_prices()
    wss_client.get_mark_price('PERP_ETH_USDC@markprice')
    wss_client.get_mark_prices()
    wss_client.get_open_interest('PERP_ETH_USDC@openinterest')
    wss_client.get_estimated_funding_rate('PERP_BTC_USDC@estfundingrate')
    wss_client.get_liquidation_push()

    time.sleep(1000)
    wss_client.stop()


if __name__ == '__main__':
    pool_size = 1000
    pool = ThreadPoolExecutor(max_workers=pool_size)
    for i in range(pool_size):
        pool.submit(websocket_task, i)
        if i % 50 == 0:
            time.sleep(1)

    pool.shutdown()
    logging.info('All done.')

