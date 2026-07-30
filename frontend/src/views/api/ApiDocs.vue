<template>
  <div class="prose max-w-none">
    <h1>API 调用文档</h1>
    <h2>接口地址</h2>
    <p><code>POST /v1/chat/completions</code></p>
    <h2>鉴权</h2>
    <p>在 Header 中传入 API Key：<code>Authorization: Bearer YOUR_API_KEY</code></p>
    <h2>cURL 示例</h2>
    <pre class="bg-gray-900 text-gray-100 p-4 rounded"><code>curl -X POST http://your-server/v1/chat/completions \
  -H "Authorization: Bearer sk-138****8000-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"stream":true}'</code></pre>
    <h2>Python 示例</h2>
    <pre class="bg-gray-900 text-gray-100 p-4 rounded"><code>import requests

url = "http://your-server/v1/chat/completions"
headers = {"Authorization": "Bearer sk-xxx", "Content-Type": "application/json"}
data = {"messages": [{"role": "user", "content": "Hello"}], "stream": True}

with requests.post(url, headers=headers, json=data, stream=True) as r:
    for line in r.iter_lines():
        if line:
            print(line.decode())</code></pre>
    <h2>Node.js 示例</h2>
    <pre class="bg-gray-900 text-gray-100 p-4 rounded"><code>const response = await fetch('http://your-server/v1/chat/completions', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer sk-xxx', 'Content-Type': 'application/json' },
  body: JSON.stringify({ messages: [{ role: 'user', content: 'Hello' }], stream: true })
})

const reader = response.body.getReader()
const decoder = new TextDecoder()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  console.log(decoder.decode(value))
}</code></pre>
  </div>
</template>
