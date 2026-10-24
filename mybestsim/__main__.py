import sys

from mybestsim import merge, report


def main() -> int:
    code = merge.main()
    if code:
        return code
    return report.main()


if __name__ == "__main__":
    sys.exit(main())
