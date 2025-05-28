{
  "description": "Generate a new text file that incorporates the file content from the provided content.",
  "content": "This text is generated to be placed in the file.  The file contains the requested template for voice + text + anyhting L.py."
}
from loguru import logger
from fastrtc import ReplyOnPause, Stream, get_stt_model, get_tts_model


# === CONFIGURATION ===
API_BASE_URL = "http://localhost:3001/api/v1"  # Usally the default host that it uses
API_KEY = "<your api here>"  # API keys here
WORKSPACE_SLUG = "<the name of the workspace you got on our anythingLLM platfom> "  # Set this to your actual workspace slug

# COLORS for FUN :D 

GREEN = '\033[92m'
LIGHTBLUE = '\033[94m'
RESET_COLOR = '\033[0m'
PINK = '\033[95m'

# === LOGGING SETUP ===
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

def chat_with_api(message):
    url = f"{API_BASE_URL}/workspace/{WORKSPACE_SLUG}/chat"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"message": message, "type": "chat | query"}
    response = requests.post(url, headers=headers, json=data)

    try:
        response = requests.post(url, headers=headers, json=data)
        logger.debug(f"Raw API response text: {response.text!r}")
        response.raise_for_status()
        response_json = response.json()
        logger.debug(f"API response: {response_json}")
        if response_json.get("type") == "abort":
            err = response_json.get("error", "Unknown error")
            return f"[Error] {err}"
        return response_json.get("textResponse") or "[No response]"
    except Exception as e:
        logger.error(f"API Error: {e}")
        return f"[API Error] {e}"

stt_model = get_stt_model()  # moonshine/base
tts_model = get_tts_model()  # kokoro

def echo(audio):
    transcript = stt_model.stt(audio)
    logger.debug(f"🎤 Transcript: {transcript}")
    response_text = chat_with_api(transcript)
    for audio_chunk in tts_model.stream_tts_sync(response_text):
        yield audio_chunk

def create_stream():
    return Stream(ReplyOnPause(echo), modality="audio", mode="send-receive")

def text_chat_mode():
    print(PINK +"\nEntering text chat mode (type 'bye' to quit)" + RESET_COLOR)
  
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        response = chat_with_api(user_input)
        print(f"\nAssistant: {response}")

def main():
    while True:
        mode = input(PINK+"Choose mode: 'text' for text chat, 'voice' for voice chat, 'bye' for exit: "+ RESET_COLOR).lower()
        if mode == 'text':
            text_chat_mode()
        elif mode == 'voice':
            print("\nEntering voice chat mode...")
            stream = create_stream()
            stream.ui.launch()
        elif mode == 'q':
            break
        else:
           print(GREEN + "Invalid mode. Please choose 'text', 'voice', or 'bye'." + RESET_COLOR)
  

if __name__ == "__main__":
    main()
