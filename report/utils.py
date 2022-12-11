from app.__main__ import check_requirements, check_version


def run_checks():
    if check_version() and check_requirements():
        print("🎉 Everything seems fine!")
