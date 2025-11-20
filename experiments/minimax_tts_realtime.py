import os
import json
import asyncio
import aiohttp
import ssl
import pygame
import io
import tempfile

# 初始化 pygame mixer
pygame.mixer.init()

# 配置参数
model = "speech-2.6-hd"
file_format = "mp3"

class PygameAudioPlayer:
    def __init__(self):
        pygame.mixer.init()
    
    def play_audio(self, audio_data):
        """使用 pygame 播放 MP3 音频"""
        try:
            # 创建内存文件对象
            audio_file = io.BytesIO(audio_data)
            
            # 加载并播放音频
            pygame.mixer.music.load(audio_file, "mp3")
            pygame.mixer.music.play()
            
            print("🔊 开始播放音频...")
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
            print("✅ 播放完成")
            return True
            
        except Exception as e:
            print(f"❌ 播放失败: {e}")
            return False

async def synthesize_and_play_realtime(api_key, text):
    """实时合成并播放语音"""
    
    url = "wss://api.minimax.io/ws/v1/t2a_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "MiniMax-TTS-Client/1.0"
    }
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    audio_player = PygameAudioPlayer()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                url, 
                headers=headers,
                ssl=ssl_context,
                heartbeat=60,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as ws:
                
                print("✅ WebSocket 连接成功")
                print(f"🎯 开始合成: {text}")
                
                # 等待连接确认
                connected_msg = await ws.receive()
                if connected_msg.type == aiohttp.WSMsgType.TEXT:
                    connected_data = json.loads(connected_msg.data)
                    if connected_data.get("event") == "connected_success":
                        print("✅ 服务器连接确认")
                    else:
                        print(f"❌ 连接失败: {connected_data}")
                        return False
                
                # 发送任务开始请求
                start_msg = {
                    "event": "task_start",
                    "model": model,
                    "voice_setting": {
                        "voice_id": "English_expressive_narrator",
                        "speed": 1.0,
                        "vol": 1.0,
                        "pitch": 0
                    },
                    "audio_setting": {
                        "format": file_format,
                        "channel": 1,
                        "sample_rate": 24000
                    }
                }
                
                await ws.send_str(json.dumps(start_msg))
                print("📤 发送任务开始请求...")
                
                # 接收任务开始响应
                start_response = await ws.receive()
                if start_response.type == aiohttp.WSMsgType.TEXT:
                    start_data = json.loads(start_response.data)
                    if start_data.get("event") == "task_started":
                        print("✅ 任务启动成功")
                    else:
                        print(f"❌ 任务启动失败: {start_data}")
                        return False
                
                # 发送文本进行合成
                continue_msg = {
                    "event": "task_continue",
                    "text": text
                }
                
                await ws.send_str(json.dumps(continue_msg))
                print("📤 发送文本进行合成...")
                
                # 接收音频数据
                complete_audio = b""
                audio_chunks = []  # 存储所有音频片段
                
                print("🎵 开始接收音频...")
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        response = json.loads(msg.data)
                        
                        if "data" in response and "audio" in response["data"]:
                            audio_hex = response["data"]["audio"]
                            if audio_hex and audio_hex.strip():
                                try:
                                    audio_bytes = bytes.fromhex(audio_hex)
                                    complete_audio += audio_bytes
                                    audio_chunks.append(audio_bytes)
                                    
                                except ValueError as e:
                                    print(f"⚠️ 音频数据格式错误: {e}")
                            
                            if response.get("is_final"):
                                print("✅ 音频合成完成")
                                break
                                
                        elif response.get("event") == "error":
                            print(f"❌ 服务器返回错误: {response}")
                            return False
                
                # 播放完整的音频
                if complete_audio:
                    print("🎵 开始播放完整音频...")
                    success = audio_player.play_audio(complete_audio)
                    
                    # 保存完整音频文件
                    timestamp = asyncio.get_event_loop().time()
                    filename = f"speech_{int(timestamp)}.mp3"
                    with open(filename, "wb") as f:
                        f.write(complete_audio)
                    print(f"💾 音频已保存: {filename}")
                    
                    return success
                
                return False
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """主函数"""
    API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJTZWFuIExpdSIsIlVzZXJOYW1lIjoiU2VhbiBMaXUiLCJBY2NvdW50IjoiIiwiU3ViamVjdElEIjoiMTk4NDY4MjY3OTg4NjQyMjg5NiIsIlBob25lIjoiIiwiR3JvdXBJRCI6IjE5ODQ2ODI2Nzk4ODIyMjQ0OTYiLCJQYWdlTmFtZSI6IiIsIk1haWwiOiJzZWFubHh4MjU2QGdtYWlsLmNvbSIsIkNyZWF0ZVRpbWUiOiIyMDI1LTExLTE2IDA4OjM0OjM4IiwiVG9rZW5UeXBlIjoxLCJpc3MiOiJtaW5pbWF4In0.lVD6EgYt8cNcz9wnU8LZ18i1_DA8Rp-FrgzcLd1Fki5a0HHrPc7OjvV5655auTGkVY8e9fT5Ni6MOy5tHw6UpudjdX-JxmMO-EJlPk8O2YDx6fQz8permkE4pF-jHqgy8BdZdA5WrH_wZ0E4PGVTki3yhxutUeuO1BFIkt9FBlDIFXgtF0fvRbozMvgJ7uWEMGbnzNrKI7ovDHY7JHxwAbLsG1R6DvLdYc0v7WQtUC7iAMHxgKOgBTw2ppyD1DILLeCDJo9QWTnpNLh-AuFzsiFZD1QByvQrRWON-4eYbWgBa8ERCB3_k5MkiMEE_ZeJrfh9KcVE1vCYshi7hNryqA"  # 🔴 替换为你的实际 API Key
    
    if not API_KEY or API_KEY == "你的_MiniMax_API_Key":
        print("❌ 请先在代码中设置你的 MiniMax API Key")
        return
    
    print("🎤 MiniMax 实时语音合成系统 (pygame 版本)")
    print("=" * 50)
    print("输入 'quit' 或 '退出' 来结束程序")
    print("=" * 50)
    
    while True:
        try:
            text = input("\n💬 请输入要合成的文本: ").strip()
            
            if text.lower() in ['quit', '退出', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if not text:
                print("⚠️ 请输入有效文本")
                continue
            
            if len(text) > 1000:
                print("⚠️ 文本过长，请控制在1000字符以内")
                continue
            
            print(f"🎯 开始合成: {text}")
            
            # 运行异步函数
            success = asyncio.run(synthesize_and_play_realtime(API_KEY, text))
            
            if success:
                print("✅ 合成播放完成")
            else:
                print("❌ 合成播放失败")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断程序")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()