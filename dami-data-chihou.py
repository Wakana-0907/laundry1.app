import numpy as np
import pandas as pd

# 再現性を保つための設定
np.random.seed(42)

# 各地方のデータ数
days_per_region = 100
total_data = []

# 地方ごとの気候の「設定値」（気温の範囲、湿度の範囲）
regions_settings = {
    "北海道": {"temp": (10, 25), "humidity": (40, 70), "wind": (1.0, 5.0)},
    "関東": {"temp": (15, 33), "humidity": (45, 80), "wind": (0.5, 4.0)},
    "関西": {"temp": (16, 34), "humidity": (45, 80), "wind": (0.5, 3.5)},
    "沖縄": {"temp": (20, 35), "humidity": (60, 90), "wind": (1.0, 5.5)},
}

# 地方ごとにデータを生成
for region, config in regions_settings.items():
    # 1. 各地方の特徴に合わせてランダムに気象データを生成
    temp = np.random.uniform(config["temp"][0], config["temp"][1], days_per_region)
    hum = np.random.uniform(
        config["humidity"][0], config["humidity"][1], days_per_region
    )
    wind = np.random.uniform(
        config["wind"][0], config["wind"][1], days_per_region
    )

    # 2. 洗濯物が乾く基本時間を計算（物理的な基本ルールは共通）
    base_time = 8 - (0.12 * temp) + (0.05 * hum) - (0.3 * wind)

    # 3. ランダムな誤差（その日の日当たりや環境の差など）を足す
    noise = np.random.normal(0, 0.3, days_per_region)
    dry_time = base_time + noise

    # 極端な数値にならないように調整（最低1.5時間〜最大12時間）
    dry_time = np.clip(dry_time, 1.5, 12)

    # リストに追加
    for i in range(days_per_region):
        total_data.append(
            {
                "地方": region,
                "気温(C)": np.round(temp[i], 1),
                "湿度(%)": np.round(hum[i], 0),
                "風速(m/s)": np.round(wind[i], 1),
                "乾く時間(時間)": np.round(dry_time[i], 2),
            }
        )

# DataFrameに変換してCSV保存
df = pd.DataFrame(total_data)
df.to_csv("laundry_regional_dummy_data.csv", index=False, encoding="utf-8-sig")
print(
    "地方別のデータ作成が完了しました！ 'laundry_regional_dummy_data.csv' を確認してください。"
)