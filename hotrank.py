import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 uuyp/deviceUk=5HoDXVaaEygPN3wcYxfVedVHcVquYj3H47mvhOtAM6XVZRdBgdCYVc7PCwddME91L&package-type=uuyp&uid=&uk=5HoDMFDIsrtdLzGzgw5woORVqfWzGBn4V82g4H7anZQGRFM8a2efTzm2nuc6Y5F1K&appVersion=5.43.0&currentTheme=System&platform=iOS",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://hybrid.youpin898.com/",
    "appType": "3",
    "systemVersion": "17.3.1",
    "App-Source": "h5",
    "Origin": "https://hybrid.youpin898.com",
    "package-type": "uuyp",
    "platform": "ios",
    "Authorization": "",
    "Content-Type": "application/json;charset=utf-8",
    "App-Version": "5.43.0",
}

url = "https://api.youpin898.com/api/youpin/bff/new/commodity/commodity/hot_list_V3_h5"
data = json.dumps({
    "configCode": "transaction_list",
    "minMarketPrice": 100,
    "queryTime": 1
})

response = requests.post(url, headers=headers, data=data)
data1 = response.json()

with open("数据.json", "w", encoding="utf-8") as f:
    json.dump(data1, f, indent=2, ensure_ascii=False)