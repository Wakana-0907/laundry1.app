import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# 乱数を固定
np.random.seed(42)
num_samples = 200  # 地方が増えたので、データも200件に増やします

# 1. 日本の全10地方のリスト
regions_list = [
    "北海道",
    "東北",
    "関東",
    "中部",
    "北陸",
    "近畿",
    "中国",
    "四国",
    "九州",
    "沖縄",
]

# --- 2. 基本データのランダム生成 ---
temperatures = np.random.uniform(10, 35, num_samples)
humidities = np.random.uniform(30, 90, num_samples)
winds = np.random.uniform(0.5, 5.0, num_samples)
suns = np.random.uniform(0.1, 1.0, num_samples)

# 「地方」の文字をランダムに割り振る（北海道、東北、関東...が均等に入ります）
regions = np.random.choice(regions_list, num_samples)

# --- 3. 地方ごとの「乾きやすさの癖」を設定（裏ルール） ---
# 北国は寒さで少し乾きにくく、南国や島国は風や日差しが強い、などの個性を数値化
region_effects = {
    "北海道": 40,
    "東北": 30,
    "関東": 0,
    "中部": 5,
    "北陸": 35,
    "近畿": 0,
    "中国": 10,
    "四国": 10,
    "九州": -10,
    "沖縄": 15,  # 湿気はあるが日差しベースで少しプラス
}

# --- 4. 乾燥時間の計算 ---
base_time = 300
drying_times = []

for i in range(num_samples):
    time_by_temp = (temperatures[i] - 20) * -8.0
    time_by_humidity = (humidities[i] - 50) * 4.0
    time_by_wind = (winds[i] - 2.0) * -20.0
    time_by_sun = (suns[i] - 0.5) * -100.0

    # その行の地方に応じた時間をプラス/マイナスする
    current_region = regions[i]
    time_by_region = region_effects[current_region]

    noise = np.random.normal(0, 15)

    calc_time = (
        base_time
        + time_by_temp
        + time_by_humidity
        + time_by_wind
        + time_by_sun
        + time_by_region
        + noise
    )
    drying_times.append(calc_time)

drying_times = np.clip(drying_times, 30, 600).astype(int)

# --- 5. 見やすいデータフレーム（表）の作成 ---
df_visual = pd.DataFrame(
    {
        "地方": regions,  # 👈 ここに「北海道」「東北」がそのまま入ります！
        "気温": np.round(temperatures, 1),
        "湿度": np.round(humidities, 0).astype(int),
        "風速": np.round(winds, 1),
        "日射量": np.round(suns, 2),
        "乾燥時間": drying_times,
    }
)

# CSVに保存（Excelで開いてもバッチリ見やすいです）
df_visual.to_csv("laundry_data_all_regions.csv", index=False, encoding="utf-8-sig")
print("📂 全国対応のCSVファイル『laundry_data_all_regions.csv』を作成しました！\n")
print("👇 CSVデータの中身のイメージ：")
print(df_visual.head(8))
print("-" * 50 + "\n")


# ===================================================
# 6. 【AIの学習パート】「文字」を自動で数字に変換して学習させる
# ===================================================
# AIは「東北」という文字のままだと計算できないので、
# プログラムの中で自動的に「地方_東北」のような0と1のデータに変換（ワンホットエンコーディング）します。
df_ai = pd.get_dummies(df_visual, columns=["地方"], dtype=int)

# AIに教える問題(X)と正解(y)
X = df_ai.drop(columns=["乾燥時間"])  # 乾燥時間以外のすべて
y = df_ai["乾燥時間"]

model = LinearRegression()
model.fit(X, y)
print("🎉 AIの学習もこのデータでバッチリ完了しました！\n")


# ===================================================
# 7. 予測してみる関数
# ===================================================
def predict_laundry_all(temp, humidity, wind, sun, region):
    # ユーザーが指定した条件を、AIが読める形式の1行のデータにする
    input_dict = {
        "気温": [temp],
        "湿度": [humidity],
        "風速": [wind],
        "日射量": [sun],
    }
    # 全地方の列を0で初期化して、指定された地方だけ1にする
    for r in regions_list:
        input_dict[f"地方_{r}"] = [1 if r == region else 0]

    input_df = pd.DataFrame(input_dict)

    # 部屋干し判定
    recommendation = "❌ 部屋干し推奨" if humidity >= 70 else "☀️ 外干しOK"

    # 予測
    pred = model.predict(input_df)[0]
    pred = max(30, pred)  # 最低30分

    hours = int(pred // 60)
    minutes = int(pred % 60)

    print(f"【予測】地域: {region} / {recommendation}")
    print(f"👉 約 {hours}時間 {minutes}分 で乾きます！\n")


# テスト実行
predict_laundry_all(temp=18, humidity=50, wind=1.5, sun=0.5, region="東北")
predict_laundry_all(temp=18, humidity=50, wind=1.5, sun=0.5, region="九州")