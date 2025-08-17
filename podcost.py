import http.client
import json
import ssl
import re
import requests
import os
from datetime import datetime

# ssl._create_default_https_context = ssl._create_unverified_context


headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
    "Authorization": "Bearer f2d4b9650c13355fc8286ac3fc34bf6e:NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh",
}

data = {
    "flow_id": "7362488342038495234",
    "uid": "123",
    "parameters": {"AGENT_USER_INPUT": "能帮我推荐几本，最近热销的中文文学类好书吗"},
    "ext": {"bot_id": "adjfidjf", "caller": "workflow"},
    "stream": False,
}
payload = json.dumps(data)

try:
    conn = http.client.HTTPSConnection("xingchen-api.xf-yun.com", timeout=120)
    conn.request(
        "POST", "/workflow/v1/chat/completions", payload, headers, encode_chunked=True
    )
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    conn.close()

    # Parse the JSON response
    response_json = json.loads(response_data)
    html_content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")

    if not html_content:
        print("Error: Could not find audio content in the API response.")
        print("Full response:", response_data)
        exit()

    # Extract the audio URL from the HTML content
    match = re.search(r'src="([^"]+)"', html_content)
    if not match:
        print("Error: Could not find audio URL in the HTML content.")
        print("HTML content:", html_content)
        exit()

    audio_url = match.group(1)

    print(f"Found audio URL: {audio_url}")

    # Download the audio file
    print("Downloading audio...")
    audio_response = requests.get(audio_url)
    audio_response.raise_for_status()  # Raise an exception for bad status codes

    # Create directory if it doesn't exist
    output_dir = "podcast_audio"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the audio file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"podcast_{timestamp}.mp3"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, 'wb') as f:
        f.write(audio_response.content)

    print(f"Successfully saved audio to: {os.path.abspath(file_path)}")

except Exception as e:
    print(f"An error occurred: {e}")
