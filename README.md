# ASTRO BODY TYPE REPORT - 占星医学体質分析システム

## 概要
伝統的な占星術と医学的体質論を組み合わせた、パーソナライズされた健康レポートを生成するWebアプリケーションです。織田剛先生の16アーキタイプ理論に基づいて、個人の出生データから包括的な体質分析を行います。

## 特徴
- 🌟 **Classic & Gorgeous デザイン**: 金色(#c9a961)とネイビー(#0f0f14)を基調とした高級感のあるデザイン
- 📊 **3段階のレポート構造**: 入力画面 → 要約レポート(2000文字) → 詳細レポート(12,000文字)
- 🎯 **16アーキタイプ分析**: 太陽と月の配置による性格タイプ分類
- 🔮 **サビアンシンボル**: 天体の正確な度数による深い洞察
- 🖨️ **印刷最適化**: プロフェッショナルな表紙とページ番号付きPDF出力
- 📱 **レスポンシブデザイン**: モバイル・タブレット・デスクトップ対応

## 技術スタック
- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with CSS Variables
- **Server**: Gunicorn (Production)
- **Deployment**: Railway

## ローカル開発

### 必要要件
- Python 3.11+
- pip

### セットアップ
```bash
# リポジトリをクローン
git clone https://github.com/francedirectjp-art/astro-medical-system-s.git
cd astro-medical-system-s

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
python app.py
```

アプリケーションは http://localhost:5000 で利用可能になります。

## Railway へのデプロイ

1. [Railway](https://railway.app/) でアカウントを作成
2. 新しいプロジェクトを作成
3. GitHubリポジトリと連携
4. 自動的にデプロイが開始されます

### 環境変数
Railway で以下の環境変数が自動設定されます：
- `PORT`: アプリケーションのポート番号

## プロジェクト構造
```
├── app.py                 # Flask アプリケーションメインファイル
├── requirements.txt       # Python依存関係
├── Procfile              # Heroku/Railway用プロセスファイル
├── railway.json          # Railway設定
├── runtime.txt           # Pythonバージョン指定
├── static/
│   ├── css/
│   │   ├── style_unified.css           # 統一デザインシステム
│   │   ├── result_unified.css          # 結果ページスタイル
│   │   └── detailed_report_unified.css # 詳細レポートスタイル
│   └── js/
│       └── main.js       # JavaScriptファイル
└── templates/
    ├── input.html                      # 入力フォーム
    ├── result_summary_enhanced.html    # 要約レポート
    └── detailed_report_complete.html   # 詳細レポート
```

## 機能詳細

### 1. 入力画面
- 名前、生年月日、出生時刻、出生地を入力
- JST（日本標準時）対応
- わかりやすいフォームデザイン

### 2. 要約レポート（2000文字）
- 16アーキタイプの特定と説明
- 7つの主要天体の配置
- 元素バランス分析
- 体質の特徴と健康アドバイス

### 3. 詳細レポート（12,000文字以上）
- 第1章: アーキタイプの深層分析
- 第2章: 7つの惑星が示す資質
- 第3章: 健康管理のポイント
- 第4章: 人間関係とコミュニケーション
- 第5章: 自己実現への道

## ライセンス
© 2024 ASTRO-MEDICAL SYSTEM. All rights reserved.

## 監修
織田剛

## 開発者
Created with ❤️ for personalized astrological medical analysis.