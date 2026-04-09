# 모두의 창업 — 합격 예측 알고리즘

> "모두의 창업" 공모 (TECH 4,000명 + LOCAL 1,000명 선발) 의 합격자를 사전 예측하는 실험.
> 발표 전 알고리즘을 lock하고, 발표 후 공식 결과와 비교해 정확도를 객관 측정한다.

## 핵심 질문

**한 줄 아이디어 요약만 가지고, 심사위원이 누구를 뽑을지 예측할 수 있는가?**

- 심사위원은 본문·팀·영상까지 본다 → 우리는 한 줄만 본다 (정보 격차)
- 그래도 의미 있는 신호가 있을지, 그 천장이 어디인지를 측정하는 게 목적

## 데이터 (2026-04-09 lock 시점)

| 항목 | 값 |
|---|---:|
| 공개 풀 | 3,797 |
| └─ TECH | 3,119 |
| └─ LOCAL | 678 |
| 비공개 풀 (불가시) | ~2,193 |
| 슬롯 | 5,000 (TECH 4,000 / LOCAL 1,000) |
| 모집 마감 | 2026-05-15 |

데이터 출처: https://www.modoo.or.kr/idea/list (AES-CBC 암호화 API, 복호화 코드 `scripts/crawl_modoo.py`)

## 방법론 한눈에

```
크롤링 → 블라인딩 → 3축 스코어링 → 검증 → 컷오프 → Lock(SHA256)
                                                       ↓
                                              발표 후 정답 비교
```

### 1. 블라인딩
닉네임·좋아요 수·등록 시각·division 태그 모두 제거. id + 한 줄 요약만 평가자(LLM 서브에이전트)에게 노출.

### 2. 분야별 3축 스코어링 (각 1-10점)

| 차원 | LOCAL (공식 기준) | TECH (정부 표준 추정) |
|---|---|---|
| s1 | 차별성 | 차별성·혁신성 |
| s2 | **지역가치** | 사업성·시장성 |
| s3 | 성장가능성 | 성장가능성 |

LOCAL은 모두의창업 공식 심사 기준 그대로. TECH는 공식 미공개라 한국 정부 창업지원사업 표준에서 추정.

### 3. 검증
- **좋아요-점수 상관계수: TECH 0.036, LOCAL 0.049** → 거의 0, 인기 anchoring 없음 (블라인딩 성공)
- 분포: 평균 13.87/30(TECH), 14.53/30(LOCAL), 범위 3-28
- 상위/하위 직관과 일치 (top: 진주성 VR / SBOM AI, bottom: 슬로건 한 줄)

### 4. Lock + SHA256
`predictions/predictions_v1_locked.csv` + `.meta.json` (SHA256 해시 기록).
발표 후 변경 불가능을 증명.

## 디렉토리

```
.
├── README.md                          # 이 파일
├── PIPELINE_README.md                 # 상세 파이프라인
├── PERSONA_ANALYSIS.md                # 보조 실험: 5인 페르소나 교차 분석
├── prompts/
│   ├── prompt_local.md                # LOCAL 스코어링 루브릭 (공식)
│   └── prompt_tech.md                 # TECH 스코어링 루브릭 (추정)
├── scripts/
│   ├── crawl_modoo.py                 # API 크롤러 + AES 복호화
│   ├── merge_scores.py                # jsonl → csv 병합
│   ├── sanity_check.py                # 분포·상관 검증
│   ├── build_predictions.py           # 컷오프 적용 → 예측 파일
│   ├── incremental_update.py          # 주간 재크롤링 (마감까지)
│   └── final_lock.py                  # 5/15 최종 lock
├── data/
│   ├── modoo_ideas_20260409_1105.csv  # v1 lock 시점 스냅샷 (닉네임 제거)
│   ├── scores_merged.csv              # 모든 스코어 결합 (닉네임 제거)
│   └── raw_scores/                    # 서브에이전트 원본 jsonl 출력
└── predictions/
    ├── predictions_v1_locked.csv      # ⭐ v1 예측 (3 시나리오 컷오프)
    └── predictions_v1_locked.meta.json # SHA256 + 메타데이터
```

## 재현하기

### 0. 의존성
```bash
pip install pycryptodome
```

### 1. 크롤링
```bash
cd scripts
python crawl_modoo.py
# → modoo_ideas_YYYYMMDD_HHMM.csv 생성
```

### 2. 블라인딩 + 분할 (수동)
공개 풀을 TECH/LOCAL로 나누고, 각 분야를 chunks로 split → `score_input_*.txt` 생성. (split 코드는 README 하단 참고)

### 3. 스코어링
LLM 서브에이전트(Claude/GPT) 10개 병렬 디스패치, 각자 `prompt_*.md`를 읽고 `score_input_*.txt`를 `scores_*.jsonl`로 출력. 본 프로젝트에서는 Claude Code의 general-purpose 서브에이전트 사용.

### 4. 병합·검증
```bash
python merge_scores.py
python sanity_check.py
```

### 5. 예측 lock
```bash
python build_predictions.py
# → predictions_v1_locked.csv + .meta.json (SHA256)
```

### 6. (마감까지) 주기적 재크롤링
```bash
python incremental_update.py
# → 신규 항목만 추출, 다시 스코어링 후 step 4-5 반복
```

### 7. 최종 lock (2026-05-15)
```bash
python final_lock.py
# → 실제 분모로 통과율 계산, predictions_FINAL_locked.csv + git commit
```

### 8. 발표 후 평가 (예정)
- Precision/Recall/F1 (FAIL 클래스 기준)
- AUROC, Brier score, Calibration plot
- 베이스라인 4종 비교: 전원 PASS, 랜덤, 좋아요/일 정렬, 우리 알고리즘
- 한계 분석: 어디서 틀렸나, 천장이 어디였나

## 한계 (정직 명시)

1. **한 줄 요약만 사용** — 심사위원은 본문·팀·영상·피치까지 본다. 예측 천장이 낮음.
2. **단일 스코어링 패스** — 같은 항목 N회 평가로 노이즈 줄이지 않음.
3. **비공개 풀 (~37%) 보이지 않음** — 정답과 우리 예측의 일부만 비교 가능.
4. **TECH 기준은 추정** — 공식 미공개. 실제 심사 기준과 어긋나면 성능 저하.
5. **공개/비공개 품질 분포 동일 가정** — 비공개가 더 강하면 우리 PASS 예측 과대평가.

## 보조 실험: 5인 페르소나 교차 분석

`PERSONA_ANALYSIS.md` 참조. 동일 데이터를 5명의 다른 페르소나(VC, 소상공인, PM, 로컬 크리에이터, 연쇄창업가)에게 평가시켜 합의/마찰을 분석.

## 라이선스

MIT (코드). 데이터는 modoo.or.kr 의 공개 데이터 + 본 프로젝트의 LLM 스코어링 결과.
