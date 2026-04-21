import json

# 读取文件（路径与你的文件一致）
file_path = "uuyoupin_hotrank/text.json"
try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 初始化总和与计数
    total = 0
    valid_count = 0
    
    # 遍历每个资产项，提取并累加AssetMergeCount
    for idx, item in enumerate(data, 1):
        if "AssetMergeCount" in item:
            val = item["AssetMergeCount"]
            total += val
            valid_count += 1
            print(f"第{idx}项（SteamAssetId: {item.get('SteamAssetId', '未知')}）: {val}")
    
    # 输出结果
    print(f"\n有效AssetMergeCount项数：{valid_count}")
    print(f"AssetMergeCount值总和：{total}")

except FileNotFoundError:
    print(f"错误：未找到文件 {file_path}")
except json.JSONDecodeError:
    print("错误：文件格式不是有效的JSON（可能裁剪导致格式不完整）")
except Exception as e:
    print(f"未知错误：{e}")
