def PDF_get_text_content(file = "C:/hello.pdf"):
	"""
	input: pdf file
	return: dict (json)
	objective: 
		- Compatibility: Supporting  3 OS Platforms
		- Compatibility: Supporting  3 Web Engines
		- Mixed-Language Documents (确保打得开)
		- try a big pdf 200MB (确保打得开)
		- Open-Source License Compliance

	todo: research different libraries 

	"""
	json = {"1":"hello world"}
	return json

def json_to_transcript(json={"1":"hello world"}, user_preference=None):
	"""
	input:
	return:
	objectives:
		- Intelligent Element Skipping
		- Context-Aware Semantics
		- User-Defined Pronunciation
		- Custom Skipping Rules
		- Logical Playback Control: figure out how to segment text into sentences


	=======================
	processing:
	- llm stuff
	- rule-based

	most complicated. can be broken down into sub functions
	"""
	s = json_to_string(json) 
	transcript = string_to_transcript(s)
	transcript = "hello world" 
	return transcript

def vocalizer(transcript:str = "hello world", tone=None, speed=None):
	"""
	input: transcript (可能有多种语言)(不同音量和语气)
	return: 读出来
	objective: 
		- Multi-language: 
		- Playback Settings: voice and speech control
	"""
	pass 


def UI(whatever):
	"""
	objectives:
		- Logical Playback Control (allow user to select sentences)
		- Playback Settings: voice and speech control
		- Adaptive UI Display
	"""
	pass


"""
0. define samele text that VIVID need to read correct. (basic tests, challenging tests, bonus tests)
1. select PDF_get_text_content: research 4 options
2. select vocalizer: research 4 options
3. json_to_transcript 
3. UI
"""