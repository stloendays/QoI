#!/usr/bin/env python3
import unittest
import numpy as np
import partition_codec as p

class PartitionCodecTests(unittest.TestCase):
    def setUp(self):
        x=np.zeros((7,8,9),dtype=np.int32)
        x[:2]=1; x[2:5]=2; x[5:]=7
        x[:,0,0]=0
        self.x=x

    def test_raw_exact(self):
        b=p.encode_raw(self.x)
        np.testing.assert_array_equal(p.decode(b),self.x)

    def test_rle_exact(self):
        b=p.encode_rle(self.x)
        np.testing.assert_array_equal(p.decode(b),self.x)

    def test_best_exact(self):
        b,m=p.encode_best(self.x)
        self.assertIn(m["method"],{"packed_zlib","rle_zlib"})
        self.assertEqual(m["bytes"],len(b))
        np.testing.assert_array_equal(p.decode(b),self.x)

    def test_dtype_boundaries(self):
        self.assertEqual(p.label_dtype(4).itemsize,1)
        self.assertEqual(p.label_dtype(255).itemsize,1)
        self.assertEqual(p.label_dtype(256).itemsize,2)
        self.assertEqual(p.label_dtype(65536).itemsize,4)

if __name__=="__main__":
    unittest.main()
