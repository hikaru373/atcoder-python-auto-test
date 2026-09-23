import subprocess
import sys
import time
from pathlib import Path


DEFAULT_FILE = "main.py"
SAMPLE_FILE = "sample.txt"
TIME_LIMIT = 2.0

# 引数の処理
def parse_args():
    file_path = DEFAULT_FILE
    sample_file = SAMPLE_FILE
    time_limit = TIME_LIMIT

    for arg in sys.argv[1:]:
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
        if arg.endswith(".py"):
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

    text = Path(sample_file).read_text(encoding="utf-8")

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

# 解答の実行
def run_test(file_path, input_data, time_limit):
    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            [sys.executable, file_path], # python3より安全な指定
            input = input_data,
            capture_output = True,
            text = True,
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
    args = parse_args()
    file_path, sample_file, time_limit = args

    # ファイル存在確認
    if not Path(file_path).exists():
        print(f"エラー: {file_path} が見つかりません。")
        return

    samples = load_samples(sample_file)

    if samples is None:
        return

    print("=" * 50)

    print(f"実行ファイル: {file_path}")
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

        result = run_test(file_path, input_data, time_limit)

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

