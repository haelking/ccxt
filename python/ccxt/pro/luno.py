# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

import ccxt.async_support
from ccxt.async_support.base.ws.cache import ArrayCache
from ccxt.async_support.base.ws.client import Client
from typing import Optional


class luno(ccxt.async_support.luno):

    def describe(self):
        return self.deep_extend(super(luno, self).describe(), {
            'has': {
                'ws': True,
                'watchTicker': False,
                'watchTickers': False,
                'watchTrades': True,
                'watchMyTrades': False,
                'watchOrders': None,  # is in beta
                'watchOrderBook': True,
                'watchOHLCV': False,
            },
            'urls': {
                'api': {
                    'ws': 'wss://ws.luno.com/api/1',
                },
            },
            'options': {
                'sequenceNumbers': {},
            },
            'streaming': {
            },
            'exceptions': {
            },
        })

    async def watch_trades(self, symbol: str, since: Optional[int] = None, limit: Optional[int] = None, params={}):
        """
        get the list of most recent trades for a particular symbol
        see https://www.luno.com/en/developers/api#tag/Streaming-API
        :param str symbol: unified symbol of the market to fetch trades for
        :param int [since]: timestamp in ms of the earliest trade to fetch
        :param int [limit]: the maximum amount of    trades to fetch
        :param dict [params]: extra parameters specific to the luno api endpoint
        :returns dict[]: a list of `trade structures <https://github.com/ccxt/ccxt/wiki/Manual#public-trades>`
        """
        await self.check_required_credentials()
        await self.load_markets()
        market = self.market(symbol)
        symbol = market['symbol']
        subscriptionHash = '/stream/' + market['id']
        subscription = {'symbol': symbol}
        url = self.urls['api']['ws'] + subscriptionHash
        messageHash = 'trades:' + symbol
        subscribe = {
            'api_key_id': self.apiKey,
            'api_key_secret': self.secret,
        }
        request = self.deep_extend(subscribe, params)
        trades = await self.watch(url, messageHash, request, subscriptionHash, subscription)
        if self.newUpdates:
            limit = trades.getLimit(symbol, limit)
        return self.filter_by_since_limit(trades, since, limit, 'timestamp', True)

    def handle_trades(self, client: Client, message, subscription):
        #
        #     {
        #         sequence: '110980825',
        #         trade_updates: [],
        #         create_update: {
        #             order_id: 'BXHSYXAUMH8C2RW',
        #             type: 'ASK',
        #             price: '24081.09000000',
        #             volume: '0.07780000'
        #         },
        #         delete_update: null,
        #         status_update: null,
        #         timestamp: 1660598775360
        #     }
        #
        rawTrades = self.safe_value(message, 'trade_updates', [])
        length = len(rawTrades)
        if length == 0:
            return
        symbol = subscription['symbol']
        market = self.market(symbol)
        messageHash = 'trades:' + symbol
        stored = self.safe_value(self.trades, symbol)
        if stored is None:
            limit = self.safe_integer(self.options, 'tradesLimit', 1000)
            stored = ArrayCache(limit)
            self.trades[symbol] = stored
        for i in range(0, len(rawTrades)):
            rawTrade = rawTrades[i]
            trade = self.parse_trade(rawTrade, market)
            stored.append(trade)
        self.trades[symbol] = stored
        client.resolve(self.trades[symbol], messageHash)

    def parse_trade(self, trade, market=None):
        #
        # watchTrades(public)
        #
        #     {
        #       "base": "69.00000000",
        #       "counter": "113.6499000000000000",
        #       "maker_order_id": "BXEEU4S2BWF5WRB",
        #       "taker_order_id": "BXKNCSF7JDHXY3H",
        #       "order_id": "BXEEU4S2BWF5WRB"
        #     }
        #
        return self.safe_trade({
            'info': trade,
            'id': None,
            'timestamp': None,
            'datetime': None,
            'symbol': market['symbol'],
            'order': None,
            'type': None,
            'side': None,
            # takerOrMaker has no meaning for public trades
            'takerOrMaker': None,
            'price': None,
            'amount': self.safe_string(trade, 'base'),
            'cost': self.safe_string(trade, 'counter'),
            'fee': None,
        }, market)

    async def watch_order_book(self, symbol: str, limit: Optional[int] = None, params={}):
        """
        watches information on open orders with bid(buy) and ask(sell) prices, volumes and other data
        :param str symbol: unified symbol of the market to fetch the order book for
        :param int [limit]: the maximum amount of order book entries to return
        :param dictConstructor [params]: extra parameters specific to the luno api endpoint
        :param str [params.type]: accepts l2 or l3 for level 2 or level 3 order book
        :returns dict: A dictionary of `order book structures <https://github.com/ccxt/ccxt/wiki/Manual#order-book-structure>` indexed by market symbols
        """
        await self.check_required_credentials()
        await self.load_markets()
        market = self.market(symbol)
        symbol = market['symbol']
        subscriptionHash = '/stream/' + market['id']
        subscription = {'symbol': symbol}
        url = self.urls['api']['ws'] + subscriptionHash
        messageHash = 'orderbook:' + symbol
        subscribe = {
            'api_key_id': self.apiKey,
            'api_key_secret': self.secret,
        }
        request = self.deep_extend(subscribe, params)
        orderbook = await self.watch(url, messageHash, request, subscriptionHash, subscription)
        return orderbook.limit()

    def handle_order_book(self, client: Client, message, subscription):
        #
        #     {
        #         "sequence": "24352",
        #         "asks": [{
        #             "id": "BXMC2CJ7HNB88U4",
        #             "price": "1234.00",
        #             "volume": "0.93"
        #         }],
        #         "bids": [{
        #             "id": "BXMC2CJ7HNB88U5",
        #             "price": "1201.00",
        #             "volume": "1.22"
        #         }],
        #         "status": "ACTIVE",
        #         "timestamp": 1528884331021
        #     }
        #
        #  update
        #     {
        #         sequence: '110980825',
        #         trade_updates: [],
        #         create_update: {
        #             order_id: 'BXHSYXAUMH8C2RW',
        #             type: 'ASK',
        #             price: '24081.09000000',
        #             volume: '0.07780000'
        #         },
        #         delete_update: null,
        #         status_update: null,
        #         timestamp: 1660598775360
        #     }
        #
        symbol = subscription['symbol']
        messageHash = 'orderbook:' + symbol
        timestamp = self.safe_string(message, 'timestamp')
        storedOrderBook = self.safe_value(self.orderbooks, symbol)
        if storedOrderBook is None:
            storedOrderBook = self.indexed_order_book({})
            self.orderbooks[symbol] = storedOrderBook
        asks = self.safe_value(message, 'asks')
        if asks is not None:
            snapshot = self.custom_parse_order_book(message, symbol, timestamp, 'bids', 'asks', 'price', 'volume', 'id')
            storedOrderBook.reset(snapshot)
        else:
            self.handle_delta(storedOrderBook, message)
            storedOrderBook['timestamp'] = timestamp
            storedOrderBook['datetime'] = self.iso8601(timestamp)
        nonce = self.safe_integer(message, 'sequence')
        storedOrderBook['nonce'] = nonce
        client.resolve(storedOrderBook, messageHash)

    def custom_parse_order_book(self, orderbook, symbol, timestamp=None, bidsKey='bids', asksKey='asks', priceKey='price', amountKey='volume', thirdKey=None):
        bids = self.parse_bids_asks(self.safe_value(orderbook, bidsKey, []), priceKey, amountKey, thirdKey)
        asks = self.parse_bids_asks(self.safe_value(orderbook, asksKey, []), priceKey, amountKey, thirdKey)
        return {
            'symbol': symbol,
            'bids': self.sort_by(bids, 0, True),
            'asks': self.sort_by(asks, 0),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'nonce': None,
        }

    def parse_bids_asks(self, bidasks, priceKey='price', amountKey='volume', thirdKey=None):
        bidasks = self.to_array(bidasks)
        result = []
        for i in range(0, len(bidasks)):
            result.append(self.custom_parse_bid_ask(bidasks[i], priceKey, amountKey, thirdKey))
        return result

    def custom_parse_bid_ask(self, bidask, priceKey='price', amountKey='volume', thirdKey=None):
        price = self.safe_number(bidask, priceKey)
        amount = self.safe_number(bidask, amountKey)
        result = [price, amount]
        if thirdKey is not None:
            thirdValue = self.safe_string(bidask, thirdKey)
            result.append(thirdValue)
        return result

    def handle_delta(self, orderbook, message):
        #
        #  create
        #     {
        #         sequence: '110980825',
        #         trade_updates: [],
        #         create_update: {
        #             order_id: 'BXHSYXAUMH8C2RW',
        #             type: 'ASK',
        #             price: '24081.09000000',
        #             volume: '0.07780000'
        #         },
        #         delete_update: null,
        #         status_update: null,
        #         timestamp: 1660598775360
        #     }
        #  del         #     {
        #         sequence: '110980825',
        #         trade_updates: [],
        #         create_update: null,
        #         delete_update: {
        #             "order_id": "BXMC2CJ7HNB88U4"
        #         },
        #         status_update: null,
        #         timestamp: 1660598775360
        #     }
        #  trade
        #     {
        #         sequence: '110980825',
        #         trade_updates: [
        #             {
        #                 "base": "0.1",
        #                 "counter": "5232.00",
        #                 "maker_order_id": "BXMC2CJ7HNB88U4",
        #                 "taker_order_id": "BXMC2CJ7HNB88U5"
        #             }
        #         ],
        #         create_update: null,
        #         delete_update: null,
        #         status_update: null,
        #         timestamp: 1660598775360
        #     }
        #
        createUpdate = self.safe_value(message, 'create_update')
        asksOrderSide = orderbook['asks']
        bidsOrderSide = orderbook['bids']
        if createUpdate is not None:
            array = self.custom_parse_bid_ask(createUpdate, 'price', 'volume', 'order_id')
            type = self.safe_string(createUpdate, 'type')
            if type == 'ASK':
                asksOrderSide.storeArray(array)
            elif type == 'BID':
                bidsOrderSide.storeArray(array)
        deleteUpdate = self.safe_value(message, 'delete_update')
        if deleteUpdate is not None:
            orderId = self.safe_string(deleteUpdate, 'order_id')
            asksOrderSide.storeArray(0, 0, orderId)
            bidsOrderSide.storeArray(0, 0, orderId)
        return message

    def handle_message(self, client: Client, message):
        if message == '':
            return
        subscriptions = list(client.subscriptions.values())
        handlers = [self.handle_order_book, self.handle_trades]
        for j in range(0, len(handlers)):
            handler = handlers[j]
            handler(client, message, subscriptions[0])
        return message
