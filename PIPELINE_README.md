# 모두의 창업 — 스코어링·예측 파이프라인

> 목적: 발표 전에 알고리즘 예측을 lock하고, 발표 후 공식 결과와 비교해 알고리즘 정확도를 객관 측정.

## 핵심 데이터 (2026-04-09 기준)

| 항목 | 값 |
|---|---|
| 공개 풀 | 3,797 (TECH 3,119 / LOCAL 678) |
| 비공개 풀 (블랙박스) | ~2,193 |
| 모집 마감 | 2026-05-15 |
| 슬롯 | TECH 4,000 / LOCAL 1,000 (총 5,000) |
| **현재 lock 상태** | `predictions_v1_locked.csv` (sha256 in `.meta.json`) |

## 파일 구조

```
modoo/
├── crawl_modoo.py                  # API 크롤러 (AES 복호화 포함)
├── modoo_ideas_20260409_1105.csv   # v1 lock 시점 스냅샷
├── prompt_local.md                 # LOCAL 3축 스코어링 루브릭 (공식)
├── prompt_tech.md                  # TECH 3축 스코어링 루브릭 (추정)
├── score_input_{tech,local}_*.txt  # 에이전트 입력 (id|summary, blinded)
├── scores_{tech,local}_*.jsonl     # 에이전트 출력 (s1/s2/s3/r)
├── merge_scores.py                 # jsonl 병합 → scores_merged.csv
├── scores_merged.csv               # 모든 스코어 + 원본 메타 결합
├── sanity_check.py                 # 분포·상관계수 검증
├── build_predictions.py            # 시나리오별 컷오프 적용 → predictions
├── predictions_v1_locked.csv       # ★ v1 lock (3가지 시나리오)
├── predictions_v1_locked.meta.json # ★ 메타데이터 + SHA256
├── incremental_update.py           # 주간 재크롤링 + 신규 항목 식별
├── final_lock.py                   # 5/15 마감 직후 최종 lock
└── PIPELINE_README.md              # 이 파일
```

## 스코어링 방법

### 차원 (각 1-10점 정수)

**LOCAL** (공식 심사 기준 그대로):
- s1 차별성 — 기존 서비스·제품 대비 차이
- s2 지역가치 — 지역 자원·특색 활용도 (핵심)
- s3 성장가능성 — 지역 정착 + 시장 확장

**TECH** (공식 기준 미공개, 표준 정부 창업지원 기준 추정):
- s1 차별성·혁신성 — 기술 차별점, 데이터·하드웨어 moat
- s2 사업성·시장성 — 명확한 고객·수익모델·TAM
- s3 성장가능성 — 확장성·SaaS 단위경제성·글로벌 잠재력

### 편향 통제

- **블라인딩**: 닉네임, 좋아요 수, division 태그, 등록 시각 모두 제거. id + 한 줄 요약만 입력.
- **검증**: 좋아요-점수 상관계수 = TECH 0.036 / LOCAL 0.049 → **거의 0**, 인기 anchoring 없음.
- **캘리브레이션**: 평균 5-6, 분포 3-9 강제 (rubric에 명시).
- **분야별 분리 스코어링**: TECH·LOCAL 다른 루브릭, 다른 통과율, 비교 안 함.

### 실행

```bash
# 1. 스코어링 입력 준비 (이미 됐음, 재실행 시 chunks 다시 split)
# 2. 10개 general-purpose Claude 서브에이전트 병렬 실행
#    - LOCAL 2개 chunk × 339건
#    - TECH 8개 chunk × ~390건
#    - 각 에이전트는 prompt_*.md 를 읽고 score_input_*.txt 를 jsonl로 출력
# 3. 병합 + 검증
python merge_scores.py
python sanity_check.py
# 4. 예측 파일 생성 (시나리오 컷오프)
python build_predictions.py
```

## v1 Lock 결과 (3개 시나리오)

| 시나리오 | TECH PASS | LOCAL PASS | 가정 |
|---|---:|---:|---|
| optimistic_82_94 | 2,558 / 3,119 | 637 / 678 | 최종 ~6,000명 (현재 비율 유지) |
| medium_50_60 | 1,560 / 3,119 | 407 / 678 | 최종 ~10,000명 |
| pessimistic_30_40 | 936 / 3,119 | 271 / 678 | 최종 ~16,000명 |

**현실 추정**: 예비창업패키지 50:1 경쟁률 참고하면 medium ~ pessimistic 사이 가능성 큼.

## 마감일 워크플로 (2026-05-15)

1. **마감 직전 재크롤링** + 신규 항목 스코어링
   ```bash
   python incremental_update.py
   # → score_input_NEW_*.txt 생성
   # 서브에이전트 dispatch → scores_*_NEW.jsonl
   python merge_scores.py
   ```

2. **최종 lock**
   ```bash
   python final_lock.py
   # → 실제 분모로 통과율 계산, predictions_FINAL_locked.csv + sha256 + git commit
   ```

3. **발표 후 평가** (별도 스크립트로 작성 예정)
   - 합격자 명단 수동/크롤로 확보
   - Precision/Recall/F1 (FAIL 클래스 기준)
   - AUROC, Brier, Calibration plot
   - 베이스라인 4종 비교: ① 전원 PASS ② 랜덤 ③ 좋아요/일 정렬 ④ 우리 알고리즘
   - 페르소나 5인 (앞서 진행한 분석)의 Top 10 픽 적중률 역추적

## 한계 (정직한 명시)

1. **한 줄 요약만 사용** — 심사위원은 본문·팀·영상까지 봄. 우리는 못 봄. **천장 낮음**.
2. **단일 스코어링 패스** — 같은 항목을 여러 번 평가하지 않음. 노이즈 ±1점 가능.
3. **비공개 풀 보이지 않음** — 약 2,193건 (~37%) 의 ground truth 없음.
4. **TECH 기준은 추정** — 공식 기준 미공개. 실제 심사 기준과 어긋나면 예측 성능 저하.
5. **공개/비공개 품질 분포 동일 가정** — 사실은 다를 가능성. 만약 비공개가 평균적으로 더 강하면 우리 PASS 예측이 과대평가.

이 한계들을 발표 후 평가에 반영해 "어디서 틀렸나"를 분석할 예정.

## 무결성

- v1 lock 파일 SHA256: `predictions_v1_locked.meta.json` 에 저장
- 최종 lock 시 git commit으로 변경 불가 증빙 추가
