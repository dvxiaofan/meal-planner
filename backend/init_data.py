#!/usr/bin/env python3
"""初始化菜品数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, init_db
from app.models.dish import Dish, Ingredient, Step

# 预置菜品数据
PRESET_DISHES = [
    # 荤菜
    {"name": "番茄炒蛋", "category": "荤菜", "taste": "咸鲜", "difficulty": 1, "cook_time": 15,
     "description": "经典家常菜，酸甜可口",
     "ingredients": [("番茄", "2个", "主料"), ("鸡蛋", "3个", "主料"), ("盐", "适量", "调料"), ("糖", "少许", "调料")],
     "steps": [("番茄切块，鸡蛋打散", None), ("热锅凉油，炒鸡蛋盛出", None), ("炒番茄出汁，加鸡蛋翻炒", None), ("加盐糖调味出锅", None)]},
    
    {"name": "宫保鸡丁", "category": "荤菜", "taste": "麻辣", "difficulty": 2, "cook_time": 20,
     "description": "川菜经典，麻辣鲜香",
     "ingredients": [("鸡胸肉", "300g", "主料"), ("花生米", "50g", "主料"), ("干辣椒", "10个", "调料"), ("花椒", "适量", "调料")],
     "steps": [("鸡胸肉切丁腌制", None), ("花生米炸熟", None), ("炒香辣椒花椒", None), ("加鸡丁翻炒，调味出锅", None)]},
    
    {"name": "红烧肉", "category": "荤菜", "taste": "咸鲜", "difficulty": 3, "cook_time": 60,
     "description": "肥而不腻，入口即化",
     "ingredients": [("五花肉", "500g", "主料"), ("冰糖", "30g", "调料"), ("生抽", "2勺", "调料"), ("老抽", "1勺", "调料")],
     "steps": [("五花肉切块焯水", None), ("炒糖色", None), ("加肉翻炒上色", None), ("加水炖煮40分钟", None), ("大火收汁", None)]},
    
    {"name": "可乐鸡翅", "category": "荤菜", "taste": "咸鲜", "difficulty": 1, "cook_time": 30,
     "description": "甜香入味，老少皆宜",
     "ingredients": [("鸡翅中", "10个", "主料"), ("可乐", "1罐", "主料"), ("生抽", "2勺", "调料"), ("姜片", "3片", "调料")],
     "steps": [("鸡翅划刀焯水", None), ("煎至两面金黄", None), ("加可乐和调料", None), ("大火收汁", None)]},
    
    {"name": "鱼香肉丝", "category": "荤菜", "taste": "酸甜", "difficulty": 2, "cook_time": 20,
     "description": "酸甜微辣，下饭神器",
     "ingredients": [("里脊肉", "200g", "主料"), ("木耳", "50g", "主料"), ("胡萝卜", "1根", "主料"), ("泡椒", "3个", "调料")],
     "steps": [("肉丝腌制", None), ("调鱼香汁", None), ("炒肉丝盛出", None), ("炒配料，加肉丝和鱼香汁", None)]},
    
    {"name": "糖醋排骨", "category": "荤菜", "taste": "酸甜", "difficulty": 2, "cook_time": 40,
     "description": "酸甜可口，外酥里嫩",
     "ingredients": [("小排", "500g", "主料"), ("醋", "3勺", "调料"), ("糖", "3勺", "调料"), ("生抽", "2勺", "调料")],
     "steps": [("排骨焯水", None), ("炸至金黄", None), ("调糖醋汁", None), ("翻炒收汁", None)]},
    
    {"name": "回锅肉", "category": "荤菜", "taste": "微辣", "difficulty": 2, "cook_time": 25,
     "description": "川菜之首，肥而不腻",
     "ingredients": [("五花肉", "300g", "主料"), ("蒜苗", "100g", "主料"), ("豆瓣酱", "2勺", "调料"), ("豆豉", "适量", "调料")],
     "steps": [("五花肉煮熟切片", None), ("煸炒出油", None), ("加豆瓣酱炒香", None), ("加蒜苗翻炒", None)]},
    
    {"name": "清蒸鲈鱼", "category": "荤菜", "taste": "清淡", "difficulty": 2, "cook_time": 20,
     "description": "鲜嫩爽滑，原汁原味",
     "ingredients": [("鲈鱼", "1条", "主料"), ("葱姜", "适量", "调料"), ("蒸鱼豉油", "2勺", "调料"), ("料酒", "1勺", "调料")],
     "steps": [("鱼处理干净划刀", None), ("铺葱姜蒸8分钟", None), ("倒掉蒸鱼水", None), ("淋豉油泼热油", None)]},
    
    {"name": "水煮牛肉", "category": "荤菜", "taste": "重辣", "difficulty": 3, "cook_time": 30,
     "description": "麻辣鲜香，肉嫩入味",
     "ingredients": [("牛肉", "300g", "主料"), ("豆芽", "200g", "主料"), ("干辣椒", "20个", "调料"), ("花椒", "一大把", "调料")],
     "steps": [("牛肉切片腌制", None), ("煮豆芽铺碗底", None), ("煮牛肉片", None), ("铺辣椒花椒泼热油", None)]},
    
    {"name": "酸菜鱼", "category": "荤菜", "taste": "酸辣", "difficulty": 3, "cook_time": 30,
     "description": "酸辣开胃，鱼肉鲜嫩",
     "ingredients": [("草鱼", "1条", "主料"), ("酸菜", "200g", "主料"), ("泡椒", "5个", "调料"), ("花椒", "适量", "调料")],
     "steps": [("鱼骨鱼片分离", None), ("炒酸菜加水煮", None), ("煮鱼骨鱼片", None), ("装盘泼热油", None)]},
    
    # 素菜
    {"name": "地三鲜", "category": "素菜", "taste": "咸鲜", "difficulty": 2, "cook_time": 20,
     "description": "东北经典，浓香下饭",
     "ingredients": [("茄子", "1个", "主料"), ("土豆", "1个", "主料"), ("青椒", "2个", "主料"), ("蒜末", "适量", "调料")],
     "steps": [("食材切块", None), ("分别过油", None), ("调汁翻炒", None), ("出锅装盘", None)]},
    
    {"name": "干煸四季豆", "category": "素菜", "taste": "微辣", "difficulty": 1, "cook_time": 15,
     "description": "干香入味，简单快手",
     "ingredients": [("四季豆", "300g", "主料"), ("肉末", "50g", "主料"), ("干辣椒", "5个", "调料"), ("花椒", "适量", "调料")],
     "steps": [("四季豆摘段", None), ("煸炒至虎皮", None), ("加肉末炒香", None), ("调味出锅", None)]},
    
    {"name": "麻婆豆腐", "category": "素菜", "taste": "麻辣", "difficulty": 2, "cook_time": 15,
     "description": "麻辣鲜香，下饭神器",
     "ingredients": [("嫩豆腐", "1块", "主料"), ("肉末", "50g", "主料"), ("豆瓣酱", "1勺", "调料"), ("花椒粉", "适量", "调料")],
     "steps": [("豆腐切块焯水", None), ("炒肉末和豆瓣酱", None), ("加豆腐烧入味", None), ("勾芡撒花椒粉", None)]},
    
    {"name": "蒜蓉西兰花", "category": "素菜", "taste": "清淡", "difficulty": 1, "cook_time": 10,
     "description": "清淡健康，营养丰富",
     "ingredients": [("西兰花", "1颗", "主料"), ("蒜末", "适量", "调料"), ("盐", "适量", "调料"), ("蚝油", "1勺", "调料")],
     "steps": [("西兰花掰小朵焯水", None), ("热锅爆香蒜末", None), ("加西兰花翻炒", None), ("调味出锅", None)]},
    
    {"name": "虎皮青椒", "category": "素菜", "taste": "微辣", "difficulty": 1, "cook_time": 10,
     "description": "开胃下饭，简单美味",
     "ingredients": [("青椒", "6个", "主料"), ("蒜末", "适量", "调料"), ("生抽", "1勺", "调料"), ("醋", "1勺", "调料")],
     "steps": [("青椒去籽拍扁", None), ("煸炒至虎皮", None), ("加蒜末炒香", None), ("淋生抽醋出锅", None)]},
    
    {"name": "酸辣土豆丝", "category": "素菜", "taste": "酸辣", "difficulty": 1, "cook_time": 10,
     "description": "酸辣爽脆，经典家常",
     "ingredients": [("土豆", "2个", "主料"), ("干辣椒", "5个", "调料"), ("醋", "2勺", "调料"), ("花椒", "适量", "调料")],
     "steps": [("土豆切丝泡水", None), ("热锅爆香辣椒花椒", None), ("加土豆丝大火翻炒", None), ("淋醋调味出锅", None)]},
    
    {"name": "凉拌黄瓜", "category": "凉菜", "taste": "酸辣", "difficulty": 1, "cook_time": 10,
     "description": "清爽开胃，夏日必备",
     "ingredients": [("黄瓜", "2根", "主料"), ("蒜末", "适量", "调料"), ("辣椒油", "1勺", "调料"), ("醋", "2勺", "调料")],
     "steps": [("黄瓜拍碎切段", None), ("加盐腌制出水", None), ("加蒜末辣椒油", None), ("淋醋拌匀", None)]},
    
    {"name": "皮蛋豆腐", "category": "凉菜", "taste": "清淡", "difficulty": 1, "cook_time": 5,
     "description": "简单快手，清爽可口",
     "ingredients": [("内酯豆腐", "1盒", "主料"), ("皮蛋", "2个", "主料"), ("生抽", "1勺", "调料"), ("香油", "少许", "调料")],
     "steps": [("豆腐倒出切块", None), ("皮蛋切块摆盘", None), ("淋生抽香油", None), ("撒葱花", None)]},
    
    # 汤羹
    {"name": "番茄蛋汤", "category": "汤羹", "taste": "清淡", "difficulty": 1, "cook_time": 15,
     "description": "酸甜开胃，家常必备",
     "ingredients": [("番茄", "2个", "主料"), ("鸡蛋", "2个", "主料"), ("盐", "适量", "调料"), ("香油", "少许", "调料")],
     "steps": [("番茄切块", None), ("炒出汁加水煮开", None), ("淋入蛋液", None), ("调味出锅", None)]},
    
    {"name": "紫菜蛋花汤", "category": "汤羹", "taste": "清淡", "difficulty": 1, "cook_time": 10,
     "description": "简单快手，营养美味",
     "ingredients": [("紫菜", "适量", "主料"), ("鸡蛋", "2个", "主料"), ("盐", "适量", "调料"), ("香油", "少许", "调料")],
     "steps": [("紫菜泡洗", None), ("水开加紫菜", None), ("淋入蛋液", None), ("调味出锅", None)]},
    
    {"name": "玉米排骨汤", "category": "汤羹", "taste": "清淡", "difficulty": 2, "cook_time": 60,
     "description": "清甜滋补，营养丰富",
     "ingredients": [("排骨", "300g", "主料"), ("玉米", "2根", "主料"), ("胡萝卜", "1根", "主料"), ("姜片", "3片", "调料")],
     "steps": [("排骨焯水", None), ("玉米胡萝卜切块", None), ("加水炖煮40分钟", None), ("调味出锅", None)]},
    
    {"name": "冬瓜排骨汤", "category": "汤羹", "taste": "清淡", "difficulty": 2, "cook_time": 50,
     "description": "清热解暑，夏日靓汤",
     "ingredients": [("排骨", "300g", "主料"), ("冬瓜", "300g", "主料"), ("姜片", "3片", "调料"), ("盐", "适量", "调料")],
     "steps": [("排骨焯水", None), ("冬瓜切块", None), ("加水炖煮30分钟", None), ("加冬瓜煮10分钟", None)]},
    
    # 主食
    {"name": "蛋炒饭", "category": "主食", "taste": "咸鲜", "difficulty": 1, "cook_time": 10,
     "description": "粒粒分明，简单美味",
     "ingredients": [("米饭", "1碗", "主料"), ("鸡蛋", "2个", "主料"), ("葱花", "适量", "调料"), ("盐", "适量", "调料")],
     "steps": [("鸡蛋打散", None), ("热锅炒蛋", None), ("加米饭翻炒", None), ("加盐葱花出锅", None)]},
    
    {"name": "西红柿鸡蛋面", "category": "主食", "taste": "咸鲜", "difficulty": 1, "cook_time": 15,
     "description": "汤鲜面滑，家常味道",
     "ingredients": [("面条", "200g", "主料"), ("番茄", "2个", "主料"), ("鸡蛋", "2个", "主料"), ("盐", "适量", "调料")],
     "steps": [("番茄切块", None), ("炒出汁加水煮开", None), ("下面条煮熟", None), ("淋蛋液调味", None)]},
    
    {"name": "酸辣粉", "category": "主食", "taste": "酸辣", "difficulty": 2, "cook_time": 20,
     "description": "酸辣开胃，重庆特色",
     "ingredients": [("红薯粉", "200g", "主料"), ("花生米", "适量", "主料"), ("醋", "2勺", "调料"), ("辣椒油", "2勺", "调料")],
     "steps": [("粉条泡软", None), ("煮粉条", None), ("调酸辣汁", None), ("加配料拌匀", None)]},
    
    {"name": "葱油拌面", "category": "主食", "taste": "咸鲜", "difficulty": 1, "cook_time": 15,
     "description": "葱香浓郁，简单快手",
     "ingredients": [("面条", "200g", "主料"), ("小葱", "100g", "主料"), ("生抽", "2勺", "调料"), ("油", "3勺", "调料")],
     "steps": [("煮面条", None), ("小葱切段", None), ("炸葱油", None), ("拌面调味", None)]},
    
    # 小吃
    {"name": "煎饺", "category": "小吃", "taste": "咸鲜", "difficulty": 2, "cook_time": 20,
     "description": "底脆馅嫩，香气扑鼻",
     "ingredients": [("速冻饺子", "1包", "主料"), ("油", "适量", "调料"), ("水", "适量", "调料")],
     "steps": [("平底锅刷油", None), ("摆入饺子", None), ("加水盖盖焖煮", None), ("水干煎至底部金黄", None)]},
    
    {"name": "炸酱面", "category": "主食", "taste": "咸鲜", "difficulty": 2, "cook_time": 25,
     "description": "酱香浓郁，北京经典",
     "ingredients": [("面条", "200g", "主料"), ("五花肉", "100g", "主料"), ("黄豆酱", "2勺", "调料"), ("黄瓜丝", "适量", "主料")],
     "steps": [("五花肉切丁", None), ("炒出油加酱", None), ("小火熬制", None), ("拌面加菜码", None)]},
    
    {"name": "红烧茄子", "category": "素菜", "taste": "咸鲜", "difficulty": 2, "cook_time": 20,
     "description": "软糯入味，下饭神器",
     "ingredients": [("茄子", "2个", "主料"), ("蒜末", "适量", "调料"), ("生抽", "2勺", "调料"), ("糖", "1勺", "调料")],
     "steps": [("茄子切滚刀块", None), ("炸至金黄", None), ("调汁", None), ("翻炒收汁", None)]},
    
    {"name": "干锅花菜", "category": "素菜", "taste": "微辣", "difficulty": 2, "cook_time": 15,
     "description": "干香入味，越嚼越香",
     "ingredients": [("花菜", "1颗", "主料"), ("五花肉", "50g", "主料"), ("干辣椒", "5个", "调料"), ("豆瓣酱", "1勺", "调料")],
     "steps": [("花菜掰小朵", None), ("煸炒至微焦", None), ("加肉和辣椒", None), ("调味出锅", None)]},
    
    {"name": "手撕包菜", "category": "素菜", "taste": "微辣", "difficulty": 1, "cook_time": 10,
     "description": "爽脆下饭，简单快手",
     "ingredients": [("包菜", "半个", "主料"), ("干辣椒", "5个", "调料"), ("醋", "1勺", "调料"), ("生抽", "1勺", "调料")],
     "steps": [("包菜手撕成块", None), ("热锅爆香辣椒", None), ("大火翻炒", None), ("淋醋出锅", None)]},
    
    {"name": "白菜豆腐汤", "category": "汤羹", "taste": "清淡", "difficulty": 1, "cook_time": 15,
     "description": "清淡养胃，家常味道",
     "ingredients": [("大白菜", "适量", "主料"), ("豆腐", "1块", "主料"), ("盐", "适量", "调料"), ("香油", "少许", "调料")],
     "steps": [("白菜切段", None), ("豆腐切块", None), ("水开加白菜豆腐", None), ("煮5分钟调味", None)]},
    
    {"name": "阳春面", "category": "主食", "taste": "清淡", "difficulty": 1, "cook_time": 10,
     "description": "清汤寡水，本味之美",
     "ingredients": [("细面条", "200g", "主料"), ("猪油", "1勺", "调料"), ("生抽", "1勺", "调料"), ("葱花", "适量", "调料")],
     "steps": [("碗底放猪油生抽", None), ("煮面条", None), ("舀面汤冲开调料", None), ("捞面撒葱花", None)]},
    
    {"name": "扬州炒饭", "category": "主食", "taste": "咸鲜", "difficulty": 2, "cook_time": 15,
     "description": "粒粒分明，配料丰富",
     "ingredients": [("米饭", "1碗", "主料"), ("鸡蛋", "2个", "主料"), ("火腿丁", "50g", "主料"), ("虾仁", "50g", "主料")],
     "steps": [("配料切丁", None), ("炒蛋", None), ("加米饭翻炒", None), ("加配料调味", None)]},
    
    {"name": "土豆炖牛肉", "category": "荤菜", "taste": "咸鲜", "difficulty": 2, "cook_time": 50,
     "description": "软烂入味，暖心暖胃",
     "ingredients": [("牛肉", "300g", "主料"), ("土豆", "2个", "主料"), ("胡萝卜", "1根", "主料"), ("八角", "2个", "调料")],
     "steps": [("牛肉切块焯水", None), ("炒牛肉上色", None), ("加水炖30分钟", None), ("加土豆胡萝卜炖软", None)]},
    
    {"name": "青椒肉丝", "category": "荤菜", "taste": "咸鲜", "difficulty": 1, "cook_time": 15,
     "description": "家常快手，下饭必备",
     "ingredients": [("里脊肉", "200g", "主料"), ("青椒", "3个", "主料"), ("生抽", "1勺", "调料"), ("淀粉", "适量", "调料")],
     "steps": [("肉丝腌制", None), ("青椒切丝", None), ("炒肉丝", None), ("加青椒翻炒出锅", None)]},
    
    {"name": "蒜苗回锅肉", "category": "荤菜", "taste": "微辣", "difficulty": 2, "cook_time": 20,
     "description": "蒜苗清香，肉片入味",
     "ingredients": [("五花肉", "300g", "主料"), ("蒜苗", "100g", "主料"), ("豆瓣酱", "1勺", "调料"), ("甜面酱", "1勺", "调料")],
     "steps": [("五花肉煮熟切片", None), ("煸炒出油", None), ("加酱炒香", None), ("加蒜苗翻炒", None)]},
    
    {"name": "西红柿炖牛腩", "category": "荤菜", "taste": "咸鲜", "difficulty": 2, "cook_time": 60,
     "description": "酸甜浓郁，营养丰富",
     "ingredients": [("牛腩", "500g", "主料"), ("番茄", "3个", "主料"), ("番茄酱", "2勺", "调料"), ("八角", "2个", "调料")],
     "steps": [("牛腩切块焯水", None), ("番茄切块", None), ("炒牛腩加番茄", None), ("炖煮50分钟", None)]},
    
    {"name": "蒜蓉粉丝蒸虾", "category": "荤菜", "taste": "清淡", "difficulty": 2, "cook_time": 15,
     "description": "鲜美嫩滑，宴客佳品",
     "ingredients": [("大虾", "10只", "主料"), ("粉丝", "1把", "主料"), ("蒜蓉", "适量", "调料"), ("生抽", "2勺", "调料")],
     "steps": [("粉丝泡软", None), ("虾开背去虾线", None), ("铺蒜蓉蒸8分钟", None), ("淋热油", None)]},
    
    {"name": "辣子鸡", "category": "荤菜", "taste": "重辣", "difficulty": 3, "cook_time": 25,
     "description": "麻辣酥香，越吃越上瘾",
     "ingredients": [("鸡腿肉", "300g", "主料"), ("干辣椒", "一大碗", "调料"), ("花椒", "一把", "调料"), ("芝麻", "适量", "调料")],
     "steps": [("鸡肉切块腌制", None), ("炸至金黄", None), ("炒香辣椒花椒", None), ("加鸡肉翻炒", None)]},
    
    {"name": "白灼虾", "category": "荤菜", "taste": "清淡", "difficulty": 1, "cook_time": 10,
     "description": "原汁原味，鲜甜可口",
     "ingredients": [("基围虾", "500g", "主料"), ("姜片", "3片", "调料"), ("料酒", "1勺", "调料"), ("蘸料", "适量", "调料")],
     "steps": [("虾洗净", None), ("水开加姜片料酒", None), ("煮至变红", None), ("捞出蘸料吃", None)]},
    
    {"name": "韭菜炒鸡蛋", "category": "荤菜", "taste": "咸鲜", "difficulty": 1, "cook_time": 10,
     "description": "简单快手，韭菜鲜香",
     "ingredients": [("韭菜", "200g", "主料"), ("鸡蛋", "3个", "主料"), ("盐", "适量", "调料")],
     "steps": [("韭菜切段", None), ("鸡蛋打散", None), ("先炒蛋", None), ("加韭菜翻炒出锅", None)]},
    
    {"name": "红烧茄子", "category": "素菜", "taste": "咸鲜", "difficulty": 2, "cook_time": 20,
     "description": "软糯入味，下饭神器",
     "ingredients": [("茄子", "2个", "主料"), ("蒜末", "适量", "调料"), ("生抽", "2勺", "调料"), ("糖", "1勺", "调料")],
     "steps": [("茄子切滚刀块", None), ("炸至金黄", None), ("调汁", None), ("翻炒收汁", None)]},
    
    {"name": "香菇青菜", "category": "素菜", "taste": "清淡", "difficulty": 1, "cook_time": 10,
     "description": "清淡鲜美，营养健康",
     "ingredients": [("青菜", "300g", "主料"), ("香菇", "5朵", "主料"), ("蒜末", "适量", "调料"), ("蚝油", "1勺", "调料")],
     "steps": [("青菜洗净", None), ("香菇切片", None), ("蒜末爆香", None), ("翻炒调味出锅", None)]},
    
    {"name": "西芹炒百合", "category": "素菜", "taste": "清淡", "difficulty": 1, "cook_time": 10,
     "description": "清脆爽口，养颜佳品",
     "ingredients": [("西芹", "200g", "主料"), ("百合", "100g", "主料"), ("盐", "适量", "调料"), ("枸杞", "少许", "调料")],
     "steps": [("西芹切段", None), ("百合掰片", None), ("焯水", None), ("翻炒调味", None)]},
    
    {"name": "红烧豆腐", "category": "素菜", "taste": "咸鲜", "difficulty": 1, "cook_time": 15,
     "description": "外焦里嫩，酱香浓郁",
     "ingredients": [("老豆腐", "1块", "主料"), ("生抽", "2勺", "调料"), ("老抽", "1勺", "调料"), ("糖", "1勺", "调料")],
     "steps": [("豆腐切块", None), ("煎至两面金黄", None), ("调汁", None), ("烧入味", None)]},
    
    {"name": "醋溜白菜", "category": "素菜", "taste": "酸辣", "difficulty": 1, "cook_time": 10,
     "description": "酸辣爽脆，开胃下饭",
     "ingredients": [("大白菜", "300g", "主料"), ("干辣椒", "5个", "调料"), ("醋", "2勺", "调料"), ("花椒", "适量", "调料")],
     "steps": [("白菜切块", None), ("热锅爆香辣椒花椒", None), ("大火翻炒白菜", None), ("淋醋出锅", None)]},
    
    {"name": "蒜蓉蒸丝瓜", "category": "素菜", "taste": "清淡", "difficulty": 1, "cook_time": 10,
     "description": "清甜爽口，夏日佳品",
     "ingredients": [("丝瓜", "2根", "主料"), ("蒜蓉", "适量", "调料"), ("生抽", "1勺", "调料"), ("油", "适量", "调料")],
     "steps": [("丝瓜去皮切段", None), ("铺蒜蓉", None), ("蒸5分钟", None), ("淋生抽泼热油", None)]},
]


def init_data():
    """初始化菜品数据"""
    init_db()
    db = SessionLocal()
    
    # 检查是否已有数据
    existing = db.query(Dish).count()
    if existing > 0:
        print(f"数据库已有 {existing} 道菜品，跳过初始化")
        db.close()
        return
    
    print("开始初始化菜品数据...")
    
    for dish_data in PRESET_DISHES:
        dish = Dish(
            name=dish_data["name"],
            category=dish_data["category"],
            taste=dish_data["taste"],
            difficulty=dish_data["difficulty"],
            cook_time=dish_data["cook_time"],
            description=dish_data["description"]
        )
        db.add(dish)
        db.flush()
        
        # 添加食材
        for name, amount, type_ in dish_data.get("ingredients", []):
            ingredient = Ingredient(dish_id=dish.id, name=name, amount=amount, type=type_)
            db.add(ingredient)
        
        # 添加步骤
        for i, (desc, duration) in enumerate(dish_data.get("steps", []), 1):
            step = Step(dish_id=dish.id, step_number=i, description=desc, duration=duration)
            db.add(step)
    
    db.commit()
    total = db.query(Dish).count()
    print(f"✅ 初始化完成，共 {total} 道菜品")
    db.close()


if __name__ == "__main__":
    init_data()
