import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# ===================================================
# 1. 全国10地方のダミーデータを自動生成（CSV保存）
# ===================================================
np.random.seed(42)  # 毎回同じデータが作られるように固定
num_samples = 200  # 生成するデータの件数

# 日本の全10地方のリスト
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

# 気象データをランダムに生成
temperatures = np.random.uniform(10, 35, num_samples)  # 気温: 10℃〜35℃
humidities = np.random.uniform(30, 90, num_samples)  # 湿度: 30%〜90%
winds = np.random.uniform(0.5, 5.0, num_samples)  # 風速: 0.5m/s〜5.0m/s
suns = np.random.uniform(0.1, 1.0, num_samples)  # 日射量: 0.1〜1.0
regions = np.random.choice(regions_list, num_samples)  # 地方をランダムに割り振り

# 地方ごとの乾燥時間の補正値（北国は少し長く、南国は短くなどの特性）
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
    "沖縄": 15,
}

# ルールに基づいて「乾燥時間（分）」を逆算する
base_time = 300
drying_times = []
for i in range(num_samples):
    time_by_temp = (temperatures[i] - 20) * -8.0  # 1度上がると8分短縮
    time_by_humidity = (humidities[i] - 50) * 4.0  # 1%上がると4分遅延
    time_by_wind = (winds[i] - 2.0) * -20.0  # 1m/s強まると20分短縮
    time_by_sun = (suns[i] - 0.5) * -100.0  # 日差しが強いと最大50分前後短縮
    time_by_region = region_effects[regions[i]]  # 地域ごとの特性

    noise = np.random.normal(0, 15)  # 現実味を出すための±15分のズレ

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

# 最低30分、最大600分（10時間）の枠に収める
drying_times = np.clip(drying_times, 30, 600).astype(int)

# 表（データフレーム）にまとめる
df_visual = pd.DataFrame(
    {
        "地方": regions,
        "気温": np.round(temperatures, 1),
        "湿度": np.round(humidities, 0).astype(int),
        "風速": np.round(winds, 1),
        "日射量": np.round(suns, 2),
        "乾燥時間": drying_times,
    }
)

# CSVファイルとして保存
df_visual.to_csv("laundry_data_all_regions.csv", index=False, encoding="utf-8-sig")
print("1. 📂 『laundry_data_all_regions.csv』の自動作成が完了しました。")


# ===================================================
# 2. AI（予測モデル）の学習パート
# ===================================================
# 「地方」の文字データを、AIが読める0と1のデータに自動変換（ワンホットエンコーディング）
df_ai = pd.get_dummies(df_visual, columns=["地方"], dtype=int)

# AIに教える問題(X)と正解(y)に分ける
X = df_ai.drop(columns=["乾燥時間"])  # 乾燥時間以外のデータ（ヒント）
y = df_ai["乾燥時間"]  # 当てたい答え

# 線形回帰モデルを作成して学習させる
model = LinearRegression()
model.fit(X, y)
print("2. 🎉 AIの学習が完了し、予測モデルが正常に作成されました！")
print("-" * 60)


# ===================================================
# 3. アプリの予測画面を再現する関数
# ===================================================
def アプリの予測画面(今の時間, 気温, 湿度, 風速, 日射量, 地方):
    # ユーザーが入力した条件のデータ（辞書型）を作る
    input_dict = {
        "気温": [気温],
        "湿度": [湿度],
        "風速": [風速],
        "日射量": [日射量],
    }

    # 指定された地方のフラグだけを1にし、他は0にする
    for r in regions_list:
        input_dict[f"地方_{r}"] = [1 if r == 地方 else 0]

    # データフレーム（表）の形に変換
    input_df = pd.DataFrame(input_dict)

    # 🔥【重要】AIが学習した時と「全く同じ項目の並び順」に強制的に並び替える（エラー対策）
    input_df = input_df[X.columns]

    # 部屋干し・外干しの自動判定（湿度が70%以上なら部屋干し推奨）
    if 湿度 >= 70:
        判定 = "❌ 湿度が高すぎます！【部屋干し】にしましょう。"
    else:
        判定 = "☀️ 【外干し】がおすすめです！"

    # AIモデルを使って、乾燥時間（分）を予測
    予測された分数 = model.predict(input_df)[0]
    予測された分数 = max(30, 予測された分数)  # 最低でも30分はかかるようにする

    # 分数を時間データ（Timedelta）に変換
    経過時間 = pd.Timedelta(minutes=int(予測された分数))

    # 「干し始めた時間」に「乾燥時間」を足して、乾燥完了時刻を計算
    干し始め = pd.to_datetime(今の時間)
    乾く時間 = 干し始め + 経過時間

    # アプリ風に結果を画面に表示
    print(f"【 洗濯物乾き時間予測アプリ 】 地域: {地方}")
    print(f"現在の状況: 気温 {気温}℃ / 湿度 {湿度}% / 風速 {風速}m/s")
    print(f"アドバイス: {判定}")
    print(f"⏰ {干し始め.strftime('%H時%M分')} に干すと...")
    print(
        f"👉 約 {経過時間.seconds // 3600}時間 {(経過時間.seconds % 3600) // 60}分後 の"
    )
    print(f"✨【 {乾く時間.strftime('%H時%M分')} 】に乾きます！")
    print("-" * 60)


# ===================================================
# 4. 予測のテスト実行（あなたの理想通りの動きをチェック！）
# ===================================================
# テスト1：朝8時00分に関東で干した場合
アプリの予測画面(
    今の時間="08:00", 気温=26.5, 湿度=45, 風速=2.5, 日射量=0.8, 地方="関東"
)

# テスト2：お昼13時15分に東北で干した場合（少し涼しい日）
アプリの予測画面(
    今の時間="13:15", 気温=18.0, 湿度=55, 風速=1.2, 日射量=0.4, 地方="東北"
)

# テスト3：夕方16時00分に沖縄で干したけどジメジメしている場合（部屋干し判定のテスト）
アプリの予測画面(
    今の時間="16:00", 気温=27.0, 湿度=75, 風速=2.0, 日射量=0.2, 地方="沖縄"
)