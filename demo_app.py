import pandas as pd
from sklearn.ensemble import IsolationForest
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from itertools import combinations

st.title("異常検知デモ")

st.subheader("デモ用CSV")
# サンプルCSV読み込み
df = pd.read_csv("data/sample_sensor.csv")
# ダウンロードボタン
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("当方で用意したCSVを使う場合はこちらからダウンロードしてアップロード", csv, "sample.csv", "text/csv")

# アップロードもOK
st.subheader("自分のCSVを使う場合はこちら")
uploaded_file = st.file_uploader("CSVをアップロード", type="csv")

if uploaded_file is not None:
    try:
    
        df = pd.read_csv(uploaded_file)
        st.subheader("データプレビュー")
        st.dataframe(df.head())

        st.subheader("異常検知に使う列を選択（複数選択。3列まで分析します）")
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        selected_cols = st.multiselect("分析対象の列を選んでください", numeric_cols)

        if len(selected_cols) < 1:
            st.warning("1つ以上列を選んでください。")
        else:
            st.subheader("異常検知スコア比較（IsolationForest）")
            result_rows = []

            # 最大3列までの組み合わせで実施（1列、2列、3列）
            for k in range(1, min(len(selected_cols), 3) + 1):
                for comb in combinations(selected_cols, k):
                    X = df[list(comb)]
                    model = IsolationForest(contamination=0.05, random_state=0)
                    preds = model.fit_predict(X)
                    anomaly_count = sum(preds == -1)
                    result_rows.append({
                        "列の組み合わせ": ", ".join(comb),
                        "異常件数": anomaly_count
                    })

            result_df = pd.DataFrame(result_rows)
            st.dataframe(result_df)

            # グラフで最も異常件数が多かった組み合わせを表示（任意）
            top_row = result_df.sort_values("異常件数", ascending=False).iloc[0]
            top_cols = top_row["列の組み合わせ"].split(", ")

            st.subheader(f"最多異常列: {top_row['列の組み合わせ']}（{top_row['異常件数']}件）")

            timestamp_col = st.selectbox("横軸に使う列（時系列など、任意）", df.select_dtypes(include='object').columns.tolist())

            if timestamp_col in df.columns:
                model = IsolationForest(contamination=0.05, random_state=0)
                df["anomaly"] = model.fit_predict(df[top_cols])
                df["anomaly_flag"] = df["anomaly"] == -1

                fig, ax = plt.subplots()
                # 青と赤で丁寧に分けてscatterすると、PRODUCT_IDなどの文字列の場合、左側から青赤の順に書いてしまう。なので青をすべてプロットして、赤で塗りつぶす。
                # ax.scatter(df.loc[~df["anomaly_flag"], timestamp_col_order], df.loc[~df["anomaly_flag"], top_cols[0]], color="blue", label=top_cols[0], s=10, zorder=1)
                ax.scatter(df[timestamp_col], df[top_cols[0]], color="blue", label=top_cols[0], s=10, zorder=1)
                # streamlitでは日本語が豆腐になったのであきらめた。ax.scatter(df.loc[ df["anomaly_flag"], timestamp_col], df.loc[ df["anomaly_flag"], top_cols[0]], color="red", label="異常", s=20, zorder=2)
                ax.scatter(df.loc[ df["anomaly_flag"], timestamp_col], df.loc[ df["anomaly_flag"], top_cols[0]], color="red", label="Anomaly", s=20, zorder=2)

                # ✅ 横軸ラベルが長い場合：90度回転
                plt.xticks(rotation=90)

                # ✅ ラベルが多すぎる場合：x軸の間引き
                labels = df[timestamp_col].unique()  # 一意なラベル一覧
                n = len(labels)

                if n > 20:  # 間引く基準（必要に応じて調整）
                    step = max(1, n // 20)
                    ax.set_xticks(range(0, n, step))
                    ax.set_xticklabels(labels[::step], rotation=90)

                # 日本語フォント指定（OS判定つき）
                jp_font = None
                for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/meiryo.ttc"]:
                    if os.path.exists(path):
                        jp_font = fm.FontProperties(fname=path)
                        plt.rcParams["font.family"] = jp_font.get_name()
                        break
                if jp_font:
                    ax.legend(prop=jp_font)
                else:
                    ax.legend()

                st.pyplot(fig)
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
else:
    st.info("↑ 上でCSVファイルをアップロードしてください。")
