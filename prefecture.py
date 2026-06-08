import numpy as np
import pandas as pd

# 毎回同じデータが作られるように固定
np.random.seed(100)
num_samples_per_pref = 10  # 1都道府県あたり10件のデータをシミュレート（計470件）

# 47都道府県のリスト
prefectures = [
    "北海道",
    "青森県",
    "岩手県",
    "宮城県",
    "秋田県",
    "山形県",
    "福島県",
    "茨城県",
    "栃木県",
    "群馬県",
    "埼玉県",
    "千葉県",
    "東京都",
    "神奈川県",
    "新潟県",
    "富山県",
    "石川県",
    "福井県",
    "山梨県",
    "長野県",
    "岐阜県",
    "静岡県",
    "愛知県",
    "三重県",
    "滋賀県",
    "京都府",
    "大阪府",
    "兵庫県",
    "奈良県",
    "和歌山県",
    "鳥取県",
    "島根県",
    "岡山県",
    "広島県",
    "山口県",
    "徳島県",
    "香川県",
    "愛媛県",
    "高知県",
    "福岡県",
    "佐賀県",
    "長崎県",
    "熊本県",
    "大分県",
    "宮崎県",
    "鹿児島県",
    "沖縄県",
]

# 都道府県ごとの乾燥補正値（北国や豪雪地帯、梅雨の長い地域は長めに、南国や太平洋側は短めに設定）
pref_effects = {
    "北海道": 45,
    "青森県": 35,
    "岩手県": 30,
    "宮城県": 15,
    "秋田県": 35,
    "山形県": 30,
    "福島県": 20,
    "茨城県": 5,
    "栃木県": 10,
    "群馬県": 0,
    "埼玉県": -5,
    "千葉県": -5,
    "東京都": 0,
    "神奈川県": -5,
    "新潟県": 40,
    "富山県": 35,
    "石川県": 35,
    "福井県": 30,
    "山梨県": 10,
    "長野県": 15,
    "岐阜県": 10,
    "静岡県": -10,
    "愛知県": -5,
    "三重県": 0,
    "滋賀県": 15,
    "京都府": 10,
    "大阪府": -5,
    "兵庫県": 0,
    "奈良県": 10,
    "和歌山県": -5,
    "鳥取県": 25,
    "島根県": 25,
    "岡山県": -10,
    "広島県": 0,
    "山口県": 5,
    "徳島県": 0,
    "香川県": -10,
    "愛媛県": -5,
    "高知県": -15,
    "福岡県": -5,
    "佐賀県": 0,
    "長崎県": 0,
    "熊本県": -5,
    "大分県": 0,
    "宮崎県": -15,
    "鹿児島県": -10,
    "沖縄県": 20,  # 気温は高いが湿度が高いため少しプラス
}

data_list = []

# 各都道府県ごとにデータを生成
for pref in prefectures:
    for _ in range(num_samples_per_pref):
        # 基本となる気象条件をランダム生成
        temp = np.random.uniform(10, 35)  # 気温: 10℃〜35℃
        humidity = np.random.uniform(30, 90)  # 湿度: 30%〜90%
        wind = np.random.uniform(0.5, 5.0)  # 風速: 0.5m/s〜5.0m/s
        sun = np.random.uniform(0.1, 1.0)  # 日射量: 0.1〜1.0

        # 乾燥時間の計算（基本300分）
        base_time = 300
        time_by_temp = (temp - 20) * -8.0
        time_by_humidity = (humidity - 50) * 4.0
        time_by_wind = (wind - 2.0) * -20.0
        time_by_sun = (sun - 0.5) * -100.0
        time_by_pref = pref_effects[pref]

        # ±10分の現実的なノイズ
        noise = np.random.normal(0, 10)

        calc_time = (
            base_time
            + time_by_temp
            + time_by_humidity
            + time_by_wind
            + time_by_sun
            + time_by_pref
            + noise
        )
        # 30分〜600分の間に収める
        final_time = int(np.clip(calc_time, 30, 600))

        # 1行分のデータを保存
        data_list.append(
            {
                "都道府県": pref,
                "気温": round(temp, 1),
                "湿度": int(round(humidity, 0)),
                "風速": round(wind, 1),
                "日射量": round(sun, 2),
                "乾燥時間(分)": final_time,
            }
        )

# データフレームに変換
df_all_prefs = pd.DataFrame(data_list)

# CSVファイルとして書き出し（Excelでの文字化けを防ぐため utf-8-sig を指定）
csv_filename = "laundry_data_47_prefectures.csv"
df_all_prefs.to_csv(csv_filename, index=False, encoding="utf-8-sig")

print(f"✨ 成功！ 47都道府県・計 {len(df_all_prefs)} 件のデータが入った CSV を作成しました。")
print(f"📁 ファイル名: {csv_filename}")