import requests
import json
import os
import time
from datetime import datetime

def tts_http_simple(api_key, text, voice_id="English_expressive_narrator", output_file=None):
    """使用 HTTP API 进行文本转语音"""
    
    url = "https://api.minimax.io/v1/t2a_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 请求数据
    data = {
        "model": "speech-2.6-hd",
        "text": text,
        "stream": False,  # 非流式，一次性获取完整音频
        "output_format": "hex",  # 返回十六进制编码的音频
        "language_boost": "auto",
        "voice_setting": {
            "voice_id": voice_id,
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    
    print("🚀 开始文本转语音...")
    print(f"📝 文本: {text}")
    print(f"🎙️ 声音: {voice_id}")
    
    # 开始计时
    start_time = time.time()
    api_start_time = None
    api_end_time = None
    save_start_time = None
    play_start_time = None
    
    try:
        # API 请求开始时间
        api_start_time = time.time()
        response = requests.post(url, headers=headers, json=data, timeout=30)
        api_end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            
            # 检查状态码
            if result.get("base_resp", {}).get("status_code") == 0:
                audio_hex = result.get("data", {}).get("audio")
                
                if audio_hex:
                    # 转换十六进制为字节
                    save_start_time = time.time()
                    audio_bytes = bytes.fromhex(audio_hex)
                    
                    # 生成文件名
                    if output_file is None:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_file = f"speech_{voice_id}_{timestamp}.mp3"
                    
                    # 保存文件
                    with open(output_file, "wb") as f:
                        f.write(audio_bytes)
                    
                    # 获取额外信息
                    extra_info = result.get("extra_info", {})
                    
                    # 播放开始时间
                    play_start_time = time.time()
                    
                    # 自动打开文件
                    try:
                        os.startfile(output_file)
                        play_end_time = time.time()
                        print("🔊 已用默认播放器打开")
                    except:
                        play_end_time = time.time()
                        print("💡 请手动打开音频文件")
                    
                    # 计算各个阶段的时间
                    total_time = time.time() - start_time
                    api_time = api_end_time - api_start_time
                    save_time = play_start_time - save_start_time
                    play_time = play_end_time - play_start_time if 'play_end_time' in locals() else 0
                    
                    print("✅ 合成成功！")
                    print(f"💾 音频保存为: {output_file}")
                    print(f"⏱️ 音频时长: {extra_info.get('audio_length', 0)} 毫秒")
                    print(f"📊 文件大小: {extra_info.get('audio_size', 0)} 字节")
                    print(f"🔊 采样率: {extra_info.get('audio_sample_rate', 0)} Hz")
                    print("\n⏰ 响应时间统计:")
                    print(f"  📡 API 请求时间: {api_time:.2f} 秒")
                    print(f"  💾 文件保存时间: {save_time:.2f} 秒")
                    print(f"  🎵 播放启动时间: {play_time:.2f} 秒")
                    print(f"  ⚡ 总响应时间: {total_time:.2f} 秒")
                    
                    return True, {
                        'total_time': total_time,
                        'api_time': api_time,
                        'save_time': save_time,
                        'play_time': play_time,
                        'audio_length': extra_info.get('audio_length', 0),
                        'file_size': extra_info.get('audio_size', 0)
                    }
                else:
                    print("❌ 未收到音频数据")
                    return False, None
            else:
                error_msg = result.get("base_resp", {}).get("status_msg", "未知错误")
                print(f"❌ API 返回错误: {error_msg}")
                return False, None
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False, None

def show_voice_options():
    """显示可用的声音选项"""
    voices = {
        # 英文声音
        "English_expressive_narrator": "英文解说员",
        "English_male_calm": "英文男声-平静", 
        "English_female_soft": "英文女声-柔和",
        "English_male_energetic": "英文男声-活力",
        "English_Graceful_Lady": "英文-优雅女士",
        "English_Insightful_Speaker": "英文-洞察力演讲者",
        
        # 中文声音
        "Chinese (Mandarin)_Lyrical_Voice": "中文-抒情声音",
        "Chinese (Mandarin)_HK_Flight_Attendant": "中文-香港空乘",
        "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85": "中文-MOSS声音1",
        "moss_audio_aaa1346a-7ce7-11f0-8e61-2e6e3c7ee85d": "中文-MOSS声音2",
        
        # 日文声音
        "Japanese_Whisper_Belle": "日文-轻声美女",
    }
    
    print("\n🎙️ 可用声音列表:")
    print("=" * 50)
    
    for voice_id, description in voices.items():
        print(f"  {voice_id:45} - {description}")

def performance_test(api_key, test_texts, voice_id="English_expressive_narrator", iterations=3):
    """性能测试：多次测试响应时间"""
    print(f"\n🎯 开始性能测试 ({iterations} 次迭代)")
    print("=" * 60)
    
    results = []
    
    for i in range(iterations):
        text = test_texts[i % len(test_texts)]  # 循环使用测试文本
        print(f"\n第 {i+1} 次测试:")
        print(f"文本: {text}")
        
        success, timing_data = tts_http_simple(api_key, text, voice_id)
        
        if success and timing_data:
            results.append(timing_data)
            print(f"✅ 第 {i+1} 次测试完成")
        else:
            print(f"❌ 第 {i+1} 次测试失败")
        
        # 每次测试之间等待一下
        if i < iterations - 1:
            print("⏳ 等待 2 秒后进行下一次测试...")
            time.sleep(2)
    
    # 统计结果
    if results:
        print(f"\n📊 性能测试结果 ({len(results)} 次成功测试):")
        print("=" * 60)
        
        avg_total = sum(r['total_time'] for r in results) / len(results)
        avg_api = sum(r['api_time'] for r in results) / len(results)
        avg_save = sum(r['save_time'] for r in results) / len(results)
        avg_play = sum(r['play_time'] for r in results) / len(results)
        
        print(f"平均总响应时间: {avg_total:.2f} 秒")
        print(f"平均 API 请求时间: {avg_api:.2f} 秒")
        print(f"平均文件保存时间: {avg_save:.2f} 秒")
        print(f"平均播放启动时间: {avg_play:.2f} 秒")
        
        # 显示每次测试的详细结果
        print(f"\n📈 详细结果:")
        for i, result in enumerate(results, 1):
            print(f"  测试 {i}: 总时间={result['total_time']:.2f}s, "
                  f"API={result['api_time']:.2f}s, "
                  f"保存={result['save_time']:.2f}s, "
                  f"播放={result['play_time']:.2f}s")

def main():
    """主函数"""
    API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJTZWFuIExpdSIsIlVzZXJOYW1lIjoiU2VhbiBMaXUiLCJBY2NvdW50IjoiIiwiU3ViamVjdElEIjoiMTk4NDY4MjY3OTg4NjQyMjg5NiIsIlBob25lIjoiIiwiR3JvdXBJRCI6IjE5ODQ2ODI2Nzk4ODIyMjQ0OTYiLCJQYWdlTmFtZSI6IiIsIk1haWwiOiJzZWFubHh4MjU2QGdtYWlsLmNvbSIsIkNyZWF0ZVRpbWUiOiIyMDI1LTExLTE2IDA4OjM0OjM4IiwiVG9rZW5UeXBlIjoxLCJpc3MiOiJtaW5pbWF4In0.lVD6EgYt8cNcz9wnU8LZ18i1_DA8Rp-FrgzcLd1Fki5a0HHrPc7OjvV5655auTGkVY8e9fT5Ni6MOy5tHw6UpudjdX-JxmMO-EJlPk8O2YDx6fQz8permkE4pF-jHqgy8BdZdA5WrH_wZ0E4PGVTki3yhxutUeuO1BFIkt9FBlDIFXgtF0fvRbozMvgJ7uWEMGbnzNrKI7ovDHY7JHxwAbLsG1R6DvLdYc0v7WQtUC7iAMHxgKOgBTw2ppyD1DILLeCDJo9QWTnpNLh-AuFzsiFZD1QByvQrRWON-4eYbWgBa8ERCB3_k5MkiMEE_ZeJrfh9KcVE1vCYshi7hNryqA"
    
    if not API_KEY or API_KEY == "你的_MiniMax_API_Key":
        print("❌ 请先在代码中设置你的 MiniMax API Key")
        return
    
    print("🎵 MiniMax HTTP TTS 系统 (带响应时间测试)")
    print("=" * 50)
    
    # 默认声音
    current_voice = "English_expressive_narrator"
    
    # 测试文本
    test_texts = [
        "Hello, this is a test of MiniMax text to speech service.",
        "The quick brown fox jumps over the lazy dog.",
        "Technology should improve our lives and make things easier.",
        "语音合成技术正在快速发展，为人们提供更好的服务。"
    ]
    
    while True:
        print(f"\n当前声音: {current_voice}")
        print("\n选项:")
        print("1. 输入文本合成语音 (单次测试)")
        print("2. 性能测试 (多次测试响应时间)")
        print("3. 选择声音")
        print("4. 显示所有声音")
        print("5. 退出")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == "1":
            text = input("请输入要合成的文本: ").strip()
            if text:
                success, timing_data = tts_http_simple(API_KEY, text, current_voice)
                if success:
                    print("✅ 合成完成")
                else:
                    print("❌ 合成失败")
        
        elif choice == "2":
            iterations = input("请输入测试次数 (默认 3): ").strip()
            try:
                iterations = int(iterations) if iterations else 3
            except:
                iterations = 3
            performance_test(API_KEY, test_texts, current_voice, iterations)
        
        elif choice == "3":
            show_voice_options()
            new_voice = input("\n请输入声音ID: ").strip()
            if new_voice:
                current_voice = new_voice
                print(f"✅ 声音已切换为: {current_voice}")
        
        elif choice == "4":
            show_voice_options()
        
        elif choice == "5" or choice.lower() in ['quit', '退出']:
            print("👋 再见！")
            break
        
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()