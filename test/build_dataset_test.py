import copy
import unittest

import numpy as np
import pandas as pd

from build_dataset import build_training_dataset, build_predict_dataset

stock_prices = {
    "GOOGL": pd.read_csv("test/GOOGL.csv", index_col=0).iloc[::-1]
}
prices = stock_prices["GOOGL"]["adjusted_close"].values

input_options = {
    "config": [
        {"type": "lookback", "n": 10, "stock_code": "GOOGL", "column": "adjusted_close"},
        {"type": "moving_avg", "n": 10, "stock_code": "GOOGL", "column": "adjusted_close"}
    ],
    "stock_codes": ["GOOGL"],
    "stock_code": "GOOGL",
    "column": "adjusted_close"
}

rnn_input_options = {
    "config": [
        {"type": "lookback", "n": 1, "stock_code": "GOOGL", "column": "adjusted_close"},
        {"type": "moving_avg", "n": 10, "stock_code": "GOOGL", "column": "adjusted_close"}
    ],
    "stock_codes": ["GOOGL"],
    "stock_code": "GOOGL",
    "column": "adjusted_close",
    "time_window": 10
}

skip_input_options = {
    "config": [
        {"type": "lookback", "n": 10, "stock_code": "GOOGL", "column": "adjusted_close", "skip": 10}
    ],
    "stock_codes": ["GOOGL"],
    "stock_code": "GOOGL",
    "column": "adjusted_close"
}

skip_rnn_input_options = {
    "config": [
        {"type": "lookback", "n": 1, "stock_code": "GOOGL", "column": "adjusted_close", "skip": 10}
    ],
    "stock_codes": ["GOOGL"],
    "stock_code": "GOOGL",
    "column": "adjusted_close",
    "time_window": 10
}

normalize_input_options = {
    "config": [
        {"type": "lookback", "n": 10, "stock_code": "GOOGL", "column": "adjusted_close"}
    ],
    "normalize": "min_max",
    "stock_codes": ["GOOGL"],
    "stock_code": "GOOGL",
    "column": "adjusted_close"
}

normalize_rnn_input_options = {
    "config": [
        {"type": "lookback", "n": 1, "stock_code": "GOOGL", "column": "adjusted_close"}
    ],
    "normalize": "min_max",
    "stock_codes": ["GOOGL"],
    "stock_code": "GOOGL",
    "column": "adjusted_close",
    "time_window": 10
}

index_input_options = {
    "config": [
        {"type": "index_price", "n": 10}
    ],
    "stock_codes": ["GOOGL"],
    "stock_code": "GOOGL",
    "column": "adjusted_close"
}

class TestBuildTrainingDataset(unittest.TestCase):
    def test_btd_1(self):
        # input_options, predict 1

        x, y, _ = build_training_dataset(input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (3637, 11))
        self.assertEqual(y.shape, (3637, 1))

        x_start = [50.3228, 54.3227, 54.8694, 52.5974, 53.1641, 54.1221, 53.2393, 51.1629, 51.3435, 50.2802]
        x_end = [1097.99, 1125.89, 1118.62, 1141.42, 1151.87, 1122.89, 1105.91, 1102.38, 1102.12, 1127.58]
        x_start.append(sum(x_start) / len(x_start))
        x_end.append(sum(x_end) / len(x_end))
        self.assertEqual(x[0].tolist(), x_start)
        self.assertEqual(x[-1].tolist(), x_end)

        self.assertEqual(y[0][0], 50.9122)
        self.assertEqual(y[-1][0], 1128.63)

    def test_btd_2(self):
        # input_options, predict 10

        x, y, _ = build_training_dataset(input_options, 10, stock_data=stock_prices)

        self.assertEqual(x.shape, (3628, 11))
        self.assertEqual(y.shape, (3628, 10))

        x_start = prices[:10].tolist()
        x_start.append(prices[:10].mean())
        x_end = prices[-20:-10].tolist()
        x_end.append(prices[-20:-10].mean())
        self.assertEqual(x[0].tolist(), x_start)
        self.assertEqual(x[-1].tolist(), x_end)

        self.assertEqual(y[0].tolist(), prices[10:20].tolist())
        self.assertEqual(y[-1].tolist(), prices[-10:].tolist())

    def test_btd_3(self):
        # rnn_input_options, predict 1

        x, y, _ = build_training_dataset(rnn_input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (3628, 10, 2))
        self.assertEqual(y.shape, (3628, 1))

        self.assertEqual(x[0, :, 0].tolist(), prices[9:19].tolist())
        self.assertEqual(x[0, 0, 1], prices[:10].mean())
        self.assertEqual(x[0, 1, 1], prices[1:11].mean())
        self.assertEqual(x[0, 9, 1], prices[9:19].mean())
        self.assertEqual(x[1, :, 0].tolist(), prices[10:20].tolist())
        self.assertEqual(x[1, 0, 1], prices[1:11].mean())
        self.assertEqual(x[1, 1, 1], prices[2:12].mean())
        self.assertEqual(x[1, 9, 1], prices[10:20].mean())
        self.assertEqual(x[-1, :, 0].tolist(), prices[-11:-1].tolist())
        self.assertEqual(x[-1, 0, 1], prices[-20:-10].mean())
        self.assertEqual(x[-1, 1, 1], prices[-19:-9].mean())
        self.assertEqual(x[-1, 9, 1], prices[-11:-1].mean())

        self.assertEqual(y[0][0], prices[19])
        self.assertEqual(y[-1][0], prices[-1])

    def test_btd_4(self):
        # rnn_input_options, predict 10

        x, y, _ = build_training_dataset(rnn_input_options, 10, stock_data=stock_prices)

        self.assertEqual(x.shape, (3619, 10, 2))
        self.assertEqual(y.shape, (3619, 10))

        self.assertEqual(x[0, :, 0].tolist(), prices[9:19].tolist())
        self.assertEqual(x[0, 0, 1], prices[:10].mean())
        self.assertEqual(x[0, 1, 1], prices[1:11].mean())
        self.assertEqual(x[0, 9, 1], prices[9:19].mean())
        self.assertEqual(x[1, :, 0].tolist(), prices[10:20].tolist())
        self.assertEqual(x[1, 0, 1], prices[1:11].mean())
        self.assertEqual(x[1, 1, 1], prices[2:12].mean())
        self.assertEqual(x[1, 9, 1], prices[10:20].mean())
        self.assertEqual(x[-1, :, 0].tolist(), prices[-20:-10].tolist())
        self.assertEqual(x[-1, 0, 1], prices[-29:-19].mean())
        self.assertEqual(x[-1, 1, 1], prices[-28:-18].mean())
        self.assertEqual(x[-1, 9, 1], prices[-20:-10].mean())

        self.assertEqual(y[0].tolist(), prices[19:29].tolist())
        self.assertEqual(y[-1].tolist(), prices[-10:].tolist())

    def test_btd_5(self):
        # index_input_options, predict 10

        x, y, _ = build_training_dataset(index_input_options, 10, stock_data=stock_prices)

        self.assertEqual(x.tolist(), [[i] for i in range(1, 11)])
        self.assertEqual(y.tolist(), prices[-10:].tolist())

    def test_btd_6(self):
        # normalize_input_options, predict 1

        x, y, other_data = build_training_dataset(normalize_input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (3637, 10))
        self.assertEqual(y.shape, (3637, 1))
        self.assertTrue("normalize_data" in other_data)
        self.assertTrue("min" in other_data["normalize_data"])
        self.assertTrue("max" in other_data["normalize_data"])

        data_min = np.array([np.nanmin(prices[i:i + 3637]) for i in range(10)])
        data_max = np.array([np.nanmax(prices[i:i + 3637]) for i in range(10)])

        self.assertEqual(other_data["normalize_data"]["min"], data_min.tolist())
        self.assertEqual(other_data["normalize_data"]["max"], data_max.tolist())

        self.assertEqual(x[0].tolist(), ((prices[:10] - data_min) / (data_max - data_min)).tolist())
        self.assertEqual(x[1].tolist(), ((prices[1:11] - data_min) / (data_max - data_min)).tolist())
        self.assertEqual(x[-1].tolist(), ((prices[-11:-1] - data_min) / (data_max - data_min)).tolist())

        self.assertEqual(y[0][0], prices[10])
        self.assertEqual(y[1][0], prices[11])
        self.assertEqual(y[-1][0], prices[-1])

    def test_btd_7(self):
        # normalize_rnn_input_options, predict 1

        x, y, other_data = build_training_dataset(normalize_rnn_input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (3637, 10, 1))
        self.assertEqual(y.shape, (3637, 1))
        self.assertTrue("normalize_data" in other_data)
        self.assertTrue("min" in other_data["normalize_data"])
        self.assertTrue("max" in other_data["normalize_data"])

        data_min = np.array([np.nanmin(prices)])
        data_max = np.array([np.nanmax(prices)])

        self.assertEqual(other_data["normalize_data"]["min"], data_min.tolist())
        self.assertEqual(other_data["normalize_data"]["max"], data_max.tolist())

        self.assertEqual(x[0, :, 0].tolist(), ((prices[:10] - data_min) / (data_max - data_min)).tolist())
        self.assertEqual(x[1, :, 0].tolist(), ((prices[1:11] - data_min) / (data_max - data_min)).tolist())
        self.assertEqual(x[-1, :, 0].tolist(), ((prices[-11:-1] - data_min) / (data_max - data_min)).tolist())

        self.assertEqual(y[0][0], prices[10])
        self.assertEqual(y[1][0], prices[11])
        self.assertEqual(y[-1][0], prices[-1])

class TestBuildPredictDataset(unittest.TestCase):
    def test_bpd_1(self):
        # input_options, predict 1

        x = build_predict_dataset(input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (1, 11))

        x_predict = prices[-10:].tolist()
        x_predict.append(prices[-10:].mean())
        self.assertEqual(x[0].tolist(), x_predict)

    def test_bpd_2(self):
        # input_options, predict 10

        x = build_predict_dataset(input_options, 10, stock_data=stock_prices)

        self.assertEqual(x.shape, (1, 11))

        x_predict = [[1125.89, 1118.62, 1141.42, 1151.87, 1122.89, 1105.91, 1102.38, 1102.12, 1127.58, 1128.63]]
        x_predict[0].append(sum(x_predict[0]) / len(x_predict[0]))
        self.assertEqual(x.tolist(), x_predict)

    def test_bpd_3(self):
        # rnn_input_options, predict 1

        x = build_predict_dataset(rnn_input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (1, 10, 2))

        self.assertEqual(x[0, :, 0].tolist(), prices[-10:].tolist())
        self.assertEqual(x[0, 0, 1], prices[-19:-9].mean())
        self.assertEqual(x[0, 1, 1], prices[-18:-8].mean())
        self.assertEqual(x[0, 9, 1], prices[-10:].mean())

    def test_bpd_4(self):
        # rnn_input_options, predict 10

        x = build_predict_dataset(rnn_input_options, 10, stock_data=stock_prices)

        self.assertEqual(x.shape, (1, 10, 2))

        self.assertEqual(x[0, :, 0].tolist(), prices[-10:].tolist())
        self.assertEqual(x[0, 0, 1], prices[-19:-9].mean())
        self.assertEqual(x[0, 1, 1], prices[-18:-8].mean())
        self.assertEqual(x[0, 9, 1], prices[-10:].mean())

    def test_bpd_5(self):
        # skip_input_options, predict 1

        x = build_predict_dataset(skip_input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (1, 10))

        self.assertEqual(x[0].tolist(), prices[-20:-10].tolist())

    def test_bpd_6(self):
        # skip_rnn_input_options, predict 1

        x = build_predict_dataset(skip_rnn_input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (1, 10, 1))

        self.assertEqual(x[0, :, 0].tolist(), prices[-20:-10].tolist())

    def test_bpd_7(self):
        # index_input_options, predict 10

        x = build_predict_dataset(index_input_options, 10, stock_data=stock_prices)

        self.assertEqual(x.tolist(), [[i] for i in range(11, 21)])

    def test_bpd_8(self):
        # normalize_input_options, predict 1

        data_min = np.array([np.nanmin(prices[i:i + 3637]) for i in range(10)])
        data_max = np.array([np.nanmax(prices[i:i + 3637]) for i in range(10)])

        test_input_options = copy.deepcopy(normalize_input_options)
        test_input_options["normalize_data"] = {"min": data_min.tolist(), "max": data_max.tolist()}

        x = build_predict_dataset(test_input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (1, 10))

        self.assertEqual(x[0].tolist(), ((prices[-10:] - data_min) / (data_max - data_min)).tolist())

    def test_bpd_9(self):
        # normalize_rnn_input_options, predict 1

        data_min = np.array([np.nanmin(prices)])
        data_max = np.array([np.nanmax(prices)])

        test_input_options = copy.deepcopy(normalize_rnn_input_options)
        test_input_options["normalize_data"] = {"min": data_min.tolist(), "max": data_max.tolist()}

        x = build_predict_dataset(test_input_options, 1, stock_data=stock_prices)

        self.assertEqual(x.shape, (1, 10, 1))

        self.assertEqual(x[0, :, 0].tolist(), ((prices[-10:] - data_min) / (data_max - data_min)).tolist())

class TestBuildTestDataset(unittest.TestCase):
    def test_btd_1(self):
        # input_options, predict 1, full test set

        x, y = build_predict_dataset(input_options, 1, stock_data=stock_prices, predict=False)

        self.assertEqual(x.shape, (100, 11))
        self.assertEqual(y.shape, (100, 1))

        x_start = [1183.99, 1177.59, 1175.06, 1189.99, 1171.6, 1182.14, 1177.98, 1159.83, 1167.11, 1174.27]
        x_end = [1097.99, 1125.89, 1118.62, 1141.42, 1151.87, 1122.89, 1105.91, 1102.38, 1102.12, 1127.58]
        x_start.append(sum(x_start) / len(x_start))
        x_end.append(sum(x_end) / len(x_end))
        self.assertEqual(x[0].tolist(), x_start)
        self.assertEqual(x[-1].tolist(), x_end)

        self.assertEqual(y[0][0], 1191.57)
        self.assertEqual(y[-1][0], 1128.63)

    def test_btd_2(self):
        # input_options, predict 1, snakes test set

        x, y = build_predict_dataset(input_options, 1, stock_data=stock_prices, predict=False, test_set="snakes")

        self.assertEqual(x.shape, (10, 11))
        self.assertEqual(y.shape, (10, 1))

        self.assertEqual(x[0][:10].tolist(), prices[-101:-91].tolist())
        self.assertEqual(x[0][10].tolist(), prices[-101:-91].mean())
        self.assertEqual(x[1][:10].tolist(), prices[-91:-81].tolist())
        self.assertEqual(x[1][10].tolist(), prices[-91:-81].mean())
        self.assertEqual(x[-1][:10].tolist(), prices[-11:-1].tolist())
        self.assertEqual(x[-1][10].tolist(), prices[-11:-1].mean())

        self.assertEqual(y[0], prices[-91])
        self.assertEqual(y[1], prices[-81])
        self.assertEqual(y[-1], prices[-1])

    def test_btd_3(self):
        # input_options, predict 10, snakes test set

        x, y = build_predict_dataset(input_options, 10, stock_data=stock_prices, predict=False, test_set="snakes")

        self.assertEqual(x.shape, (10, 11))
        self.assertEqual(y.shape, (10, 10))

        x_start = [1183.99, 1177.59, 1175.06, 1189.99, 1171.6, 1182.14, 1177.98, 1159.83, 1167.11, 1174.27]
        x_end = [1089.51, 1099.12, 1107.3, 1078.63, 1084.41, 1084, 1101.51, 1079.86, 1070.06, 1097.99]
        x_start.append(sum(x_start) / len(x_start))
        x_end.append(sum(x_end) / len(x_end))
        self.assertEqual(x[0].tolist(), x_start)
        self.assertEqual(x[-1].tolist(), x_end)

        y_start = stock_prices["GOOGL"]["adjusted_close"].values[-100:-90].tolist()
        y_end = stock_prices["GOOGL"]["adjusted_close"].values[-10:].tolist()
        self.assertEqual(y[0].tolist(), y_start)
        self.assertEqual(y[-1].tolist(), y_end)

    def test_btd_4(self):
        # input_options, predict 10, full test set

        x, y = build_predict_dataset(input_options, 10, stock_data=stock_prices, predict=False, test_set="full")

        self.assertEqual(x.shape, (100, 11))
        self.assertEqual(y.shape, (100, 10))

        self.assertEqual(x[0][:10].tolist(), prices[-119:-109].tolist())
        self.assertEqual(x[0][10], prices[-119:-109].mean())
        self.assertEqual(x[1][:10].tolist(), prices[-118:-108].tolist())
        self.assertEqual(x[1][10], prices[-118:-108].mean())
        self.assertEqual(x[-1][:10].tolist(), prices[-20:-10].tolist())
        self.assertEqual(x[-1][10], prices[-20:-10].mean())

        self.assertEqual(y[0].tolist(), prices[-109:-99].tolist())
        self.assertEqual(y[1].tolist(), prices[-108:-98].tolist())
        self.assertEqual(y[-1].tolist(), prices[-10:].tolist())

    def test_btd_5(self):
        # rnn_input_options, predict 1, full test set

        x, y = build_predict_dataset(rnn_input_options, 1, stock_data=stock_prices, predict=False)

        self.assertEqual(x.shape, (100, 10, 2))
        self.assertEqual(y.shape, (100, 1))

        self.assertEqual(x[0, :, 0].tolist(), prices[-110:-100].tolist())
        self.assertEqual(x[0, 0, 1], prices[-119:-109].mean())
        self.assertEqual(x[0, 1, 1], prices[-118:-108].mean())
        self.assertEqual(x[0, 9, 1], prices[-110:-100].mean())
        self.assertEqual(x[1, :, 0].tolist(), prices[-109:-99].tolist())
        self.assertEqual(x[1, 0, 1], prices[-118:-108].mean())
        self.assertEqual(x[1, 1, 1], prices[-117:-107].mean())
        self.assertEqual(x[1, 9, 1], prices[-109:-99].mean())
        self.assertEqual(x[-1, :, 0].tolist(), prices[-11:-1].tolist())
        self.assertEqual(x[-1, 0, 1], prices[-20:-10].mean())
        self.assertEqual(x[-1, 1, 1], prices[-19:-9].mean())
        self.assertEqual(x[-1, 9, 1], prices[-11:-1].mean())

        self.assertEqual(y[0], prices[-100])
        self.assertEqual(y[1], prices[-99])
        self.assertEqual(y[-1], prices[-1])

    def test_btd_6(self):
        # rnn_input_options, predict 1, snakes test set

        x, y = build_predict_dataset(rnn_input_options, 1, stock_data=stock_prices, predict=False, test_set="snakes")

        self.assertEqual(x.shape, (10, 10, 2))
        self.assertEqual(y.shape, (10, 1))

        self.assertEqual(x[0, :, 0].tolist(), prices[-101:-91].tolist())
        self.assertEqual(x[0, 0, 1], prices[-110:-100].mean())
        self.assertEqual(x[0, 1, 1], prices[-109:-99].mean())
        self.assertEqual(x[0, 9, 1], prices[-101:-91].mean())
        self.assertEqual(x[1, :, 0].tolist(), prices[-91:-81].tolist())
        self.assertEqual(x[1, 0, 1], prices[-100:-90].mean())
        self.assertEqual(x[1, 1, 1], prices[-99:-89].mean())
        self.assertEqual(x[1, 9, 1], prices[-91:-81].mean())
        self.assertEqual(x[-1, :, 0].tolist(), prices[-11:-1].tolist())
        self.assertEqual(x[-1, 0, 1], prices[-20:-10].mean())
        self.assertEqual(x[-1, 1, 1], prices[-19:-9].mean())
        self.assertEqual(x[-1, 9, 1], prices[-11:-1].mean())

        self.assertEqual(y[0], prices[-91])
        self.assertEqual(y[1], prices[-81])
        self.assertEqual(y[-1], prices[-1])

    def test_btd_7(self):
        # rnn_input_options, predict 10, snakes test set

        x, y = build_predict_dataset(rnn_input_options, 10, stock_data=stock_prices, predict=False, test_set="snakes")

        self.assertEqual(x.shape, (10, 10, 2))
        self.assertEqual(y.shape, (10, 10))

        self.assertEqual(x[0, :, 0].tolist(), prices[-110:-100].tolist())
        self.assertEqual(x[0, 0, 1], prices[-119:-109].mean())
        self.assertEqual(x[0, 1, 1], prices[-118:-108].mean())
        self.assertEqual(x[0, 9, 1], prices[-110:-100].mean())
        self.assertEqual(x[1, :, 0].tolist(), prices[-100:-90].tolist())
        self.assertEqual(x[1, 0, 1], prices[-109:-99].mean())
        self.assertEqual(x[1, 1, 1], prices[-108:-98].mean())
        self.assertEqual(x[1, 9, 1], prices[-100:-90].mean())
        self.assertEqual(x[-1, :, 0].tolist(), prices[-20:-10].tolist())
        self.assertEqual(x[-1, 0, 1], prices[-29:-19].mean())
        self.assertEqual(x[-1, 1, 1], prices[-28:-18].mean())
        self.assertEqual(x[-1, 9, 1], prices[-20:-10].mean())

        self.assertEqual(y[0].tolist(), prices[-100:-90].tolist())
        self.assertEqual(y[1].tolist(), prices[-90:-80].tolist())
        self.assertEqual(y[-1].tolist(), prices[-10:].tolist())

    def test_btd_8(self):
        # rnn_input_options, predict 10, full test set

        x, y = build_predict_dataset(rnn_input_options, 10, stock_data=stock_prices, predict=False, test_set="full")

        self.assertEqual(x.shape, (100, 10, 2))
        self.assertEqual(y.shape, (100, 10))

        self.assertEqual(x[0, :, 0].tolist(), prices[-119:-109].tolist())
        self.assertEqual(x[0, 0, 1], prices[-128:-118].mean())
        self.assertEqual(x[0, 1, 1], prices[-127:-117].mean())
        self.assertEqual(x[0, 9, 1], prices[-119:-109].mean())
        self.assertEqual(x[1, :, 0].tolist(), prices[-118:-108].tolist())
        self.assertEqual(x[1, 0, 1], prices[-127:-117].mean())
        self.assertEqual(x[1, 1, 1], prices[-126:-116].mean())
        self.assertEqual(x[1, 9, 1], prices[-118:-108].mean())
        self.assertEqual(x[-1, :, 0].tolist(), prices[-20:-10].tolist())
        self.assertEqual(x[-1, 0, 1], prices[-29:-19].mean())
        self.assertEqual(x[-1, 1, 1], prices[-28:-18].mean())
        self.assertEqual(x[-1, 9, 1], prices[-20:-10].mean())

        self.assertEqual(y[0].tolist(), prices[-109:-99].tolist())
        self.assertEqual(y[1].tolist(), prices[-108:-98].tolist())
        self.assertEqual(y[-1].tolist(), prices[-10:].tolist())

    def test_btd_9(self):
        # skip_input_options, predict 1, full test set

        x, y = build_predict_dataset(skip_input_options, 1, stock_data=stock_prices, predict=False)

        self.assertEqual(x.shape, (100, 10))
        self.assertEqual(y.shape, (100, 1))

        self.assertEqual(x[0].tolist(), prices[-120:-110].tolist())
        self.assertEqual(x[1].tolist(), prices[-119:-109].tolist())
        self.assertEqual(x[-1].tolist(), prices[-21:-11].tolist())

        self.assertEqual(y[0][0], prices[-100])
        self.assertEqual(y[1][0], prices[-99])
        self.assertEqual(y[-1][0], prices[-1])

    def test_btd_10(self):
        # skip_input_options, predict 1, snakes test set

        x, y = build_predict_dataset(skip_input_options, 1, stock_data=stock_prices, predict=False, test_set="snakes")

        self.assertEqual(x.shape, (10, 10))
        self.assertEqual(y.shape, (10, 1))

        self.assertEqual(x[0].tolist(), prices[-111:-101].tolist())
        self.assertEqual(x[1].tolist(), prices[-101:-91].tolist())
        self.assertEqual(x[-1].tolist(), prices[-21:-11].tolist())

        self.assertEqual(y[0][0], prices[-91])
        self.assertEqual(y[1][0], prices[-81])
        self.assertEqual(y[-1][0], prices[-1])

    def test_btd_11(self):
        # skip_rnn_input_options, predict 1, full test set

        x, y = build_predict_dataset(skip_rnn_input_options, 1, stock_data=stock_prices, predict=False)

        self.assertEqual(x.shape, (100, 10, 1))
        self.assertEqual(y.shape, (100, 1))

        self.assertEqual(x[0, :, 0].tolist(), prices[-120:-110].tolist())
        self.assertEqual(x[1, :, 0].tolist(), prices[-119:-109].tolist())
        self.assertEqual(x[-1, :, 0].tolist(), prices[-21:-11].tolist())

        self.assertEqual(y[0][0], prices[-100])
        self.assertEqual(y[1][0], prices[-99])
        self.assertEqual(y[-1][0], prices[-1])

    def test_btd_12(self):
        # skip_rnn_input_options, predict 1, snakes test set

        x, y = build_predict_dataset(skip_rnn_input_options, 1, stock_data=stock_prices, predict=False, test_set="snakes")

        self.assertEqual(x.shape, (10, 10, 1))
        self.assertEqual(y.shape, (10, 1))

        self.assertEqual(x[0, :, 0].tolist(), prices[-111:-101].tolist())
        self.assertEqual(x[1, :, 0].tolist(), prices[-101:-91].tolist())
        self.assertEqual(x[-1, :, 0].tolist(), prices[-21:-11].tolist())

        self.assertEqual(y[0][0], prices[-91])
        self.assertEqual(y[1][0], prices[-81])
        self.assertEqual(y[-1][0], prices[-1])

    def test_btd_13(self):
        # normalize_input_options, predict 1, full test set

        data_min = np.array([np.nanmin(prices[i:i + 3637]) for i in range(10)])
        data_max = np.array([np.nanmax(prices[i:i + 3637]) for i in range(10)])

        test_input_options = copy.deepcopy(normalize_input_options)
        test_input_options["normalize_data"] = {"min": data_min.tolist(), "max": data_max.tolist()}

        x, y = build_predict_dataset(test_input_options, 1, stock_data=stock_prices, predict=False)

        self.assertEqual(x.shape, (100, 10))
        self.assertEqual(y.shape, (100, 1))

        self.assertEqual(x[0].tolist(), ((prices[-110:-100] - data_min) / (data_max - data_min)).tolist())
        self.assertEqual(x[1].tolist(), ((prices[-109:-99] - data_min) / (data_max - data_min)).tolist())
        self.assertEqual(x[-1].tolist(), ((prices[-11:-1] - data_min) / (data_max - data_min)).tolist())

        self.assertEqual(y[0][0], prices[-100])
        self.assertEqual(y[1][0], prices[-99])
        self.assertEqual(y[-1][0], prices[-1])

    def test_btd_14(self):
        # normalize_rnn_input_options, predict 1, full test set

        data_min = np.array([np.nanmin(prices)])
        data_max = np.array([np.nanmax(prices)])

        test_input_options = copy.deepcopy(normalize_rnn_input_options)
        test_input_options["normalize_data"] = {"min": data_min.tolist(), "max": data_max.tolist()}

        x, y = build_predict_dataset(test_input_options, 1, stock_data=stock_prices, predict=False)

        self.assertEqual(x.shape, (100, 10, 1))
        self.assertEqual(y.shape, (100, 1))

        self.assertEqual(x[0, :, 0].tolist(), ((prices[-110:-100] - data_min) / (data_max - data_min)).tolist())
        self.assertEqual(x[1, :, 0].tolist(), ((prices[-109:-99] - data_min) / (data_max - data_min)).tolist())
        self.assertEqual(x[-1, :, 0].tolist(), ((prices[-11:-1] - data_min) / (data_max - data_min)).tolist())

        self.assertEqual(y[0][0], prices[-100])
        self.assertEqual(y[1][0], prices[-99])
        self.assertEqual(y[-1][0], prices[-1])

if __name__ == '__main__':
    unittest.main()
