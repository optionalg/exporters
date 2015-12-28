import re
import unittest

import boto
import moto
import mock

from exporters.records.base_record import BaseRecord
from exporters.writers.s3_writer import S3Writer


def create_fake_key():
    key = mock.Mock()
    return key


def create_fake_bucket():
    bucket = mock.Mock()
    bucket.new_key.side_effect = create_fake_key()
    return bucket


def create_fake_connection():
    connection = mock.Mock()
    connection.get_bucket.side_effect = create_fake_bucket()
    return connection


class S3WriterTest(unittest.TestCase):

    def setUp(self):
        self.mock_s3 = moto.mock_s3()
        self.mock_s3.start()
        self.s3_conn = boto.connect_s3()
        self.s3_conn.create_bucket('fake_bucket')

    def tearDown(self):
        self.mock_s3.stop()

    def get_batch(self):
        data = [
            {'name': 'Roberto', 'birthday': '12/05/1987'},
            {'name': 'Claudia', 'birthday': '21/12/1985'},
        ]
        return [BaseRecord(d) for d in data]


    def test_write_s3(self):
        # given
        items_to_write = self.get_batch()
        options = self.get_writer_config()

        # when:
        try:
            writer = S3Writer(options)
            writer.write_batch(items_to_write)
            writer.flush()
        finally:
            writer.close()

        # then:
        bucket = self.s3_conn.get_bucket('fake_bucket')
        saved_keys = [k for k in bucket.list()]
        self.assertEquals(1, len(saved_keys))
        self.assertTrue(re.match('tests/.*[.]gz', saved_keys[0].name))

    def test_connect_to_specific_region(self):
        # given:
        conn = boto.connect_s3()
        conn.create_bucket('another_fake_bucket')

        options = self.get_writer_config()
        options['options']['aws_region'] = 'eu-west-1'
        options['options']['bucket'] = 'another_fake_bucket'

        # when:
        writer = S3Writer(options)

        # then:
        self.assertEquals('eu-west-1', writer.aws_region)
        writer.close()

    def test_write_pointer(self):
        # given:
        conn = boto.connect_s3()
        conn.create_bucket('pointer_fake_bucket')

        options = self.get_writer_config()
        options['options']['save_pointer'] = 'pointer/LAST'
        options['options']['bucket'] = 'pointer_fake_bucket'

        items_to_write = self.get_batch()

        # when:
        try:
            writer = S3Writer(options)
            writer.write_batch(items_to_write)
            writer.flush()
        finally:
            writer.close()

        # then:
        bucket = self.s3_conn.get_bucket('pointer_fake_bucket')
        saved_keys = [k for k in bucket.list('pointer/')]
        self.assertEquals(1, len(saved_keys))
        key = saved_keys[0]
        self.assertEqual('tests/', key.get_contents_as_string())


    def test_connect_to_bucket_location(self):
        # given:
        conn = boto.s3.connect_to_region('eu-west-1')
        conn.create_bucket('another_fake_bucket')

        options = self.get_writer_config()
        options['options']['bucket'] = 'another_fake_bucket'

        # when:
        writer = S3Writer(options)

        # then:
        self.assertEquals('eu-west-1', writer.aws_region)
        writer.close()

    def get_writer_config(self):
        return {
            'name': 'exporters.writers.s3_writer.S3Writer',
            'options': {
                'bucket': 'fake_bucket',
                'aws_access_key_id': 'FAKE_ACCESS_KEY',
                'aws_secret_access_key': 'FAKE_SECRET_KEY',
                'filebase': 'tests/',
            }
        }
