import os
import json
import asyncio
import aiohttp
import ssl

# 配置参数
model = "speech-2.6-hd"
file_format = "mp3"

async def synthesize_speech(api_key, text, output_file="minimax_speech.mp3"):
    """使用 MiniMax TTS API 合成语音"""
    
    url = "wss://api.minimax.io/ws/v1/t2a_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "MiniMax-TTS-Client/1.0"
    }
    
    print("🚀 开始连接 MiniMax TTS 服务...")
    print(f"📝 文本: {text}")
    
    # 创建 SSL 上下文（跳过证书验证以兼容更多环境）
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # 使用 aiohttp 创建 WebSocket 连接
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                url, 
                headers=headers,
                ssl=ssl_context,
                heartbeat=60,  # 心跳保持连接
                timeout=aiohttp.ClientTimeout(total=30)
            ) as ws:
                
                print("✅ WebSocket 连接成功")
                
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
                chunk_counter = 0
                total_audio_size = 0
                audio_data = b""
                
                print("🎯 开始接收音频数据...")
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        response = json.loads(msg.data)
                        
                        if "data" in response and "audio" in response["data"]:
                            audio_hex = response["data"]["audio"]
                            if audio_hex and audio_hex.strip():
                                try:
                                    audio_bytes = bytes.fromhex(audio_hex)
                                    audio_data += audio_bytes
                                    total_audio_size += len(audio_bytes)
                                    chunk_counter += 1
                                    print(f"📦 收到第 {chunk_counter} 个音频片段, 大小: {len(audio_bytes)} 字节")
                                except ValueError as e:
                                    print(f"⚠️ 音频数据格式错误: {e}")
                            
                            if response.get("is_final"):
                                print(f"✅ 音频合成完成: 共 {chunk_counter} 个片段, 总大小: {total_audio_size} 字节")
                                
                                # 保存音频文件
                                if audio_data:
                                    with open(output_file, "wb") as f:
                                        f.write(audio_data)
                                    print(f"💾 音频已保存到: {output_file}")
                                    print(f"📊 文件大小: {len(audio_data)} 字节")
                                    return True
                                else:
                                    print("❌ 没有收到音频数据")
                                    return False
                                    
                        elif response.get("event") == "error":
                            print(f"❌ 服务器返回错误: {response}")
                            return False
                            
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"❌ WebSocket 错误: {msg}")
                        return False
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        print("🔌 连接已关闭")
                        break
                
                # 发送任务结束
                finish_msg = {"event": "task_finish"}
                await ws.send_str(json.dumps(finish_msg))
                print("🔌 任务结束")
                
                return False
                
    except aiohttp.ClientError as e:
        print(f"❌ 客户端错误: {e}")
        return False
    except asyncio.TimeoutError:
        print("⏰ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

async def main():
    # 设置你的 API Key - 直接替换这里的字符串
    API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJTZWFuIExpdSIsIlVzZXJOYW1lIjoiU2VhbiBMaXUiLCJBY2NvdW50IjoiIiwiU3ViamVjdElEIjoiMTk4NDY4MjY3OTg4NjQyMjg5NiIsIlBob25lIjoiIiwiR3JvdXBJRCI6IjE5ODQ2ODI2Nzk4ODIyMjQ0OTYiLCJQYWdlTmFtZSI6IiIsIk1haWwiOiJzZWFubHh4MjU2QGdtYWlsLmNvbSIsIkNyZWF0ZVRpbWUiOiIyMDI1LTExLTE2IDA4OjM0OjM4IiwiVG9rZW5UeXBlIjoxLCJpc3MiOiJtaW5pbWF4In0.lVD6EgYt8cNcz9wnU8LZ18i1_DA8Rp-FrgzcLd1Fki5a0HHrPc7OjvV5655auTGkVY8e9fT5Ni6MOy5tHw6UpudjdX-JxmMO-EJlPk8O2YDx6fQz8permkE4pF-jHqgy8BdZdA5WrH_wZ0E4PGVTki3yhxutUeuO1BFIkt9FBlDIFXgtF0fvRbozMvgJ7uWEMGbnzNrKI7ovDHY7JHxwAbLsG1R6DvLdYc0v7WQtUC7iAMHxgKOgBTw2ppyD1DILLeCDJo9QWTnpNLh-AuFzsiFZD1QByvQrRWON-4eYbWgBa8ERCB3_k5MkiMEE_ZeJrfh9KcVE1vCYshi7hNryqA"  # 🔴 替换为你的实际 API Key
    
    # 要转换的文本
    TEXT = "Hello, this is a test of MiniMax text to speech service. The technology is amazing! Now I can convert text to speech easily."
    
    if not API_KEY or API_KEY == "你的_MiniMax_API_Key":
        print("❌ 请先在代码中设置你的 MiniMax API Key")
        return
    
    success = await synthesize_speech(API_KEY, TEXT, "minimax_speech.mp3")
    
    if success:
        print("🎉 TTS 服务完成！")
        print("💡 你可以在当前目录找到 'minimax_speech.mp3' 文件")
    else:
        print("❌ TTS 服务失败")

if __name__ == "__main__":
    print("🔧 开始运行 MiniMax TTS 服务 (aiohttp 版本)...")
    asyncio.run(main())