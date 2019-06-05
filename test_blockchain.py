import unittest
from blockchain import Block

class TestBlockchain(unittest.TestCase):

    def test_random_block_should_have_bad_hash(self):
        bad_block = Block("TRANS", "", "", output=None, public_key_hash="")
        self.assertFalse(bad_block.verify())


if __name__ == "__main__":
    unittest.main()