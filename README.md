# 異常検知デモアプリ

このアプリは、CSVファイルをアップロードして、`IsolationForest` による異常検知を行い、異常スコアの比較や可視化を行うStreamlitアプリです。

## 使用方法

1. [Streamlit Cloud](https://share.streamlit.io/) またはローカル環境で起動
2. CSVファイルをアップロード
3. 数値列を1〜3列選択して異常検知を実行
4. 最も異常が多い列組み合わせの可視化を確認

## 起動方法（ローカル）

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
streamlit run app.py
