---
title: "파일 기반 가계부 콘솔 프로그램 단계별 진행 계획"
created: 2026-06-01
mission: "2주차 1단계 - 파일 기반 가계부 콘솔 프로그램 만들기"
tags:
  - plan
  - roadmap
  - vibe-coding
  - Python
  - CLI
  - Docker
  - GitHub
---

# 파일 기반 가계부 콘솔 프로그램 단계별 진행 계획

> [!summary]
> 이 문서는 나중에 바이브코딩으로 한 단계씩 진행하기 좋도록 프로젝트 구현 순서를 나눈 계획서다.  
> 각 단계는 **목표 → 할 일 → 완료 기준** 순서로 정리한다.

## 전체 흐름

```text
0단계 기준 정하기
→ 1단계 프로젝트 뼈대
→ 2단계 Docker 개발 기준 잡기
→ 3단계 데이터 모델과 저장소
→ 4단계 카테고리 기능
→ 5단계 거래 추가
→ 6단계 거래 목록
→ 7단계 거래 검색
→ 8단계 월별 요약
→ 9단계 예산 기능
→ 10단계 수정/삭제
→ 11단계 CSV import/export
→ 12단계 데코레이터와 공통 오류 처리
→ 13단계 Docker 실행 환경 구성
→ 14단계 README와 최종 문서 정리
→ 15단계 테스트 시나리오 점검
→ 16단계 GitHub 원격 저장소 연결
→ 17단계 다른 Mac에서 재현 검증
```

---

# 0단계. 프로젝트 기준 정하기

## 목표

구현 전에 중요한 선택지를 먼저 고정한다.  
이 단계에서 방향을 정해두면 이후 구현 중 구조가 흔들리지 않는다.

## 할 일

- 내부 저장 포맷 결정
  - 추천: `JSONL`
- CSV import/export 포맷 결정
  - 요구사항상 CSV 스키마 필요
- 기본 저장 폴더 결정
  - 추천: `./data`
- 저장 파일 이름 결정
  - `transactions.jsonl`
  - `categories.jsonl`
  - `budgets.jsonl`
- `update` 방식 결정
  - 옵션 기반
  - 또는 대화형 기반
- 카테고리 삭제 정책 결정
  - 추천: 사용 중인 카테고리는 삭제 차단
- 기본 카테고리 자동 생성 여부 결정
  - 예: `food`, `transport`, `rent`, `salary`
- Docker 사용 방식 결정
  - 로컬 Python 실행도 지원할지
  - Docker 실행을 기본 권장 방식으로 둘지
  - 데이터 파일을 컨테이너 안에 둘지, 호스트의 `./data`를 마운트할지
- GitHub 업로드 정책 결정
  - `data/` 실제 가계부 데이터는 Git에 올리지 않는 것을 추천
  - 대신 `data/.gitkeep` 또는 샘플 CSV만 관리

## 완료 기준

- 저장 방식, 파일 구조, 명령 정책이 결정되어 있다.
- Docker와 GitHub에서 어떤 파일을 관리할지 결정되어 있다.
- 이후 단계에서 설계 선택을 다시 고민하지 않아도 된다.

---

# 1단계. 프로젝트 뼈대 만들기

## 목표

실행 가능한 최소 Python 패키지 구조를 만든다.

## 할 일

- 패키지 폴더 생성
  - `budget_app/`
- 기본 모듈 생성
  - `budget_app/__main__.py`
  - `budget_app/cli.py`
  - `budget_app/models.py`
  - `budget_app/storage.py`
  - `budget_app/services.py`
  - `budget_app/validators.py`
  - `budget_app/decorators.py`
- `python -m budget_app --help` 실행 가능하게 만들기
- `argparse` 기반 CLI 틀 만들기
- README 초안 생성
- `.gitignore` 초안 생성
  - `__pycache__/`
  - `.pytest_cache/`
  - `.venv/`
  - `data/*.jsonl`
  - `*.log`

## 완료 기준

```bash
python -m budget_app --help
```

위 명령이 오류 없이 실행된다.

---

# 2단계. Docker 개발 기준 잡기

## 목표

나중에 맥북이 아닌 아이맥에서도 같은 방식으로 실행할 수 있도록 Docker 기준을 먼저 정한다.

이 단계에서는 완성된 Docker 환경을 만들기보다, **어떤 방식으로 Docker화할지 설계만 고정**한다.

## 할 일

- Python 버전 결정
  - 미션 요구: Python 3.10 이상
  - 추천: `python:3.11-slim`
- Docker 실행 방식 결정
  - 추천: 프로젝트 폴더를 컨테이너에 마운트해서 실행
- 데이터 저장 방식 결정
  - 추천: 호스트의 `./data` 폴더를 컨테이너에 마운트
  - 이유: 컨테이너를 지워도 가계부 데이터가 남아야 함
- Docker에서 실행할 기본 명령 결정
  - 예: `python -m budget_app --help`
  - 예: `python -m budget_app list`
- 나중에 만들 파일 목록 정리
  - `Dockerfile`
  - `docker-compose.yml`
  - `.dockerignore`
- GitHub에 올릴 파일과 올리지 않을 파일 정리
  - 올릴 것: 소스 코드, 문서, Docker 설정, README
  - 올리지 않을 것: 개인 가계부 데이터, 캐시, 가상환경

## 완료 기준

- Docker에서 어떤 Python 이미지를 쓸지 정해져 있다.
- 데이터 보존을 위해 `./data`를 마운트한다는 정책이 정해져 있다.
- 이후 구현할 때 Docker를 고려한 파일 경로 정책을 유지할 수 있다.

---

# 3단계. 데이터 모델과 저장소 구현

## 목표

거래, 카테고리, 예산 데이터를 파일에 저장하고 다시 읽을 수 있게 만든다.

## 할 일

- `Transaction` dataclass 정의
- `Budget` dataclass 정의
- 필요하면 `Category` 모델 정의
- JSONL 읽기 함수 구현
- JSONL 쓰기 함수 구현
- `./data` 폴더 자동 생성
- 저장 파일 자동 초기화
  - `transactions.jsonl`
  - `categories.jsonl`
  - `budgets.jsonl`
- Docker 컨테이너 안에서도 동일하게 동작하도록 상대 경로 기준 유지
  - 기본값: `./data`
  - 옵션: `--data-dir`
- 거래 ID 생성 규칙 구현
  - 예: `TX-000001`
- 거래를 한 줄씩 읽는 제너레이터 구현
- 파일이 없거나 비어 있을 때 안전하게 처리

## 완료 기준

- 코드 내부에서 거래를 저장하고 다시 읽을 수 있다.
- 저장 파일이 없을 때도 프로그램이 깨지지 않는다.
- 거래 조회가 제너레이터 기반으로 동작한다.
- 로컬과 Docker 모두 같은 `./data` 구조를 사용할 수 있는 형태다.

---

# 4단계. category 기능 구현

## 목표

거래 추가 전에 필요한 카테고리 관리 기능을 만든다.

## 할 일

- `category add` 구현
- `category list` 구현
- `category remove` 구현
- 중복 카테고리 추가 방지
- 빈 카테고리 이름 방지
- 사용 중인 카테고리 삭제 차단
- 카테고리 저장 파일과 연동

## 완료 기준

```bash
python -m budget_app category add food
python -m budget_app category list
python -m budget_app category remove food
```

위 명령들이 정상 동작한다.

---

# 5단계. add 기능 구현

## 목표

대화형 입력으로 거래를 추가할 수 있게 만든다.

## 할 일

- `add` 명령 구현
- 대화형 입력 구현
  - 날짜
  - 타입
  - 카테고리
  - 금액
  - 메모
  - 태그
- 날짜 형식 검증
- 타입 검증
  - `income`
  - `expense`
- 금액 검증
  - 양수 정수
- 카테고리 존재 여부 확인
- 태그 쉼표 구분 처리
- 저장 성공 메시지 출력
- 생성된 거래 ID 출력

## 완료 기준

```bash
python -m budget_app add
```

위 명령으로 거래가 저장된다.

저장 완료 후 다음과 비슷한 메시지가 출력된다.

```text
[저장 완료] id=TX-000001
```

---

# 6단계. list 기능 구현

## 목표

저장된 거래 목록을 최신순으로 확인할 수 있게 만든다.

## 할 일

- `list` 명령 구현
- `--limit N` 옵션 지원
- 최신순 출력
- 거래가 없을 때 안내 메시지 출력
- 출력 포맷 정리
- 제너레이터 기반 읽기 유지

## 완료 기준

```bash
python -m budget_app list --limit 3
```

위 명령으로 최신 거래 3개가 출력된다.

---

# 7단계. search 기능 구현

## 목표

조건 기반으로 거래를 검색할 수 있게 만든다.

## 할 일

- `search` 명령 구현
- 기간 조건 지원
  - `--from`
  - `--to`
- 카테고리 조건 지원
  - `--category`
- 타입 조건 지원
  - `--type`
- 메모 키워드 조건 지원
  - `-q`
- 태그 조건 지원
  - `--tag`
- 여러 조건 조합 처리
- 검색 결과 최신순 출력
- 검색 결과가 없을 때 안내 메시지 출력
- 제너레이터 기반 검색 유지

## 완료 기준

```bash
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food --type expense
```

위처럼 여러 조건을 조합해 거래를 검색할 수 있다.

---

# 8단계. summary 기능 구현

## 목표

특정 월의 수입, 지출, 잔액, 카테고리별 지출 요약을 출력한다.

## 할 일

- `summary --month YYYY-MM` 구현
- 해당 월 거래 필터링
- 총수입 계산
- 총지출 계산
- 잔액 계산
- 카테고리별 지출 합계 계산
- `--top N` 옵션 지원
- 데이터가 없는 달 처리
- 출력 포맷 정리

## 완료 기준

```bash
python -m budget_app summary --month 2024-01 --top 3
```

위 명령으로 다음 정보를 볼 수 있다.

- 총수입
- 총지출
- 잔액
- 카테고리별 지출 TOP 3

---

# 9단계. budget 기능 구현

## 목표

월별 예산을 저장하고 `summary` 결과와 연결한다.

## 할 일

- `budget set --month YYYY-MM --amount 금액` 구현
- 월별 예산 저장
- 기존 월 예산이 있으면 갱신
- 예산 금액 검증
- `summary`에서 예산 정보 출력
- 예산 사용률 계산
- 예산 초과 여부 출력
- 예산 초과 시 경고 메시지 출력

## 완료 기준

```bash
python -m budget_app budget set --month 2024-01 --amount 500000
python -m budget_app summary --month 2024-01
```

`summary`에서 예산 대비 사용률과 초과 여부가 보인다.

---

# 10단계. update/delete 구현

## 목표

기존 거래를 ID 기준으로 수정하거나 삭제할 수 있게 만든다.

## 할 일

- `delete --id <id>` 구현
- 존재하지 않는 ID 처리
- `update --id <id>` 구현
- update 방식 적용
  - 0단계에서 정한 옵션 기반 또는 대화형 기반
- 수정하지 않은 필드는 기존 값 유지
- 수정 입력값 검증
- 카테고리 변경 시 존재 여부 확인
- 임시 파일 작성 후 rename 방식 적용
- 수정/삭제 성공 메시지 출력

## 완료 기준

```bash
python -m budget_app delete --id TX-000001
python -m budget_app update --id TX-000002 --amount 18000
```

위 명령으로 거래를 안전하게 수정/삭제할 수 있다.

---

# 11단계. CSV import/export 구현

## 목표

CSV 파일로 거래를 일괄 등록하고, 조건에 맞는 거래를 CSV로 내보낸다.

## 할 일

- `import --from <csv>` 구현
- CSV 헤더 검증
- 필수 컬럼 검증
- 행별 데이터 검증
- 유효한 거래 저장
- 처리 건수 출력
- `export --out <csv> --month YYYY-MM` 구현
- `export --out <csv> --from YYYY-MM-DD --to YYYY-MM-DD` 구현
- export 조건 필수 처리
- UTF-8 인코딩 적용
- CSV 헤더 포함
- 태그를 쉼표 구분 문자열로 변환

## 완료 기준

```bash
python -m budget_app import --from input.csv
python -m budget_app export --out output.csv --month 2024-01
```

CSV로 거래를 가져오고 내보낼 수 있다.

---

# 12단계. 데코레이터와 공통 오류 처리

## 목표

프로그램 전체의 안정성과 사용자 경험을 정리한다.

## 할 일

- 예외 처리 데코레이터 구현
- 실행 시간 측정 데코레이터 구현
- 필요하면 로그 데코레이터 구현
- 스택트레이스 직접 출력 방지
- 사용자 친화 오류 메시지 출력
- 오류 원인과 해결 힌트 제공
- 정상 종료 exit code `0`
- 오류 종료 exit code `0`이 아닌 값
- 주요 명령에 데코레이터 적용

## 완료 기준

오류가 발생해도 다음처럼 출력된다.

```text
[오류] 날짜 형식이 올바르지 않습니다: 2024-13-01
힌트: YYYY-MM-DD 형식으로 입력하세요. 예) 2024-01-15
```

---

# 13단계. Docker 실행 환경 구성

## 목표

맥북, 아이맥 등 어떤 Mac에서 실행해도 같은 Python 환경으로 동작하도록 Docker 실행 환경을 만든다.

## 할 일

- `Dockerfile` 작성
  - Python 3.10 이상 이미지 사용
  - 추천: `python:3.11-slim`
  - 작업 디렉터리 설정
  - 프로젝트 파일 복사 또는 마운트 기준 정리
- `.dockerignore` 작성
  - `.git`
  - `__pycache__/`
  - `.pytest_cache/`
  - `.venv/`
  - `data/*.jsonl`
  - 불필요한 로컬 파일 제외
- `docker-compose.yml` 작성
  - 현재 프로젝트를 컨테이너에 마운트
  - `./data`를 컨테이너의 데이터 폴더로 마운트
  - 기본 실행 명령 또는 쉘 진입 명령 제공
- Docker 실행 명령 정리
  - 이미지 빌드
  - help 실행
  - `add`, `list`, `summary` 등 명령 실행
- Docker 안에서 파일 권한과 데이터 저장 위치 확인
- 로컬 Python 실행과 Docker 실행이 같은 결과를 내는지 비교

## 완료 기준

다음과 비슷한 명령이 동작한다.

```bash
docker compose run --rm app python -m budget_app --help
docker compose run --rm app python -m budget_app list --limit 3
```

Docker에서 실행해도 `./data`에 데이터가 저장되고, 컨테이너를 삭제해도 데이터가 유지된다.

---

# 14단계. README와 최종 문서 정리

## 목표

제출 가능한 수준으로 사용법과 내부 구조를 문서화한다.

## 할 일

- 실행 방법 작성
- 저장 파일 위치 작성
- 저장 파일 형식 작성
- 주요 명령 예시 작성
- Docker 실행 방법 작성
  - Docker 설치 필요 여부
  - 이미지 빌드 방법
  - `docker compose run --rm app ...` 사용 예시
  - `./data` 볼륨 마운트 설명
- CSV import/export 스키마 작성
- update 정책 작성
- category 삭제 정책 작성
- 데이터 초기화 정책 작성
- GitHub에서 clone 후 실행하는 방법 작성
- 기능 목록 체크리스트 작성
- 선택 구현 사항이 있다면 별도 표시

## 완료 기준

README만 보고 다음을 알 수 있다.

- 어떻게 실행하는지
- 데이터가 어디 저장되는지
- 어떤 명령을 사용할 수 있는지
- Docker로 어떻게 실행하는지
- 다른 Mac에서 어떻게 같은 환경을 재현하는지
- CSV는 어떤 형식이어야 하는지
- 오류 상황은 어떻게 처리되는지

---

# 15단계. 테스트 시나리오 점검

## 목표

실제 터미널에서 요구사항이 정상 동작하는지 확인한다.

## 할 일

- 정상 흐름 테스트
  - 카테고리 추가
  - 거래 추가
  - 목록 조회
  - 검색
  - 요약
  - 예산 설정
  - 수정
  - 삭제
  - import
  - export
- 오류 케이스 테스트
  - 잘못된 날짜
  - 잘못된 금액
  - 존재하지 않는 카테고리
  - 존재하지 않는 ID
  - 빈 데이터 summary
  - 잘못된 CSV 헤더
  - export 조건 누락
- 파일 안정성 확인
  - update/delete 후 파일이 깨지지 않는지 확인
- README 명령 예시 검증
- Docker 실행 테스트
  - `docker compose run --rm app python -m budget_app --help`
  - `docker compose run --rm app python -m budget_app list`
  - `docker compose run --rm app python -m budget_app summary --month YYYY-MM`
- Docker에서 생성한 데이터가 호스트 `./data`에 남는지 확인

## 완료 기준

- 주요 기능이 터미널에서 실제로 동작한다.
- 오류 상황에서도 프로그램이 친절하게 안내한다.
- Docker 환경에서도 동일하게 동작한다.
- 제출 전 체크리스트를 통과한다.

---

# 16단계. GitHub 원격 저장소 연결

## 목표

프로젝트를 GitHub 원격 저장소에 올려 맥북과 아이맥에서 같은 코드를 받을 수 있게 만든다.

## 할 일

- 로컬 Git 상태 확인
  - 변경 파일 확인
  - 커밋 누락 여부 확인
- `.gitignore` 점검
  - 개인 데이터 파일이 올라가지 않도록 확인
  - 예: `data/*.jsonl`
- GitHub에서 새 원격 저장소 생성
- 로컬 저장소에 remote 연결
  - 예: `origin`
- 첫 push 진행
- GitHub 웹에서 파일이 정상 업로드됐는지 확인
- README가 GitHub에서 보기 좋게 렌더링되는지 확인

## 완료 기준

GitHub 원격 저장소에 다음 파일들이 올라가 있다.

- `budget_app/` 소스 코드
- `docs/` 문서
- `README.md`
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `.gitignore`

개인 가계부 데이터 파일은 올라가지 않는다.

---

# 17단계. 다른 Mac에서 재현 검증

## 목표

아이맥 같은 다른 Mac에서 GitHub 저장소를 clone한 뒤 Docker로 동일하게 실행되는지 확인한다.

## 할 일

- 아이맥에 필요한 도구 확인
  - Git
  - Docker Desktop
- GitHub 저장소 clone

```bash
git clone <repository-url>
```

- 프로젝트 폴더로 이동

```bash
cd <repository-name>
```

- Docker 이미지 빌드 또는 compose 실행

```bash
docker compose build
docker compose run --rm app python -m budget_app --help
```

- 기본 기능 실행 확인
  - `category list`
  - `add`
  - `list`
  - `summary`
- `./data` 폴더가 자동 생성되는지 확인
- 컨테이너를 지웠다가 다시 실행해도 `./data` 데이터가 유지되는지 확인
- README의 안내만 보고 실행 가능한지 확인

## 완료 기준

- 아이맥에서 별도 Python 설치나 가상환경 세팅 없이 Docker로 실행된다.
- 맥북과 아이맥에서 같은 명령이 같은 방식으로 동작한다.
- 데이터는 각 Mac의 로컬 `./data` 폴더에 저장된다.

---

# 바이브코딩 진행 예시

나중에 다음처럼 한 단계씩 요청하면 된다.

```text
0단계 기준 정하기부터 하자.
1단계 프로젝트 뼈대 만들어줘.
2단계 Docker 개발 기준 잡자.
3단계 데이터 모델과 저장소 구현하자.
5단계 add 기능만 구현하고 테스트하자.
13단계 Docker 실행 환경 구성하자.
16단계 GitHub 원격 저장소 연결하자.
17단계 아이맥에서 재현 검증하는 순서 정리하자.
```

> [!tip]
> 한 번에 여러 단계를 밀기보다, 한 단계 구현 후 실행 확인까지 하고 다음 단계로 넘어가는 것이 좋다.  
> 이 프로젝트는 기능이 많고 Docker/GitHub 재현까지 포함하므로, 단계별로 고정하면서 가야 구조와 실행 환경이 깔끔하게 유지된다.
