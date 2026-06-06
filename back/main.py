import json
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Coffee Bean Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BEANS_FILE = Path(__file__).parent / "beans.json"


class Preference(BaseModel):
    acidity: str = Field(..., description="낮음/중간/높음")
    body: str = Field(..., description="가벼움/중간/묵직")
    roast: str = Field(..., description="라이트/미디엄/다크")
    flavor: str = Field(..., description="과일·꽃/견과·초콜릿/흙·스파이스")
    sweetness: int = Field(..., ge=1, le=5)
    caffeine: str = Field(..., description="낮음/보통/높음")
    brew_method: str = Field(..., description="에스프레소/드립/콜드브루/모카포트/프렌치프레스")


class BeanRecommendation(BaseModel):
    rank: int
    name: str
    origin: str
    score: int
    roast: str
    flavor_category: str
    flavor_notes: List[str]
    acidity: int
    body: int
    sweetness: int
    caffeine: str
    brew_tip: str
    description: str
    match_reasons: List[str]


class RecommendResponse(BaseModel):
    recommendations: List[BeanRecommendation]


ACIDITY_MAP = {"낮음": 1, "중간": 3, "높음": 5}
BODY_MAP = {"가벼움": 1, "중간": 3, "묵직": 5}
CAFFEINE_MAP = {"낮음": 1, "보통": 3, "높음": 5}


def load_beans():
    with open(BEANS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def score_bean(bean: dict, pref: Preference):
    score = 0
    reasons = []

    user_acidity = ACIDITY_MAP[pref.acidity]
    diff = abs(user_acidity - bean["acidity"])
    score += max(0, 20 - diff * 5)
    if diff <= 1:
        reasons.append(f"선호하시는 {pref.acidity} 산미와 잘 맞아요")

    user_body = BODY_MAP[pref.body]
    diff = abs(user_body - bean["body"])
    score += max(0, 20 - diff * 5)
    if diff <= 1:
        reasons.append(f"{pref.body} 바디감을 좋아하신다면 추천")

    if pref.roast == bean["roast"]:
        score += 15
        reasons.append(f"{pref.roast} 로스팅 정확히 일치")

    if pref.flavor == bean["flavor_category"]:
        score += 20
        reasons.append(f"{pref.flavor} 계열 풍미가 뚜렷")

    diff = abs(pref.sweetness - bean["sweetness"])
    score += max(0, 10 - diff * 2)

    user_caffeine = CAFFEINE_MAP[pref.caffeine]
    bean_caffeine = CAFFEINE_MAP[bean["caffeine"]]
    if user_caffeine == bean_caffeine:
        score += 10
    elif abs(user_caffeine - bean_caffeine) <= 2:
        score += 5

    if pref.brew_method in bean["recommended_brew"]:
        score += 5
        reasons.append(f"{pref.brew_method} 추출에 잘 어울려요")

    return score, reasons


@app.get("/")
def root():
    return {
        "service": "Coffee Bean Recommender API",
        "endpoints": ["/health", "/recommend"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(pref: Preference):
    beans = load_beans()
    scored = []
    for bean in beans:
        score, reasons = score_bean(bean, pref)
        scored.append({
            "name": bean["name"],
            "origin": bean["origin"],
            "score": score,
            "roast": bean["roast"],
            "flavor_category": bean["flavor_category"],
            "flavor_notes": bean["flavor_notes"],
            "acidity": bean["acidity"],
            "body": bean["body"],
            "sweetness": bean["sweetness"],
            "caffeine": bean["caffeine"],
            "brew_tip": bean["brew_tip"],
            "description": bean["description"],
            "match_reasons": reasons,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top3 = scored[:3]
    for i, bean in enumerate(top3, 1):
        bean["rank"] = i

    return {"recommendations": top3}
