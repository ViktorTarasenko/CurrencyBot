class CurrencyService:
    def __init__(self, time_source):
        self.currency_list = {}
        self.time_source = time_source

    def rates_list(self, base_currency):
        return {"rates":{"CAD":1.3256719184,"HKD":7.781278962,"ISK":127.9888785913,"PHP":50.718257646,"DKK":6.9213160334,"HUF":313.2530120482,"CZK":23.203892493,"GBP":0.7770157553,"RON":4.4466172382,"SEK":9.8225208526,"IDR":13707.4976830399,"INR":71.6167747915,"BRL":4.3874884152,"RUB":63.7683039852,"HRK":6.9040778499,"JPY":112.0111214087,"THB":31.4402224282,"CHF":0.9838739574,"EUR":0.9267840593,"MYR":4.1839666358,"BGN":1.8126042632,"TRY":6.0987951807,"CNY":7.0238183503,"NOK":9.3100092678,"NZD":1.5797961075,"ZAR":15.103429101,"USD":1.0,"MXN":18.6918443003,"SGD":1.400463392,"AUD":1.5101019462,"ILS":3.4299351251,"KRW":1206.4782205746,"PLN":3.968952734},"base":"USD","date":"2020-02-20"}

    def exchange(self, base_currency, target_currency, amount):
        return 10

    def history(self, ndays, base_currency, target_currency):
        return {"rates":{"2019-11-27":{"CAD":1.3266418385},"2019-11-28":{"CAD":1.3289413903},"2019-12-03":{"CAD":1.3320386596},"2019-12-02":{"CAD":1.3295835979},"2019-11-29":{"CAD":1.3307230013}},"start_at":"2019-11-27","base":"USD","end_at":"2019-12-03"}

    def __history(self, start_date, end_date, base_currency, target_currency):
        return [{"CAD": 1}]
