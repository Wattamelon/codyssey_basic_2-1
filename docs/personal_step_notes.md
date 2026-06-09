---
title: "개인 학습 노트 - 단계별 구현 이해"
created: 2026-06-07
project: "파일 기반 가계부 콘솔 프로그램"
status: "private-note"
---

# 개인 학습 노트 - 단계별 구현 이해

> 이 문서는 프로젝트를 진행하면서 내가 헷갈리는 개념을 계속 정리하기 위한 개인 학습 노트다.  
> GitHub에 올릴 공식 문서가 아니라, 내가 이해하기 위한 설명 문서이므로 `.gitignore`에 등록해둔다.

---

# 1단계에서 한 일 전체 요약

1단계에서는 아직 가계부 기능을 구현하지 않았다.

즉, 아직 다음 기능들은 실제로 동작하지 않는다.

- 거래 추가
- 거래 목록 조회
- 거래 검색
- 월별 요약
- 예산 저장
- 카테고리 관리
- CSV import/export
- JSONL 파일 저장

1단계에서 한 일은 **프로그램이 앞으로 커질 수 있도록 기본 구조를 만든 것**이다.

쉽게 말하면 다음과 같다.

```text
아직 가게 영업을 시작한 것이 아니다.
간판을 달고, 출입문을 만들고, 계산대 자리와 창고 자리를 정해둔 상태다.
```

이번 단계의 핵심 목표는 세 가지였다.

1. `python -m budget_app` 명령으로 프로그램이 실행되게 만들기
2. `argparse`로 명령어 구조를 미리 잡기
3. 앞으로 들어갈 코드를 역할별 파일로 나누기

---

# 1단계에서 만들어진 파일 목록

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

README.md
.gitignore
```

각 파일은 아직 완성된 기능을 담고 있는 것이 아니라, 앞으로 기능을 넣기 위한 자리다.

---

# `budget_app/` 폴더는 왜 만들었을까?

`budget_app/`는 이 프로젝트의 Python 패키지 폴더다.

Python에서 패키지는 관련된 코드 파일들을 하나의 묶음으로 관리하는 폴더다.

이번 프로젝트는 단순한 스크립트 하나가 아니다.

미션 요구사항을 보면 기능이 많다.

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

이 기능을 전부 `main.py` 하나에 넣으면 처음에는 편해 보여도 금방 복잡해진다.

그래서 `budget_app/`라는 패키지 폴더를 만들고, 그 안에 역할별 파일을 나누었다.

```text
budget_app/
  cli.py         -> 터미널 명령어 처리
  models.py      -> 데이터 모양
  storage.py     -> 파일 저장
  services.py    -> 가계부 규칙
  validators.py  -> 입력 검증
  decorators.py  -> 공통 처리
```

---

# `budget_app/__init__.py`

현재 코드:

```python
"""File-based budget book console application."""

__all__ = ["__version__"]

__version__ = "0.1.0"
```

## 이 파일은 무엇을 위해 만들었을까?

`__init__.py`는 이 폴더가 Python 패키지라는 것을 나타내는 파일이다.

예전 Python에서는 폴더 안에 `__init__.py`가 있어야 패키지로 인식되는 경우가 많았다.  
요즘 Python은 없어도 동작하는 경우가 있지만, 패키지의 시작점이라는 의미로 만드는 것이 일반적이다.

## 이 코드의 의미

```python
"""File-based budget book console application."""
```

이것은 모듈 설명 문자열이다.  
이 패키지가 무엇인지 짧게 설명한다.

```python
__all__ = ["__version__"]
```

이 패키지에서 외부에 공개하고 싶은 이름을 적어둔 것이다.

```python
__version__ = "0.1.0"
```

현재 앱 버전이다.

지금 당장은 꼭 필요하지 않지만, 프로젝트가 커졌을 때 버전을 표시하거나 배포할 때 사용할 수 있다.

## 초보자 관점에서 기억할 점

`__init__.py`는 "이 폴더는 Python 패키지다"라는 표시라고 보면 된다.

---

# `budget_app/__main__.py`

현재 코드:

```python
"""Module entry point for ``python -m budget_app``."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
```

## 이 파일은 무엇을 위해 만들었을까?

이 파일은 다음 명령을 가능하게 하기 위해 만들었다.

```bash
python -m budget_app
```

Python에서 `python -m 패키지명`을 실행하면, 그 패키지 안의 `__main__.py`가 실행된다.

즉:

```bash
python -m budget_app
```

를 실행하면 Python은 내부적으로:

```text
budget_app/__main__.py 파일을 실행해야겠다.
```

라고 판단한다.

## 코드 설명

```python
from .cli import main
```

같은 패키지 안에 있는 `cli.py`에서 `main` 함수를 가져온다.

여기서 `.`은 "현재 패키지"를 뜻한다.

```python
if __name__ == "__main__":
```

이 파일이 직접 실행될 때만 아래 코드를 실행하라는 뜻이다.

```python
raise SystemExit(main())
```

`main()` 함수를 실행하고, 그 반환값을 프로그램 종료 코드로 사용한다.

예를 들어:

```python
return 0
```

이면 정상 종료다.

```python
return 1
```

이면 오류 종료로 볼 수 있다.

## 왜 `cli.py`의 main을 부를까?

`__main__.py` 안에 CLI 코드를 전부 넣지 않은 이유는 역할을 나누기 위해서다.

```text
__main__.py:
실행 진입점 역할만 한다.

cli.py:
실제 명령어 파싱과 CLI 처리를 담당한다.
```

이렇게 하면 `__main__.py`는 아주 작고 단순하게 유지된다.

---

# `budget_app/cli.py`

이 파일은 1단계에서 가장 중요한 파일이다.

CLI는 Command Line Interface의 줄임말이다.  
즉, 터미널 명령어로 프로그램을 조작하는 부분이다.

## 이 파일은 무엇을 위해 만들었을까?

`cli.py`는 사용자가 입력한 명령어를 해석하기 위해 만들었다.

예:

```bash
python -m budget_app list --limit 3
```

이 명령을 프로그램이 이해하려면 다음을 알아야 한다.

```text
명령어는 list다.
limit 옵션은 3이다.
```

이 해석 작업을 `cli.py`가 담당한다.

## 현재 코드 구조

현재 `cli.py`에는 핵심 함수가 두 개 있다.

```python
def build_parser() -> argparse.ArgumentParser:
    ...

def main(argv: Sequence[str] | None = None) -> int:
    ...
```

## `build_parser()`는 무엇을 할까?

`build_parser()`는 CLI 명령어 구조를 만든다.

```python
parser = argparse.ArgumentParser(
    prog="budget_app",
    description="파일 기반 가계부 콘솔 프로그램",
)
```

이 코드는 최상위 CLI 파서를 만든다.

`prog="budget_app"`는 도움말에 표시될 프로그램 이름이다.

`description`은 도움말에 표시될 설명이다.

실행하면 이런 식으로 보인다.

```bash
python -m budget_app --help
```

```text
usage: budget_app [-h] [--data-dir DATA_DIR] <command> ...

파일 기반 가계부 콘솔 프로그램
```

## `--data-dir` 옵션

```python
parser.add_argument(
    "--data-dir",
    default="./data",
    help="저장 파일을 둘 데이터 폴더 경로 (기본값: ./data)",
)
```

이 옵션은 데이터 저장 폴더를 바꿀 수 있게 하기 위해 만들었다.

기본값은:

```text
./data
```

이다.

나중에 사용자는 이렇게 실행할 수 있다.

```bash
python -m budget_app list --data-dir ./test_data
```

또는 Docker에서도 같은 기본 경로를 사용할 수 있다.

```text
컨테이너 내부 /app/data
호스트 프로젝트의 ./data
```

## subparser는 무엇일까?

```python
subparsers = parser.add_subparsers(dest="command", metavar="<command>")
```

이 코드는 하위 명령어들을 만들 준비를 한다.

이번 앱은 명령어가 하나가 아니다.

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

이런 명령어를 등록하기 위해 subparser를 쓴다.

## `add` 명령

```python
subparsers.add_parser("add", help="거래를 대화형으로 추가합니다.")
```

이 코드는 `add` 명령을 등록한다.

아직 실제 거래 추가 기능은 없다.  
하지만 `argparse`가 `add`라는 명령어를 알아듣게 되었다.

## `list` 명령

```python
list_parser = subparsers.add_parser("list", help="거래 목록을 최신순으로 출력합니다.")
list_parser.add_argument("--limit", type=int, default=10, help="출력할 최대 거래 수")
```

이 코드는 `list` 명령과 `--limit` 옵션을 등록한다.

예:

```bash
python -m budget_app list --limit 3
```

나중에 이 명령은 최신 거래 3개를 출력하게 될 것이다.

현재는 아직 구현 전이라 준비 중 메시지만 출력한다.

## `search` 명령

```python
search_parser = subparsers.add_parser("search", help="조건에 맞는 거래를 검색합니다.")
search_parser.add_argument("--from", dest="date_from", help="검색 시작일 YYYY-MM-DD")
search_parser.add_argument("--to", dest="date_to", help="검색 종료일 YYYY-MM-DD")
search_parser.add_argument("--category", help="카테고리 조건")
search_parser.add_argument("--type", choices=["income", "expense"], help="거래 타입")
search_parser.add_argument("-q", "--query", dest="keyword", help="메모 키워드")
search_parser.add_argument("--tag", help="태그 조건")
```

이 코드는 검색 조건들을 미리 등록한다.

`--from`은 Python 예약어 `from`과 이름이 겹친다.  
그래서 내부 변수명은 `dest="date_from"`으로 바꿨다.

즉 사용자는:

```bash
--from 2024-01-01
```

라고 입력하지만, 코드 내부에서는:

```python
args.date_from
```

으로 접근하게 된다.

`--type`은 `choices=["income", "expense"]`가 있다.

이 말은 다음 두 값만 허용한다는 뜻이다.

```text
income
expense
```

## `summary` 명령

```python
summary_parser = subparsers.add_parser("summary", help="월별 요약을 출력합니다.")
summary_parser.add_argument("--month", required=True, help="요약할 월 YYYY-MM")
summary_parser.add_argument("--top", type=int, default=3, help="카테고리 TOP N")
```

`summary`는 특정 월의 요약을 출력하는 명령이다.

`--month`는 필수 옵션이다.

그래서 나중에 이렇게 실행해야 한다.

```bash
python -m budget_app summary --month 2024-01
```

`--top`은 카테고리별 지출 TOP N을 출력할 때 쓸 옵션이다.

## `budget` 명령

```python
budget_parser = subparsers.add_parser("budget", help="월별 예산을 관리합니다.")
budget_subparsers = budget_parser.add_subparsers(dest="budget_command", metavar="<action>")
budget_set_parser = budget_subparsers.add_parser("set", help="월 예산을 설정합니다.")
budget_set_parser.add_argument("--month", required=True, help="예산 월 YYYY-MM")
budget_set_parser.add_argument("--amount", required=True, type=int, help="예산 금액")
```

`budget`은 한 번 더 하위 명령을 가진다.

예:

```bash
python -m budget_app budget set --month 2024-01 --amount 500000
```

구조는 이렇게 된다.

```text
budget
  set
```

즉 `budget`이라는 큰 명령 안에 `set`이라는 작은 명령이 있다.

## `category` 명령

```python
category_parser = subparsers.add_parser("category", help="카테고리를 관리합니다.")
category_subparsers = category_parser.add_subparsers(dest="category_command", metavar="<action>")
category_add_parser = category_subparsers.add_parser("add", help="카테고리를 추가합니다.")
category_add_parser.add_argument("name", help="추가할 카테고리 이름")
category_subparsers.add_parser("list", help="카테고리 목록을 출력합니다.")
category_remove_parser = category_subparsers.add_parser("remove", help="카테고리를 삭제합니다.")
category_remove_parser.add_argument("name", help="삭제할 카테고리 이름")
```

`category`도 하위 명령을 가진다.

```text
category
  add 이름
  list
  remove 이름
```

예:

```bash
python -m budget_app category add food
python -m budget_app category list
python -m budget_app category remove food
```

여기서 `name`은 위치 인자다.

`--name food`처럼 옵션으로 쓰는 것이 아니라:

```bash
category add food
```

처럼 순서로 들어가는 값이다.

## `update`, `delete`, `import`, `export`

이 명령들도 미션 요구사항에 맞춰 미리 등록했다.

```python
update_parser = subparsers.add_parser("update", help="ID 기준으로 거래를 수정합니다.")
update_parser.add_argument("--id", required=True, help="수정할 거래 ID")
```

`update`는 ID 기준으로 거래를 수정한다.

```python
delete_parser = subparsers.add_parser("delete", help="ID 기준으로 거래를 삭제합니다.")
delete_parser.add_argument("--id", required=True, help="삭제할 거래 ID")
```

`delete`는 ID 기준으로 거래를 삭제한다.

```python
import_parser = subparsers.add_parser("import", help="CSV 파일에서 거래를 가져옵니다.")
import_parser.add_argument("--from", dest="csv_path", required=True, help="가져올 CSV 경로")
```

`import`는 CSV 파일에서 거래를 가져온다.

```python
export_parser = subparsers.add_parser("export", help="거래를 CSV 파일로 내보냅니다.")
export_parser.add_argument("--out", required=True, help="내보낼 CSV 경로")
export_parser.add_argument("--month", help="내보낼 월 YYYY-MM")
export_parser.add_argument("--from", dest="date_from", help="내보내기 시작일 YYYY-MM-DD")
export_parser.add_argument("--to", dest="date_to", help="내보내기 종료일 YYYY-MM-DD")
```

`export`는 조건에 맞는 거래를 CSV 파일로 내보낸다.

## `main()` 함수

```python
def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI parser and route to command handlers."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    print(f"[준비 중] '{args.command}' 명령은 이후 단계에서 구현합니다.")
    return 0
```

`main()`은 CLI 실행의 중심 함수다.

흐름은 다음과 같다.

```text
1. build_parser()로 명령어 해석기를 만든다.
2. parser.parse_args(argv)로 사용자가 입력한 명령어를 해석한다.
3. 명령어가 없으면 help를 출력한다.
4. 명령어가 있으면 현재는 준비 중 메시지를 출력한다.
5. 정상 종료 코드 0을 반환한다.
```

현재는 아직 실제 명령 처리 함수가 없다.

나중에는 이런 식으로 바뀔 것이다.

```python
if args.command == "add":
    return handle_add_command(args)

if args.command == "list":
    return handle_list_command(args)
```

지금은 1단계라서 명령 구조만 잡고, 실제 기능은 다음 단계에서 구현한다.

---

# `budget_app/models.py`

현재 코드:

```python
"""Data models for the budget application."""
```

## 이 파일은 무엇을 위해 만들었을까?

이 파일은 데이터 구조를 정의하기 위해 만들었다.

나중에 여기에 이런 클래스가 들어갈 것이다.

```python
@dataclass
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)
```

`Transaction`은 거래 한 건을 표현한다.

또 예산을 표현하는 `Budget`도 들어갈 수 있다.

```python
@dataclass
class Budget:
    month: str
    amount: int
```

## 왜 따로 분리했을까?

데이터 구조는 여러 곳에서 쓰인다.

```text
storage.py:
파일에서 읽은 데이터를 Transaction으로 바꿈

services.py:
Transaction을 기준으로 검색, 요약 계산

cli.py:
Transaction을 사용자에게 출력
```

그래서 데이터 구조를 `models.py`에 모아두면 다른 파일들이 공통으로 가져다 쓸 수 있다.

---

# `budget_app/storage.py`

현재 코드:

```python
"""File storage helpers for JSONL and CSV data."""
```

## 이 파일은 무엇을 위해 만들었을까?

이 파일은 파일 저장과 읽기를 담당하기 위해 만들었다.

이번 프로젝트는 데이터베이스를 쓰지 않는다.  
대신 파일을 사용한다.

예정 파일:

```text
data/
  transactions.jsonl
  categories.jsonl
  budgets.jsonl
```

그래서 나중에 `storage.py`에는 이런 함수들이 들어갈 수 있다.

```python
def ensure_data_dir(data_dir):
    ...

def append_jsonl(path, data):
    ...

def iter_jsonl(path):
    ...

def replace_jsonl(path, rows):
    ...
```

## 왜 따로 분리했을까?

파일을 여는 코드가 여러 기능에 흩어지면 유지보수가 어려워진다.

나쁜 구조:

```text
cli.py에서 파일 열기
services.py에서 파일 열기
validators.py에서 파일 열기
```

좋은 구조:

```text
storage.py만 파일 읽기/쓰기를 담당
다른 파일은 storage.py에 요청
```

이렇게 하면 나중에 저장 방식을 JSONL에서 CSV로 바꾸거나, 파일 경로 정책을 바꿀 때 수정 범위가 줄어든다.

---

# `budget_app/services.py`

현재 코드:

```python
"""Business logic services for budget operations."""
```

## 이 파일은 무엇을 위해 만들었을까?

이 파일은 가계부의 핵심 규칙을 담당하기 위해 만들었다.

예를 들어 거래 추가는 단순히 파일에 저장하는 일이 아니다.

거래 추가에는 이런 규칙이 있다.

```text
날짜가 올바른가?
타입이 income 또는 expense인가?
금액이 양수인가?
카테고리가 존재하는가?
새 ID를 어떻게 만들 것인가?
어떤 파일에 저장할 것인가?
```

이런 판단과 흐름을 `services.py`에서 담당한다.

나중에 들어갈 수 있는 함수 예:

```python
def add_transaction(...):
    ...

def search_transactions(...):
    ...

def summarize_month(...):
    ...

def set_budget(...):
    ...
```

## 왜 따로 분리했을까?

CLI는 사용자 입력과 출력에 집중해야 한다.

파일 저장은 `storage.py`가 담당해야 한다.

그 사이에서 실제 가계부 규칙을 판단하는 곳이 `services.py`다.

```text
cli.py:
사용자 입력 받기

services.py:
입력값을 바탕으로 가계부 규칙 처리

storage.py:
파일에 저장하거나 파일에서 읽기
```

---

# `budget_app/validators.py`

현재 코드:

```python
"""Input validation helpers."""
```

## 이 파일은 무엇을 위해 만들었을까?

이 파일은 입력값 검증을 담당하기 위해 만들었다.

이번 미션에서는 검증할 것이 많다.

```text
날짜가 YYYY-MM-DD 형식인가?
월이 YYYY-MM 형식인가?
금액이 양수 정수인가?
type이 income 또는 expense인가?
카테고리 이름이 비어 있지 않은가?
CSV 필수 컬럼이 있는가?
```

나중에 이런 함수들이 들어갈 수 있다.

```python
def validate_date(value):
    ...

def validate_month(value):
    ...

def validate_amount(value):
    ...

def validate_transaction_type(value):
    ...
```

## 왜 따로 분리했을까?

검증 코드는 여러 기능에서 반복된다.

예:

```text
add:
날짜, 금액, 타입 검증

update:
수정 날짜, 수정 금액, 수정 타입 검증

import:
CSV 각 행의 날짜, 금액, 타입 검증

budget:
월, 예산 금액 검증
```

검증 코드를 한곳에 모아두면 중복을 줄일 수 있다.

---

# `budget_app/decorators.py`

현재 코드:

```python
"""Reusable decorators for command handling."""
```

## 이 파일은 무엇을 위해 만들었을까?

이 파일은 여러 명령에서 공통으로 필요한 부가 기능을 담기 위해 만들었다.

예:

```text
오류 처리
실행 시간 측정
로그 출력
```

나중에 이런 데코레이터가 들어갈 수 있다.

```python
def handle_errors(func):
    ...

def measure_time(func):
    ...
```

## 왜 따로 분리했을까?

각 명령마다 try/except를 직접 쓰면 코드가 반복된다.

나쁜 구조:

```python
def handle_add_command(args):
    try:
        ...
    except AppError:
        ...

def handle_list_command(args):
    try:
        ...
    except AppError:
        ...
```

좋은 구조:

```python
@handle_errors
def handle_add_command(args):
    ...

@handle_errors
def handle_list_command(args):
    ...
```

공통 처리는 데코레이터로 빼고, 각 명령 함수는 자기 핵심 기능에 집중하게 만든다.

---

# `README.md`

## 이 파일은 무엇을 위해 만들었을까?

README는 프로젝트 설명서다.

GitHub에 올리면 저장소 첫 화면에 보인다.

README에는 최종적으로 다음 내용이 들어가야 한다.

```text
프로젝트 소개
실행 방법
주요 명령어
저장 파일 구조
CSV 스키마
Docker 실행 방법
GitHub clone 후 실행 방법
```

1단계에서는 아직 프로젝트가 완성되지 않았기 때문에, 현재 진행 상태와 기본 실행 방법만 적어두었다.

---

# `.gitignore`

## 이 파일은 무엇을 위해 만들었을까?

`.gitignore`는 Git이 추적하지 않을 파일을 적는 파일이다.

이번 프로젝트에서 GitHub에 올리면 안 되는 파일들이 있다.

대표적으로:

```text
.DS_Store
__pycache__/
.venv/
data/*.jsonl
data/*.csv
*.log
```

특히 중요한 것은 `data/*.jsonl`, `data/*.csv`다.

이 파일들은 실제 가계부 데이터가 될 수 있다.  
개인적인 수입/지출 내역이 들어갈 수 있으므로 GitHub에 올리지 않는 것이 좋다.

또 이 문서 자체도 개인 학습 노트라서 `.gitignore`에 등록했다.

```text
docs/personal_step_notes.md
```

---

# 1단계 구조를 직접 설계하려면 어떻게 생각해야 할까?

프로젝트 구조를 직접 만들 때는 처음부터 파일 이름을 외우려고 하지 않는 것이 좋다.

대신 다음 질문을 순서대로 던지면 된다.

## 1. 이 프로그램은 어떻게 실행될까?

이번 프로젝트는 CLI 프로그램이다.

실행 방식:

```bash
python -m budget_app
```

그래서 필요하다.

```text
budget_app/__main__.py
```

## 2. 사용자는 무엇을 입력할까?

사용자는 명령어를 입력한다.

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

그래서 필요하다.

```text
budget_app/cli.py
```

## 3. 이 프로그램이 다루는 데이터는 무엇일까?

이 프로그램은 거래, 카테고리, 예산을 다룬다.

그래서 필요하다.

```text
budget_app/models.py
```

## 4. 데이터는 어디에 저장될까?

이 프로그램은 파일에 저장한다.

```text
transactions.jsonl
categories.jsonl
budgets.jsonl
```

그래서 필요하다.

```text
budget_app/storage.py
```

## 5. 가계부 규칙은 어디에 둘까?

예를 들어:

```text
없는 카테고리로 거래를 추가하면 안 된다.
금액은 양수여야 한다.
summary는 총수입/총지출/잔액을 계산해야 한다.
```

이런 규칙은 필요하다.

```text
budget_app/services.py
```

## 6. 입력 검증은 어디에 둘까?

날짜, 금액, 타입, 월 형식 검증은 여러 기능에서 반복된다.

그래서 필요하다.

```text
budget_app/validators.py
```

## 7. 반복되는 부가 기능은 어디에 둘까?

예외 처리, 실행 시간 측정, 로그 출력은 여러 명령에서 반복된다.

그래서 필요하다.

```text
budget_app/decorators.py
```

---

# 이 프로젝트 요구사항에 맞춘 구조화 기준

이번 미션은 다음을 요구한다.

```text
파일 기반 저장
CRUD
검색
요약
import/export
제너레이터 스트리밍
데코레이터
타입 힌트
모듈 분리
```

이 요구사항을 구조로 바꾸면 다음과 같다.

| 요구사항 | 구조화 결과 |
| --- | --- |
| 파일 기반 저장 | `storage.py` |
| 거래 데이터 구조 | `models.py` |
| CRUD/검색/요약 규칙 | `services.py` |
| CLI 명령 | `cli.py` |
| 입력 검증 | `validators.py` |
| 데코레이터 요구 | `decorators.py` |
| `python -m budget_app` 실행 | `__main__.py` |
| 패키지 표시 | `__init__.py` |
| 사용법 문서화 | `README.md` |
| GitHub 제외 파일 관리 | `.gitignore` |

즉, 파일 이름을 아무렇게나 정한 것이 아니라, 미션 요구사항을 보고 책임별로 나눈 것이다.

---

# 앞으로 단계가 진행되면 이 문서에 추가할 것

앞으로 단계별로 헷갈리는 내용이 생기면 이 문서에 계속 추가하면 된다.

예:

```text
2단계:
Docker 기준을 왜 이렇게 잡았는지

3단계:
Transaction dataclass를 왜 그렇게 만들었는지
JSONL 저장 함수가 어떻게 동작하는지

4단계:
category add/list/remove가 어떤 흐름으로 동작하는지

5단계:
add 명령에서 CLI, Service, Storage가 어떻게 연결되는지

13단계:
Dockerfile과 docker-compose.yml이 각각 무슨 역할인지
```

이 문서는 공식 제출 문서가 아니라, 프로젝트를 이해하기 위한 개인 설명서로 계속 확장하면 된다.

