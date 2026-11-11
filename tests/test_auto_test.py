import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "auto-test.py"

# 入力を2倍して出力する解答
DOUBLE = "print(int(input()) * 2)\n"

SAMPLE = "3\n\n6\n\n10\n\n20\n"

CPP_DOUBLE = "#include <iostream>\nint main() { int n; std::cin >> n; std::cout << n * 2 << std::endl; }\n"


class AutoTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory() # 一時ディレクトリ
        self.dir = Path(self.tmp.name) # パスをPathオブジェクトとして保存

    def tearDown(self):
        self.tmp.cleanup()

# auto-test.py を実行して標準出力を返す
    def run_script(self, solution, sample, *args):
        (self.dir / "main.py").write_text(solution, encoding="utf-8")
        (self.dir / "sample.txt").write_bytes(sample.encode("utf-8"))

        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd = self.dir,
            capture_output = True,
            encoding = "utf-8",
            timeout = 60 # Windowsではコンパイルに20秒以上かかるため長めに設定
        )
        return result.stdout

# AC
    def test_all_ac(self):
        out = self.run_script(DOUBLE, SAMPLE)
        self.assertIn("Sample 1: AC", out)
        self.assertIn("Sample 2: AC", out)
        self.assertIn("ALL AC (2/2)", out)

    # Windows形式の改行
    def test_crlf_sample(self):
        out = self.run_script(DOUBLE, SAMPLE.replace("\n", "\r\n"))
        self.assertIn("ALL AC (2/2)", out)

    # BOM付きUTF-8
    def test_bom_sample(self):
        out = self.run_script(DOUBLE, "\ufeff" + SAMPLE)
        self.assertIn("ALL AC (2/2)", out)

    # 日本語・絵文字の入出力
    def test_unicode_io(self):
        out = self.run_script("print(input() + '🎉')\n", "こんにちは𠮷\n\nこんにちは𠮷🎉\n")
        self.assertIn("ALL AC (1/1)", out)

# WA
    def test_wa(self):
        out = self.run_script("print(int(input()) * 3)\n", SAMPLE)
        self.assertIn("Sample 1: WA", out)
        self.assertIn("Result: 0/2 AC", out)

# RE
    def test_re(self):
        out = self.run_script("raise ValueError\n", SAMPLE)
        self.assertIn("Sample 1: RE", out)
        self.assertIn("ValueError", out)

# TLE
    def test_tle(self):
        out = self.run_script("while True:\n    pass\n", "1\n\n1\n", "0.5")
        self.assertIn("Sample 1: TLE", out)
        self.assertIn("TLE制限: 0.5秒", out)

# 引数指定
    def test_custom_files(self):
        (self.dir / "a.py").write_text(DOUBLE, encoding="utf-8")
        (self.dir / "b.txt").write_text(SAMPLE, encoding="utf-8")
        out = self.run_script("", "", "a.py", "b.txt")
        self.assertIn("実行ファイル: a.py", out)
        self.assertIn("ALL AC (2/2)", out)

    # 存在しないファイル
    def test_missing_file(self):
        out = self.run_script(DOUBLE, SAMPLE, "none.py")
        self.assertIn("エラー: none.py が見つかりません。", out)

    # 存在しないファイル
    def test_odd_blocks(self):
        out = self.run_script(DOUBLE, "3\n\n6\n\n10\n")
        self.assertIn("入力と出力の数が一致しません", out)

# C++
    def run_other(self, file_name, solution):
        (self.dir / file_name).write_text(solution, encoding="utf-8")
        return self.run_script("", SAMPLE, file_name)

    @unittest.skipUnless(shutil.which("g++"), "g++がありません")
    def test_cpp(self):
        out = self.run_other("main.cpp", CPP_DOUBLE)
        self.assertIn("言語: C++", out)
        self.assertIn("ALL AC (2/2)", out)

    @unittest.skipUnless(shutil.which("g++"), "g++がありません")
    def test_cpp_compile_error(self):
        out = self.run_other("main.cpp", "int main() { return x; }\n")
        self.assertIn("CE (Compile Error)", out)

    # 未対応の拡張子
    def test_unknown_extension(self):
        out = self.run_script(DOUBLE, SAMPLE, "main.xyz")
        self.assertIn("エラー: 不明な引数です: main.xyz", out)

# 使い方
    def test_help(self):
        for flag in ("-h", "--help"):
            with self.subTest(flag=flag):
                out = self.run_script(DOUBLE, SAMPLE, flag)
                self.assertIn("使い方", out)
                self.assertNotIn("Sample", out) # テストは実行しない
                self.assertNotIn("エラー", out)

    # 他の引数と一緒に指定
    def test_help_with_other_args(self):
        out = self.run_script(DOUBLE, SAMPLE, "main.py", "-h")
        self.assertIn("使い方", out)
        self.assertNotIn("Sample", out)
        self.assertNotIn("エラー", out)

    # 不正な引数があっても使い方を優先
    def test_help_with_invalid_arg(self):
        out = self.run_script(DOUBLE, SAMPLE, "foo", "--help")
        self.assertIn("使い方", out)
        self.assertNotIn("エラー", out)


if __name__ == "__main__":
    unittest.main()
