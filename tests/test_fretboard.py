import unittest

from visual_banjo.fretboard import chord_notes, fretboard_notes, note_name


class FretboardTests(unittest.TestCase):
    def test_open_g_tuning(self):
        board = fretboard_notes("g", 12)
        self.assertEqual([row[0] for row in board], [None, "D", "G", "B", "D"])
        self.assertEqual(board[0][5], "G")
        self.assertEqual(board[0][6], "G#")
        self.assertEqual(board[1][12], "D")

    def test_double_c_tuning(self):
        board = fretboard_notes("c", 5)
        self.assertEqual([row[0] for row in board], [None, "C", "G", "C", "D"])
        self.assertEqual(board[0][5], "G")
        self.assertEqual(board[2][5], "C")

    def test_major_and_minor(self):
        self.assertEqual(chord_notes("G"), {"G", "B", "D"})
        self.assertEqual(chord_notes("G", "minor"), {"G", "A#", "D"})
        self.assertEqual(chord_notes("C#"), {"C#", "F", "G#"})

    def test_validation(self):
        with self.assertRaises(ValueError):
            fretboard_notes("x")
        with self.assertRaises(ValueError):
            fretboard_notes("g", -1)
        with self.assertRaises(ValueError):
            chord_notes("H")
        with self.assertRaises(ValueError):
            chord_notes("G", "diminished")

    def test_note_wrap(self):
        self.assertEqual(note_name(60), "C")
        self.assertEqual(note_name(72), "C")


if __name__ == "__main__":
    unittest.main()
