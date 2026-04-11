import requests

def validate_glm_token(api_key: str) -> bool:
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "glm-4.7",  # 用最便宜的模型，消耗最少
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1  # 限制输出，节省费用
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            print('resp ----', resp.json())
            return True
        elif resp.status_code == 401:
            print("Token 无效或已过期")
            return False
        else:
            print(f"其他错误: {resp.status_code} - {resp.json()}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

if __name__ == "__main__":
    import os

    api_key = '0be0079595174a779dadc1211d1dfdc1.65Ee9RMPq6gxnFdT'
    if not api_key:
        print("请设置 GLM_API_KEY 环境变量")
        exit(1)
    if validate_glm_token(api_key):
        print("Token 有效")
    else:
        print("Token 无效")
