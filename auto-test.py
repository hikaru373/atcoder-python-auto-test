import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


DEFAULT_FILE = "main.py"
SAMPLE_FILE = "sample.txt"
TIME_LIMIT = 2.0

# 実行ファイル名（Windowsは.exeが必要）
EXE = "main.exe" if os.name == "nt" else "main"

# ウォームアップ実行の制限時間（秒）
WARMUP_TIME_LIMIT = 5.0

# 対応言語（拡張子: 言語名, コンパイルコマンド, 実行コマンド）
# {src}: ソースファイル, {exe}: 実行ファイル
LANGUAGES = {
    ".py": {
        "name": "Python",
        "compile": None,
        "run": [sys.executable, "-X", "utf8", "{src}"] # 解答側もUTF-8で入出力
    },
    ".cpp": {
        "name": "C++",
        "compile": ["g++", "-std=c++20", "-O2", "-o", "{exe}", "{src}"],
        "run": ["{exe}"]
    },
}

# 引数の処理
def parse_args():
    file_path = DEFAULT_FILE
    sample_file = SAMPLE_FILE
    time_limit = TIME_LIMIT

    for arg in sys.argv[1:]:
        # 使い方
        if arg in ("-h", "--help"):
            print(0)
            sys.exit(0)

        # 秒数
        try:
            value = float(arg)
            if value <= 0:
                print("エラー: 秒数は0より大きい値を指定してください。")
                sys.exit(1)
            time_limit = value
            continue
        except ValueError:
            pass

        # 実行ファイル
        if Path(arg).suffix in LANGUAGES:
            file_path = arg
            continue

        # テキストファイル
        if arg.endswith(".txt"):
            sample_file = arg
            continue

        print(f"エラー: 不明な引数です: {arg}")
        sys.exit(1)

    return file_path, sample_file, time_limit

# サンプルを解析
def load_samples(sample_file):
    if not Path(sample_file).exists():
        print(f"エラー: {sample_file} が見つかりません。")
        return None

    # BOM付きUTF-8にも対応
    text = Path(sample_file).read_text(encoding="utf-8-sig")

    # Windows改行にも対応
    text = text.replace("\r\n", "\n")

    if not text.strip():
        print("エラー: サンプルがありません。")
        return None

    # 空行2つ以上でサンプルを区切る
    blocks = text.strip().split("\n\n")

    if len(blocks) % 2 != 0:
        print("エラー: 入力と出力の数が一致しません。")
        print(f"検出されたブロック数: {len(blocks)}")
        return None

    samples = []

    for i in range(0, len(blocks), 2):
        input_data = blocks[i]
        expected_output = blocks[i + 1]

        samples.append((input_data + "\n", expected_output))

    return samples

# 出力比較
def normalize_output(text):
    return "\n".join(
        line.rstrip()
        for line in text.strip().splitlines()
    )

# コマンド中の{src}などを置き換える
def fill_command(command, src, work_dir):
    return [
        arg.format(src=src, exe=str(Path(work_dir) / EXE))
        for arg in command
    ]

# コンパイルして実行コマンドを返す（失敗時はNone）
def build(file_path, work_dir):
    lang = LANGUAGES[Path(file_path).suffix]
    src = str(Path(file_path).resolve())

    command = fill_command(lang["run"], src, work_dir)

    if lang["compile"] is None:
        return command

    compile_command = fill_command(lang["compile"], src, work_dir)

    if shutil.which(compile_command[0]) is None:
        print(f"エラー: {compile_command[0]} が見つかりません。{lang['name']}のコンパイラをインストールしてください。")
        return None

    # 削除しても良い
    print("コンパイル中...")
    
    result = subprocess.run(
        compile_command,
        capture_output = True,
        encoding = "utf-8",
        errors = "replace"
    )

    # コンパイルエラー
    if result.returncode != 0:
        print("CE (Compile Error)")
        print()
        print((result.stderr or result.stdout).strip())
        return None

    warm_up(command)

    return command

# 特にWindowsで生成直後の実行ファイルは初回起動が遅いため、計測前に一度だけ空実行する
def warm_up(command):
    try:
        subprocess.run(
            command,
            input = "",
            capture_output = True,
            encoding = "utf-8",
            errors = "replace",
            timeout = WARMUP_TIME_LIMIT
        )
    except subprocess.TimeoutExpired:
        pass

# 解答の実行
def run_test(command, input_data, time_limit):
    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            command,
            input = input_data,
            capture_output = True,
            encoding = "utf-8",
            timeout = time_limit
        )

        elapsed_time = time.perf_counter() - start_time

        # 実行時エラー
        if result.returncode != 0:
            return {
                "status": "RE",
                "time": elapsed_time,
                "stderr": result.stderr
            }

        # 通常
        return {
            "status": "OK",
            "time": elapsed_time,
            "stdout": result.stdout
        }

    # タイムアウト
    except subprocess.TimeoutExpired:
        elapsed_time = time.perf_counter() - start_time

        return {
            "status": "TLE",
            "time": elapsed_time
        }


def main():
    # Windowsでも日本語・絵文字を表示できるようにする
    sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    file_path, sample_file, time_limit = args

    # ファイル存在確認
    if not Path(file_path).exists():
        print(f"エラー: {file_path} が見つかりません。")
        return

    samples = load_samples(sample_file)

    if samples is None:
        return

    with tempfile.TemporaryDirectory() as work_dir:
        command = build(file_path, work_dir)

        if command is None:
            return

        run_samples(command, file_path, samples, time_limit)


def run_samples(command, file_path, samples, time_limit):
    print("=" * 50)

    print(f"実行ファイル: {file_path}")
    print(f"言語: {LANGUAGES[Path(file_path).suffix]['name']}")
    print(f"サンプル数: {len(samples)}")
    print(f"TLE制限: {time_limit}秒")

    print("=" * 50)
    print()

    results = {
        "AC": 0,
        "WA": 0,
        "TLE": 0,
        "RE": 0
    }

    # 全サンプル実行
    for i, (input_data, expected_output) in enumerate(samples, 1):

        result = run_test(command, input_data, time_limit)

        status = result["status"]
        elapsed_time = result["time"]

        if status == "TLE":
            results["TLE"] += 1
            print(
                f"Sample {i}: TLE "
                f"({elapsed_time:.3f}s / {time_limit}s)"
            )
            continue

        if status == "RE":
            results["RE"] += 1
            print(
                f"Sample {i}: RE "
                f"({elapsed_time:.3f}s)"
            )
            if result["stderr"]:
                print()
                print("Runtime Error:")
                print(
                    result["stderr"].strip()
                )
            print("-" * 50)
            continue

        # -------------------------
        # AC / WA
        # -------------------------

        actual_output = result["stdout"]

        if (normalize_output(actual_output) == normalize_output(expected_output)):
            results["AC"] += 1
            print(
                f"Sample {i}: AC "
                f"({elapsed_time:.3f}s)"
            )
        else:
            results["WA"] += 1
            print(
                f"Sample {i}: WA "
                f"({elapsed_time:.3f}s)"
            )
            print()
            print("Input:")
            print(input_data.rstrip())
            print()
            print("Expected:")
            print(expected_output)
            print()
            print("Actual:")
            print(actual_output.rstrip())
            print("-" * 50)

    # 最終結果
    total = len(samples)
    print()
    print("=" * 50)
    print(f"AC : {results['AC']}")
    print(f"WA : {results['WA']}")
    print(f"TLE: {results['TLE']}")
    print(f"RE : {results['RE']}")
    print()
    if results["AC"] == total:
        print(f"🎉 ALL AC ({total}/{total})")
    else:
        print(
            f"Result: "
            f"{results['AC']}/{total} AC"
        )
    print("=" * 50)


if __name__ == "__main__":
    main()

