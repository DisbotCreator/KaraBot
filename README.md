# 🎤 Karabot - Discordカラオケボット

DiscordでYouTubeの「歌っちゃ王」から音源を流して、カラオケを楽しめるボットです。
Gemini APIを使用して自動的に歌唱スコアを査定します。

## ✨ 機能

- **YouTube音源再生** - 「歌っちゃ王」から自動検索・再生
- **歌詞表示** - Gemini APIから取得した歌詞をチャットに表示
- **スコア査定** - Gemini AIがリアルタイムで歌唱スコアを評価
- **スラッシュコマンド** - シンプルで使いやすいコマンドUI
- **ガイドライン準拠** - 健全で安全な設計

## 📋 必要な環境

- Python 3.9以上
- Discord Bot Token
- Gemini API Key
- FFmpeg（音声処理用）

## 🚀 セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. FFmpegのインストール

**Windows:**
```bash
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 3. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、トークンを設定します：

```bash
cp .env.example .env
```

`.env` ファイルを編集：
```
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Discord Bot Tokenの取得方法
1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリック
3. Bot を追加
4. Token をコピー

#### Gemini API Keyの取得方法
1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. 「Create API Key」をクリック
3. APIキーをコピー

### 4. ボットの実行

```bash
python main.py
```

## 🎮 使用方法

### コマンド一覧

| コマンド | 説明 |
|---------|------|
| `/karaoke [曲名]` | カラオケを開始（例: `/karaoke 米津玄師 - Lemon`） |
| `/score [コメント]` | 歌唱スコアを査定 |
| `/stop` | カラオケを停止 |
| `/disconnect` | ボイスチャンネルから切断 |
| `/help` | ヘルプを表示 |

### 使用例

1. ボイスチャンネルに参加
2. `/karaoke 曲名` で曲を検索・再生
3. 歌詞がチャットに表示される
4. 歌う
5. `/score` でスコアを査定
6. 結果がチャットに表示される

## ⚙️ 設定

### 音声フォーマット
- ビットレート: 最高音質
- 形式: MP3/AAC（YouTube提供形式）

### スコア評価項目
- **総合スコア**: 0～100点
- **音程精度**: 正確さの評価
- **リズム精度**: リズムのタイミング正確さ
- **フィードバック**: 改善提案

## 📝 ガイドラインに関する注意

このボットは以下のガイドラインに準拠しています：

- ✅ 著作権を尊重し、歌詞は最初のサビまでに制限
- ✅ YouTubeの規約に準拠した音源取得
- ✅ プライバシー保護: ユーザーデータを保存しない
- ✅ 適切なレート制限: API呼び出しを制御

## 🛠️ トラブルシューティング

### FFmpegが見つからない
```
ffmpeg: command not found
```
**対策**: FFmpegをインストールして、PATHに追加してください

### Gemini API エラー
```
google.generativeai.error.APIError
```
**対策**: API Keyが正しく設定されているか確認してください

### YouTube検索エラー
```
yt_dlp.utils.DownloadError
```
**対策**: インターネット接続を確認し、VPNを使用している場合は無効化してください

## 📄 ライセンス

MIT License - 自由に使用・改変・配布できます

## 🤝 貢献

バグ報告や機能提案は Issue でお願いします！

## 🎵 楽しいカラオケライフを！

Karabot で友達と一緒にカラオケを楽しみましょう！
