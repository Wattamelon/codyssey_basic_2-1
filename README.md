# 파일 기반 가계부 콘솔 프로그램

Python 표준 라이브러리만 사용해 만드는 파일 기반 가계부 CLI 애플리케이션입니다.

## 현재 진행 상태

- 1단계: 프로젝트 뼈대 구성 완료
- CLI 골격과 `--help` 출력 준비
- 실제 가계부 기능은 이후 단계에서 구현 예정

## 1단계에서 진행한 것

1단계의 목표는 가계부 기능을 바로 구현하는 것이 아니라, 앞으로 기능을 넣을 수 있는 **프로젝트 기본 구조**를 만드는 것이었습니다.

쉽게 말하면 아직 집 안의 가구를 들여놓은 단계는 아니고, 집의 방 구조와 출입문을 먼저 만든 상태입니다.

이번 단계에서 진행한 일은 다음과 같습니다.

### 1. Python 패키지 폴더 생성

`budget_app/` 폴더를 만들었습니다.

```text
budget_app/
  __init__.py
  __main__.py
  cli.py
  models.py
  storage.py
  services.py
  validators.py
  decorators.py
```

이 폴더는 앞으로 가계부 프로그램의 실제 코드가 들어갈 공간입니다.

### 2. `python -m budget_app` 실행 가능하게 만들기

다음 명령으로 프로그램을 실행할 수 있게 만들었습니다.

```bash
python -m budget_app
```

이를 위해 `budget_app/__main__.py`를 만들었습니다.

`__main__.py`는 Python에서 다음 명령을 실행했을 때 가장 먼저 실행되는 파일입니다.

```bash
python -m budget_app
```

즉, `__main__.py`는 이 프로그램의 터미널 실행 진입점입니다.

### 3. CLI 파서 골격 만들기

`budget_app/cli.py`에 `argparse` 기반 CLI 구조를 만들었습니다.

현재 지원하도록 등록해둔 명령은 다음과 같습니다.

```text
add
list
search
summary
budget
category
update
delete
import
export
```

아직 각 명령의 실제 기능은 구현하지 않았습니다.  
대신 명령어와 옵션 구조를 먼저 잡아두었습니다.

예를 들어 다음 명령을 실행하면 도움말이 출력됩니다.

```bash
python -m budget_app --help
python -m budget_app list --help
python -m budget_app search --help
python -m budget_app category --help
```

이것은 앞으로 사용자가 어떤 명령을 입력할 수 있을지 미리 정리한 것입니다.

### 4. 각 모듈의 역할을 나누기 위한 빈 파일 생성

아직 기능은 없지만, 역할별 파일을 미리 나누었습니다.

| 파일 | 앞으로 담당할 역할 |
| --- | --- |
| `budget_app/__main__.py` | `python -m budget_app` 실행 진입점 |
| `budget_app/cli.py` | 명령어 파싱, 사용자 입력/출력 |
| `budget_app/models.py` | `Transaction`, `Budget` 같은 데이터 구조 |
| `budget_app/storage.py` | JSONL/CSV 파일 읽기와 쓰기 |
| `budget_app/services.py` | 거래 추가, 검색, 요약 같은 핵심 규칙 |
| `budget_app/validators.py` | 날짜, 금액, 타입 등 입력 검증 |
| `budget_app/decorators.py` | 오류 처리, 실행 시간 측정 같은 공통 기능 |

이렇게 나누는 이유는 이후 기능이 많아져도 코드가 한 파일에 뒤섞이지 않게 하기 위해서입니다.

### 5. 기본 README 작성

프로젝트 설명, 실행 방법, 예정 저장 구조를 적은 `README.md`를 만들었습니다.

README는 나중에 GitHub에 올렸을 때 프로젝트 첫 화면에 보이는 설명서 역할을 합니다.

### 6. `.gitignore` 작성

GitHub에 올리지 않을 파일들을 관리하기 위해 `.gitignore`를 만들었습니다.

현재 무시하도록 한 대표 파일은 다음과 같습니다.

```text
.DS_Store
__pycache__/
.venv/
.pytest_cache/
*.pdf
data/*.jsonl
data/*.csv
*.log
```

특히 `data/*.jsonl`, `data/*.csv`는 실제 개인 가계부 데이터가 GitHub에 올라가지 않도록 하기 위한 설정입니다.

## 1단계에서 아직 하지 않은 것

아래 기능들은 아직 구현하지 않았습니다. 이후 단계에서 하나씩 구현할 예정입니다.

- 거래 추가
- 거래 목록 조회
- 거래 검색
- 월별 요약
- 예산 설정
- 카테고리 추가/삭제
- 거래 수정/삭제
- CSV 가져오기/내보내기
- 실제 JSONL 파일 저장
- Docker 실행 환경 구성

현재는 다음 명령을 실행하면 실제 기능 대신 준비 중 메시지가 출력됩니다.

```bash
python -m budget_app add
```

출력 예시:

```text
[준비 중] 'add' 명령은 이후 단계에서 구현합니다.
```

즉, 1단계는 **실제 가계부 기능 구현 전, 프로그램이 실행될 수 있는 기본 틀을 만든 단계**입니다.

## 실행 방법

```bash
python -m budget_app --help
```

명령별 도움말 예시:

```bash
python -m budget_app list --help
python -m budget_app search --help
python -m budget_app category --help
```

## 예정 저장 구조

기본 데이터 폴더는 `./data`입니다.

```text
data/
  transactions.jsonl
  categories.jsonl
  budgets.jsonl
```

개인 가계부 데이터 파일은 Git에 올리지 않는 것을 기본 정책으로 합니다.
