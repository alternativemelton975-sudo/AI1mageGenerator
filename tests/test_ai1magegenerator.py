import os
import tempfile
import unittest

from AI1mageGenerator import generate_image


class GenerateImageTests(unittest.TestCase):
    def test_generate_image_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "sample.svg")
            result = generate_image("A sunset over mountains", output_path=output_path)
            self.assertTrue(os.path.exists(output_path))
            self.assertEqual(result, output_path)


if __name__ == "__main__":
    unittest.main()
