import requests
import json
import os

# ==============================================
# 【1】从环境变量读取隐私配置（GitHub Secrets 安全注入）
# ==============================================
DeviceToken = os.getenv("UU_DEVICE_TOKEN")
signature = os.getenv("UU_SIGNATURE")
requesttag = os.getenv("UU_REQUESTTAG")
uk = os.getenv("UU_UK")
Authorization = os.getenv("UU_AUTH")
deviceUk = os.getenv("UU_DEVICE_UK")
SessionId = os.getenv("UU_SESSION_ID")
acw_tc = os.getenv("UU_ACW_TC")

# ==============================================
# 【2】请求配置（完全使用你提供的原生请求头）
# ==============================================
INVENTORY_HEADERS = {
    "User-Agent": "iOS/17.3.1 AppleStore com.uu898.uusteam/5.43.0 Alamofire/5.2.2",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "AppType": "3",
    "Content-Encoding": "gzip",
    "DeviceSysVersion": "17.3.1",
    "Gameid": "730",
    "package-type": "uuyp",
    "platform": "ios",
    "version": "5.43.0",
    "tracestate": "bnro=iOS/17.3.1_iOS/15E148/00000000-0000-0000-0000-000000000000",
    "api-version": "1.0",
    "Accept-Language": "en-TW;q=1.0, zh-TW;q=0.9",
    "app-version": "5.43.0",
    "currentTheme": "Dark",
    "traceparent": "00-7cdf9feda1d94a45a2f038f6ff130ee06-a43bd73e4d254d13-01",

    # 私有字段
    "DeviceToken": DeviceToken,
    "signature": signature,
    "requesttag": requesttag,
    "uk": uk,
    "Authorization": Authorization,
    "deviceUk": deviceUk
}

# 热销榜请求头
HOT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 uuyp/deviceUk=" + deviceUk + "&package-type=uuyp&uid=&uk=" + uk + "&appVersion=5.43.0&currentTheme=System&platform=iOS",
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

COOKIES = {"acw_tc": acw_tc}

# ==============================================
# 【3】API 地址
# ==============================================
INVENTORY_API = "https://api.youpin898.com/api/youpin/commodity-agg/inventory/list/pull"
HOT_API = "https://api.youpin898.com/api/youpin/bff/new/commodity/commodity/hot_list_V3_h5"

# ==============================================
# 【4】拉取库存（翻页直到 hasNext == false）
# ==============================================
def fetch_my_inventory():
    all_items = []
    page = 1
    print("📦 开始拉取库存...")

    while True:
        payload = {
            "SessionId": SessionId,
            "RefreshType": 2,
            "IsMerge": 1,
            "Version": "5.43.0",
            "CommodityName": "",
            "Platform": "ios",
            "AppType": 3,
            "AssetStatus": 0,
            "GameID": "730",
            "Tags": [],
            "PageIndex": page
        }

        try:
            resp = requests.post(
                INVENTORY_API,
                headers=INVENTORY_HEADERS,
                cookies=COOKIES,
                data=json.dumps(payload, separators=(',', ':'))
            )
            data = resp.json()
        except Exception as e:
            print(f"请求失败：{e}")
            break

        if data.get("Code") != 0:
            print(f"API 返回错误：{data}")
            break

        item_list = data.get("Data", {}).get("ItemsInfos", [])
        if not item_list:
            break

        all_items.extend(item_list)

        has_next = data.get("Data", {}).get("hasNext", False)
        if not has_next:
            break

        page += 1

    print(f"✅ 库存拉取完成：共 {len(all_items)} 件")
    with open("inventory.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    return all_items

# ==============================================
# 【5】拉取热销榜（三个有效价位）
# ==============================================
def fetch_hot_items():
    hot_list = []
    print("🔥 开始拉取热销榜...")

    price_ranges = [100, 1000, 10000]
    for price in price_ranges:
        payload = {
            "configCode": "transaction_list",
            "minMarketPrice": price,
            "queryTime": 1
        }
        try:
            resp = requests.post(HOT_API, headers=HOT_HEADERS, json=payload)
            items = resp.json().get("data", [])
            if isinstance(items, list):
                hot_list.extend(items)
        except Exception as e:
            print(f"  ⚠️ 价位 ￥{price} 请求失败：{e}")
            continue

    # 去重（按 templateName）
    unique_hot = list({item["templateName"]: item for item in hot_list}.values())
    print(f"✅ 热销榜拉取完成：共 {len(unique_hot)} 个不重复商品")
    with open("hot_list.json", "w", encoding="utf-8") as f:
        json.dump(unique_hot, f, ensure_ascii=False, indent=2)
    return unique_hot

# ==============================================
# 【6】核心匹配：库存 ShotName == 热销 templateName
# ==============================================
def match_inventory_hot(inventory, hot_list):
    inventory_names = {item.get("ShotName") for item in inventory if item.get("ShotName")}
    matched = [item for item in hot_list if item.get("templateName") in inventory_names]
    return matched


# ==============================================
# 【7】格式化输出：显示商品名和参考价格
# ==============================================
def print_matched(result):
    print("\n" + "="*60)
    print(f"🎯 匹配完成！你的库存中【在热销榜】的商品：{len(result)} 件")
    print("="*60)
    for i, item in enumerate(result, 1):
        name = item.get("templateName", "未知")
        price = item.get("price", "无价格")
        print(f"  {i}. {name}  —  参考价：{price}")
    print("="*60)

# ==============================================
# 【7】主程序入口
# ==============================================
if __name__ == "__main__":
    # 1. 拉取数据
    inventory = fetch_my_inventory()
    hot_items = fetch_hot_items()

    # 2. 匹配
    result = match_inventory_hot(inventory, hot_items)

    # 3. 输出结果
    print_matched(result)

    # 4. 保存最终结果
    output = {
        "inventory_count": len(inventory),
        "hot_count": len(hot_items),
        "match_count": len(result),
        "match_list": result
    }

    with open("match_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ 全部完成！文件已保存：")
    print("   - inventory.json      你的全部库存")
    print("   - hot_list.json       平台热销榜")
    print("   - match_result.json   匹配结果（可直接上架）")