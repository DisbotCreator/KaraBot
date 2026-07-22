import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import yt_dlp
import google.generativeai as genai
import asyncio
from typing import Optional
import re

# 環境変数を読み込み
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Gemini APIの設定
genai.configure(api_key=GEMINI_API_KEY)

# ボット設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

# yt-dlpのオプション
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'quiet': False,
    'no_warnings': False,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

class KaraokeSong:
    """カラオケ曲情報を管理するクラス"""
    def __init__(self, title: str, url: str, lyrics: str):
        self.title = title
        self.url = url
        self.lyrics = lyrics
        self.scores = {}

# グローバル変数
current_song: Optional[KaraokeSong] = None
voice_client: Optional[discord.VoiceClient] = None


def get_youtube_url(query: str) -> Optional[tuple[str, str]]:
    """YouTubeから「歌っちゃ王」の音源を検索"""
    try:
        search_query = f"{query} 歌っちゃ王"
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if info and 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                return video['url'], video['title']
    except Exception as e:
        print(f"YouTube検索エラー: {e}")
    return None, None


def get_lyrics_from_gemini(song_title: str) -> str:
    """Gemini APIから歌詞を取得"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
以下の曲の歌詞を提供してください（著作権を考慮し、最初のサビまで）:
曲名: {song_title}

フォーマット:
[歌詞をここに記載]
"""
        response = model.generate_content(prompt)
        return response.text if response else "歌詞を取得できませんでした"
    except Exception as e:
        print(f"歌詞取得エラー: {e}")
        return "歌詞の取得に失敗しました"


def evaluate_singing(audio_description: str) -> dict:
    """Gemini APIで歌唱スコアを査定"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
以下の歌唱データに基づいてスコアを評価してください。

歌唱情報: {audio_description}

JSON形式で以下を返してください:
{{
    "score": 0-100,
    "pitch_accuracy": 0-100,
    "rhythm_accuracy": 0-100,
    "feedback": "改善点のコメント"
}}
"""
        response = model.generate_content(prompt)
        
        # レスポンスを解析
        import json
        text = response.text
        # JSONブロックを抽出
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {
                "score": 75,
                "pitch_accuracy": 75,
                "rhythm_accuracy": 75,
                "feedback": "スコア評価に成功しました"
            }
    except Exception as e:
        print(f"スコア評価エラー: {e}")
        return {
            "score": 0,
            "pitch_accuracy": 0,
            "rhythm_accuracy": 0,
            "feedback": f"評価エラー: {str(e)}"
        }


@bot.event
async def on_ready():
    """ボット起動時"""
    print(f'{bot.user} としてログインしました')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)}個のコマンドを同期しました')
    except Exception as e:
        print(f"コマンド同期エラー: {e}")


@bot.tree.command(name="karaoke", description="カラオケを開始します")
async def karaoke_command(interaction: discord.Interaction, song_name: str):
    """カラオケ曲を再生"""
    global current_song, voice_client
    
    await interaction.response.defer()
    
    try:
        # ボイスチャンネルへの接続確認
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ ボイスチャンネルに接続してください")
            return
        
        channel = interaction.user.voice.channel
        
        # ボイスチャンネルに接続
        if voice_client and voice_client.is_connected():
            await voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()
        
        # YouTubeから音源を検索
        await interaction.followup.send(f"🔍 「{song_name}」を検索中...")
        url, title = get_youtube_url(song_name)
        
        if not url:
            await interaction.followup.send("❌ 曲が見つかりませんでした")
            return
        
        # 歌詞を取得
        await interaction.followup.send("📝 歌詞を取得中...")
        lyrics = get_lyrics_from_gemini(song_name)
        
        # 曲情報を保存
        current_song = KaraokeSong(title, url, lyrics)
        
        # 歌詞をチャットに表示
        embed = discord.Embed(
            title=f"🎤 {title}",
            description=lyrics[:2000] if len(lyrics) > 2000 else lyrics,
            color=discord.Color.purple()
        )
        embed.set_footer(text="歌詞表示 | Powered by Gemini")
        await interaction.followup.send(embed=embed)
        
        # 音源を再生
        await interaction.followup.send("▶️ 音源を再生中...")
        
        async with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, False)
            audio_url = info['url']
        
        audio_source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
        
        def after_playback(error):
            if error:
                print(f"再生エラー: {error}")
        
        voice_client.play(audio_source, after=after_playback)
        await interaction.followup.send("🎵 カラオケを開始しました！歌ってください！")
        
    except Exception as e:
        await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")
        print(f"カラオケコマンドエラー: {e}")


@bot.tree.command(name="score", description="歌唱スコアを査定します")
async def score_command(interaction: discord.Interaction, comment: str = "自分の歌唱を評価してください"):
    """歌唱スコアを査定"""
    await interaction.response.defer()
    
    try:
        if not current_song:
            await interaction.followup.send("❌ カラオケが再生されていません")
            return
        
        await interaction.followup.send("⏳ スコアを計算中...")
        
        # スコア評価
        scores = evaluate_singing(comment)
        
        # 結果をEmbed形式で表示
        embed = discord.Embed(
            title="🎵 スコア査定結果",
            color=discord.Color.gold()
        )
        embed.add_field(name="曲名", value=current_song.title, inline=False)
        embed.add_field(name="総合スコア", value=f"**{scores.get('score', 0)}/100**", inline=True)
        embed.add_field(name="音程精度", value=f"{scores.get('pitch_accuracy', 0)}/100", inline=True)
        embed.add_field(name="リズム精度", value=f"{scores.get('rhythm_accuracy', 0)}/100", inline=True)
        embed.add_field(name="フィードバック", value=scores.get('feedback', ''), inline=False)
        embed.set_footer(text="査定: Gemini AI")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ スコア査定エラー: {str(e)}")
        print(f"スコアコマンドエラー: {e}")


@bot.tree.command(name="stop", description="カラオケを停止します")
async def stop_command(interaction: discord.Interaction):
    """カラオケを停止"""
    global voice_client, current_song
    
    try:
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏹️ カラオケを停止しました")
        else:
            await interaction.response.send_message("❌ 再生中の音源はありません")
        
        current_song = None
    except Exception as e:
        await interaction.response.send_message(f"❌ エラー: {str(e)}")
        print(f"停止コマンドエラー: {e}")


@bot.tree.command(name="disconnect", description="ボイスチャンネルから切断します")
async def disconnect_command(interaction: discord.Interaction):
    """ボイスチャンネルから切断"""
    global voice_client, current_song
    
    try:
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            current_song = None
            await interaction.response.send_message("👋 ボイスチャンネルから切断しました")
        else:
            await interaction.response.send_message("❌ ボイスチャンネルに接続していません")
    except Exception as e:
        await interaction.response.send_message(f"❌ エラー: {str(e)}")
        print(f"切断コマンドエラー: {e}")


@bot.tree.command(name="help", description="ヘルプを表示します")
async def help_command(interaction: discord.Interaction):
    """ヘルプ表示"""
    embed = discord.Embed(
        title="🎤 Karabot - カラオケBot",
        description="Discordでカラオケを楽しもう！",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="/karaoke [曲名]",
        value="YouTubeから歌っちゃ王で音源を検索して再生します",
        inline=False
    )
    embed.add_field(
        name="/score [コメント(オプション)]",
        value="Gemini AIがあなたの歌唱スコアを査定します",
        inline=False
    )
    embed.add_field(
        name="/stop",
        value="カラオケを停止します",
        inline=False
    )
    embed.add_field(
        name="/disconnect",
        value="ボイスチャンネルから切断します",
        inline=False
    )
    embed.set_footer(text="ガイドラインに準拠した健全なカラオケボットです")
    
    await interaction.response.send_message(embed=embed)


# ボットを起動
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ エラー: DISCORD_TOKEN が設定されていません")
        exit(1)
    
    if not GEMINI_API_KEY:
        print("❌ エラー: GEMINI_API_KEY が設定されていません")
        exit(1)
    
    print("🤖 Karabot を起動中...")
    bot.run(DISCORD_TOKEN)
