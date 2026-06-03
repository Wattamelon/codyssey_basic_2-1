---
title: "파일 기반 가계부 콘솔 프로그램 이론 정리"
created: 2026-06-01
mission: "2주차 1단계 - 파일 기반 가계부 콘솔 프로그램 만들기"
tags:
  - Python
  - CLI
  - JSONL
  - CSV
  - Generator
  - Decorator
  - FileIO
  - Architecture
---

# 파일 기반 가계부 콘솔 프로그램 이론 정리

> [!summary]
> 이번 미션은 단순히 `input()`으로 값을 받아 저장하는 프로그램이 아니라, **파일 기반 데이터 저장**, **CLI 명령 설계**, **CRUD**, **검색/요약**, **CSV import/export**, **제너레이터 스트리밍**, **데코레이터 기반 공통 관심사 분리**, **타입 힌트와 모듈화**까지 포함하는 작은 서비스형 콘솔 애플리케이션을 만드는 과제다.

## 목차

- [[#1. 미션 전체 그림]]
- [[#2. 요구 기능 요약]]
- [[#3. CLI 프로그램의 기본 개념]]
- [[#4. 데이터 모델 설계]]
- [[#5. 파일 저장 방식 JSONL과 CSV]]
- [[#6. 파일 I/O와 영구 저장]]
- [[#7. CRUD 개념]]
- [[#8. 제너레이터와 스트리밍 처리]]
- [[#9. 데코레이터]]
- [[#10. 입력 검증과 예외 처리]]
- [[#11. 검색 기능 설계]]
- [[#12. 월별 요약과 예산]]
- [[#13. 카테고리 관리]]
- [[#14. import/export 개념]]
- [[#15. update/delete와 파일 원자성]]
- [[#16. 모듈화와 계층 분리]]
- [[#17. 타입 힌트]]
- [[#18. 출력 포맷과 콘솔 UX]]
- [[#19. README에 포함해야 할 내용]]
- [[#20. 구현 전 체크리스트]]

---

# 1. 미션 전체 그림

이번 미션의 결과물은 **파일 기반 가계부 콘솔 프로그램**이다. 사용자는 터미널에서 명령을 입력해 수입과 지출 내역을 관리한다.

예를 들면 다음과 같은 형태다.

```bash
python -m budget_app add
python -m budget_app list --limit 10
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food
python -m budget_app summary --month 2024-01 --top 3
python -m budget_app budget set --month 2024-01 --amount 500000
python -m budget_app category add food
python -m budget_app import --from data.csv
python -m budget_app export --out export.csv --month 2024-01
```

핵심은 다음 4가지다.

1. **데이터를 파일에 영구 저장한다.**
   프로그램을 종료해도 거래 내역, 카테고리, 예산 정보가 사라지면 안 된다.

2. **명령어 기반으로 동작한다.**
   사용자는 `add`, `list`, `search`, `summary`, `budget`, `category`, `update`, `delete`, `import`, `export` 같은 명령어를 사용한다.

3. **큰 파일도 처리할 수 있게 설계한다.**
   저장 파일 전체를 한 번에 메모리에 올리는 방식보다, 한 줄씩 읽는 제너레이터 기반 스트리밍 처리가 요구된다.

4. **유지보수 가능한 구조를 만든다.**
   CLI, 서비스 로직, 저장소, 데이터 모델을 한 파일에 뒤섞지 않고 모듈로 나눈다.

> [!important]
> 이 미션의 진짜 목표는 "가계부" 자체보다, 작은 프로그램을 **서비스처럼 구조화하는 감각**을 익히는 것이다.

---

# 2. 요구 기능 요약

PDF에서 확인한 주요 기능은 다음과 같다.

| 기능 | 명령 | 핵심 역할 |
| --- | --- | --- |
| 거래 추가 | `add` | 날짜, 타입, 카테고리, 금액, 메모, 태그를 입력받아 저장 |
| 거래 목록 | `list` | 최신순 거래 목록 출력, `--limit` 지원 |
| 거래 검색 | `search` | 기간, 카테고리, 타입, 키워드, 태그 조건으로 검색 |
| 월별 요약 | `summary` | 특정 월의 총수입, 총지출, 잔액, 카테고리별 TOP N 출력 |
| 예산 설정/조회 | `budget set` 등 | 월 예산 저장, 요약에서 사용률과 초과 여부 표시 |
| 카테고리 관리 | `category add/list/remove` | 카테고리 추가, 목록, 삭제 |
| 거래 수정 | `update` | id 기반으로 특정 거래 수정 |
| 거래 삭제 | `delete --id` | id 기반으로 특정 거래 삭제 |
| 가져오기 | `import --from file.csv` | CSV 거래 내역 일괄 등록 |
| 내보내기 | `export --out file.csv` | 조건에 맞는 거래를 CSV로 저장 |

추가 조건도 있다.

- 데이터는 최소 3개 이상의 파일로 분리 저장한다.
  - 예: `transactions.jsonl`
  - 예: `categories.jsonl` 또는 `categories.csv`
  - 예: `budgets.jsonl` 또는 `budgets.csv`
- `README.md`에는 실행 방법, 저장 파일 위치/형식, 주요 명령 예시, CSV 스키마가 있어야 한다.
- Python 3.10 이상을 사용한다.
- 외부 라이브러리 없이 표준 라이브러리만 사용해야 한다.
- CLI 옵션 표기는 리눅스 표준처럼 `-` 또는 `--`로 통일한다.
- 오류 시 스택트레이스를 그대로 보여주지 말고 원인과 해결 힌트를 출력한다.
- 정상 종료는 exit code `0`, 오류 종료는 `0`이 아닌 값이어야 한다.

---

# 3. CLI 프로그램의 기본 개념

CLI는 **Command Line Interface**의 약자다. 그래픽 화면 대신 터미널 명령어로 프로그램을 조작하는 방식이다.

## 3.1 명령과 옵션

CLI는 보통 다음 요소로 구성된다.

```text
프로그램명 명령어 옵션 값
```

예:

```bash
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food
```

여기서 의미는 다음과 같다.

| 부분 | 의미 |
| --- | --- |
| `python -m budget_app` | 실행할 프로그램 |
| `search` | 수행할 명령 |
| `--from 2024-01-01` | 시작일 옵션 |
| `--to 2024-01-31` | 종료일 옵션 |
| `--category food` | 카테고리 조건 |

## 3.2 대화형 입력과 옵션 입력

이 미션에서는 두 가지 입력 방식이 섞인다.

### 대화형 입력

`add` 명령은 실행 후 사용자에게 순서대로 질문한다.

```text
날짜(YYYY-MM-DD): 2024-01-15
타입(income/expense): expense
카테고리: food
금액(양수): 15000
메모(선택): 점심
태그(쉼표로 구분): meal
```

장점:

- 초보 사용자가 사용하기 쉽다.
- 필수 입력을 단계별로 안내할 수 있다.

단점:

- 자동화가 어렵다.
- 테스트할 때 입력 흐름을 따로 처리해야 한다.

### 옵션 입력

`search`, `list`, `summary`, `export`, `delete` 같은 명령은 옵션으로 입력받는 것이 자연스럽다.

```bash
python -m budget_app list --limit 3
python -m budget_app delete --id TX-000012
```

장점:

- 자동화와 테스트가 쉽다.
- 사용자가 한 줄로 원하는 작업을 명확히 표현할 수 있다.

단점:

- 옵션 이름과 형식을 사용자가 알아야 한다.

## 3.3 argparse

Python 표준 라이브러리에는 CLI 파서를 만들 수 있는 `argparse`가 있다.

`argparse`의 역할:

- 명령어와 옵션을 해석한다.
- `--help` 메시지를 자동 생성한다.
- 필수 옵션 누락을 감지한다.
- 옵션 타입 변환을 도와준다.

예를 들어 사용자가 다음처럼 입력하면:

```bash
python -m budget_app list --limit 5
```

프로그램 내부에서는 대략 이런 정보가 생긴다.

```text
command = "list"
limit = 5
```

> [!tip]
> `argparse`는 표준 라이브러리이므로 이번 미션의 "외부 라이브러리 금지" 조건을 만족한다.

## 3.4 CLI 파서란?

CLI 파서는 사용자가 터미널에 입력한 문자열을 프로그램이 이해할 수 있는 구조로 바꿔주는 도구다.

사용자는 터미널에 이렇게 입력한다.

```bash
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food
```

사람은 이 문장을 읽고 바로 이해할 수 있다.

```text
budget_app 프로그램의 search 기능을 실행하되,
2024-01-01부터 2024-01-31까지,
category가 food인 거래를 찾으라는 뜻
```

하지만 프로그램 입장에서는 처음에 이것이 그냥 문자열 조각들의 묶음이다.

```text
["search", "--from", "2024-01-01", "--to", "2024-01-31", "--category", "food"]
```

CLI 파서는 이 조각들을 해석해서 다음처럼 의미 있는 데이터로 바꿔준다.

```text
command = "search"
from_date = "2024-01-01"
to_date = "2024-01-31"
category = "food"
```

즉, CLI 파서는 **터미널 명령어 번역기**라고 보면 된다.

## 3.5 `argparse`가 없으면 어떻게 될까?

`argparse`를 사용하지 않으면 직접 명령어를 해석해야 한다.

예를 들어 사용자가 다음처럼 입력했다고 하자.

```bash
python -m budget_app list --limit 5
```

프로그램 내부에서는 보통 `sys.argv`로 입력값을 볼 수 있다.

```python
import sys

print(sys.argv)
```

대략 이런 리스트가 나온다.

```python
["/path/to/budget_app", "list", "--limit", "5"]
```

직접 파싱하려면 다음 일을 해야 한다.

```text
1. 두 번째 값이 명령어인지 확인한다.
2. "--limit" 옵션이 있는지 찾는다.
3. "--limit" 다음 값이 존재하는지 확인한다.
4. "5"를 정수로 바꾼다.
5. 값이 없거나 숫자가 아니면 오류를 낸다.
6. --help도 직접 처리한다.
```

이런 일을 모든 명령마다 직접 만들면 코드가 금방 복잡해진다.

`argparse`는 이 반복 작업을 대신해준다.

## 3.6 `argparse`의 기본 구조

`argparse`의 기본 흐름은 보통 이렇다.

```python
import argparse

parser = argparse.ArgumentParser(
    prog="budget_app",
    description="파일 기반 가계부 콘솔 프로그램",
)

parser.add_argument("command")
parser.add_argument("--limit", type=int, default=10)

args = parser.parse_args()

print(args.command)
print(args.limit)
```

사용자가 이렇게 실행하면:

```bash
python -m budget_app list --limit 5
```

`args` 안에는 이런 값이 들어간다.

```text
args.command = "list"
args.limit = 5
```

여기서 중요한 점은 `--limit`으로 들어온 `"5"`가 `type=int` 덕분에 정수 `5`로 변환된다는 것이다.

## 3.7 명령어가 여러 개일 때: subparser

이번 미션은 명령어가 하나가 아니다.

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

이렇게 여러 명령을 가진 CLI에서는 `subparser`를 사용한다.

개념적으로는 다음과 같다.

```text
큰 파서:
budget_app 전체를 담당

작은 파서:
add 명령 담당
list 명령 담당
search 명령 담당
summary 명령 담당
...
```

예시:

```python
import argparse

parser = argparse.ArgumentParser(prog="budget_app")
subparsers = parser.add_subparsers(dest="command", required=True)

list_parser = subparsers.add_parser("list")
list_parser.add_argument("--limit", type=int, default=10)

search_parser = subparsers.add_parser("search")
search_parser.add_argument("--category")
search_parser.add_argument("--type", choices=["income", "expense"])

args = parser.parse_args()
```

실행:

```bash
python -m budget_app list --limit 3
```

결과:

```text
args.command = "list"
args.limit = 3
```

실행:

```bash
python -m budget_app search --category food --type expense
```

결과:

```text
args.command = "search"
args.category = "food"
args.type = "expense"
```

## 3.8 `argparse`에서 자주 쓰는 옵션들

| 코드 | 의미 |
| --- | --- |
| `add_argument("name")` | 필수 위치 인자 |
| `add_argument("--limit")` | 선택 옵션 |
| `type=int` | 입력값을 정수로 변환 |
| `default=10` | 값이 없을 때 기본값 |
| `required=True` | 반드시 입력해야 하는 옵션 |
| `choices=[...]` | 허용된 값만 받음 |
| `dest="command"` | 파싱 결과가 저장될 이름 |

예:

```python
search_parser.add_argument("--type", choices=["income", "expense"])
```

이렇게 하면 사용자가 잘못 입력했을 때 `argparse`가 막아준다.

```bash
python -m budget_app search --type wrong
```

`wrong`은 `income`, `expense` 중 하나가 아니므로 오류가 난다.

## 3.9 이번 미션의 CLI 파서 설계 방향

이번 미션에서는 다음처럼 설계하는 것이 좋다.

```text
budget_app
  add
  list --limit N
  search --from DATE --to DATE --category NAME --type TYPE -q TEXT --tag TAG
  summary --month YYYY-MM --top N
  budget set --month YYYY-MM --amount AMOUNT
  category add NAME
  category list
  category remove NAME
  update --id ID ...
  delete --id ID
  import --from CSV
  export --out CSV --month YYYY-MM
```

CLI 파서의 책임은 여기까지다.

```text
사용자의 입력을 해석한다.
옵션 값을 args에 담는다.
어떤 명령을 실행해야 할지 결정한다.
```

반대로 CLI 파서가 직접 하면 좋지 않은 일도 있다.

```text
거래 파일에 저장하기
summary 계산하기
카테고리 삭제 정책 판단하기
CSV 파일을 직접 처리하기
```

이런 일은 `service`나 `repository` 계층으로 넘기는 것이 좋다.

> [!important]
> CLI 파서는 "입력 해석 담당"이다.  
> 실제 가계부 규칙은 Service가, 파일 저장은 Repository가 담당하게 나누면 구조가 깔끔해진다.

---

# 4. 데이터 모델 설계

데이터 모델은 프로그램이 다루는 정보를 코드에서 어떤 구조로 표현할지 정하는 것이다.

이번 미션의 중심 모델은 `Transaction`이다.

## 4.1 거래 내역 Transaction

거래 내역은 최소 다음 필드를 가져야 한다.

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `id` | Y | 유일한 거래 ID |
| `type` | Y | `income` 또는 `expense` |
| `date` | Y | `YYYY-MM-DD` 형식 |
| `amount` | Y | 양수 정수 |
| `category` | Y | 등록된 카테고리 |
| `memo` | N | 메모 문자열 |
| `tags` | N | 쉼표로 구분된 태그 목록 |

거래 예시:

```json
{
  "id": "TX-000012",
  "type": "expense",
  "date": "2024-01-15",
  "amount": 15000,
  "category": "food",
  "memo": "점심",
  "tags": ["meal"]
}
```

## 4.2 타입은 왜 중요할까?

`type`은 수입과 지출을 구분한다.

- `income`: 수입
- `expense`: 지출

요약 계산에서 `type`이 핵심이다.

```text
총수입 = income 거래 금액 합계
총지출 = expense 거래 금액 합계
잔액 = 총수입 - 총지출
```

## 4.3 amount는 왜 양수로 저장할까?

지출을 음수로 저장하는 방식도 가능하지만, 이 미션에서는 `amount`가 **양수**여야 한다.

그 이유는 다음과 같다.

- 입력 검증이 단순해진다.
- 수입/지출 구분은 `type`이 담당한다.
- `amount`에 음수와 양수가 섞이면 요약 계산에서 실수가 생기기 쉽다.

따라서 지출 15000원은 다음처럼 저장한다.

```json
{
  "type": "expense",
  "amount": 15000
}
```

음수로 저장하지 않는다.

## 4.4 dataclass

Python의 `dataclasses.dataclass`는 데이터 객체를 간결하게 정의하기 위한 표준 기능이다.

> [!summary]
> `dataclass`는 **데이터를 담는 클래스**를 쉽게 만들기 위한 문법이다.  
> 이번 미션에서는 `Transaction`, `Budget`처럼 "값을 담는 객체"를 만들 때 아주 잘 맞는다.

장점:

- 생성자 `__init__`을 자동으로 만들어준다.
- 객체 비교와 출력이 편해진다.
- 데이터 모델의 필드가 한눈에 보인다.
- 타입 힌트와 궁합이 좋다.

개념적으로는 다음처럼 생각하면 된다.

```python
from dataclasses import dataclass

@dataclass
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = None
```

> [!warning]
> 실제 구현에서는 `tags: list[str] = []`처럼 빈 리스트를 기본값으로 직접 두면 안 된다. 가변 객체 기본값 문제 때문에 `field(default_factory=list)`를 써야 한다.

## 4.5 dataclass가 없으면 어떻게 될까?

먼저 일반 클래스로 거래 데이터를 표현한다고 생각해보자.

```python
class Transaction:
    def __init__(self, id, type, date, amount, category, memo="", tags=None):
        self.id = id
        self.type = type
        self.date = date
        self.amount = amount
        self.category = category
        self.memo = memo
        self.tags = tags or []
```

거래 하나를 만들면:

```python
tx = Transaction(
    id="TX-000001",
    type="expense",
    date="2024-01-15",
    amount=15000,
    category="food",
    memo="점심",
    tags=["meal"],
)
```

이 방식도 가능하다.  
하지만 데이터 클래스가 많아질수록 다음 코드가 계속 반복된다.

```text
필드 이름 받기
받은 값을 self에 넣기
기본값 처리하기
객체 출력 형식 만들기
객체 비교 방식 만들기
```

`dataclass`는 이런 반복을 줄여준다.

## 4.6 dataclass로 쓰면 무엇이 자동으로 생길까?

다음 코드를 보자.

```python
from dataclasses import dataclass, field

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

이렇게 쓰면 Python이 내부적으로 다음과 비슷한 생성자를 만들어준다.

```python
def __init__(self, id, type, date, amount, category, memo="", tags=None):
    self.id = id
    self.type = type
    self.date = date
    self.amount = amount
    self.category = category
    self.memo = memo
    self.tags = tags
```

즉, 직접 `__init__`을 작성하지 않아도 된다.

객체를 출력했을 때도 보기 좋다.

```python
tx = Transaction(
    id="TX-000001",
    type="expense",
    date="2024-01-15",
    amount=15000,
    category="food",
)

print(tx)
```

일반 객체라면 이런 식으로 보일 수 있다.

```text
<__main__.Transaction object at 0x...>
```

`dataclass`는 보통 이런 식으로 필드 내용을 보여준다.

```text
Transaction(id='TX-000001', type='expense', date='2024-01-15', amount=15000, category='food', memo='', tags=[])
```

디버깅할 때 훨씬 편하다.

## 4.7 `field(default_factory=list)`가 왜 필요할까?

초보자가 자주 하는 실수가 있다.

```python
@dataclass
class Transaction:
    id: str
    tags: list[str] = []
```

이렇게 쓰면 모든 `Transaction` 객체가 같은 리스트를 공유할 수 있다.  
한 거래의 태그를 수정했는데 다른 거래에도 영향을 줄 수 있다는 뜻이다.

그래서 리스트, 딕셔너리처럼 바뀔 수 있는 값은 이렇게 써야 한다.

```python
from dataclasses import dataclass, field

@dataclass
class Transaction:
    id: str
    tags: list[str] = field(default_factory=list)
```

`default_factory=list`의 의미:

```text
객체를 새로 만들 때마다 빈 리스트를 새로 만들어라.
```

즉, 거래마다 독립적인 태그 리스트를 갖게 된다.

## 4.8 dataclass와 타입 힌트

`dataclass`는 타입 힌트와 함께 쓴다.

```python
@dataclass
class Budget:
    month: str
    amount: int
```

여기서:

| 필드 | 타입 | 의미 |
| --- | --- | --- |
| `month` | `str` | `YYYY-MM` 형식 월 |
| `amount` | `int` | 예산 금액 |

타입 힌트가 있다고 해서 Python이 항상 자동으로 타입을 강제하는 것은 아니다.

```python
budget = Budget(month="2024-01", amount="abc")
```

이런 코드가 실행 자체는 될 수 있다.  
그래서 입력 검증은 여전히 따로 해야 한다.

타입 힌트의 역할은 다음에 가깝다.

```text
이 필드는 이런 타입으로 쓰기로 약속한다.
IDE와 사람이 코드를 읽기 쉽게 한다.
검증 함수가 무엇을 확인해야 하는지 명확해진다.
```

## 4.9 dataclass와 파일 저장

파일에 저장할 때는 dataclass 객체를 그대로 저장할 수 없다.  
JSON으로 저장하려면 보통 딕셔너리로 바꿔야 한다.

예:

```python
from dataclasses import asdict

tx = Transaction(
    id="TX-000001",
    type="expense",
    date="2024-01-15",
    amount=15000,
    category="food",
)

data = asdict(tx)
```

`data`는 이런 딕셔너리가 된다.

```python
{
    "id": "TX-000001",
    "type": "expense",
    "date": "2024-01-15",
    "amount": 15000,
    "category": "food",
    "memo": "",
    "tags": [],
}
```

이제 `json.dumps(data)`로 JSON 문자열을 만들 수 있다.

반대로 파일에서 읽은 딕셔너리를 dataclass 객체로 만들 수도 있다.

```python
data = {
    "id": "TX-000001",
    "type": "expense",
    "date": "2024-01-15",
    "amount": 15000,
    "category": "food",
    "memo": "",
    "tags": [],
}

tx = Transaction(**data)
```

`Transaction(**data)`는 딕셔너리의 키와 값을 생성자 인자로 풀어서 전달한다.

```python
Transaction(
    id="TX-000001",
    type="expense",
    date="2024-01-15",
    amount=15000,
    category="food",
    memo="",
    tags=[],
)
```

와 비슷하다.

> [!tip]
> 이번 미션에서는 `Transaction -> dict -> JSONL 저장`, `JSONL 읽기 -> dict -> Transaction` 흐름을 자주 쓰게 된다.

---

# 5. 파일 저장 방식 JSONL과 CSV

미션에서는 저장 포맷으로 `JSONL` 또는 `CSV` 중 하나를 선택할 수 있다. 단, import/export CSV 스키마는 별도로 요구된다.

## 5.1 JSON

JSON은 데이터를 `{}`와 `[]`로 표현하는 텍스트 형식이다.

예:

```json
{
  "id": "TX-000012",
  "type": "expense",
  "date": "2024-01-15",
  "amount": 15000,
  "category": "food",
  "memo": "점심",
  "tags": ["meal"]
}
```

장점:

- 구조화된 데이터를 표현하기 좋다.
- 문자열, 숫자, 리스트, 객체를 자연스럽게 담을 수 있다.
- Python의 `json` 표준 라이브러리로 처리할 수 있다.

단점:

- 큰 JSON 배열 파일은 일부만 수정하기 어렵다.
- 전체 파일이 하나의 JSON 구조라면 파일 전체를 읽어야 할 때가 많다.

## 5.2 JSONL

JSONL은 **JSON Lines**의 약자다. 한 줄에 JSON 객체 하나를 저장한다.

예:

```jsonl
{"id":"TX-000001","type":"expense","date":"2024-01-01","amount":8000,"category":"food","memo":"김밥","tags":["meal"]}
{"id":"TX-000002","type":"income","date":"2024-01-05","amount":300000,"category":"salary","memo":"알바비","tags":[]}
{"id":"TX-000003","type":"expense","date":"2024-01-07","amount":45000,"category":"transport","memo":"교통카드","tags":["bus"]}
```

장점:

- 한 줄씩 읽을 수 있어 스트리밍 처리에 좋다.
- 거래를 추가할 때 파일 끝에 한 줄만 append하면 된다.
- 큰 파일을 다루기 쉽다.

단점:

- 특정 거래를 수정/삭제하려면 보통 새 파일을 만들어 다시 써야 한다.
- 사람이 직접 편집할 때 JSON보다 조금 낯설 수 있다.

> [!tip]
> 이번 미션의 "제너레이터 기반 스트리밍 처리"와 가장 잘 어울리는 저장 방식은 JSONL이다.

## 5.3 CSV

CSV는 쉼표로 열을 구분하는 표 형식 텍스트 파일이다.

예:

```csv
date,type,category,amount,memo,tags
2024-01-15,expense,food,15000,점심,meal
2024-01-20,income,salary,500000,월급,
```

장점:

- 엑셀이나 구글 스프레드시트에서 열기 쉽다.
- import/export에 적합하다.
- Python의 `csv` 표준 라이브러리로 처리할 수 있다.

단점:

- 리스트나 중첩 구조를 표현하기 불편하다.
- 쉼표, 줄바꿈, 따옴표가 들어간 문자열을 조심해야 한다.
- 태그 같은 리스트는 `"meal,lunch"`처럼 별도 규칙을 정해야 한다.

## 5.4 import/export CSV 최소 스키마

PDF 기준으로 CSV 최소 스키마는 다음과 같다.

| column | required | 설명 |
| --- | --- | --- |
| `date` | Y | `YYYY-MM-DD` |
| `type` | Y | `income` 또는 `expense` |
| `category` | Y | 등록된 카테고리 |
| `amount` | Y | 양수 정수 |
| `memo` | N | 문자열 |
| `tags` | N | 쉼표로 구분한 문자열 |

공통 조건:

- UTF-8
- 헤더 포함

---

# 6. 파일 I/O와 영구 저장

파일 I/O는 파일을 읽고 쓰는 작업이다.

이번 미션에서 파일 I/O는 단순한 부가기능이 아니라 핵심이다. 데이터베이스를 사용하지 않기 때문에 파일이 곧 저장소 역할을 한다.

## 6.1 영구 저장

영구 저장이란 프로그램이 종료되어도 데이터가 남아 있는 것을 말한다.

메모리에만 저장하면:

```text
프로그램 실행 -> 거래 추가 -> 프로그램 종료 -> 데이터 사라짐
```

파일에 저장하면:

```text
프로그램 실행 -> 거래 추가 -> 파일 저장 -> 프로그램 종료 -> 다음 실행 때 파일에서 복구
```

## 6.2 저장 파일 분리

요구사항상 저장 파일은 최소 3개 이상이어야 한다.

추천 구조:

```text
data/
  transactions.jsonl
  categories.jsonl
  budgets.jsonl
```

역할:

| 파일 | 내용 |
| --- | --- |
| `transactions.jsonl` | 거래 내역 |
| `categories.jsonl` | 카테고리 목록 |
| `budgets.jsonl` | 월별 예산 |

이렇게 분리하면 좋은 점:

- 거래 내역과 설정성 데이터를 섞지 않는다.
- 각 파일의 책임이 명확하다.
- 카테고리만 읽고 싶을 때 거래 파일까지 읽을 필요가 없다.
- README에서 파일 구조를 설명하기 쉽다.

## 6.3 기본 저장 폴더

PDF에서는 기본 저장 폴더로 `./data`를 권장하고, 옵션으로 변경 가능하게 하라고 되어 있다.

예:

```bash
python -m budget_app list --data-dir ./my_data
```

이렇게 하면 테스트할 때도 편하다.

```text
실제 데이터: ./data
테스트 데이터: ./tmp/test_data
```

---

# 7. CRUD 개념

CRUD는 데이터를 다루는 가장 기본적인 네 가지 작업이다.

| 약어 | 뜻 | 이번 미션의 예 |
| --- | --- | --- |
| C | Create | `add`, `category add`, `budget set` |
| R | Read | `list`, `search`, `summary`, `category list` |
| U | Update | `update`, `budget set` |
| D | Delete | `delete`, `category remove` |

## 7.1 Create

Create는 새 데이터를 만드는 것이다.

거래 추가 과정:

1. 사용자 입력을 받는다.
2. 입력값을 검증한다.
3. 새 ID를 생성한다.
4. 거래 객체를 만든다.
5. 파일에 저장한다.
6. 생성된 ID를 출력한다.

## 7.2 Read

Read는 저장된 데이터를 읽는 것이다.

예:

- 최신 거래 목록 출력
- 조건에 맞는 거래 검색
- 특정 월의 요약 출력

## 7.3 Update

Update는 기존 데이터를 수정하는 것이다.

파일 기반 저장에서는 update가 생각보다 어렵다. JSONL 파일 중간의 한 줄만 "깔끔하게" 바꾸기 어렵기 때문이다.

일반적인 방식:

1. 원본 파일을 한 줄씩 읽는다.
2. 수정 대상 ID를 찾는다.
3. 해당 줄은 수정된 데이터로 바꾼다.
4. 나머지 줄은 그대로 쓴다.
5. 임시 파일에 먼저 저장한다.
6. 성공하면 원본 파일을 임시 파일로 교체한다.

## 7.4 Delete

Delete도 update와 비슷하다.

1. 원본 파일을 한 줄씩 읽는다.
2. 삭제할 ID와 일치하는 줄은 건너뛴다.
3. 나머지 줄만 임시 파일에 쓴다.
4. 성공하면 원본 파일을 교체한다.

> [!important]
> 파일 기반 CRUD에서 update/delete는 "기존 파일 직접 수정"보다 "새 파일 작성 후 교체"가 안전하다.

---

# 8. 제너레이터와 스트리밍 처리

미션에서 중요한 개념 중 하나가 `yield` 기반 제너레이터다.

> [!summary]
> 제너레이터는 데이터를 **한 번에 전부 만들지 않고, 필요할 때 하나씩 꺼내 쓰는 방식**이다.  
> 이번 가계부 미션에서는 `transactions.jsonl` 파일을 한 줄씩 읽으면서 거래를 하나씩 처리할 때 사용한다.

## 8.1 제너레이터란?

제너레이터는 값을 한 번에 모두 만들지 않고, 필요할 때 하나씩 만들어내는 객체다.

조금 더 쉽게 말하면, 제너레이터는 **자동 판매기**처럼 생각할 수 있다.

```text
일반 리스트:
처음부터 음료 100개를 전부 책상 위에 올려둔다.

제너레이터:
버튼을 누를 때마다 음료 1개씩 나온다.
```

일반 함수:

```python
def get_numbers():
    return [1, 2, 3]
```

제너레이터 함수:

```python
def generate_numbers():
    yield 1
    yield 2
    yield 3
```

일반 함수는 리스트 전체를 한 번에 반환한다. 제너레이터는 값을 하나씩 흘려보낸다.

## 8.2 `return`과 `yield`의 차이

초보자가 가장 헷갈리기 쉬운 부분이 `return`과 `yield`의 차이다.

### `return`

`return`은 함수를 **끝내면서 결과를 돌려준다**.

```python
def normal_function():
    print("시작")
    return 1
    print("여기는 실행되지 않음")

result = normal_function()
print(result)
```

실행 흐름:

```text
1. normal_function() 호출
2. "시작" 출력
3. return 1 실행
4. 함수 종료
5. result에 1 저장
```

`return`이 실행되면 함수는 끝난다. 그 아래 코드는 실행되지 않는다.

### `yield`

`yield`는 함수를 완전히 끝내지 않고, 값을 하나 내보낸 뒤 **잠시 멈춘다**.

```python
def generator_function():
    print("첫 번째 준비")
    yield 1

    print("두 번째 준비")
    yield 2

    print("세 번째 준비")
    yield 3
```

이 함수는 호출한다고 바로 실행되지 않는다.

```python
gen = generator_function()
```

위 코드를 실행해도 아직 `"첫 번째 준비"`가 출력되지 않는다.  
이때 `gen`은 값을 꺼낼 준비가 된 제너레이터 객체다.

값을 꺼내려면 `next()`를 사용한다.

```python
print(next(gen))
print(next(gen))
print(next(gen))
```

실행 흐름:

```text
첫 번째 next(gen)
-> "첫 번째 준비" 출력
-> yield 1
-> 1을 바깥으로 내보내고 함수 멈춤

두 번째 next(gen)
-> 멈췄던 yield 1 다음 줄부터 다시 실행
-> "두 번째 준비" 출력
-> yield 2
-> 2를 바깥으로 내보내고 함수 멈춤

세 번째 next(gen)
-> 멈췄던 yield 2 다음 줄부터 다시 실행
-> "세 번째 준비" 출력
-> yield 3
-> 3을 바깥으로 내보내고 함수 멈춤
```

핵심 차이:

| 구분 | `return` | `yield` |
| --- | --- | --- |
| 함수 종료 여부 | 값을 돌려주고 함수 종료 | 값을 내보내고 함수 일시 정지 |
| 여러 번 값 전달 | 보통 한 번 | 여러 번 가능 |
| 메모리 사용 | 결과를 한 번에 만들기 쉬움 | 값을 하나씩 만들기 쉬움 |
| 대표 사용처 | 계산 결과 반환 | 큰 데이터 반복 처리 |

> [!important]
> `yield`가 들어간 함수는 일반 함수가 아니라 **제너레이터 함수**가 된다.  
> 제너레이터 함수는 호출하면 결과값이 바로 나오는 것이 아니라, 값을 하나씩 꺼낼 수 있는 제너레이터 객체를 만든다.

## 8.3 `for`문과 제너레이터

실제로는 `next()`를 직접 쓰는 경우보다 `for`문으로 제너레이터를 사용하는 경우가 많다.

```python
def generate_numbers():
    yield 1
    yield 2
    yield 3

for number in generate_numbers():
    print(number)
```

`for`문은 내부적으로 다음 일을 한다.

```text
1. 제너레이터에서 next()로 값을 하나 꺼낸다.
2. 꺼낸 값을 number에 넣는다.
3. for문 본문을 실행한다.
4. 다시 next()로 다음 값을 꺼낸다.
5. 더 이상 값이 없으면 반복을 끝낸다.
```

즉, 아래 코드는:

```python
for tx in iter_transactions():
    print(tx)
```

대략 이런 뜻이다.

```text
거래를 하나 꺼낸다.
출력한다.
다음 거래를 하나 꺼낸다.
출력한다.
더 이상 거래가 없으면 멈춘다.
```

## 8.4 리스트 방식과 제너레이터 방식 비교

거래 파일을 읽는 함수를 만든다고 생각해보자.

### 리스트 방식

```python
def read_all_transactions():
    transactions = []

    with open("transactions.jsonl", "r", encoding="utf-8") as file:
        for line in file:
            transaction = parse_transaction(line)
            transactions.append(transaction)

    return transactions
```

사용:

```python
transactions = read_all_transactions()

for tx in transactions:
    print(tx)
```

이 방식은 파일의 모든 거래를 리스트에 담은 뒤 반환한다.

장점:

- 이해하기 쉽다.
- 정렬, 개수 세기, 여러 번 반복하기가 편하다.

단점:

- 파일이 크면 메모리를 많이 쓴다.
- 첫 번째 거래 하나만 필요해도 전체 파일을 다 읽는다.

### 제너레이터 방식

```python
def iter_transactions():
    with open("transactions.jsonl", "r", encoding="utf-8") as file:
        for line in file:
            transaction = parse_transaction(line)
            yield transaction
```

사용:

```python
for tx in iter_transactions():
    print(tx)
```

이 방식은 거래를 하나 읽고, 하나 내보내고, 다시 다음 줄을 읽는다.

장점:

- 메모리를 적게 쓴다.
- 큰 파일에도 강하다.
- 조건 검색과 잘 어울린다.
- "필요한 만큼만" 처리할 수 있다.

단점:

- 한 번 지나간 값을 다시 쓰려면 다시 읽어야 한다.
- 전체 정렬이 필요한 작업은 결국 일부 데이터를 모아야 할 수 있다.

> [!note]
> 제너레이터는 "항상 리스트보다 좋다"가 아니다.  
> **큰 데이터를 한 번 훑으며 처리할 때** 특히 좋다.

## 8.5 왜 필요한가?

거래 파일이 작을 때는 차이가 별로 없다.

하지만 거래가 10만 건, 100만 건이 되면 전체 파일을 리스트로 읽는 방식은 부담이 커진다.

```python
transactions = read_all_transactions()
```

이 방식은 모든 거래를 메모리에 올린다.

반면 제너레이터는 다음처럼 한 건씩 처리한다.

```python
for tx in iter_transactions():
    ...
```

장점:

- 메모리 사용량이 작다.
- 큰 파일도 처리 가능하다.
- 조건에 맞는 데이터만 바로 출력할 수 있다.
- `list`, `search`, `summary`, `export`에 잘 어울린다.

## 8.6 이번 미션에서 제너레이터를 쓰는 위치

이번 미션에서 가장 자연스러운 제너레이터 사용처는 거래 파일 읽기다.

예상 저장 파일:

```text
data/transactions.jsonl
```

파일 내용:

```jsonl
{"id":"TX-000001","type":"expense","date":"2024-01-01","amount":8000,"category":"food","memo":"김밥","tags":["meal"]}
{"id":"TX-000002","type":"income","date":"2024-01-05","amount":300000,"category":"salary","memo":"알바비","tags":[]}
{"id":"TX-000003","type":"expense","date":"2024-01-07","amount":45000,"category":"transport","memo":"교통카드","tags":["bus"]}
```

이 파일을 읽는 함수는 개념적으로 이렇게 만들 수 있다.

```python
import json

def iter_transactions(path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            data = json.loads(line)
            yield data
```

사용:

```python
for transaction in iter_transactions("data/transactions.jsonl"):
    print(transaction["id"], transaction["amount"])
```

여기서 중요한 점:

- 파일 전체를 리스트로 만들지 않는다.
- 한 줄 읽는다.
- JSON으로 바꾼다.
- `yield`로 한 거래를 내보낸다.
- 다음 거래는 필요할 때 읽는다.

## 8.7 검색에서의 제너레이터 흐름

`search` 명령을 예로 들어보자.

```bash
python -m budget_app search --category food
```

내부 흐름은 이렇게 생각할 수 있다.

```text
transactions.jsonl 첫 줄 읽기
-> category가 food인지 검사
-> 맞으면 출력
-> 다음 줄 읽기
-> category가 food인지 검사
-> 맞으면 출력
-> 파일 끝까지 반복
```

코드 개념:

```python
def search_by_category(path, category):
    for tx in iter_transactions(path):
        if tx["category"] == category:
            yield tx
```

사용:

```python
for tx in search_by_category("data/transactions.jsonl", "food"):
    print(tx)
```

여기서 `search_by_category()`도 제너레이터다.  
왜냐하면 함수 안에 `yield tx`가 있기 때문이다.

> [!tip]
> 제너레이터는 여러 개를 이어 붙일 수 있다.  
> `파일 읽기 제너레이터 -> 검색 제너레이터 -> 출력` 같은 흐름을 만들 수 있다.

## 8.8 summary에서의 제너레이터 흐름

`summary`는 거래를 출력하는 기능이 아니라 합계를 계산하는 기능이다.

```bash
python -m budget_app summary --month 2024-01
```

흐름:

```text
거래를 하나씩 읽는다.
해당 월 거래인지 확인한다.
income이면 총수입에 더한다.
expense면 총지출에 더한다.
expense면 카테고리별 합계에도 더한다.
마지막에 결과를 출력한다.
```

이 경우에도 전체 거래 리스트가 꼭 필요하지 않다.

```python
total_income = 0
total_expense = 0

for tx in iter_transactions("data/transactions.jsonl"):
    if not tx["date"].startswith("2024-01"):
        continue

    if tx["type"] == "income":
        total_income += tx["amount"]
    else:
        total_expense += tx["amount"]
```

`summary`는 모든 거래를 한 번 훑으면서 필요한 숫자만 누적하면 된다.  
이런 작업은 제너레이터와 잘 맞는다.

## 8.9 제너레이터를 사용할 때 주의할 점

### 한 번 소비하면 다시 처음으로 돌아가지 않는다

제너레이터는 값을 하나씩 꺼내는 흐름이다.  
한 번 끝까지 읽으면 다시 처음으로 돌아가지 않는다.

```python
gen = generate_numbers()

for number in gen:
    print(number)

for number in gen:
    print(number)  # 아무것도 출력되지 않음
```

다시 반복하고 싶으면 제너레이터를 새로 만들어야 한다.

```python
for number in generate_numbers():
    print(number)

for number in generate_numbers():
    print(number)
```

### 정렬하려면 결국 모아야 한다

제너레이터는 하나씩 처리하는 데 강하지만, 정렬은 전체를 비교해야 한다.

```python
transactions = list(iter_transactions(path))
transactions.sort(key=lambda tx: tx["date"], reverse=True)
```

이렇게 하면 리스트로 모으게 된다.

따라서 최신순 정렬이 필요한 `list`, `search`에서는 다음 중 하나를 선택해야 한다.

- 결과를 모은 뒤 정렬한다.
- 저장 순서를 최신순으로 유지한다.
- `--limit`이 있을 때 필요한 개수만 관리한다.

이번 미션에서는 정확한 최신순 출력이 중요하므로, 필요한 경우 일부 리스트화를 허용해도 된다.

### `yield`와 `return`을 섞을 때

제너레이터 함수에서도 `return`을 쓸 수 있지만, 일반 함수처럼 값을 반환하는 용도로 자주 쓰지는 않는다.

```python
def gen():
    yield 1
    return
    yield 2
```

이 경우 `yield 2`는 실행되지 않는다.  
제너레이터 안의 `return`은 "이제 더 이상 내보낼 값이 없다"는 뜻에 가깝다.

## 8.10 이 미션에서 기억할 핵심

| 질문 | 답 |
| --- | --- |
| 제너레이터는 무엇인가? | 값을 한 번에 만들지 않고 하나씩 내보내는 객체 |
| `yield`는 무엇인가? | 값을 하나 내보내고 함수를 잠시 멈추는 키워드 |
| 왜 쓰는가? | 큰 파일을 메모리에 전부 올리지 않기 위해 |
| 어디에 쓰는가? | 거래 파일 읽기, 검색, 요약, export |
| 주의할 점은? | 한 번 소비하면 다시 쓰려면 새로 만들어야 하고, 정렬은 모아야 할 수 있다 |

## 8.11 스트리밍 처리

스트리밍 처리는 데이터를 한꺼번에 다 읽지 않고 흐름처럼 조금씩 처리하는 방식이다.

예:

```text
파일 한 줄 읽기 -> JSON 파싱 -> 조건 검사 -> 출력 또는 집계 -> 다음 줄 읽기
```

`search` 명령은 스트리밍 처리의 대표 예다.

```text
transactions.jsonl 전체를 리스트로 만들지 않고,
한 줄씩 읽으면서 조건에 맞는 거래만 출력한다.
```

## 8.11.1 스트리밍 처리를 일상 예시로 이해하기

스트리밍 처리는 물건을 한꺼번에 창고로 다 옮긴 뒤 검사하는 방식이 아니라, **컨베이어 벨트 위에 올라오는 물건을 하나씩 검사하는 방식**에 가깝다.

```text
전체 로딩 방식:
상자 10만 개를 전부 방 안에 넣는다.
그다음 하나씩 열어본다.

스트리밍 방식:
상자가 하나 들어온다.
검사한다.
필요하면 처리한다.
다음 상자가 들어온다.
검사한다.
```

가계부 파일로 바꿔 말하면:

```text
전체 로딩 방식:
transactions.jsonl의 모든 거래를 리스트로 만든다.
그 리스트를 검색하거나 요약한다.

스트리밍 방식:
transactions.jsonl을 한 줄 읽는다.
그 한 줄의 거래만 검사한다.
필요한 계산을 한다.
다음 줄로 넘어간다.
```

## 8.11.2 전체 로딩 방식의 문제

다음 코드는 이해하기 쉽다.

```python
def read_all(path):
    rows = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            rows.append(line)

    return rows
```

하지만 이 코드는 파일의 모든 줄을 리스트에 담는다.

파일이 10줄이면 괜찮다.  
파일이 100줄이어도 괜찮다.  
하지만 파일이 100만 줄이면 부담이 커진다.

문제:

- 메모리를 많이 사용한다.
- 첫 결과를 얻기까지 전체 파일을 읽어야 한다.
- 검색 조건에 맞는 거래가 3개뿐이어도 100만 줄을 전부 리스트에 담는다.

## 8.11.3 스트리밍 방식의 장점

스트리밍 방식은 한 줄씩 처리한다.

```python
def iter_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            yield line
```

이 함수는 파일 전체를 리스트로 만들지 않는다.

사용:

```python
for line in iter_lines("transactions.jsonl"):
    print(line)
```

흐름:

```text
파일 첫 줄 읽기
-> yield로 바깥에 전달
-> for문 본문 실행
-> 파일 둘째 줄 읽기
-> yield로 바깥에 전달
-> for문 본문 실행
```

장점:

- 메모리를 적게 쓴다.
- 큰 파일에 강하다.
- 조건에 맞지 않는 데이터는 바로 버릴 수 있다.
- 검색, 요약, export 같은 작업에 잘 맞는다.

## 8.11.4 스트리밍 검색 예시

예를 들어 `category`가 `food`인 거래만 찾는다고 하자.

전체 로딩 방식:

```python
transactions = read_all_transactions(path)

for tx in transactions:
    if tx.category == "food":
        print(tx)
```

이 방식은 모든 거래를 먼저 메모리에 올린다.

스트리밍 방식:

```python
for tx in iter_transactions(path):
    if tx.category == "food":
        print(tx)
```

이 방식은 한 거래씩 읽으면서 조건을 확인한다.

```text
TX-000001 읽기 -> food인가? 맞으면 출력
TX-000002 읽기 -> food인가? 아니면 버림
TX-000003 읽기 -> food인가? 맞으면 출력
```

## 8.11.5 스트리밍 요약 예시

요약은 모든 거래를 출력할 필요가 없다.  
필요한 숫자만 계속 더하면 된다.

```python
total_income = 0
total_expense = 0

for tx in iter_transactions(path):
    if not tx.date.startswith("2024-01"):
        continue

    if tx.type == "income":
        total_income += tx.amount
    elif tx.type == "expense":
        total_expense += tx.amount
```

이 코드는 거래를 모두 리스트에 저장하지 않는다.  
대신 `total_income`, `total_expense`라는 숫자만 계속 갱신한다.

이런 형태가 스트리밍 처리의 장점이 가장 잘 드러나는 예다.

## 8.11.6 스트리밍 처리에도 한계가 있다

스트리밍 처리는 좋지만 모든 문제를 해결하지는 않는다.

### 정렬

정렬은 전체 데이터를 비교해야 한다.

```python
sorted_transactions = sorted(iter_transactions(path), key=lambda tx: tx.date)
```

이 코드는 겉보기에는 제너레이터를 쓰지만, `sorted()`가 내부적으로 모든 값을 모은다.

즉, 최신순 정렬을 완벽하게 하려면 어느 정도 메모리를 써야 한다.

### 여러 번 반복

제너레이터는 한 번 끝까지 읽으면 다시 사용할 수 없다.

```python
transactions = iter_transactions(path)

for tx in transactions:
    ...

for tx in transactions:
    ...  # 이미 소비되어 아무것도 안 나올 수 있음
```

다시 읽고 싶으면 새 제너레이터를 만들어야 한다.

```python
for tx in iter_transactions(path):
    ...

for tx in iter_transactions(path):
    ...
```

## 8.11.7 이번 미션에서의 현실적인 선택

이번 미션에서는 다음 기준으로 생각하면 된다.

| 기능 | 스트리밍 적합도 | 이유 |
| --- | --- | --- |
| `search` | 높음 | 조건에 맞는 거래만 하나씩 찾으면 됨 |
| `summary` | 높음 | 합계 숫자만 누적하면 됨 |
| `export` | 높음 | 조건에 맞는 거래를 CSV에 하나씩 쓰면 됨 |
| `list --limit` | 중간 | 최신순 때문에 일부 정렬 또는 최근 N개 관리 필요 |
| `update/delete` | 높음 | 원본 파일을 한 줄씩 읽고 임시 파일에 쓰면 됨 |

> [!important]
> 스트리밍 처리는 "무조건 리스트를 쓰지 말라"는 뜻이 아니다.  
> **파일을 읽는 기본 방식은 한 줄씩 처리하되, 정렬처럼 꼭 필요한 경우에만 리스트로 모은다**고 이해하면 된다.

## 8.12 최신순 출력과 스트리밍의 충돌

요구사항에는 `list`와 `search` 결과를 최신순으로 출력하라는 조건이 있다.

여기서 한 가지 고민이 생긴다.

- 최신순 정렬을 완벽하게 하려면 모든 결과를 모아 정렬해야 한다.
- 하지만 모든 결과를 모으면 스트리밍의 장점이 줄어든다.

해결 전략:

1. 거래를 애초에 날짜순으로 저장한다.
2. 제한된 개수만 필요하면 최근 N개만 유지한다.
3. 검색 결과가 아주 클 수 있다면 결과 누적 범위를 제한하거나, 정렬 비용을 감수한다.

이번 미션에서는 요구사항 충족이 우선이므로, 최신순 출력이 필요한 경우에는 **필요한 범위 안에서만 리스트화**하는 방식을 생각할 수 있다.

---

# 9. 데코레이터

데코레이터는 함수의 앞뒤에 공통 기능을 덧붙이는 도구다.

> [!summary]
> 데코레이터는 **기존 함수 코드를 직접 고치지 않고, 함수 실행 전후에 부가 기능을 붙이는 문법**이다.  
> 이번 미션에서는 오류 처리, 실행 시간 측정, 로그 출력처럼 여러 명령에서 반복되는 기능을 깔끔하게 분리할 때 쓴다.

이번 미션에서는 다음과 같은 공통 관심사를 데코레이터로 분리하라고 되어 있다.

- 예외 처리
- 실행 로그
- 실행 시간 측정

## 9.1 공통 관심사란?

여러 기능에서 반복적으로 필요한 보조 기능을 공통 관심사라고 한다.

예:

```text
add 실행 전후 로그 남기기
list 실행 시간 측정하기
search에서 오류가 나면 친절한 메시지 출력하기
```

이런 코드를 모든 함수에 직접 넣으면 중복이 많아진다.

## 9.2 데코레이터의 개념

데코레이터는 함수를 감싸는 함수다.

조금 더 쉽게 말하면, 데코레이터는 함수에 입히는 **겉옷** 같은 것이다.

```text
원래 함수:
명령의 핵심 기능만 수행한다.

데코레이터를 입힌 함수:
명령 실행 전 로그 출력
-> 원래 함수 실행
-> 오류가 나면 친절한 메시지 출력
-> 실행 시간 출력
```

원래 함수의 코드를 매번 고치지 않고도 기능을 덧붙일 수 있다.

개념적으로:

```python
@decorator
def command():
    ...
```

이것은 다음과 비슷하다.

```python
command = decorator(command)
```

즉, 원래 함수를 다른 함수로 감싼다.

## 9.3 함수도 값이다

데코레이터를 이해하려면 먼저 Python에서 함수도 값처럼 다룰 수 있다는 것을 알아야 한다.

```python
def say_hello():
    print("hello")

greeting = say_hello
greeting()
```

위 코드에서 `greeting = say_hello`는 함수를 복사해서 실행한 것이 아니다.  
`say_hello`라는 함수 자체를 `greeting`이라는 이름으로도 부를 수 있게 만든 것이다.

그래서 다음 두 호출은 같은 함수를 실행한다.

```python
say_hello()
greeting()
```

이 개념이 데코레이터의 출발점이다.

## 9.4 함수를 인자로 받는 함수

함수는 값처럼 다룰 수 있으므로, 다른 함수의 인자로 전달할 수 있다.

```python
def say_hello():
    print("hello")

def run_function(func):
    print("함수를 실행하기 전")
    func()
    print("함수를 실행한 후")

run_function(say_hello)
```

실행 흐름:

```text
1. run_function에 say_hello 함수를 전달한다.
2. "함수를 실행하기 전" 출력
3. func() 실행
4. 실제로는 say_hello()가 실행된다.
5. "hello" 출력
6. "함수를 실행한 후" 출력
```

여기서 `run_function()`은 이미 데코레이터와 비슷한 일을 하고 있다.  
원래 함수 앞뒤에 다른 일을 끼워 넣고 있기 때문이다.

## 9.5 함수를 반환하는 함수

데코레이터는 보통 함수를 인자로 받고, 새로운 함수를 반환한다.

```python
def simple_decorator(func):
    def wrapper():
        print("함수 실행 전")
        func()
        print("함수 실행 후")

    return wrapper
```

여기서 역할은 다음과 같다.

| 이름 | 역할 |
| --- | --- |
| `simple_decorator` | 데코레이터 함수 |
| `func` | 감싸고 싶은 원래 함수 |
| `wrapper` | 원래 함수 앞뒤에 기능을 붙인 새 함수 |
| `return wrapper` | 새 함수를 바깥으로 돌려줌 |

사용:

```python
def say_hello():
    print("hello")

decorated = simple_decorator(say_hello)
decorated()
```

출력:

```text
함수 실행 전
hello
함수 실행 후
```

핵심은 이것이다.

```text
say_hello 함수 자체를 바꾸지 않았는데,
say_hello 앞뒤에 동작이 추가되었다.
```

## 9.6 `@decorator` 문법

Python은 데코레이터를 더 짧게 쓸 수 있도록 `@` 문법을 제공한다.

아래 두 코드는 같은 의미다.

### 직접 감싸기

```python
def say_hello():
    print("hello")

say_hello = simple_decorator(say_hello)
```

### `@` 문법 사용

```python
@simple_decorator
def say_hello():
    print("hello")
```

즉:

```python
@simple_decorator
def say_hello():
    ...
```

는 다음과 같은 뜻이다.

```python
say_hello = simple_decorator(say_hello)
```

> [!important]
> `@decorator`는 마법처럼 보이지만, 실제로는 **함수를 다른 함수로 감싸서 다시 같은 이름에 넣는 문법**이다.

## 9.7 인자가 있는 함수 감싸기

실제 프로그램의 함수는 대부분 인자를 가진다.

예:

```python
def add_transaction(date, amount):
    print(date, amount)
```

이런 함수를 감싸려면 `wrapper`도 인자를 받을 수 있어야 한다.

```python
def simple_decorator(func):
    def wrapper(*args, **kwargs):
        print("함수 실행 전")
        result = func(*args, **kwargs)
        print("함수 실행 후")
        return result

    return wrapper
```

여기서:

- `*args`는 위치 인자를 모은다.
- `**kwargs`는 키워드 인자를 모은다.

예:

```python
@simple_decorator
def add_transaction(date, amount):
    print(f"{date}: {amount}")

add_transaction("2024-01-15", 15000)
```

실행 흐름:

```text
1. add_transaction("2024-01-15", 15000) 호출
2. 실제로는 wrapper("2024-01-15", 15000) 실행
3. "함수 실행 전" 출력
4. func(*args, **kwargs) 실행
5. 원래 add_transaction 실행
6. "2024-01-15: 15000" 출력
7. "함수 실행 후" 출력
```

## 9.7.1 `*args` 쉽게 이해하기

`*args`는 함수에 들어온 **위치 인자들을 튜플로 모아주는 문법**이다.

위치 인자는 이름 없이 순서대로 전달하는 값이다.

```python
def add(a, b):
    return a + b

add(3, 5)
```

여기서 `3`과 `5`가 위치 인자다.

`*args`를 쓰면 인자 개수가 정해져 있지 않아도 받을 수 있다.

```python
def show_args(*args):
    print(args)

show_args(1, 2, 3)
```

출력:

```text
(1, 2, 3)
```

즉:

```text
*args = 위치 인자를 전부 모은 튜플
```

예:

```python
def wrapper(*args):
    print(args)

wrapper("2024-01-15", 15000, "food")
```

출력:

```text
("2024-01-15", 15000, "food")
```

## 9.7.2 `**kwargs` 쉽게 이해하기

`**kwargs`는 함수에 들어온 **키워드 인자들을 딕셔너리로 모아주는 문법**이다.

키워드 인자는 이름을 붙여 전달하는 값이다.

```python
def add_transaction(date, amount, category):
    ...

add_transaction(date="2024-01-15", amount=15000, category="food")
```

여기서 `date=...`, `amount=...`, `category=...`가 키워드 인자다.

`**kwargs`를 쓰면 이런 키워드 인자들을 딕셔너리로 받을 수 있다.

```python
def show_kwargs(**kwargs):
    print(kwargs)

show_kwargs(date="2024-01-15", amount=15000, category="food")
```

출력:

```text
{"date": "2024-01-15", "amount": 15000, "category": "food"}
```

즉:

```text
**kwargs = 키워드 인자를 전부 모은 딕셔너리
```

## 9.7.3 데코레이터에서 왜 `*args`, `**kwargs`를 쓸까?

데코레이터는 여러 종류의 함수를 감쌀 수 있어야 한다.

예를 들어 다음 함수들은 인자 모양이 다 다르다.

```python
def handle_add_command(args):
    ...

def calculate_summary(month, top):
    ...

def save_transaction(transaction, data_dir="./data"):
    ...
```

데코레이터가 특정 인자만 받도록 만들면 한 종류의 함수만 감쌀 수 있다.

```python
def wrapper(args):
    return func(args)
```

이렇게 만들면 `handle_add_command(args)`는 감쌀 수 있지만, `calculate_summary(month, top)`은 감싸기 어렵다.

그래서 데코레이터의 `wrapper`는 보통 이렇게 만든다.

```python
def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
```

이 뜻은 다음과 같다.

```text
어떤 위치 인자가 들어오든 args로 받고,
어떤 키워드 인자가 들어오든 kwargs로 받고,
그대로 원래 함수에 다시 전달한다.
```

예:

```python
def wrapper(*args, **kwargs):
    print("실행 전")
    result = func(*args, **kwargs)
    print("실행 후")
    return result
```

이렇게 하면 인자 모양이 다른 함수도 하나의 데코레이터로 감쌀 수 있다.

## 9.7.4 `*args`, `**kwargs`를 다시 풀어 전달하기

`*args`와 `**kwargs`는 받을 때도 쓰지만, 다시 전달할 때도 쓴다.

```python
def original(a, b, c=None):
    print(a, b, c)

args = (1, 2)
kwargs = {"c": 3}

original(*args, **kwargs)
```

이 코드는 다음과 같다.

```python
original(1, 2, c=3)
```

데코레이터에서:

```python
func(*args, **kwargs)
```

는 "내가 받은 인자들을 원래 함수에 그대로 넘겨라"라는 뜻이다.

## 9.8 반환값이 있는 함수 감싸기

원래 함수가 값을 반환한다면, wrapper도 그 값을 다시 반환해야 한다.

나쁜 예:

```python
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    return wrapper
```

이 데코레이터는 원래 함수의 반환값을 버린다.

좋은 예:

```python
def good_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result

    return wrapper
```

이번 미션에서 CLI 명령 함수가 exit code를 반환한다면, 데코레이터는 그 exit code를 그대로 돌려줘야 한다.

```python
@good_decorator
def handle_list_command(args):
    ...
    return 0
```

## 9.8.1 데코레이터의 함수 반환값이 왜 중요할까?

데코레이터는 원래 함수를 감싼다.  
그런데 감싼 함수가 원래 함수의 결과를 돌려주지 않으면, 바깥 코드는 결과를 잃어버린다.

예를 들어 원래 함수가 계산 결과를 반환한다고 하자.

```python
def add(a, b):
    return a + b
```

잘못된 데코레이터:

```python
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        print("계산 시작")
        func(*args, **kwargs)
        print("계산 끝")

    return wrapper
```

사용:

```python
@bad_decorator
def add(a, b):
    return a + b

result = add(3, 5)
print(result)
```

출력:

```text
계산 시작
계산 끝
None
```

원래 `add(3, 5)`는 `8`을 반환해야 한다.  
하지만 `wrapper`가 `func()`의 결과를 반환하지 않았기 때문에 `None`이 나온다.

올바른 데코레이터:

```python
def good_decorator(func):
    def wrapper(*args, **kwargs):
        print("계산 시작")
        result = func(*args, **kwargs)
        print("계산 끝")
        return result

    return wrapper
```

이제:

```python
result = add(3, 5)
```

는 다시 `8`을 받을 수 있다.

## 9.8.2 CLI에서 반환값은 exit code일 수 있다

이번 미션의 CLI 명령 함수는 이런 식으로 설계할 수 있다.

```python
def handle_list_command(args):
    ...
    return 0
```

여기서 `0`은 정상 종료를 뜻한다.

오류가 있으면:

```python
def handle_delete_command(args):
    ...
    return 1
```

처럼 `0`이 아닌 값을 반환할 수 있다.

그런데 데코레이터가 반환값을 버리면 문제가 생긴다.

```python
@bad_decorator
def handle_list_command(args):
    return 0
```

이 경우 실제 반환값이 `None`이 될 수 있다.  
그러면 프로그램의 종료 코드 처리도 애매해진다.

따라서 데코레이터는 항상 원래 함수의 반환값을 보존해야 한다.

```python
result = func(*args, **kwargs)
return result
```

## 9.8.3 예외 처리 데코레이터의 반환값

예외 처리 데코레이터는 조금 다르다.

```python
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AppError:
            return 1

    return wrapper
```

정상 상황:

```text
원래 함수가 return 0
-> 데코레이터도 return 0
```

오류 상황:

```text
원래 함수 실행 중 AppError 발생
-> 데코레이터가 오류 메시지 출력
-> return 1
```

즉, 데코레이터가 반환값을 보존한다는 말은 다음 뜻이다.

```text
정상일 때는 원래 함수의 결과를 그대로 돌려준다.
오류를 처리하는 데코레이터라면 오류 상황에서 약속된 오류 값을 돌려준다.
```

## 9.9 함수 이름 보존하기: `functools.wraps`

데코레이터를 만들 때는 `functools.wraps`를 자주 사용한다.

```python
from functools import wraps

def simple_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
```

왜 필요할까?

데코레이터는 원래 함수를 `wrapper` 함수로 바꾼다.  
그 결과 함수 이름이나 설명이 전부 `wrapper`처럼 보일 수 있다.

`@wraps(func)`를 붙이면 원래 함수의 이름, 설명, 메타데이터를 최대한 유지해준다.

> [!tip]
> 데코레이터를 직접 만들 때는 거의 습관처럼 `@wraps(func)`를 붙이는 것이 좋다.

## 9.9.1 `functools.wraps`가 없으면 생기는 일

데코레이터는 원래 함수를 `wrapper`로 바꾼다.

```python
def simple_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

@simple_decorator
def handle_add_command(args):
    """거래를 추가한다."""
    return 0
```

이제 함수 이름을 확인해보면:

```python
print(handle_add_command.__name__)
```

`handle_add_command`가 아니라 `wrapper`로 보일 수 있다.

```text
wrapper
```

왜냐하면 실제로는 다음과 같은 일이 일어났기 때문이다.

```python
handle_add_command = simple_decorator(handle_add_command)
```

그리고 `simple_decorator()`가 반환한 것은 `wrapper` 함수다.

## 9.9.2 이름이 바뀌면 왜 불편할까?

함수 이름이 `wrapper`로 바뀌면 다음 상황에서 불편하다.

- 디버깅할 때 어떤 함수인지 알아보기 어렵다.
- 로그에 함수 이름을 남길 때 전부 `wrapper`로 나온다.
- 테스트나 문서화 도구가 원래 함수 정보를 잃을 수 있다.
- `help()`나 함수 설명을 볼 때 원래 설명이 사라질 수 있다.

예를 들어 로그가 이렇게 나오면 별 도움이 안 된다.

```text
[로그] wrapper 실행
[로그] wrapper 실행
[로그] wrapper 실행
```

원래는 이렇게 나와야 읽기 좋다.

```text
[로그] handle_add_command 실행
[로그] handle_search_command 실행
[로그] handle_summary_command 실행
```

## 9.9.3 `@wraps(func)`를 붙이면?

`functools.wraps`를 사용하면 wrapper 함수가 원래 함수의 정보를 물려받는다.

```python
from functools import wraps

def simple_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
```

이제:

```python
print(handle_add_command.__name__)
```

는 원래 이름에 가깝게 유지된다.

```text
handle_add_command
```

`@wraps(func)`가 보존해주는 대표 정보:

| 정보 | 의미 |
| --- | --- |
| `__name__` | 함수 이름 |
| `__doc__` | 함수 설명 문자열 |
| `__module__` | 함수가 속한 모듈 |
| 일부 메타데이터 | 디버깅과 문서화에 필요한 정보 |

## 9.9.4 wraps를 어디에 붙여야 할까?

`@wraps(func)`는 `wrapper` 함수 바로 위에 붙인다.

```python
def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ...

    return wrapper
```

헷갈리지 말아야 할 점:

```python
@wraps(func)
def wrapper(...):
    ...
```

는 `wrapper`를 꾸미는 것이다.  
즉, "이 wrapper는 func를 감싼 함수이니 func의 정보를 보존해라"라는 뜻이다.

> [!important]
> 데코레이터를 만들 때 `wrapper`가 있다면 거의 항상 `@wraps(func)`도 같이 있다고 기억하면 된다.

## 9.10 예외 처리 데코레이터

미션에서는 오류가 발생했을 때 스택트레이스를 그대로 출력하지 말아야 한다.

나쁜 UX:

```text
Traceback (most recent call last):
  File "...", line ...
ValueError: invalid literal for int()
```

좋은 UX:

```text
[오류] 금액은 양수 정수여야 합니다.
힌트: 예) 15000
```

예외 처리 데코레이터는 이런 역할을 할 수 있다.

```text
명령 실행
-> 오류 발생 여부 확인
-> 오류가 있으면 사용자 친화 메시지 출력
-> 오류 exit code 반환
```

예시:

```python
from functools import wraps

class AppError(Exception):
    pass

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AppError as error:
            print(f"[오류] {error}")
            print("힌트: 입력값을 다시 확인하세요.")
            return 1

    return wrapper
```

사용:

```python
@handle_errors
def handle_add_command(args):
    raise AppError("금액은 양수 정수여야 합니다.")
```

실행 결과:

```text
[오류] 금액은 양수 정수여야 합니다.
힌트: 입력값을 다시 확인하세요.
```

이렇게 하면 `handle_add_command`, `handle_search_command`, `handle_summary_command`마다 매번 `try/except`를 반복하지 않아도 된다.

## 9.11 실행 시간 측정 데코레이터

시간 측정은 프로그램 성능을 확인하는 데 도움이 된다.

흐름:

```text
시작 시간 기록
명령 실행
종료 시간 기록
걸린 시간 계산
로그 출력 또는 저장
```

이 기능을 명령마다 직접 작성하면 지저분해진다. 데코레이터로 분리하면 핵심 로직은 깔끔하게 유지된다.

예시:

```python
from functools import wraps
from time import perf_counter

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            end = perf_counter()
            elapsed = end - start
            print(f"[실행 시간] {elapsed:.3f}초")

    return wrapper
```

여기서 `finally`는 함수가 성공하든 오류가 나든 마지막에 실행된다.  
그래서 실행 시간 측정에 잘 맞는다.

## 9.12 데코레이터 여러 개 붙이기

데코레이터는 한 함수에 여러 개 붙일 수 있다.

```python
@handle_errors
@measure_time
def handle_summary_command(args):
    ...
```

이 코드는 아래와 비슷하다.

```python
handle_summary_command = handle_errors(measure_time(handle_summary_command))
```

실행 순서를 쉽게 생각하면:

```text
바깥쪽 handle_errors가 전체를 감싼다.
그 안에서 measure_time이 시간을 잰다.
그 안에서 원래 handle_summary_command가 실행된다.
```

데코레이터 순서는 결과에 영향을 줄 수 있다.  
예를 들어 오류 처리 데코레이터가 가장 바깥에 있으면, 안쪽에서 발생한 오류를 잡기 쉽다.

## 9.13 이번 미션에서 데코레이터를 쓰는 위치

추천 사용처:

| 데코레이터 | 적용 대상 | 목적 |
| --- | --- | --- |
| `handle_errors` | CLI 명령 처리 함수 | 스택트레이스 대신 친절한 오류 메시지 출력 |
| `measure_time` | `list`, `search`, `summary`, `import`, `export` | 처리 시간 확인 |
| `log_command` | 주요 명령 처리 함수 | 어떤 명령이 실행됐는지 기록 |

예:

```python
@handle_errors
@measure_time
def handle_search_command(args):
    results = service.search_transactions(
        date_from=args.date_from,
        date_to=args.date_to,
        category=args.category,
        transaction_type=args.type,
        keyword=args.q,
        tag=args.tag,
    )

    for tx in results:
        print_transaction(tx)

    return 0
```

이렇게 하면 `handle_search_command()` 안에는 검색 핵심 로직만 남기고, 오류 처리와 시간 측정은 바깥으로 분리할 수 있다.

## 9.14 데코레이터를 사용할 때 주의할 점

### 원래 함수의 반환값을 꼭 반환하기

CLI 함수가 `0`이나 `1` 같은 exit code를 반환한다면, 데코레이터도 그 값을 그대로 반환해야 한다.

```python
result = func(*args, **kwargs)
return result
```

이 부분을 빼먹으면 함수가 `None`을 반환하게 된다.

### 너무 많은 일을 데코레이터에 넣지 않기

데코레이터는 공통 관심사를 분리할 때 좋다.  
하지만 핵심 비즈니스 로직까지 데코레이터에 넣으면 오히려 읽기 어려워진다.

좋은 사용:

- 오류 메시지 정리
- 실행 시간 측정
- 로그 출력

피하는 것이 좋은 사용:

- 거래 저장 로직
- 카테고리 검증 로직 전체
- summary 계산 로직

### 데코레이터 실행 순서 이해하기

여러 데코레이터를 붙이면 순서가 중요하다.

```python
@A
@B
def func():
    ...
```

이 코드는:

```python
func = A(B(func))
```

와 같다.

헷갈리면 처음에는 데코레이터를 하나씩만 붙이고, 동작을 확인한 뒤 늘리는 것이 좋다.

## 9.15 데코레이터 핵심 요약

| 질문 | 답 |
| --- | --- |
| 데코레이터는 무엇인가? | 함수를 감싸서 실행 전후에 기능을 추가하는 함수 |
| `@decorator`는 무슨 뜻인가? | `함수 = decorator(함수)`를 짧게 쓴 문법 |
| 왜 쓰는가? | 반복되는 오류 처리, 로그, 시간 측정을 한곳에 모으기 위해 |
| 이번 미션 어디에 쓰는가? | CLI 명령 함수의 오류 처리, 실행 시간 측정 |
| 주의할 점은? | 반환값 보존, `@wraps` 사용, 실행 순서 이해 |

---

# 10. 입력 검증과 예외 처리

입력 검증은 사용자가 입력한 값이 프로그램 규칙에 맞는지 확인하는 과정이다.

## 10.1 검증해야 할 항목

거래 추가/수정에서 검증해야 할 것:

| 항목 | 검증 |
| --- | --- |
| 날짜 | `YYYY-MM-DD` 형식인지 |
| 타입 | `income` 또는 `expense`인지 |
| 카테고리 | 등록된 카테고리인지 |
| 금액 | 양수 정수인지 |
| 메모 | 문자열인지 |
| 태그 | 쉼표 구분 문자열을 리스트로 변환 가능한지 |

## 10.2 날짜 검증

날짜는 문자열 모양만 맞는다고 충분하지 않다.

예:

```text
2024-13-99
```

이 문자열은 `YYYY-MM-DD`처럼 보이지만 실제 날짜가 아니다.

Python에서는 `datetime.date.fromisoformat()` 같은 표준 기능으로 검증할 수 있다.

## 10.3 금액 검증

`amount`는 양수 정수여야 한다.

허용:

```text
1
15000
500000
```

거부:

```text
0
-1000
abc
15.5
```

## 10.4 카테고리 검증

거래를 추가할 때 카테고리는 등록된 목록에 있어야 한다.

등록되지 않은 카테고리를 허용하면:

```text
food
Food
foods
식비
```

처럼 비슷한 의미의 카테고리가 흩어져 summary가 부정확해진다.

따라서 없는 카테고리라면:

- 다시 입력하도록 안내하거나
- 먼저 `category add`를 하도록 안내해야 한다.

## 10.5 예외와 사용자 메시지

예외는 프로그램 실행 중 예상하지 못한 문제를 표현하는 방식이다.

하지만 사용자는 내부 스택트레이스보다 다음 정보를 원한다.

- 무엇이 잘못됐는지
- 어떻게 고치면 되는지
- 프로그램이 계속 사용 가능한지

좋은 오류 메시지 예:

```text
[오류] 존재하지 않는 카테고리입니다: snack
힌트: category add snack 명령으로 먼저 추가하세요.
```

---

# 11. 검색 기능 설계

검색은 저장된 거래 중 조건에 맞는 거래만 찾는 기능이다.

지원 조건:

- 기간: `--from`, `--to`
- 카테고리: `--category`
- 타입: `--type`
- 메모 키워드: `-q`
- 태그: `--tag`

## 11.1 조건 조합

사용자가 여러 조건을 함께 줄 수 있다.

예:

```bash
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food --type expense
```

이 경우 의미는:

```text
2024년 1월 1일부터 1월 31일까지의 거래 중
카테고리가 food이고
타입이 expense인 거래
```

즉, 조건들은 보통 AND로 결합된다.

## 11.2 날짜 범위

검색 범위에서 주의할 점:

- `--from`만 있으면 해당 날짜 이후
- `--to`만 있으면 해당 날짜 이전
- 둘 다 있으면 양 끝 포함 범위

예:

```text
from <= transaction.date <= to
```

## 11.3 키워드 검색

`-q`는 메모 키워드 검색이다.

예:

```bash
python -m budget_app search -q 점심
```

메모에 `점심`이 포함된 거래를 찾는다.

대소문자 처리를 어떻게 할지도 정해야 한다.

- 한글 위주라면 단순 포함 검색으로 충분할 수 있다.
- 영어 메모까지 고려하면 소문자로 변환해 비교할 수 있다.

## 11.4 태그 검색

태그는 문자열 하나가 아니라 목록이다.

예:

```json
"tags": ["meal", "friend"]
```

`--tag meal`이면 `tags` 목록에 `"meal"`이 포함되어 있는지 확인해야 한다.

## 11.5 최신순 출력

검색 결과는 최신순으로 출력해야 한다.

최신순 기준:

1. 날짜가 늦은 거래 먼저
2. 같은 날짜라면 ID가 큰 거래 먼저 또는 저장 순서 역순

정렬 기준은 README에 명확히 적어두면 좋다.

---

# 12. 월별 요약과 예산

`summary`는 가계부의 핵심 리포트다.

## 12.1 summary 기본 출력

명령:

```bash
python -m budget_app summary --month 2024-01
```

출력해야 할 항목:

- 총수입
- 총지출
- 잔액
- 카테고리별 지출 합계 TOP N

계산:

```text
총수입 = 해당 월 income 거래의 amount 합계
총지출 = 해당 월 expense 거래의 amount 합계
잔액 = 총수입 - 총지출
```

## 12.2 월 필터

`--month YYYY-MM`은 해당 월에 속하는 거래만 대상으로 한다.

예:

```text
2024-01-01
2024-01-15
2024-01-31
```

위 날짜들은 `2024-01`에 포함된다.

간단한 방식:

```text
date 문자열이 "2024-01"로 시작하는지 확인
```

더 엄밀한 방식:

```text
date 객체로 파싱한 뒤 year/month 비교
```

## 12.3 카테고리별 지출 TOP N

`--top N` 옵션이 있으면 지출 합계가 큰 카테고리 N개를 출력한다.

예:

```text
food: 220000
transport: 85000
rent: 500000
```

정렬 기준:

1. 지출 합계 내림차순
2. 동률이면 카테고리 이름순 등 보조 기준

## 12.4 데이터가 없는 달

해당 월 거래가 없으면 명확히 출력해야 한다.

예:

```text
2024-03 데이터 없음
```

단순히 빈 화면을 보여주면 사용자가 오류인지 정상인지 알기 어렵다.

## 12.5 예산 사용률

예산이 설정되어 있다면 summary에서 사용률을 함께 출력해야 한다.

```text
예산 사용률 = 총지출 / 예산 * 100
```

예:

```text
월 예산: 500000
총지출: 420000
사용률: 84.0%
초과 여부: 정상
```

예산 초과 시:

```text
월 예산: 500000
총지출: 650000
사용률: 130.0%
경고: 예산을 초과했습니다.
```

---

# 13. 카테고리 관리

카테고리는 거래를 분류하는 기준이다.

## 13.1 category add

새 카테고리를 추가한다.

```bash
python -m budget_app category add food
```

고려할 점:

- 이미 존재하는 카테고리는 중복 추가하지 않는다.
- 카테고리 이름의 앞뒤 공백은 제거한다.
- 빈 문자열은 허용하지 않는다.

## 13.2 category list

등록된 카테고리를 출력한다.

```bash
python -m budget_app category list
```

출력은 정렬되어 있으면 보기 좋다.

```text
food
rent
salary
transport
```

## 13.3 category remove

카테고리를 삭제한다.

```bash
python -m budget_app category remove food
```

중요한 조건:

> 삭제하려는 카테고리를 사용하는 거래가 존재하면 삭제를 막거나, 대체 카테고리를 요구해야 한다.

삭제를 그냥 허용하면 과거 거래의 `category`가 더 이상 유효하지 않은 상태가 된다.

가능한 정책:

1. 삭제 차단
   - "이 카테고리를 사용하는 거래가 있어 삭제할 수 없습니다."

2. 대체 카테고리 요구
   - "food를 meal로 변경한 뒤 삭제합니다."

미션 요구에는 삭제를 막거나 대체 카테고리를 요구하라고 되어 있으므로, 둘 중 하나를 문서에 명확히 정해야 한다.

---

# 14. import/export 개념

import/export는 외부 파일과 데이터를 주고받는 기능이다.

## 14.1 import

명령:

```bash
python -m budget_app import --from transactions.csv
```

역할:

- CSV 파일을 읽는다.
- 각 행을 검증한다.
- 유효한 거래를 저장한다.
- 처리 건수를 출력한다.

주의할 점:

- CSV 헤더가 있어야 한다.
- 필수 컬럼이 없으면 오류 처리한다.
- 날짜, 타입, 카테고리, 금액 검증을 수행한다.
- 등록되지 않은 카테고리를 어떻게 처리할지 정책을 정한다.

## 14.2 export

명령:

```bash
python -m budget_app export --out result.csv --month 2024-01
```

또는:

```bash
python -m budget_app export --out result.csv --from 2024-01-01 --to 2024-01-31
```

역할:

- 조건에 맞는 거래를 찾는다.
- CSV 형식으로 저장한다.
- 처리 건수를 출력한다.

중요 조건:

- `--month YYYY-MM` 또는 `--from YYYY-MM-DD --to YYYY-MM-DD` 중 하나 이상의 조건을 필수로 받는다.
- CSV는 UTF-8, 헤더 포함이어야 한다.

## 14.3 CSV에서 tags 처리

내부 데이터에서는 태그가 리스트일 수 있다.

```json
"tags": ["meal", "friend"]
```

CSV에서는 한 칸에 넣어야 하므로 보통 다음처럼 저장한다.

```csv
tags
meal,friend
```

주의:

- 태그 내부에 쉼표를 허용하면 복잡해진다.
- 이번 미션에서는 태그 구분자를 쉼표로 고정하고, 태그 자체에는 쉼표를 허용하지 않는 것이 단순하다.

---

# 15. update/delete와 파일 원자성

파일 기반 저장에서 update/delete는 특히 조심해야 한다.

## 15.1 왜 직접 수정하면 위험할까?

거래 파일:

```jsonl
{"id":"TX-000001",...}
{"id":"TX-000002",...}
{"id":"TX-000003",...}
```

중간 줄만 수정하려다가 프로그램이 중간에 종료되면 파일이 깨질 수 있다.

예:

```text
쓰기 도중 전원 종료
디스크 오류
예외 발생
```

## 15.2 임시 파일 후 교체 방식

더 안전한 방식:

1. 원본 파일을 읽는다.
2. 새 내용을 임시 파일에 쓴다.
3. 쓰기가 끝나면 임시 파일을 원본 파일로 교체한다.

흐름:

```text
transactions.jsonl
-> transactions.jsonl.tmp 작성
-> 성공 시 transactions.jsonl.tmp 를 transactions.jsonl 로 rename
```

`rename`은 같은 파일 시스템 안에서는 보통 원자적이다. 즉, 사용자는 이전 파일 또는 새 파일 중 하나만 보게 된다.

## 15.3 update 방식

요구사항에서 update는 두 방식 중 하나를 선택하라고 되어 있다.

### 안 A: 옵션 기반

```bash
python -m budget_app update --id TX-000012 --date 2024-01-16 --amount 18000
```

장점:

- 자동화하기 쉽다.
- 한 줄 명령으로 수정 가능하다.

단점:

- 옵션이 많아질 수 있다.

### 안 B: 대화형 기반

```bash
python -m budget_app update --id TX-000012
```

실행 후 수정할 필드를 선택/입력한다.

장점:

- 사용자가 편하다.
- 기존 값을 보여주고 필요한 항목만 수정하기 좋다.

단점:

- 자동화와 테스트가 옵션 기반보다 어렵다.

> [!note]
> 어떤 방식을 선택하든 README에 명확히 적어야 한다.

---

# 16. 모듈화와 계층 분리

미션은 한 파일에 몰아넣지 말고 최소 3개 이상 모듈로 분리하라고 요구한다.

> [!summary]
> 모듈화는 코드를 역할별 파일로 나누는 것이고, 계층 분리는 각 파일이 맡을 책임을 정하는 것이다.  
> 쉽게 말해 **CLI는 입력만, Service는 규칙만, Repository는 파일 저장만, Model은 데이터 모양만 담당하게 나누는 것**이다.

권장 계층:

```text
CLI / Service / Repository / Model
```

## 16.0 모듈이란?

Python에서 모듈은 보통 `.py` 파일 하나를 말한다.

예:

```text
models.py
services.py
storage.py
cli.py
```

각 파일은 하나의 모듈이다.

예를 들어 `models.py`에 `Transaction` 클래스를 정의하면 다른 파일에서 가져다 쓸 수 있다.

```python
from budget_app.models import Transaction
```

모듈화는 코드를 파일별로 나누는 작업이다.

```text
한 파일에 전부 넣기:
main.py 안에 CLI, 저장, 계산, 검증, 출력이 전부 있음

모듈화:
models.py     -> 데이터 구조
storage.py    -> 파일 읽기/쓰기
services.py   -> 업무 규칙
cli.py        -> 명령어 처리
validators.py -> 입력 검증
```

## 16.0.1 왜 한 파일에 몰아넣으면 힘들까?

처음에는 한 파일이 편해 보인다.

```text
main.py 하나만 열면 모든 코드가 보인다.
파일 이동을 안 해도 된다.
빨리 시작할 수 있다.
```

하지만 기능이 늘어나면 문제가 생긴다.

```text
add 기능 코드
list 기능 코드
search 기능 코드
summary 계산 코드
파일 저장 코드
CSV 처리 코드
오류 처리 코드
출력 포맷 코드
```

이 모든 것이 한 파일에 섞이면 다음 문제가 생긴다.

- 어디에 어떤 코드가 있는지 찾기 어렵다.
- 작은 수정이 다른 기능에 영향을 줄 수 있다.
- 같은 코드가 여러 곳에 반복된다.
- 테스트하기 어렵다.
- 나중에 저장 방식을 바꾸기 어렵다.

모듈화는 이 문제를 줄이기 위한 정리 방식이다.

## 16.0.2 계층 분리란?

계층 분리는 단순히 파일을 나누는 것보다 한 단계 더 나아간 개념이다.

파일을 아무렇게나 나누면 모듈화는 되었지만 구조가 여전히 복잡할 수 있다.

나쁜 예:

```text
a.py
b.py
c.py
```

파일은 나뉘었지만 각 파일이 무엇을 담당하는지 알기 어렵다.

좋은 예:

```text
models.py      -> 데이터 구조
repositories.py -> 파일 저장소 접근
services.py    -> 가계부 규칙
cli.py         -> 사용자 명령 처리
```

계층 분리는 이렇게 책임을 기준으로 파일을 나누는 것이다.

> [!important]
> 모듈화가 "파일을 나누는 것"이라면, 계층 분리는 "책임을 기준으로 파일을 나누는 것"이다.

## 16.1 Model 계층

역할:

- 데이터 구조 정의
- `Transaction`, `Category`, `Budget` 같은 모델 정의
- dict 변환, 검증 보조 함수 제공 가능

예:

```text
models.py
```

Model 계층은 데이터의 모양을 정의한다.

이번 미션의 대표 모델은 다음과 같다.

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

Model은 보통 이런 질문에 답한다.

```text
거래는 어떤 필드를 가지는가?
예산은 어떤 필드를 가지는가?
카테고리는 문자열만 있으면 되는가?
파일에서 읽은 dict를 Transaction으로 어떻게 바꾸는가?
Transaction을 dict로 어떻게 바꾸는가?
```

Model이 직접 하면 좋지 않은 일:

```text
터미널 입력 받기
파일 열고 저장하기
summary 출력하기
사용자에게 오류 메시지 출력하기
```

Model은 데이터 모양에 집중한다.

## 16.2 Repository 계층

Repository는 저장소 접근을 담당한다.

역할:

- 파일 읽기
- 파일 쓰기
- JSONL/CSV 파싱
- 거래 iterating
- update/delete 시 파일 교체

예:

```text
repositories.py
storage.py
```

Repository가 있으면 서비스 계층은 파일 포맷을 자세히 몰라도 된다.

Repository는 저장소 담당자다.

이번 미션에서는 데이터베이스를 사용하지 않고 파일을 사용한다.  
그래서 Repository는 파일 저장소와 대화한다.

Repository가 하는 일:

```text
transactions.jsonl 파일 열기
한 줄씩 읽기
JSON 문자열을 dict로 바꾸기
dict를 Transaction으로 바꾸기
Transaction을 JSONL 한 줄로 저장하기
update/delete 때 임시 파일로 교체하기
```

예:

```python
class TransactionRepository:
    def iter_all(self):
        ...

    def append(self, transaction):
        ...

    def replace_all(self, transactions):
        ...
```

Service는 이렇게 사용할 수 있다.

```python
for tx in transaction_repository.iter_all():
    ...
```

중요한 점:

```text
Service는 transactions.jsonl이 정확히 어떻게 생겼는지 몰라도 된다.
Repository가 알아서 파일을 읽고 Transaction 객체로 넘겨준다.
```

Repository가 직접 하면 좋지 않은 일:

```text
예산 초과 여부 판단하기
카테고리별 TOP N 계산하기
터미널에 예쁘게 출력하기
argparse 옵션 처리하기
```

Repository는 저장과 읽기에 집중한다.

## 16.3 Service 계층

Service는 실제 업무 규칙을 담당한다.

역할:

- 거래 추가 규칙
- 카테고리 존재 검증
- 월별 요약 계산
- 예산 초과 판단
- 검색 조건 적용

예:

```text
services.py
```

Service는 이 프로그램의 머리에 해당한다.

예를 들어 거래 추가는 단순히 파일에 한 줄 쓰는 일이 아니다.

거래 추가에는 이런 규칙이 있다.

```text
날짜가 올바른가?
type이 income 또는 expense인가?
amount가 양수인가?
category가 등록되어 있는가?
id를 어떻게 만들 것인가?
저장 후 무엇을 반환할 것인가?
```

이런 규칙은 Service 계층에 두는 것이 좋다.

예:

```python
class BudgetService:
    def add_transaction(self, input_data):
        # 1. 입력 검증
        # 2. 카테고리 존재 확인
        # 3. ID 생성
        # 4. Transaction 생성
        # 5. Repository에 저장 요청
        # 6. 생성된 Transaction 반환
        ...
```

Service가 Repository를 사용하는 흐름:

```text
Service:
카테고리 목록이 필요해.

Repository:
categories.jsonl에서 읽어서 줄게.

Service:
입력된 카테고리가 목록에 있는지 확인할게.
문제 없으면 거래를 만들어 저장해달라고 요청할게.

Repository:
transactions.jsonl에 저장할게.
```

Service가 직접 하면 좋지 않은 일:

```text
argparse 세팅
input() 호출
print()로 출력 포맷 만들기
파일 open()을 직접 많이 다루기
```

Service는 업무 규칙에 집중한다.

## 16.4 CLI 계층

CLI는 사용자 입력과 출력에 집중한다.

역할:

- argparse 설정
- 명령어 라우팅
- 대화형 입력
- 결과 출력
- exit code 결정

예:

```text
cli.py
__main__.py
```

CLI 계층은 사용자와 프로그램 사이의 창구다.

CLI가 하는 일:

```text
argparse로 명령어 해석하기
add 명령에서 input()으로 값 받기
사용자에게 결과 출력하기
오류 메시지 출력하기
Service 함수 호출하기
exit code 결정하기
```

예:

```python
def handle_add_command(args):
    date = input("날짜(YYYY-MM-DD): ")
    transaction_type = input("타입(income/expense): ")
    category = input("카테고리: ")
    amount = input("금액(양수): ")

    transaction = service.add_transaction(
        date=date,
        transaction_type=transaction_type,
        category=category,
        amount=amount,
    )

    print(f"[저장 완료] id={transaction.id}")
    return 0
```

CLI가 직접 하면 좋지 않은 일:

```text
transactions.jsonl에 직접 쓰기
summary 계산 로직 직접 구현하기
카테고리 삭제 정책 직접 판단하기
```

CLI는 사용자와의 입출력에 집중하고, 핵심 규칙은 Service에 맡긴다.

## 16.5 왜 나누는가?

한 파일에 모두 넣으면 처음에는 빠르지만 곧 복잡해진다.

나누면 좋은 점:

- 기능별 책임이 명확하다.
- 테스트가 쉬워진다.
- 저장 방식을 바꿔도 서비스 로직 변경이 줄어든다.
- CLI 문구를 바꿔도 데이터 처리 로직은 그대로 둘 수 있다.

## 16.6 계층별 흐름 예시: add

`add` 명령이 실행될 때 흐름은 이렇게 나눌 수 있다.

```text
사용자
-> CLI
-> Service
-> Repository
-> File
```

조금 더 자세히:

```text
1. 사용자:
   python -m budget_app add 실행

2. CLI:
   input()으로 날짜, 타입, 카테고리, 금액을 받음

3. Service:
   입력값 검증
   카테고리 존재 확인
   거래 ID 생성
   Transaction 객체 생성

4. Repository:
   Transaction을 JSONL 한 줄로 변환
   transactions.jsonl에 append

5. CLI:
   [저장 완료] id=TX-000001 출력
```

각 계층이 자기 일만 한다.

## 16.7 계층별 흐름 예시: summary

`summary` 명령은 이렇게 흐른다.

```text
1. CLI:
   --month, --top 옵션을 argparse로 받음

2. Service:
   해당 월 거래만 필터링
   총수입 계산
   총지출 계산
   잔액 계산
   카테고리별 지출 TOP N 계산
   예산 사용률 계산

3. Repository:
   거래를 한 줄씩 읽어서 Service에 제공
   예산 파일에서 해당 월 예산 제공

4. CLI:
   계산 결과를 보기 좋게 출력
```

중요한 점:

```text
summary 계산은 Service가 한다.
파일 읽기는 Repository가 한다.
출력은 CLI가 한다.
```

## 16.8 추천 폴더 구조

이번 미션에서는 다음 정도 구조가 적당하다.

```text
budget_app/
  __init__.py
  __main__.py
  cli.py
  models.py
  repositories.py
  services.py
  validators.py
  decorators.py
  formatters.py
```

각 파일 역할:

| 파일 | 역할 |
| --- | --- |
| `__main__.py` | `python -m budget_app` 실행 진입점 |
| `cli.py` | argparse 설정, 명령어 라우팅, 입력/출력 |
| `models.py` | `Transaction`, `Budget` 등 데이터 구조 |
| `repositories.py` | 파일 읽기/쓰기, JSONL 처리 |
| `services.py` | 거래 추가, 검색, 요약 등 업무 규칙 |
| `validators.py` | 날짜, 금액, 타입, 카테고리 검증 |
| `decorators.py` | 오류 처리, 실행 시간 측정 데코레이터 |
| `formatters.py` | 거래 목록, summary 출력 문자열 생성 |

`formatters.py`는 필수는 아니지만, 출력 포맷 코드가 많아지면 분리하면 좋다.

## 16.9 의존 방향

계층을 나눌 때는 어떤 파일이 어떤 파일을 import하는지도 중요하다.

추천 방향:

```text
CLI -> Service -> Repository -> Model
```

또는:

```text
CLI -> Service
Service -> Repository
Service -> Model
Repository -> Model
```

피하고 싶은 방향:

```text
Repository -> CLI
Model -> CLI
Model -> Service
```

왜냐하면 Repository나 Model은 사용자 입력/출력을 몰라야 하기 때문이다.

좋은 흐름:

```text
cli.py가 services.py를 호출한다.
services.py가 repositories.py를 호출한다.
repositories.py가 models.py를 사용한다.
```

나쁜 흐름:

```text
models.py 안에서 input()을 호출한다.
repositories.py 안에서 argparse를 다룬다.
services.py 안에서 print()를 너무 많이 한다.
```

> [!tip]
> 아래 계층은 위 계층을 몰라도 되는 구조가 유지보수하기 쉽다.  
> `Model`은 가장 아래에 있고, `CLI`는 가장 위에 있다고 생각하면 된다.

## 16.10 초보자가 헷갈리기 쉬운 기준

어떤 코드를 어디에 넣어야 할지 헷갈릴 때는 질문을 던지면 된다.

| 질문 | 넣을 곳 |
| --- | --- |
| "이 데이터는 어떤 필드를 가지지?" | `models.py` |
| "파일에서 어떻게 읽고 쓰지?" | `repositories.py` |
| "이 입력값이 유효한가?" | `validators.py` |
| "거래 추가 규칙은 무엇이지?" | `services.py` |
| "summary 계산은 어떻게 하지?" | `services.py` |
| "사용자가 어떤 명령을 입력했지?" | `cli.py` |
| "화면에 어떻게 보여줄까?" | `cli.py` 또는 `formatters.py` |
| "오류를 공통으로 어떻게 처리하지?" | `decorators.py` |

## 16.11 나쁜 구조와 좋은 구조 비교

### 나쁜 구조

```python
def handle_add():
    date = input("날짜: ")
    amount = int(input("금액: "))

    if amount <= 0:
        print("오류")
        return

    with open("data/transactions.jsonl", "a") as file:
        file.write(...)

    print("저장 완료")
```

이 함수는 너무 많은 일을 한다.

```text
입력 받기
검증하기
파일 열기
저장하기
출력하기
```

### 좋은 구조

```text
CLI:
입력 받기, 결과 출력

Validator:
금액 검증

Service:
거래 생성 규칙 처리

Repository:
파일 저장
```

함수 하나가 모든 일을 하지 않고, 각자 맡은 일을 처리한다.

## 16.12 이 미션에서 기억할 핵심

| 개념 | 쉬운 설명 |
| --- | --- |
| 모듈화 | 코드를 역할별 파일로 나누는 것 |
| 계층 분리 | 파일을 책임 기준으로 나누는 것 |
| Model | 데이터 모양 담당 |
| Repository | 파일 읽기/쓰기 담당 |
| Service | 가계부 규칙과 계산 담당 |
| CLI | 사용자 명령과 출력 담당 |
| Validator | 입력값 검증 담당 |
| Decorator | 공통 오류 처리/시간 측정 담당 |

이렇게 나누면 구현량은 처음에 조금 늘어나는 것처럼 보인다.  
하지만 기능이 많아질수록 어디를 수정해야 하는지 명확해지고, 전체 코드가 훨씬 덜 흔들린다.

---

# 17. 타입 힌트

타입 힌트는 변수, 함수 인자, 반환값의 타입을 표시하는 문법이다.

예:

```python
def parse_amount(value: str) -> int:
    ...
```

의미:

- `value`는 문자열이다.
- 반환값은 정수다.

## 17.1 타입 힌트의 장점

- 함수 계약이 명확해진다.
- 코드를 읽기 쉬워진다.
- IDE 자동완성과 오류 탐지가 좋아진다.
- 데이터 모델과 서비스 함수의 의도가 드러난다.

## 17.2 이번 미션에서 타입 힌트를 붙이면 좋은 곳

- 모델 클래스 필드
- 파싱 함수
- 검증 함수
- repository 메서드
- service 메서드
- CLI handler 함수

예:

```text
iter_transactions() -> Iterator[Transaction]
add_transaction(...) -> Transaction
search_transactions(...) -> Iterator[Transaction]
calculate_summary(...) -> MonthlySummary
```

---

# 18. 출력 포맷과 콘솔 UX

콘솔 프로그램도 UX가 중요하다.

## 18.1 좋은 출력의 조건

- 성공/실패 여부가 명확하다.
- 생성된 ID를 보여준다.
- 검색 결과가 읽기 쉽다.
- 데이터가 없을 때도 메시지를 출력한다.
- 오류 메시지는 해결 힌트를 포함한다.

## 18.2 거래 목록 출력

외부 라이브러리 없이도 문자열 정렬로 가독성을 높일 수 있다.

예:

```text
TX-000012 | 2024-01-15 | expense | food | 15000 | 점심
TX-000011 | 2024-01-14 | income  | salary | 500000 | 월급
```

## 18.3 표 출력

표를 만들 때 고려할 점:

- 각 열의 너비
- 한글 폭 문제
- 너무 긴 메모 처리
- 빈 값 표시 방식

외부 라이브러리 금지 조건이 있으므로 `tabulate` 같은 패키지는 사용하지 않는다.

## 18.4 오류 출력

권장 형식:

```text
[오류] 날짜 형식이 올바르지 않습니다: 2024-13-01
힌트: YYYY-MM-DD 형식으로 입력하세요. 예) 2024-01-15
```

## 18.5 exit code

프로그램 종료 코드는 운영체제에게 실행 결과를 알려주는 숫자다.

| 코드 | 의미 |
| --- | --- |
| `0` | 성공 |
| `1` 이상 | 오류 |

CLI 프로그램에서는 중요하다. 다른 스크립트가 이 프로그램을 호출할 때 성공/실패를 판단할 수 있기 때문이다.

---

# 19. README에 포함해야 할 내용

미션 요구상 README에는 다음 내용이 들어가야 한다.

## 19.1 실행 방법

예:

```bash
python -m budget_app <command> [options]
```

## 19.2 저장 파일 위치와 형식

예:

```text
기본 저장 폴더: ./data
transactions.jsonl: 거래 내역
categories.jsonl: 카테고리
budgets.jsonl: 월별 예산
```

## 19.3 주요 명령 예시

예:

```bash
python -m budget_app add
python -m budget_app list --limit 5
python -m budget_app search --category food
python -m budget_app summary --month 2024-01 --top 3
python -m budget_app budget set --month 2024-01 --amount 500000
python -m budget_app category add food
python -m budget_app delete --id TX-000012
python -m budget_app import --from input.csv
python -m budget_app export --out output.csv --month 2024-01
```

## 19.4 CSV 스키마

표로 정리:

| column | required | 설명 |
| --- | --- | --- |
| `date` | Y | `YYYY-MM-DD` |
| `type` | Y | `income` 또는 `expense` |
| `category` | Y | 등록된 카테고리 |
| `amount` | Y | 양수 정수 |
| `memo` | N | 문자열 |
| `tags` | N | 쉼표 구분 문자열 |

## 19.5 update 정책

update를 옵션 방식으로 할지 대화형 방식으로 할지 명시해야 한다.

예:

```text
이 프로그램의 update는 옵션 기반으로 동작합니다.
수정하지 않을 필드는 옵션을 생략하면 기존 값을 유지합니다.
```

또는:

```text
이 프로그램의 update는 대화형으로 동작합니다.
기존 거래를 보여준 뒤 수정할 필드만 선택해 변경합니다.
```

## 19.6 카테고리 삭제 정책

예:

```text
사용 중인 카테고리는 삭제할 수 없습니다.
먼저 해당 거래를 다른 카테고리로 수정한 뒤 삭제하세요.
```

---

# 20. 구현 전 체크리스트

아래 항목을 먼저 결정하면 구현이 훨씬 부드러워진다.

## 20.1 저장 포맷

- [ ] 내부 저장은 JSONL로 할 것인가, CSV로 할 것인가?
- [ ] import/export CSV는 요구 스키마를 지키는가?
- [ ] UTF-8 인코딩을 사용할 것인가?

추천:

```text
내부 저장: JSONL
외부 교환: CSV
```

## 20.2 파일 구조

- [ ] `transactions` 파일
- [ ] `categories` 파일
- [ ] `budgets` 파일
- [ ] 기본 저장 폴더 `./data`
- [ ] `--data-dir` 옵션 지원 여부

## 20.3 데이터 모델

- [ ] `Transaction`
- [ ] `Budget`
- [ ] `Category`
- [ ] `MonthlySummary` 같은 요약 모델 필요 여부

## 20.4 명령어

- [ ] `add`
- [ ] `list`
- [ ] `search`
- [ ] `summary`
- [ ] `budget set`
- [ ] `category add/list/remove`
- [ ] `update`
- [ ] `delete`
- [ ] `import`
- [ ] `export`

## 20.5 검증 규칙

- [ ] 날짜 형식 검증
- [ ] 타입 검증
- [ ] 금액 양수 정수 검증
- [ ] 카테고리 존재 검증
- [ ] 태그 파싱 규칙
- [ ] 없는 ID 처리
- [ ] 빈 파일 처리

## 20.6 안정성

- [ ] update/delete 시 임시 파일 후 rename
- [ ] 파일이 없을 때 자동 생성 또는 안내
- [ ] 오류 시 스택트레이스 대신 사용자 메시지
- [ ] 정상/오류 exit code 구분

## 20.7 구조

- [ ] CLI 계층
- [ ] Service 계층
- [ ] Repository 계층
- [ ] Model 계층
- [ ] 데코레이터 모듈
- [ ] 검증 유틸 모듈

---

# 핵심 개념 한 줄 요약

| 개념 | 한 줄 요약 |
| --- | --- |
| CLI | 터미널 명령어로 프로그램을 조작하는 인터페이스 |
| argparse | CLI 명령과 옵션을 파싱하는 Python 표준 라이브러리 |
| dataclass | 데이터 중심 클래스를 간결하게 정의하는 도구 |
| JSONL | 한 줄에 JSON 객체 하나를 저장하는 스트리밍 친화 포맷 |
| CSV | 표 형태 데이터를 주고받기 좋은 텍스트 포맷 |
| CRUD | 생성, 조회, 수정, 삭제 |
| Generator | 데이터를 한 번에 모두 만들지 않고 하나씩 생성하는 객체 |
| yield | 제너레이터 함수에서 값을 하나씩 내보내는 키워드 |
| Decorator | 함수 실행 전후에 공통 기능을 덧붙이는 도구 |
| Validation | 입력값이 규칙에 맞는지 확인하는 과정 |
| Atomic write | 임시 파일에 쓴 뒤 rename으로 안전하게 교체하는 방식 |
| Repository | 저장소 접근을 담당하는 계층 |
| Service | 업무 규칙과 계산을 담당하는 계층 |
| Model | 데이터 구조를 정의하는 계층 |

---

# 추천 구현 방향

> [!done]
> 실제 코드 작성 단계에서는 다음 방향이 가장 미션 요구와 잘 맞는다.

1. 내부 저장은 `JSONL`을 사용한다.
2. import/export는 `CSV`로 제공한다.
3. 저장 파일은 `transactions.jsonl`, `categories.jsonl`, `budgets.jsonl`로 분리한다.
4. 거래 읽기는 제너레이터로 구현한다.
5. update/delete는 임시 파일 작성 후 rename으로 처리한다.
6. 공통 오류 처리와 실행 시간 측정은 데코레이터로 분리한다.
7. 모듈은 최소 `models`, `storage/repository`, `services`, `cli`, `decorators`로 나눈다.
8. README에는 실행법, 명령 예시, 데이터 파일, CSV 스키마, 정책을 명확히 적는다.

이렇게 잡으면 요구사항을 만족하면서도 나중에 기능을 추가하기 쉬운 구조가 된다.
