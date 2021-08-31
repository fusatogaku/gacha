# ガチャのプログラム。
データベースからデータを取得し、単発・天井・保証・10連ガチャを引くことができるプログラム。
※データベースは未実装。変数で作成。

## 資料
https://qiita.com/41semicolon/items/9d4d200c14b09cb28fd9

## 使い方
python3 gacha.py option

--option
    normal: 単発ガチャを実行。
    ceil : 天井対応のガチャを実行。
    rescue : 保証ガチャ(10連とかで★4確定 みたいな)を実行。
    ten : 10連ガチャ(保証付き)を実行。
