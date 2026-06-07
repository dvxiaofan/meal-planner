#!/usr/bin/env python3
"""从 TheMealDB 自动匹配菜品图片

用法:
  python match_images.py             # 匹配所有无图的菜品
  python match_images.py --limit 10  # 最多匹配 10 道
  python match_images.py --dry       # 只看会匹配什么，不下载
"""
import sys
import os
import argparse
import urllib.request
import urllib.parse
import json
import re
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, init_db
from app.models.dish import Dish

# 中英对照（搜索时优先用英文，效果更好）
CN_TO_EN = {
    "番茄炒蛋": "Chinese Tomato Egg Stir Fry",
    "宫保鸡丁": "Kung Pao Chicken",
    "红烧肉": "Red Braised Pork",
    "可乐鸡翅": "Cola Chicken Wings",
    "鱼香肉丝": "Yuxiang Shredded Pork",
    "糖醋排骨": "Sweet and Sour Pork",
    "回锅肉": "Twice Cooked Pork",
    "清蒸鲈鱼": "Steamed Sea Bass",
    "水煮牛肉": "Sichuan Boiled Beef",
    "酸菜鱼": "Sauerkraut Fish",
    "地三鲜": "Di San Xian",
    "干煸四季豆": "Dry Fried Green Beans",
    "麻婆豆腐": "Mapo Tofu",
    "蒜蓉西兰花": "Garlic Broccoli",
    "虎皮青椒": "Tiger Skin Peppers",
    "酸辣土豆丝": "Hot and Sour Potato",
    "凉拌黄瓜": "Sesame Cucumber Salad",
    "皮蛋豆腐": "Century Egg Tofu",
    "番茄蛋汤": "Tomato Egg Drop Soup",
    "紫菜蛋花汤": "Seaweed Egg Drop Soup",
    "玉米排骨汤": "Corn and Pork Rib Soup",
    "冬瓜排骨汤": "Winter Melon Pork Rib Soup",
    "蛋炒饭": "Egg Fried Rice",
    "西红柿鸡蛋面": "Tomato Egg Noodle",
    "酸辣粉": "Hot and Sour Glass Noodles",
    "葱油拌面": "Scallion Oil Noodles",
    "煎饺": "Potstickers",
    "炸酱面": "Beijing Zhajiang Noodles",
    "红烧茄子": "Chinese Braised Eggplant",
    "干锅花菜": "Dry Pot Cauliflower",
    "手撕包菜": "Stir Fried Cabbage",
    "白菜豆腐汤": "Cabbage Tofu Soup",
    "阳春面": "Yang Chun Noodles",
    "扬州炒饭": "Yangzhou Fried Rice",
    "土豆炖牛肉": "Beef and Potato Stew",
    "青椒肉丝": "Green Pepper Shredded Pork",
    "蒜苗回锅肉": "Twice Cooked Pork",
    "西红柿炖牛腩": "Tomato Beef Brisket Stew",
    "蒜蓉粉丝蒸虾": "Garlic Vermicelli Shrimp",
    "辣子鸡": "Chongqing Chicken",
    "白灼虾": "Cantonese Poached Shrimp",
    "韭菜炒鸡蛋": "Chinese Chive Egg",
    "香菇青菜": "Bok Choy Mushroom Stir Fry",
    "西芹炒百合": "Stir Fried Celery Lily",
    "红烧豆腐": "Braised Tofu",
    "醋溜白菜": "Vinegar Stir Fried Cabbage",
    "蒜蓉蒸丝瓜": "Steamed Loofah",
}

# 关键词辅助（用于相似度匹配）
CN_KEYWORDS = {
    "豆腐": "tofu",
    "蛋": "egg",
    "白菜": "cabbage",
    "虾": "shrimp",
    "鸡": "chicken",
    "鱼": "fish",
    "牛": "beef",
    "排骨": "pork",
    "茄子": "eggplant",
    "椒": "pepper",
    "面": "noodle",
    "饭": "rice",
    "汤": "soup",
    "豆": "bean",
    "瓜": "melon",
}

API = "https://www.themealdb.com/api/json/v1/1/search.php"
FILTER_API = "https://www.themealdb.com/api/json/v1/1/filter.php"
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 中文菜谱缓存（启动时一次性拉全 Chinese 分类）
_CHINESE_CACHE: list[dict] | None = None


def _load_chinese_cache() -> list[dict]:
    global _CHINESE_CACHE
    if _CHINESE_CACHE is not None:
        return _CHINESE_CACHE
    try:
        url = f"{FILTER_API}?a=Chinese"
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
        _CHINESE_CACHE = data.get("meals") or []
    except Exception:
        _CHINESE_CACHE = []
    return _CHINESE_CACHE


def _tokenize(name: str) -> set[str]:
    """把中文菜名拆成关键字集合"""
    tokens = set()
    for k in CN_KEYWORDS:
        if k in name:
            tokens.add(k)
    # 保留所有单字便于简单匹配
    for ch in name:
        if "一" <= ch <= "鿿":
            tokens.add(ch)
    return tokens


def _score(cn_name: str, en_meal_name: str) -> int:
    """简单的关键字匹配得分"""
    cn_tokens = _tokenize(cn_name)
    en_lower = en_meal_name.lower()
    score = 0
    # 中文关键字转英文后比对
    for k in CN_KEYWORDS:
        if k in cn_name and CN_KEYWORDS[k] in en_lower:
            score += 3
    # 整字比对
    for ch in cn_tokens:
        if ch in CN_KEYWORDS:
            continue
        if ch in en_meal_name:  # 罕见
            score += 1
    return score


def search_dish(name: str) -> dict | None:
    """查询 TheMealDB，返回首个匹配（先精确搜索，再中文分类相似度匹配）"""
    # 第一阶段：精确搜索（用映射的英文）
    query = CN_TO_EN.get(name, name)
    url = f"{API}?s={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        meals = data.get("meals")
        if isinstance(meals, list) and meals:
            return meals[0]
    except Exception as e:
        print(f"  ! 精确搜索失败: {e}")

    # 第二阶段：相似度匹配（Chinese 全表）
    cache = _load_chinese_cache()
    if not cache:
        return None
    scored = [(m, _score(name, m.get("strMeal", ""))) for m in cache]
    scored.sort(key=lambda x: x[1], reverse=True)
    best, best_score = scored[0] if scored else (None, 0)
    if best_score >= 3:
        # 拿到 id 后再请求详情（filter 只返回缩略图元数据，search 才有完整图）
        meal_id = best.get("idMeal")
        if meal_id:
            try:
                detail_url = f"{API}?i={meal_id}"
                with urllib.request.urlopen(detail_url, timeout=10) as resp:
                    detail = json.loads(resp.read())
                detail_meals = detail.get("meals")
                if isinstance(detail_meals, list) and detail_meals:
                    return detail_meals[0]
            except Exception:
                pass
            return best  # 退而求其次
    return None


def download_image(url: str, save_path: str) -> bool:
    """下载图片到本地"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        with open(save_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  ! 下载失败: {e}")
        return False


def match_all(limit: int | None = None, dry: bool = False):
    init_db()
    db = SessionLocal()
    try:
        q = db.query(Dish).filter((Dish.image_url == None) | (Dish.image_url == ""))
        dishes = q.all()
        if limit:
            dishes = dishes[:limit]
        total = len(dishes)
        print(f"🔍 待匹配 {total} 道菜" + ("（dry run）" if dry else ""))
        matched = 0
        for i, dish in enumerate(dishes, 1):
            print(f"[{i}/{total}] {dish.name} ...", end=" ")
            meal = search_dish(dish.name)
            if not meal:
                print("未找到")
                continue
            thumb = meal.get("strMealThumb")
            if not thumb:
                print("无图片")
                continue
            if dry:
                print(f"会匹配 → {meal.get('strMeal')} ({thumb})")
                matched += 1
                continue
            ext = thumb.split(".")[-1].split("?")[0] or "jpg"
            safe_name = re.sub(r"[^\w一-鿿]", "_", dish.name)
            filename = f"meal_{dish.id}_{safe_name}.{ext}"
            save_path = os.path.join(UPLOAD_DIR, filename)
            if download_image(thumb, save_path):
                dish.image_url = f"/uploads/{filename}"
                db.commit()
                matched += 1
                print(f"✅ {meal.get('strMeal')}")
            else:
                print("下载失败")
            time.sleep(0.3)  # 礼貌限速
        print(f"\n🎉 完成：{matched}/{total} 道菜已{'dry-run' if dry else '匹配'}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="最多匹配几道")
    parser.add_argument("--dry", action="store_true", help="只看匹配结果，不下载")
    args = parser.parse_args()
    match_all(limit=args.limit, dry=args.dry)