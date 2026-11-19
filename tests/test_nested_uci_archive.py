import unittest
from io import BytesIO
from zipfile import ZipFile

from src.data import _read_math_csv_from_zip


class NestedUciArchiveTests(unittest.TestCase):
    def test_loader_finds_math_csv_inside_nested_student_zip(self):
        csv_bytes = (
            b"school;sex;G1;G2;G3\n"
            b"GP;F;5;6;7\n"
            b"MS;M;10;11;12\n"
        )
        inner_buffer = BytesIO()
        with ZipFile(inner_buffer, "w") as inner:
            inner.writestr("student-mat.csv", csv_bytes)

        outer_buffer = BytesIO()
        with ZipFile(outer_buffer, "w") as outer:
            outer.writestr("student.zip", inner_buffer.getvalue())

        frame = _read_math_csv_from_zip(outer_buffer.getvalue())
        self.assertIsNotNone(frame)
        self.assertEqual(len(frame), 2)
        self.assertEqual(frame["G3"].tolist(), [7, 12])

    def test_loader_returns_none_when_math_csv_is_missing(self):
        buffer = BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr("readme.txt", "not the student dataset")
        self.assertIsNone(_read_math_csv_from_zip(buffer.getvalue()))


if __name__ == "__main__":
    unittest.main()
