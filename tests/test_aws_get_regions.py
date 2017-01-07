import os
from unittest import TestCase

import main.aws


class TestAws_get_regions(TestCase):
    def test_aws_get_regions(self):
        regions = main.aws.aws_get_regions(os.environ.get('AWS_KEY'), os.environ.get('AWS_SECRET'))
        self.assertIn('us-east-1', regions)
        self.assertIn('eu-west-1', regions)
