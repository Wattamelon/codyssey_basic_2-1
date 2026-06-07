"""Command-line interface setup for the budget application."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="파일 기반 가계부 콘솔 프로그램",
    )
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="저장 파일을 둘 데이터 폴더 경로 (기본값: ./data)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    subparsers.add_parser("add", help="거래를 대화형으로 추가합니다.")

    list_parser = subparsers.add_parser("list", help="거래 목록을 최신순으로 출력합니다.")
    list_parser.add_argument("--limit", type=int, default=10, help="출력할 최대 거래 수")

    search_parser = subparsers.add_parser("search", help="조건에 맞는 거래를 검색합니다.")
    search_parser.add_argument("--from", dest="date_from", help="검색 시작일 YYYY-MM-DD")
    search_parser.add_argument("--to", dest="date_to", help="검색 종료일 YYYY-MM-DD")
    search_parser.add_argument("--category", help="카테고리 조건")
    search_parser.add_argument("--type", choices=["income", "expense"], help="거래 타입")
    search_parser.add_argument("-q", "--query", dest="keyword", help="메모 키워드")
    search_parser.add_argument("--tag", help="태그 조건")

    summary_parser = subparsers.add_parser("summary", help="월별 요약을 출력합니다.")
    summary_parser.add_argument("--month", required=True, help="요약할 월 YYYY-MM")
    summary_parser.add_argument("--top", type=int, default=3, help="카테고리 TOP N")

    budget_parser = subparsers.add_parser("budget", help="월별 예산을 관리합니다.")
    budget_subparsers = budget_parser.add_subparsers(dest="budget_command", metavar="<action>")
    budget_set_parser = budget_subparsers.add_parser("set", help="월 예산을 설정합니다.")
    budget_set_parser.add_argument("--month", required=True, help="예산 월 YYYY-MM")
    budget_set_parser.add_argument("--amount", required=True, type=int, help="예산 금액")

    category_parser = subparsers.add_parser("category", help="카테고리를 관리합니다.")
    category_subparsers = category_parser.add_subparsers(dest="category_command", metavar="<action>")
    category_add_parser = category_subparsers.add_parser("add", help="카테고리를 추가합니다.")
    category_add_parser.add_argument("name", help="추가할 카테고리 이름")
    category_subparsers.add_parser("list", help="카테고리 목록을 출력합니다.")
    category_remove_parser = category_subparsers.add_parser("remove", help="카테고리를 삭제합니다.")
    category_remove_parser.add_argument("name", help="삭제할 카테고리 이름")

    update_parser = subparsers.add_parser("update", help="ID 기준으로 거래를 수정합니다.")
    update_parser.add_argument("--id", required=True, help="수정할 거래 ID")

    delete_parser = subparsers.add_parser("delete", help="ID 기준으로 거래를 삭제합니다.")
    delete_parser.add_argument("--id", required=True, help="삭제할 거래 ID")

    import_parser = subparsers.add_parser("import", help="CSV 파일에서 거래를 가져옵니다.")
    import_parser.add_argument("--from", dest="csv_path", required=True, help="가져올 CSV 경로")

    export_parser = subparsers.add_parser("export", help="거래를 CSV 파일로 내보냅니다.")
    export_parser.add_argument("--out", required=True, help="내보낼 CSV 경로")
    export_parser.add_argument("--month", help="내보낼 월 YYYY-MM")
    export_parser.add_argument("--from", dest="date_from", help="내보내기 시작일 YYYY-MM-DD")
    export_parser.add_argument("--to", dest="date_to", help="내보내기 종료일 YYYY-MM-DD")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI parser and route to command handlers."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    print(f"[준비 중] '{args.command}' 명령은 이후 단계에서 구현합니다.")
    return 0
