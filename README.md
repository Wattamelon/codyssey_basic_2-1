# 파일 기반 가계부 콘솔 프로그램

Python 표준 라이브러리만 사용해 만드는 파일 기반 가계부 CLI 애플리케이션입니다.

## 현재 진행 상태

- 1단계: 프로젝트 뼈대 구성 완료
- CLI 골격과 `--help` 출력 준비
- 실제 가계부 기능은 이후 단계에서 구현 예정

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
