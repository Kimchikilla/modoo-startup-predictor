# GitHub Actions — 자동 배포 설정

`master` 브랜치에 push되고 `site/`, `predictions/`, `scripts/build_site_data.py` 중 하나라도 바뀌면 자동으로 Cloudflare Pages에 배포됩니다.

## 1회만 설정 (필수)

### Step 1: Cloudflare API 토큰 발급

1. https://dash.cloudflare.com/profile/api-tokens 접속
2. **Create Token** 클릭
3. **Edit Cloudflare Workers** 템플릿 선택 (또는 Custom token):
   - Permissions:
     - `Account → Cloudflare Pages → Edit`
     - `User → User Details → Read` (선택)
   - Account Resources: `Include → Specific account → (본인 계정)`
4. **Continue to summary → Create Token**
5. 생성된 토큰 복사 (한 번만 보임!)

### Step 2: GitHub Secrets 등록

터미널에서 (한 번만):

```bash
cd /c/Users/User/desktop/modoo/repo
gh secret set CLOUDFLARE_API_TOKEN --body "여기에_복사한_토큰_붙여넣기"
gh secret set CLOUDFLARE_ACCOUNT_ID --body "16d2f2bea852fe397eea39749a2eab11"
```

### Step 3: 첫 실행 (테스트)

```bash
gh workflow run deploy.yml
gh run watch
```

또는 그냥 site/ 안의 파일을 하나 수정하고 push하면 자동 트리거됨.

## 작동 방식

- `site/` 변경 → 즉시 deploy
- `predictions/` 변경 → `data.json` 재생성 후 deploy
- `scripts/build_site_data.py` 변경 → data.json 재생성 후 deploy
- 그 외 파일 변경(README, scripts 외)은 deploy 안 함 (불필요한 배포 방지)
- 수동 트리거: GitHub Actions 탭 → `Deploy to Cloudflare Pages` → `Run workflow`

## 마감일 워크플로 통합

5/15 마감 후:
```bash
python scripts/incremental_update.py   # 신규 항목 크롤링
# 신규 항목 스코어링 (서브에이전트)
python scripts/merge_scores.py
python scripts/final_lock.py            # → predictions_FINAL_locked.csv
git add predictions/ && git commit -m "FINAL lock 5/15" && git push
# → GitHub Actions가 자동으로 data.json 재생성하고 사이트에 반영
```

수동 wrangler 호출 없이 git push 한 번이면 끝.
