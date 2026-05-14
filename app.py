import json
import re
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from tkinter import ttk, messagebox
from urllib.parse import urlparse, parse_qs
import webbrowser

import requests

URL = (
    "https://flights.ctrip.com/fuzzysearch/search"
    "?fromUrl=https%253A%252F%252Fflights.ctrip.com%252Ffuzzy%252F%2523ctm_ref%253Dfli_hp_sb_findlprice_t"
    "&channel=online_budget"
)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,zh-HK;q=0.7,en-US;q=0.6,en;q=0.5",
}

CITY_CODE_MAP = {
    "万州": "WXN",
    "三亚": "SYX",
    "三明": "SQJ",
    "上海": "SHA",
    "上饶": "SQD",
    "且末": "IQM",
    "东京": "TYO",
    "东营": "DOY",
    "中卫": "ZHY",
    "中国澳门": "MFM",
    "中国台北": "TPE",
    "中国香港": "HKG",
    "中国高雄": "KHH",
    "临汾": "LFQ",
    "临沂": "LYI",
    "临沧": "LNJ",
    "丹东": "DDG",
    "丹佛": "DEN",
    "丽江": "LJG",
    "义乌": "YIW",
    "乌兰察布": "UCB",
    "乌兰巴托": "ULN",
    "乌兰浩特": "HLH",
    "乌海": "WUA",
    "乌鲁木齐": "URC",
    "九寨沟": "JZH",
    "九江": "JIU",
    "二连浩特": "ERL",
    "五大连池": "DTU",
    "井冈山": "JGS",
    "伊宁": "YIN",
    "伊斯坦布尔": "IST",
    "伊春": "LDS",
    "佛山": "FUO",
    "佳木斯": "JMU",
    "保山": "BSD",
    "信阳": "XAI",
    "克拉玛依": "KRY",
    "六盘水": "LPF",
    "兰州": "LHW",
    "兴义": "ACX",
    "包头": "BAV",
    "北京": "BJS",
    "北海": "BHY",
    "十堰": "WDS",
    "南京": "NKG",
    "南充": "NAO",
    "南宁": "NNG",
    "南昌": "KHN",
    "南通": "NTG",
    "南阳": "NNY",
    "博乐": "BPL",
    "厦门": "XMN",
    "台北": "TPE",
    "台州": "HYN",
    "合肥": "HFE",
    "吉隆坡": "KUL",
    "名古屋": "NGO",
    "吐鲁番": "TLQ",
    "吕梁": "LLV",
    "呼伦贝尔": "XRQ",
    "呼和浩特": "HET",
    "和田": "HTN",
    "哈密": "HMI",
    "哈尔滨": "HRB",
    "喀什": "KHG",
    "嘉峪关": "JGN",
    "固原": "GYU",
    "堪培拉": "CBR",
    "塔城": "TCG",
    "大同": "DAT",
    "大庆": "DQA",
    "大理": "DLU",
    "大连": "DLC",
    "大阪": "OSA",
    "天水": "THQ",
    "天津": "TSN",
    "太原": "TYN",
    "威海": "WEH",
    "宁波": "NGB",
    "宁蒗": "NLH",
    "安庆": "AQG",
    "安顺": "AVA",
    "宜宾": "YBP",
    "宜昌": "YIH",
    "宜春": "YIC",
    "富蕴": "FYN",
    "岳阳": "YYA",
    "巫山": "WSK",
    "巴中": "BZX",
    "巴厘岛": "DPS",
    "巴黎": "PAR",
    "常州": "CZX",
    "常德": "CGD",
    "广元": "GYS",
    "广州": "CAN",
    "庆阳": "IQN",
    "库尔勒": "KRL",
    "库车": "KCA",
    "康定": "KGT",
    "延吉": "YNJ",
    "延安": "ENY",
    "张家口": "ZQZ",
    "张家界": "DYG",
    "张掖": "YZY",
    "徐州": "XUZ",
    "德令哈": "HXD",
    "德里": "DEL",
    "忻州": "WUT",
    "怀化": "HJJ",
    "恩施": "ENH",
    "惠州": "HUZ",
    "成都": "CTU",
    "扎兰屯": "NZL",
    "扬州": "YTY",
    "承德": "CDE",
    "抚远": "FYJ",
    "拉萨": "LXA",
    "揭阳": "SWA",
    "攀枝花": "PZI",
    "敦煌": "DNH",
    "文山": "WNH",
    "新加坡": "SIN",
    "新源": "NLT",
    "无锡": "WUX",
    "日喀则": "RKZ",
    "日照": "RIZ",
    "昆明": "KMG",
    "昌都": "BPX",
    "昭通": "ZAT",
    "普吉岛": "HKT",
    "普洱": "SYM",
    "景德镇": "JDZ",
    "曼谷": "BKK",
    "朝阳": "CHG",
    "札幌": "SPK",
    "杭州": "HGH",
    "松原": "YSQ",
    "林芝": "LZY",
    "果洛": "GMQ",
    "柳州": "LZH",
    "格尔木": "GOQ",
    "桂林": "KWL",
    "梅州": "MXZ",
    "梧州": "WUZ",
    "榆林": "UYN",
    "武夷山": "WUS",
    "武汉": "WUH",
    "毕节": "BFJ",
    "永州": "LLF",
    "汉中": "HZG",
    "池州": "JUH",
    "沈阳": "SHE",
    "沧源": "CWJ",
    "河池": "HCJ",
    "泉州": "JJN",
    "泸州": "LZO",
    "洛阳": "LYA",
    "济南": "TNA",
    "济宁": "JNG",
    "海口": "HAK",
    "海拉尔": "HLD",
    "淮安": "HIA",
    "深圳": "SZX",
    "温州": "WNZ",
    "湛江": "ZHA",
    "满洲里": "NZH",
    "漠河": "OHE",
    "潍坊": "WEF",
    "澜沧": "JMJ",
    "澳门": "MFM",
    "烟台": "YNT",
    "牡丹江": "MDG",
    "玉树": "YUS",
    "珠海": "ZUH",
    "琼海": "BAR",
    "白城": "DBC",
    "白山": "NBS",
    "百色": "AEB",
    "盐城": "YNZ",
    "石家庄": "SJW",
    "石河子": "SHF",
    "祁连": "HBQ",
    "神农架": "HPG",
    "福冈": "FUK",
    "福州": "FOC",
    "秦皇岛": "BPE",
    "稻城": "DCY",
    "红原": "AHJ",
    "绵阳": "MIG",
    "罗马": "ROM",
    "舟山": "HSN",
    "芒市": "LUM",
    "花土沟": "HTT",
    "若羌": "RQA",
    "荆门": "JM1",
    "荔波": "LLB",
    "莎车": "QSZ",
    "莫斯科": "MOW",
    "营口": "YKH",
    "衡阳": "HNY",
    "衢州": "JUZ",
    "襄阳": "XFN",
    "西双版纳": "JHG",
    "西宁": "XNN",
    "西安": "SIA",
    "西昌": "XIC",
    "贵阳": "KWE",
    "赣州": "KOW",
    "赤峰": "CIF",
    "达州": "DAX",
    "迪庆": "DIG",
    "迪拜": "DXB",
    "通化": "TNH",
    "通辽": "TGO",
    "遵义": "ZYI",
    "邯郸": "HDG",
    "邵阳": "WGN",
    "郑州": "CGO",
    "鄂尔多斯": "DSN",
    "重庆": "CKG",
    "金昌": "JIC",
    "金边": "PNH",
    "釜山": "PUS",
    "铜仁": "TEN",
    "银川": "INC",
    "锡林浩特": "XIL",
    "锦州": "JNZ",
    "长春": "CGQ",
    "长沙": "CSX",
    "长治": "CIH",
    "阜阳": "FUG",
    "阿克苏": "AKU",
    "阿勒泰": "AAT",
    "阿尔山": "YIE",
    "阿拉善右旗": "RHT",
    "阿拉善左旗": "AXF",
    "阿里": "NGQ",
    "陇南": "LNL",
    "霍林郭勒": "HUO",
    "青岛": "TAO",
    "鞍山": "AOG",
    "额济纳旗": "EJN",
    "首尔": "SEL",
    "香港": "HKG",
    "马尼拉": "MNL",
    "高雄": "KHH",
    "鸡西": "JXA",
    "黄山": "TXN",
    "黎平": "HZH",
    "黑河": "HEK",
    "黔江": "JIQ",
    "齐齐哈尔": "NDG",
    "龙岩": "LCX",
}


def normalize_city_codes(raw_text: str) -> tuple[set[str], list[str]]:
    """返回 (匹配到的IATA代码集合, 未识别的城市名列表)"""
    parts = [p.strip() for p in re.split(r"[，,;；\s]+", raw_text) if p.strip()]
    codes = set()
    unknown = []
    for part in parts:
        if len(part) == 3 and part.isalpha():
            codes.add(part.upper())
            continue
        if part in CITY_CODE_MAP:
            codes.add(CITY_CODE_MAP[part])
        else:
            unknown.append(part)
    return codes, unknown


def parse_itinerary_link(href: str, text: str) -> dict | None:
    if "flights.ctrip.com/itinerary/oneway/" not in href:
        return None
    try:
        path = urlparse(href).path
        segments = path.strip("/").split("/")
        if len(segments) < 3:
            return None
        route = segments[-1]
        if "-" not in route:
            return None
        depart, arrive = route.split("-", 1)
        query = parse_qs(urlparse(href).query)
        date = (query.get("date") or [""])[0]
        price_text_match = re.search(r"¥\s*(\d+)", text)
        price = int(price_text_match.group(1)) if price_text_match else None
        return {
            "depart": depart,
            "arrive": arrive,
            "date": date,
            "price": price,
            "link": href,
        }
    except Exception:
        return None


def _resolve_cities(text: str, label: str) -> list[dict]:
    """解析城市文本，返回 API 所需的城市列表。"""
    city_codes, unknown = normalize_city_codes(text)
    if unknown:
        raise ValueError(f"{label}中未识别的城市: {', '.join(unknown)}\n请使用中文城市名或三字母IATA代码")
    code_to_name = {v: k for k, v in CITY_CODE_MAP.items()}
    return [{"ct": 1, "code": c, "name": code_to_name.get(c, c)} for c in city_codes]


def fetch_low_price_flights(
    cookie: str | None,
    departure_text: str,
    arrive_text: str,
    date_start: str,
    date_end: str,
    max_price: int | None = None,
) -> list[dict]:
    api_url = "https://m.ctrip.com/restapi/soa2/19728/fuzzySearch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Content-Type": "application/json",
        "Origin": "https://flights.ctrip.com",
        "Referer": "https://flights.ctrip.com/fuzzysearch/search",
    }
    if cookie:
        headers["Cookie"] = cookie

    # ---- 出发城市 ----
    depart_codes = _resolve_cities(departure_text, "出发城市")
    if not depart_codes:
        depart_codes = [{"ct": 1, "code": "SHA", "name": "上海"}]

    # ---- 目的地（客户端过滤） ----
    arrive_text = arrive_text.strip()
    arrive_filter_codes: set[str] | None = None          # None = 不过滤
    if arrive_text and arrive_text != "全国":
        arrive_city_list, unknown = normalize_city_codes(arrive_text)
        if unknown:
            raise ValueError(
                f"目的地中未识别的城市: {', '.join(unknown)}\n请使用中文城市名或三字母IATA代码"
            )
        if arrive_city_list:
            arrive_filter_codes = arrive_city_list

    # API 始终用全国搜索，结果再按目的地过滤
    arrive_codes = [{"ct": 3, "code": "DOMESTIC_ALL", "name": "全中国"}]

    # ---- 日期范围 ----
    if not date_start:
        today = datetime.now()
        date_start = f"{today.year}-{today.month}-{today.day}"
    if not date_end:
        end = datetime.now() + timedelta(days=30)
        date_end = f"{end.year}-{end.month}-{end.day}"

    payload = {
        "tt": 1,
        "source": "online_special_search",
        "st": 18,
        "segments": [
            {
                "dcs": depart_codes,
                "acs": arrive_codes,
                "dow": [],
                "sr": None,
                "drl": [{"begin": date_start, "end": date_end}],
                "ddate": None,
            }
        ],
        "filters": None,
    }
    resp = requests.post(api_url, headers=headers, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for route in data.get("routes", []):
        depart_city = route.get("departCity", {})
        arrive_city = route.get("arriveCity", {})
        depart_code = depart_city.get("code", "")
        depart_name = depart_city.get("name", depart_code)
        arrive_code = arrive_city.get("code", "")
        arrive_name = arrive_city.get("name", arrive_code)

        # 按目的地过滤
        if arrive_filter_codes and arrive_code not in arrive_filter_codes:
            continue

        for pl in route.get("pl", []):
            price = pl.get("price")
            if price is None:
                continue
            # 按最高价格过滤
            if max_price is not None and price > max_price:
                continue
            date = pl.get("departDate", "")
            link = (
                f"https://flights.ctrip.com/itinerary/oneway/"
                f"{depart_code}-{arrive_code}?date={date}&sortByPrice=true"
            )
            results.append({
                "depart": depart_name,
                "arrive": arrive_name,
                "date": date,
                "price": int(price),
                "link": link,
            })
    return results


def fetch_return_cheapest(
    cookie: str | None,
    depart_code: str,
    arrive_code: str,
    date_start: str,
    date_end: str,
) -> dict | None:
    """查询从 arrive_code → depart_code 的返程最低价。

    返回 {"price": int, "date": str, "link": str} 或 None。
    """
    api_url = "https://m.ctrip.com/restapi/soa2/19728/fuzzySearch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Content-Type": "application/json",
        "Origin": "https://flights.ctrip.com",
        "Referer": "https://flights.ctrip.com/fuzzysearch/search",
    }
    if cookie:
        headers["Cookie"] = cookie

    code_to_name = {v: k for k, v in CITY_CODE_MAP.items()}
    payload = {
        "tt": 1,
        "source": "online_special_search",
        "st": 18,
        "segments": [
            {
                "dcs": [{"ct": 1, "code": arrive_code, "name": code_to_name.get(arrive_code, arrive_code)}],
                "acs": [{"ct": 1, "code": depart_code, "name": code_to_name.get(depart_code, depart_code)}],
                "dow": [],
                "sr": None,
                "drl": [{"begin": date_start, "end": date_end}],
                "ddate": None,
            }
        ],
        "filters": None,
    }
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None

    best: dict | None = None
    for route in data.get("routes", []):
        rc = route.get("arriveCity", {}).get("code", "")
        if rc != depart_code:
            continue
        for pl in route.get("pl", []):
            price = pl.get("price")
            if price is None:
                continue
            if best is None or price < best["price"]:
                date = pl.get("departDate", "")
                best = {
                    "price": int(price),
                    "date": date,
                    "link": (
                        f"https://flights.ctrip.com/itinerary/oneway/"
                        f"{arrive_code}-{depart_code}?date={date}&sortByPrice=true"
                    ),
                }
    return best


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("携程特价机票查询（含返程）")
        self.geometry("1280x720")
        self.minsize(1100, 620)

        self.departure_var = tk.StringVar(value="烟台,威海,青岛")
        self.arrive_var = tk.StringVar(value="全国")
        today = datetime.now()
        self.date_start_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))
        end = today + timedelta(days=30)
        self.date_end_var = tk.StringVar(value=end.strftime("%Y-%m-%d"))
        # 返程日期默认：去程结束后 1~15 天
        ret_start = end + timedelta(days=1)
        ret_end = end + timedelta(days=15)
        self.ret_start_var = tk.StringVar(value=ret_start.strftime("%Y-%m-%d"))
        self.ret_end_var = tk.StringVar(value=ret_end.strftime("%Y-%m-%d"))
        self.max_price_var = tk.StringVar(value="800")
        self.cookie_var = tk.StringVar()
        self.status_var = tk.StringVar(value="就绪")

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.X)

        # ---- 第一行：出发城市 & 目的地 & 最高价格 ----
        row1 = ttk.Frame(top)
        row1.pack(fill=tk.X, pady=(0, 6))

        dep_frame = ttk.Frame(row1)
        dep_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(dep_frame, text="出发城市 (逗号分隔)").pack(anchor=tk.W)
        ttk.Entry(dep_frame, textvariable=self.departure_var).pack(fill=tk.X, pady=(2, 0))

        arr_frame = ttk.Frame(row1)
        arr_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(arr_frame, text='目的地 (留空或"全国"=全部)').pack(anchor=tk.W)
        ttk.Entry(arr_frame, textvariable=self.arrive_var).pack(fill=tk.X, pady=(2, 0))

        price_frame = ttk.Frame(row1)
        price_frame.pack(side=tk.LEFT)
        ttk.Label(price_frame, text="最高价格 (元)").pack(anchor=tk.W)
        ttk.Entry(price_frame, textvariable=self.max_price_var, width=10).pack(pady=(2, 0))

        # ---- 第二行：去程日期 + 快捷按钮 | 返程日期 + 快捷按钮 ----
        row2 = ttk.Frame(top)
        row2.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(row2, text="✈ 去程", font=("", 9, "bold")).pack(side=tk.LEFT, padx=(0, 8))

        ds_frame = ttk.Frame(row2)
        ds_frame.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(ds_frame, text="开始日期").pack(anchor=tk.W)
        ttk.Entry(ds_frame, textvariable=self.date_start_var, width=14).pack(pady=(2, 0))

        de_frame = ttk.Frame(row2)
        de_frame.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(de_frame, text="结束日期").pack(anchor=tk.W)
        ttk.Entry(de_frame, textvariable=self.date_end_var, width=14).pack(pady=(2, 0))

        quick = ttk.Frame(row2)
        quick.pack(side=tk.LEFT, pady=(14, 0), padx=(0, 20))
        for label, days in [("3天", 3), ("7天", 7), ("15天", 15), ("30天", 30)]:
            ttk.Button(
                quick, text=label, width=4,
                command=lambda d=days: self._set_date_range(self.date_start_var, self.date_end_var, d),
            ).pack(side=tk.LEFT, padx=2)

        ttk.Separator(row2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Label(row2, text="↩ 返程", font=("", 9, "bold")).pack(side=tk.LEFT, padx=(0, 8))

        rs_frame = ttk.Frame(row2)
        rs_frame.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(rs_frame, text="开始日期").pack(anchor=tk.W)
        ttk.Entry(rs_frame, textvariable=self.ret_start_var, width=14).pack(pady=(2, 0))

        re_frame = ttk.Frame(row2)
        re_frame.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(re_frame, text="结束日期").pack(anchor=tk.W)
        ttk.Entry(re_frame, textvariable=self.ret_end_var, width=14).pack(pady=(2, 0))

        quick_ret = ttk.Frame(row2)
        quick_ret.pack(side=tk.LEFT, pady=(14, 0))
        for label, days in [("3天", 3), ("7天", 7), ("15天", 15), ("30天", 30)]:
            ttk.Button(
                quick_ret, text=label, width=4,
                command=lambda d=days: self._set_date_range(self.ret_start_var, self.ret_end_var, d),
            ).pack(side=tk.LEFT, padx=2)

        # ---- 第三行：Cookie ----
        row3 = ttk.Frame(top)
        row3.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row3, text="Cookie (可选)").pack(anchor=tk.W)
        ttk.Entry(row3, textvariable=self.cookie_var).pack(fill=tk.X, pady=(2, 0))

        # ---- 按钮栏 ----
        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill=tk.X, pady=(4, 0))
        self.query_btn = ttk.Button(btn_frame, text="🔍 查询特价（含返程）", command=self.on_query)
        self.query_btn.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(btn_frame, mode="indeterminate")
        self.progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.status_label = ttk.Label(btn_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT)

        # ---- 结果表格（去程 + 返程合并） ----
        columns = (
            "depart", "arrive",
            "go_date", "go_price",
            "ret_price", "ret_date", "total",
            "go_link", "ret_link",
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)

        self.tree.heading("depart",    text="出发城市")
        self.tree.heading("arrive",    text="目的地")
        self.tree.heading("go_date",   text="去程日期")
        self.tree.heading("go_price",  text="去程价格")
        self.tree.heading("ret_price", text="返程价格")
        self.tree.heading("ret_date",  text="返程日期")
        self.tree.heading("total",     text="往返总价")
        self.tree.heading("go_link",   text="去程链接")
        self.tree.heading("ret_link",  text="返程链接")

        self.tree.column("depart",    width=70,  anchor=tk.CENTER)
        self.tree.column("arrive",    width=70,  anchor=tk.CENTER)
        self.tree.column("go_date",   width=95,  anchor=tk.CENTER)
        self.tree.column("go_price",  width=70,  anchor=tk.CENTER)
        self.tree.column("ret_price", width=70,  anchor=tk.CENTER)
        self.tree.column("ret_date",  width=95,  anchor=tk.CENTER)
        self.tree.column("total",     width=75,  anchor=tk.CENTER)
        self.tree.column("go_link",   width=310, anchor=tk.W)
        self.tree.column("ret_link",  width=310, anchor=tk.W)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=6)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=6)

        self.tree.bind("<Double-1>", self.on_open_link)

        tip = ttk.Label(self, text="💡 双击行打开去程链接；双击\"返程链接\"列打开返程链接", padding=(10, 0, 10, 8))
        tip.pack(side=tk.BOTTOM, anchor=tk.W)

    # ------------------------------------------------------------------ helpers
    def _set_date_range(self, start_var: tk.StringVar, end_var: tk.StringVar, days: int):
        start_str = start_var.get().strip()
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            start = datetime.now()
            start_var.set(start.strftime("%Y-%m-%d"))
        end_var.set((start + timedelta(days=days)).strftime("%Y-%m-%d"))

    def on_open_link(self, _event):
        item = self.tree.selection()
        if not item:
            return
        col = self.tree.identify_column(_event.x)
        try:
            col_idx = int(col.replace("#", "")) - 1
        except ValueError:
            col_idx = -1
        col_name = self.tree["columns"][col_idx] if 0 <= col_idx < len(self.tree["columns"]) else ""
        if col_name == "ret_link":
            link = self.tree.set(item[0], "ret_link")
        else:
            link = self.tree.set(item[0], "go_link")
        if link and link != "-":
            webbrowser.open(link)

    # ------------------------------------------------------------------ query
    def on_query(self):
        self.query_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_var.set("正在查询去程...")
        threading.Thread(target=self._do_query, daemon=True).start()

    def _do_query(self):
        try:
            cookie = self.cookie_var.get().strip() or None
            departure_text = self.departure_var.get()
            arrive_text = self.arrive_var.get()
            date_start = self.date_start_var.get().strip()
            date_end = self.date_end_var.get().strip()
            ret_start = self.ret_start_var.get().strip()
            ret_end = self.ret_end_var.get().strip()

            # 校验日期
            for d, name in [
                (date_start, "去程开始日期"), (date_end, "去程结束日期"),
                (ret_start, "返程开始日期"), (ret_end, "返程结束日期"),
            ]:
                if d:
                    try:
                        datetime.strptime(d, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError(f"{name}格式错误，请使用 YYYY-MM-DD 格式")

            # 最高价格
            max_price_text = self.max_price_var.get().strip()
            max_price = None
            if max_price_text:
                try:
                    max_price = int(max_price_text)
                except ValueError:
                    raise ValueError("最高价格请填写整数，如 800")

            # ---------- 1. 查询去程 ----------
            go_results = fetch_low_price_flights(
                cookie, departure_text, arrive_text, date_start, date_end, max_price
            )
            go_results.sort(key=lambda x: (x["price"], x["date"], x["depart"], x["arrive"]))

            total = len(go_results)
            if total == 0:
                self._update_table([])
                self.status_var.set("未找到去程航班")
                return

            # ---------- 2. 逐路线查询返程最低价 ----------
            name_to_code = CITY_CODE_MAP
            return_cache: dict[tuple[str, str], dict | None] = {}
            route_set: set[tuple[str, str]] = set()
            for r in go_results:
                d_code = name_to_code.get(r["depart"], r["depart"])
                a_code = name_to_code.get(r["arrive"], r["arrive"])
                route_set.add((d_code, a_code))

            # 多线程并发查询返程（最多 8 个线程）
            done = 0
            total_routes = len(route_set)
            with ThreadPoolExecutor(max_workers=8) as pool:
                future_map = {
                    pool.submit(fetch_return_cheapest, cookie, d, a, ret_start, ret_end): (d, a)
                    for d, a in route_set
                }
                for future in as_completed(future_map):
                    d_code, a_code = future_map[future]
                    done += 1
                    self.status_var.set(f"查询返程 {done}/{total_routes} …")
                    try:
                        return_cache[(d_code, a_code)] = future.result()
                    except Exception:
                        return_cache[(d_code, a_code)] = None

            # ---------- 3. 合并结果 ----------
            combined = []
            for r in go_results:
                d_code = name_to_code.get(r["depart"], r["depart"])
                a_code = name_to_code.get(r["arrive"], r["arrive"])
                ret = return_cache.get((d_code, a_code))
                entry = {
                    "depart": r["depart"],
                    "arrive": r["arrive"],
                    "go_date": r["date"],
                    "go_price": r["price"],
                    "go_link": r["link"],
                }
                if ret:
                    entry["ret_price"] = ret["price"]
                    entry["ret_date"] = ret["date"]
                    entry["ret_link"] = ret["link"]
                    entry["total"] = r["price"] + ret["price"]
                else:
                    entry["ret_price"] = None
                    entry["ret_date"] = "-"
                    entry["ret_link"] = "-"
                    entry["total"] = None
                combined.append(entry)

            combined.sort(key=lambda x: (x["total"] if x["total"] is not None else 999999, x["go_date"]))
            self._update_table(combined)
            self.status_var.set(f"完成: {len(combined)} 条去程, {len(route_set)} 条返程路线")

        except ValueError as exc:
            self.status_var.set("输入有误")
            self.after(0, lambda: messagebox.showwarning("提示", str(exc)))
        except Exception as exc:
            self.status_var.set("查询失败")
            self.after(0, lambda: messagebox.showerror("错误", f"查询失败: {exc}"))
        finally:
            self.progress.stop()
            self.query_btn.config(state=tk.NORMAL)

    def _update_table(self, combined: list[dict]):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in combined:
            ret_price_str = f"¥{r['ret_price']}" if r["ret_price"] is not None else "无返程"
            total_str = f"¥{r['total']}" if r["total"] is not None else "-"
            self.tree.insert("", tk.END, values=(
                r["depart"], r["arrive"],
                r["go_date"], f"¥{r['go_price']}",
                ret_price_str, r["ret_date"], total_str,
                r["go_link"], r["ret_link"],
            ))


if __name__ == "__main__":
    App().mainloop()
