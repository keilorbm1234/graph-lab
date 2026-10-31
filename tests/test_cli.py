"""End-to-end CLI acceptance tests (US1-AS1..AS3, US2-AS1..AS2, US3-AS1..AS5)."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from graph.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


class TestGraphCLI(unittest.TestCase):
    """CLI contract and acceptance scenario tests for `graph show <archivo>`."""

    def _run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = int(exc.code) if isinstance(exc.code, int) else 1
        return code, stdout_buf.getvalue(), stderr_buf.getvalue()

    def _write_temp_csv(self, content: str) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="")
        with tmp:
            tmp.write(content)
        self.addCleanup(lambda p=Path(tmp.name): p.unlink(missing_ok=True))
        return Path(tmp.name)

    def test_us1_as1_small_dag_csv(self) -> None:
        """T007 (US1-AS1): data/small-dag.csv -> 9 vertices (including isolated watch) and 9 edges."""
        code, out, err = self._run_cli("show", str(DATA_DIR / "small-dag.csv"))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        expected = "\n".join(
            [
                "Vertices: 9, Edges: 9",
                "Vertices:",
                "belt",
                "jacket",
                "pants",
                "shirt",
                "shoes",
                "socks",
                "tie",
                "undershorts",
                "watch",
                "Edges:",
                "belt -> jacket",
                "pants -> belt",
                "pants -> shoes",
                "shirt -> belt",
                "shirt -> tie",
                "socks -> shoes",
                "tie -> jacket",
                "undershorts -> pants",
                "undershorts -> shoes",
            ]
        ) + "\n"
        self.assertEqual(out, expected)

    def test_us1_as2_cs_curriculum_csv(self) -> None:
        """T008 (US1-AS2): data/cs-curriculum.csv -> 19 vertices, 23 unique edges, silent deduplication."""
        code, out, err = self._run_cli("show", str(DATA_DIR / "cs-curriculum.csv"))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], "Vertices: 19, Edges: 23")
        self.assertIn("Programming Fundamentals", lines)
        self.assertIn("Object-Oriented Programming", lines)
        self.assertIn("Probability and Statistics", lines)
        self.assertEqual(lines.count("Data Structures -> Algorithms"), 1)

    def test_us1_as3_build_with_cycle_csv(self) -> None:
        """T009 (US1-AS3): data/build-with-cycle.csv -> 11 vertices, 13 edges (cycle + self-loop)."""
        code, out, err = self._run_cli("show", str(DATA_DIR / "build-with-cycle.csv"))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        expected = "\n".join(
            [
                "Vertices: 11, Edges: 13",
                "Vertices:",
                "api",
                "auth",
                "config",
                "core",
                "logging",
                "metrics",
                "session",
                "storage",
                "user-profile",
                "utils",
                "web",
                "Edges:",
                "api -> web",
                "auth -> api",
                "auth -> session",
                "config -> core",
                "core -> auth",
                "core -> storage",
                "logging -> core",
                "metrics -> metrics",
                "session -> user-profile",
                "storage -> api",
                "user-profile -> auth",
                "utils -> config",
                "utils -> logging",
            ]
        ) + "\n"
        self.assertEqual(out, expected)

    def test_us2_as1_cli_trimmed_names(self) -> None:
        """T013 (US2-AS1): CLI output with trimmed spaces around vertex names."""
        csv_path = self._write_temp_csv("source,target\n utils , logging \nutils,config\n")
        code, out, err = self._run_cli("show", str(csv_path))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        expected = "\n".join(
            [
                "Vertices: 3, Edges: 2",
                "Vertices:",
                "config",
                "logging",
                "utils",
                "Edges:",
                "utils -> config",
                "utils -> logging",
            ]
        ) + "\n"
        self.assertEqual(out, expected)

    def test_us2_as2_cli_case_sensitive_names(self) -> None:
        """T014 (US2-AS2): CLI output preserves case sensitivity."""
        csv_path = self._write_temp_csv("source,target\nAuth,Session\nauth,session\n")
        code, out, err = self._run_cli("show", str(csv_path))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        expected = "\n".join(
            [
                "Vertices: 4, Edges: 2",
                "Vertices:",
                "Auth",
                "Session",
                "auth",
                "session",
                "Edges:",
                "Auth -> Session",
                "auth -> session",
            ]
        ) + "\n"
        self.assertEqual(out, expected)

    def test_us3_as1_cli_nonexistent_file(self) -> None:
        """T016 (US3-AS1): Nonexistent file returns exit code 1 and error on stderr with empty stdout."""
        code, out, err = self._run_cli("show", "data/nonexistent.csv")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("nonexistent.csv", err)

    def test_us3_as2_cli_empty_file(self) -> None:
        """T017 (US3-AS2): Empty file returns exit code 1 and error on stderr with empty stdout."""
        csv_path = self._write_temp_csv("")
        code, out, err = self._run_cli("show", str(csv_path))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(csv_path.name, err)

    def test_us3_as3_cli_header_only_file(self) -> None:
        """T018 (US3-AS3): Header-only file returns exit code 0 and empty graph output."""
        csv_path = self._write_temp_csv("source,target\n")
        code, out, err = self._run_cli("show", str(csv_path))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "Vertices: 0, Edges: 0\nVertices:\nEdges:\n")

    def test_us3_as4_cli_invalid_header(self) -> None:
        """T019 (US3-AS4): Invalid header returns exit code 1, line 1, and literal row in stderr."""
        csv_path = self._write_temp_csv("origen,destino\na,b\n")
        code, out, err = self._run_cli("show", str(csv_path))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("1", err)
        self.assertIn("origen,destino", err)

    def test_us3_as5_cli_invalid_rows(self) -> None:
        """T020 (US3-AS5): Invalid rows (1 col, 3 cols, blank line, empty source, ',') return exit code 1."""
        for bad_row in ("watch", "a,b,c", "", ",shoes", ",", "   ,shoes"):
            with self.subTest(bad_row=bad_row):
                csv_path = self._write_temp_csv(f"source,target\nundershorts,pants\n{bad_row}\n")
                code, out, err = self._run_cli("show", str(csv_path))
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertIn("3", err)
                if bad_row:
                    self.assertIn(bad_row, err)

    def test_toposort_us1_as1_small_dag_csv(self) -> None:
        """T006 (US1-AS1): graph toposort data/small-dag.csv -> 9 vertices in lexicographical topo order."""
        code, out, err = self._run_cli("toposort", str(DATA_DIR / "small-dag.csv"))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        expected = "\n".join(
            [
                "Topological order (9):",
                "shirt",
                "socks",
                "tie",
                "undershorts",
                "pants",
                "belt",
                "jacket",
                "shoes",
                "watch",
            ]
        ) + "\n"
        self.assertEqual(out, expected)

    def test_toposort_us1_as2_cs_curriculum_csv(self) -> None:
        """T007 (US1-AS2): graph toposort data/cs-curriculum.csv -> 19 courses in lexicographical topo order."""
        code, out, err = self._run_cli("toposort", str(DATA_DIR / "cs-curriculum.csv"))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        expected = "\n".join(
            [
                "Topological order (19):",
                "Calculus I",
                "Calculus II",
                "Computer Networks",
                "Discrete Mathematics",
                "Linear Algebra",
                "Probability and Statistics",
                "Programming Fundamentals",
                "Computer Architecture",
                "Object-Oriented Programming",
                "Data Structures",
                "Algorithms",
                "Databases",
                "Machine Learning",
                "Operating Systems",
                "Distributed Systems",
                "Software Engineering",
                "Capstone Project",
                "Theory of Computation",
                "Compilers",
            ]
        ) + "\n"
        self.assertEqual(out, expected)

    def test_toposort_us1_as3_header_only_empty_graph(self) -> None:
        """T008 (US1-AS3): graph toposort on header-only file -> Topological order (0): with exit code 0."""
        csv_path = self._write_temp_csv("source,target\n")
        code, out, err = self._run_cli("toposort", str(csv_path))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "Topological order (0):\n")

    def test_toposort_us2_as1_build_with_cycle_csv(self) -> None:
        """T014 (US2-AS1): graph toposort data/build-with-cycle.csv -> exit 1, empty stdout, auth cycle in stderr."""
        code, out, err = self._run_cli("toposort", str(DATA_DIR / "build-with-cycle.csv"))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertEqual(err, "Error: cycle detected: auth -> session -> user-profile -> auth\n")

    def test_toposort_us2_as2_build_with_self_loop_after_fixing_first_cycle(self) -> None:
        """T015 (US2-AS2): After fixing auth cycle in build-with-cycle.csv, reports metrics -> metrics."""
        lines = (DATA_DIR / "build-with-cycle.csv").read_text(encoding="utf-8").splitlines()
        filtered_lines = [line for line in lines if line.strip() != "user-profile,auth"]
        csv_path = self._write_temp_csv("\n".join(filtered_lines) + "\n")
        code, out, err = self._run_cli("toposort", str(csv_path))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertEqual(err, "Error: cycle detected: metrics -> metrics\n")

    def test_toposort_us3_as1_invalid_files_and_load_error_priority_over_cycle(self) -> None:
        """T018 (US3-AS1): Invalid CSV files fail with load error on toposort, even when a cycle precedes bad row."""
        # Nonexistent file
        code, out, err = self._run_cli("toposort", "data/nonexistent.csv")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("nonexistent.csv", err)

        # Empty 0-byte file
        empty_path = self._write_temp_csv("")
        code, out, err = self._run_cli("toposort", str(empty_path))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(empty_path.name, err)

        # Invalid header
        bad_header_path = self._write_temp_csv("from,to\na,b\n")
        code, out, err = self._run_cli("toposort", str(bad_header_path))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("1", err)
        self.assertIn("from,to", err)

        # File with BOTH a cycle in rows 2-3 AND an invalid row at line 4 (P-01 priority check)
        for bad_row in ("watch", "a,b,c", "", ",shoes", ",", "   ,shoes"):
            with self.subTest(bad_row=bad_row):
                csv_path = self._write_temp_csv(f"source,target\nauth,session\nsession,auth\n{bad_row}\n")
                code, out, err = self._run_cli("toposort", str(csv_path))
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertNotIn("cycle detected", err)
                self.assertIn("4", err)

    def test_toposort_us3_as2_trim_internal_spaces_and_case_sensitive_ascii_order(self) -> None:
        """T019 (US3-AS2): Trims outer spaces, preserves internal spaces, and orders 'Zeta' before 'alpha'."""
        csv_path = self._write_temp_csv(
            "source,target\n"
            " alpha , Data Science \n"
            " Zeta , Data Science \n"
        )
        code, out, err = self._run_cli("toposort", str(csv_path))
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        expected = "\n".join(
            [
                "Topological order (3):",
                "Zeta",
                "alpha",
                "Data Science",
            ]
        ) + "\n"
        self.assertEqual(out, expected)


if __name__ == "__main__":
    unittest.main()
