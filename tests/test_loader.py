"""Unit and acceptance tests for CSV graph loader (US2 & US3: T013, T014, T016-T020)."""

from pathlib import Path
import tempfile
import unittest

from graph.loader import GraphLoadError, load_graph_from_csv


class TestGraphLoader(unittest.TestCase):
    """Tests for CSV normalization and strict error validation in src/graph/loader.py."""

    def _write_temp_csv(self, content: str) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="")
        with tmp:
            tmp.write(content)
        self.addCleanup( lambda p=Path(tmp.name): p.unlink(missing_ok=True) )
        return Path(tmp.name)

    def test_us2_as1_trim_leading_and_trailing_spaces(self) -> None:
        """T013 (US2-AS1): Trim leading/trailing spaces while preserving internal spaces and isolated vertex."""
        csv_path = self._write_temp_csv(
            "source,target\n"
            " utils , logging \n"
            "utils,config\n"
            " watch ,   \n"
        )
        graph = load_graph_from_csv(csv_path)
        self.assertEqual(graph.vertices, {"utils", "logging", "config", "watch"})
        self.assertEqual(graph.adjacency["utils"], {"logging", "config"})
        self.assertEqual(graph.adjacency["watch"], set())
        self.assertEqual(graph.vertex_count(), 4)
        self.assertEqual(graph.edge_count(), 2)

    def test_us2_as2_case_sensitive_vertex_names(self) -> None:
        """T014 (US2-AS2): Vertex names differing only in case are treated as distinct vertices."""
        csv_path = self._write_temp_csv(
            "source,target\n"
            "Auth,Session\n"
            "auth,session\n"
        )
        graph = load_graph_from_csv(csv_path)
        self.assertEqual(graph.vertices, {"Auth", "Session", "auth", "session"})
        self.assertEqual(graph.vertex_count(), 4)
        self.assertEqual(graph.edge_count(), 2)

    def test_us3_as1_nonexistent_file_raises_error(self) -> None:
        """T016 (US3-AS1): Nonexistent file raises GraphLoadError mentioning path and cause."""
        missing_path = Path("data/does-not-exist-file.csv")
        with self.assertRaises(GraphLoadError) as ctx:
            load_graph_from_csv(missing_path)
        self.assertIn("does-not-exist-file.csv", str(ctx.exception))

    def test_us3_as2_empty_file_raises_error(self) -> None:
        """T017 (US3-AS2): Completely empty file (0 bytes) raises GraphLoadError."""
        csv_path = self._write_temp_csv("")
        with self.assertRaises(GraphLoadError) as ctx:
            load_graph_from_csv(csv_path)
        self.assertIn(csv_path.name, str(ctx.exception))

    def test_us3_as3_header_only_file_returns_empty_graph(self) -> None:
        """T018 (US3-AS3): Header-only CSV (source,target) returns valid empty graph (0 vertices, 0 edges)."""
        csv_path = self._write_temp_csv("source,target\n")
        graph = load_graph_from_csv(csv_path)
        self.assertEqual(graph.vertex_count(), 0)
        self.assertEqual(graph.edge_count(), 0)

    def test_us3_as4_missing_or_different_header_raises_error_with_line_1(self) -> None:
        """T019 (US3-AS4): Missing or different header reports line 1 and literal row content."""
        for bad_header in ("origen,destino\na,b\n", "from,to\na,b\n", "undershorts,pants\n"):
            with self.subTest(bad_header=bad_header):
                csv_path = self._write_temp_csv(bad_header)
                with self.assertRaises(GraphLoadError) as ctx:
                    load_graph_from_csv(csv_path)
                msg = str(ctx.exception)
                self.assertIn("1", msg)
                first_line = bad_header.splitlines()[0]
                self.assertIn(first_line, msg)

    def test_us3_as5_fewer_or_more_than_two_columns_or_intermediate_blank_line(self) -> None:
        """T020 (US3-AS5): Rows with != 2 columns or intermediate blank line abort with line number and row."""
        cases = [
            ("source,target\nundershorts,pants\nwatch\n", 3, "watch"),
            ("source,target\nundershorts,pants\na,b,c\n", 3, "a,b,c"),
            ("source,target\n\nundershorts,pants\n", 2, ""),
        ]
        for content, expected_line, expected_row in cases:
            with self.subTest(content=content):
                csv_path = self._write_temp_csv(content)
                with self.assertRaises(GraphLoadError) as ctx:
                    load_graph_from_csv(csv_path)
                msg = str(ctx.exception)
                self.assertIn(str(expected_line), msg)
                if expected_row:
                    self.assertIn(expected_row, msg)

    def test_us3_as5_empty_source_and_both_empty_comma_row(self) -> None:
        """T020 (US3-AS5): Empty source (',shoes', ',', '   ,shoes') aborts with line number and row."""
        cases = [
            ("source,target\n,shoes\n", 2, ",shoes"),
            ("source,target\n,\n", 2, ","),
            ("source,target\n   ,shoes\n", 2, "   ,shoes"),
        ]
        for content, expected_line, expected_row in cases:
            with self.subTest(content=content):
                csv_path = self._write_temp_csv(content)
                with self.assertRaises(GraphLoadError) as ctx:
                    load_graph_from_csv(csv_path)
                msg = str(ctx.exception)
                self.assertIn(str(expected_line), msg)
                self.assertIn(expected_row, msg)


if __name__ == "__main__":
    unittest.main()
