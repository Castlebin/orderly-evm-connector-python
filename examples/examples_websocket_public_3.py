# from orderly_evm_connector.websocket.websocket_api import WebsocketAPIClient as WebsocketClients
import json

from utils.config import get_account_info
import time, logging
from orderly_evm_connector.websocket.websocket_api import WebsocketPublicAPIClient
from datetime import datetime
import os
from multiprocessing import Pool

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

    logging.info(message)

    try:
        response = json.loads(message)
        #if 'event' in response and response['event'] == 'ping':
            #return
        if 'ts' in response:
            ts = response['ts']
            logging.info(f"ts={ts} now={current_timestamp_ms}, Time difference: {current_timestamp_ms - ts}")
    except ValueError:
        return


# Public websocket does not need to pass orderly_key and orderly_secret arguments

def websocket_task(wss_client):
    logging.info(f"Starting websocket task pid: {os.getpid()} , clientId: {wss_client.wss_id}")
    # #Request orderbook data
    #wss_client.request_orderbook('orderbook','PERP_BTC_USDC')
    # #orderbook depth 100 push every 1s
    #wss_client.get_orderbook('PERP_NEAR_USDC@orderbook')
    # #orderbookupdate updated orderbook push every 200ms
    #wss_client.get_orderbookupdate('PERP_BTC_USDC@orderbookupdate')
    #wss_client.get_trade('PERP_NEAR_USDC@trade')
    #wss_client.get_24h_ticker('PERP_NEAR_USDC@ticker')
    #wss_client.get_24h_tickers()
    #wss_client.get_bbo('PERP_BTC_USDC@bbo')
    wss_client.get_bbos()
    #wss_client.get_kline("PERP_NEAR_USDC@kline_1m")
    #wss_client.get_index_price('PERP_ETH_USDC@indexprice')
    #wss_client.get_index_prices()
    # wss_client.get_mark_price('PERP_ETH_USDC@markprice')
    # wss_client.get_mark_prices()
    # wss_client.get_open_interest('PERP_ETH_USDC@openinterest')
    # wss_client.get_estimated_funding_rate('PERP_BTC_USDC@estfundingrate')
    # wss_client.get_liquidation_push()

    time.sleep(1000)
    wss_client.stop()


if __name__ == '__main__':
    pool_size = 10
    p = Pool(pool_size)
    for i in range(pool_size):
        wss_client = WebsocketPublicAPIClient(
            orderly_testnet=orderly_testnet,
            orderly_account_id=orderly_account_id,
            wss_id=wss_id + str(i),
            on_message=message_handler,
            on_close=on_close,
            debug=True,
        )
        p.apply_async(websocket_task, args=(wss_client,))
        time.sleep(1)

    logging.info('Waiting for all subprocesses done...')
    p.close()
    p.join()
    logging.info('All subprocesses done.')


