import requests
import json

url = "https://open.bigmodel.cn/api/paas/v4/audio/speech"

payload = json.dumps({
   "model": "glm-tts",
   "input": "- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制- **消息发送流程（异步）** - 使用 Cele.",
   "voice": "tongtong",
   "response_format": "wav"
})
headers = {
   'Authorization': 'Bearer 0be0079595174a779dadc1211d1dfdc1.65Ee9RMPq6gxnFdT',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)