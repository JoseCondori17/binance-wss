from extract.binance_client import extract_all
from transform.kline_processor import transform_merge


if __name__ == "__main__":
    data = extract_all()
    transformed_data = transform_merge(data)
    print(transformed_data.head())