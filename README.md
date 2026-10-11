## **※現在Pythonのみの対応となっております。他の言語に関しましては今後実装予定です。**
# 目次
1. 概要
2. 背景
3. 主な機能
4. セットアップ手順
5. 使い方
6. ディレクトリ構成
7. データ構造
8. 使用技術
9. 終わりに
<br><br><br>
# ① 概要
Pythonで作成した自動テストプログラムです。
拡張機能[「AtCoder Sample Copy」](https://chromewebstore.google.com/detail/bjankhpbegjhlkihejjacecbnhbmhhef?utm_source=item-share-cb)と連携することで、AtCoderのサンプル入出力を利用したテストを効率化できます。
<br><br><br>
# ② 背景
AtCoderで問題を解く際、サンプル入出力をローカル環境でテストするために、問題ページから入力例・出力例を一つずつコピーする必要がありました。<br>
拡張機能[「AtCoder Sample Copy」](https://chromewebstore.google.com/detail/bjankhpbegjhlkihejjacecbnhbmhhef?utm_source=item-share-cb)と組み合わせることで、AtCoderのサンプルテストをより効率的に実行できるようにすることを目指しています。
<br><br><br>
# ③ 主な機能
- 拡張機能[「AtCoder Sample Copy」](https://chromewebstore.google.com/detail/bjankhpbegjhlkihejjacecbnhbmhhef?utm_source=item-share-cb)に対応したサンプル入出力の自動テスト
- 実行結果の判定（AC、WA、RE、TLE）
- コマンドラインによるファイル・制限時間などを変更可能
<br><br><br>
# ④ セットアップ手順
<video src="https://github.com/user-attachments/assets/381e889b-cf3e-42b6-8e02-e972305d50e7" controls width="100%">
</video>

[Chrome 拡張機能](https://chromewebstore.google.com/detail/atcoder-sample-copy/bjankhpbegjhlkihejjacecbnhbmhhef?pli=1)<br>
[自動テストプログラム](https://github.com/hikaru373/atcoder-python-auto-test/releases/tag/v1.0.0)
<br><br><br>
# ⑤ 使い方
2026年10月中に説明動画の完成を予定しています。<br>
<br>
![使い方画像](https://github.com/user-attachments/assets/0f0e34a9-8d03-489f-8e90-073cfef12e14)
※画像は生成AIを使用して作成しています。
<br><br><br>
# ⑥ ディレクトリ構成
<pre>
atcoder-python-auto-test
├── .gitignore
├── LICENSE
├── README.md
├── auto-test.py
└── .github
     ├── PULL_REQUEST_TEMPLATE.md
     └── ISSUE_TEMPLATE
          ├── bug.yml
          ├── documentation.yml
          └── enhancement.yml

</pre>
<br><br><br>
# ⑦ データ構造
入力例と出力例を1組ずつ順番に記述し、複数のサンプルにも対応しています。<br>
```
入力例1

出力例1

入力例2

出力例2
...
```
<br><br><br>
# ⑧ 使用技術
- **フロントエンド**：なし
- **バックエンド**：Python
- **データベース**：なし
- **インフラ**：ローカル環境
- **バージョン管理**：Git / GitHub
- **動作確認環境**：macOS 15.6

### 選定理由
- **Python**：AtCoderで使用する言語として普段から利用しており、実行処理や入出力の比較を簡潔に実装できるため。

<br><br><br>
# ⑨ 終わりに
最後までご覧いただき、ありがとうございました。<br>
バグ報告や機能要望などがございましたら、以下よりお気軽にご連絡ください。
<br>
- [お問い合わせフォーム](https://forms.gle/deKPjNbf3YAGCCjE7)
- [GitHub Issues](https://github.com/hikaru373/atcoder-python-auto-test/issues)
- [メール](mailto:star3.14wars.sh@gmail.com)
