import http.client
import json
import ssl

# ssl._create_default_https_context = ssl._create_unverified_context


headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
    "Authorization": "Bearer f2d4b9650c13355fc8286ac3fc34bf6e:NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh",
}

data = {
    "flow_id": "7362777714092728320",
    "uid": "123",
    "parameters": {"AGENT_USER_INPUT": "能帮我推荐几本好书吗"},
    "ext": {"bot_id": "adjfidjf", "caller": "workflow"},
    "stream": False,
}
payload = json.dumps(data)

conn = http.client.HTTPSConnection("xingchen-api.xf-yun.com", timeout=120)
conn.request(
    "POST", "/workflow/v1/chat/completions", payload, headers, encode_chunked=True
)
res = conn.getresponse()

if data.get("stream"):
    while chunk := res.readline():
        print(chunk.decode("utf-8"))
else:
    data = res.readline()
    print(data.decode("utf-8"))
