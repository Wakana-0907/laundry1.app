import numpy as np
import pandas as pd

# 再現性を保つための設定
np.random.seed(42)

# 1. 100日分のリアルな天気データをランダムに生成
days = 100
temperature = np.random.uniform(15, 35, days)  # 気温：15℃〜35℃
humidity = np.random.uniform(40, 90, days)  # 湿度：40%〜90%
wind_speed = np.random.uniform(0.5, 5.0, days)  # 風速：0.5m/s〜5.0m/s

# 2. 物理的な理屈をもとに「乾く時間（時間）」を計算
# 気温が高い・風が強い → 早く乾く（マイナス効果）
# 湿度が高い → 乾きにくい（プラス効果）
base_time = 8 - (0.12 * temperature) + (0.05 * humidity) - (0.3 * wind_speed)

# 3. 現実らしい「バラつき（誤差）」を少し加える
noise = np.random.normal(0, 0.3, days)
dry_time = base_time + noise

# 念のため、乾く時間がマイナスや極端に短くならないように調整（最低1.5時間）
dry_time = np.clip(dry_time, 1.5, 12)

# 4. データをまとめてCSVファイルとして保存
df = pd.DataFrame(
    {
        "気温(C)": np.round(temperature, 1),
        "湿度(%)": np.round(humidity, 0),
        "風速(m/s)": np.round(wind_speed, 1),
        "乾く時間(時間)": np.round(dry_time, 2),
    }
)

# CSVとして出力
df.to_csv("laundry_dummy_data.csv", index=False, encoding="utf-8-sig")
print("データ作成が完了しました！ 'laundry_dummy_data.csv' を確認してください。")