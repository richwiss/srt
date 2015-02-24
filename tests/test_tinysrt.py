#!/usr/bin/env python
# vim: set fileencoding=utf8

import tinysrt
import os
from datetime import timedelta
from nose.tools import eq_ as eq, assert_not_equal as neq, ok_ as ok

try:
    from io import StringIO
except ImportError:  # Python 2 fallback
    from cStringIO import StringIO


class TestTinysrt(object):
    @classmethod
    def setup_class(cls):
        cls.srt_filename = cls._fixture('srt_samples/monsters.srt')
        cls.srt_filename_bad_order = cls._fixture('srt_samples/monsters-bad-order.srt')

        with open(cls.srt_filename) as srt_f:
            cls.srt_sample = srt_f.read()

        with open(cls.srt_filename_bad_order) as srt_bad_f:
            cls.srt_sample_bad_order = srt_bad_f.read()

    def setup(self):
        self.srt_f = open(self.srt_filename)
        self.srt_bad_order_f = open(self.srt_filename_bad_order)

    def teardown(self):
        self.srt_f.close()
        self.srt_bad_order_f.close()

    def _fixture(path):
        return os.path.join(os.path.dirname(__file__), path)

    def test_timedelta_to_srt_timestamp(self):
        timedelta_ts = timedelta(hours=1, minutes=2, seconds=3, milliseconds=400)
        eq(tinysrt.timedelta_to_srt_timestamp(timedelta_ts), '01:02:03,400')


    def test_srt_timestamp_to_timedelta(self):
        eq(
            timedelta(hours=1, minutes=2, seconds=3, milliseconds=400),
            tinysrt.srt_timestamp_to_timedelta('01:02:03,400'),
        )

    def _test_monsters_subs(self, subs):
        eq(3, len(subs))

        eq(421, subs[0].index)
        eq(
            timedelta(
                hours=0,
                minutes=31,
                seconds=37,
                milliseconds=894,
            ),
            subs[0].start,
        )
        eq(
            timedelta(
                hours=0,
                minutes=31,
                seconds=39,
                milliseconds=928,
            ),
            subs[0].end,
        )
        eq(
            '我有个点子\nOK, look, I think I have a plan here.',
            subs[0].content,
        )

        eq(422, subs[1].index)
        eq(
            timedelta(
                hours=0,
                minutes=31,
                seconds=39,
                milliseconds=931,
            ),
            subs[1].start,
        )
        eq(
            timedelta(
                hours=0,
                minutes=31,
                seconds=41,
                milliseconds=931,
            ),
            subs[1].end,
        )
        eq(
            '我们要拿一堆汤匙\nUsing mainly spoons,',
            subs[1].content,
        )

    def test_parse_general(self):
        subs = list(tinysrt.parse(self.srt_sample))
        self._test_monsters_subs(subs)


    def test_parse_file(self):
        srt_f = open(self.srt_filename)
        subs = list(tinysrt.parse_file(srt_f))
        self._test_monsters_subs(subs)
        srt_f.close()

    def test_parse_file_buffer_size_irrelevant(self):
        srt_f = open(self.srt_filename)

        subs = []

        for buf_size in range(4):
            srt_f.seek(0)
            subs.append(list(tinysrt.parse_file(srt_f)))

        ok(all(sub == subs[0] for sub in subs))

        srt_f.close()


    def test_compose(self):
        subs = tinysrt.parse(self.srt_sample)
        eq(self.srt_sample, tinysrt.compose(subs))


    def test_default_subtitle_sorting_is_by_start_time(self):
        subs = tinysrt.parse(self.srt_sample_bad_order)
        sorted_subs = sorted(subs)

        eq(
            [x.index for x in sorted_subs],
            [422, 421, 423],
        )


    def test_subtitle_equality_false(self):
        subs_1 = list(tinysrt.parse(self.srt_sample))
        subs_2 = list(tinysrt.parse(self.srt_sample))
        subs_2[0].content += 'blah'

        neq(subs_1, subs_2)


    def test_subtitle_equality_true(self):
        subs_1 = list(tinysrt.parse(self.srt_sample))
        subs_2 = list(tinysrt.parse(self.srt_sample))
        eq(subs_1, subs_2)


    def test_compose_file(self):
        srt_in_f = open(self.srt_filename)
        srt_out_f = StringIO()

        subs = tinysrt.parse_file(srt_in_f)
        tinysrt.compose_file(subs, srt_out_f)

        srt_in_f.seek(0)
        srt_out_f.seek(0)

        eq(srt_in_f.read(), srt_out_f.read())

        srt_in_f.close()


    def test_compose_file_num(self):
        srt_in_f = open(self.srt_filename)
        srt_out_f = StringIO()

        subs = tinysrt.parse_file(srt_in_f)
        num_written = tinysrt.compose_file(subs, srt_out_f)

        eq(3, num_written)

        srt_in_f.close()


    def test_compose_file_num_none(self):
        srt_out_f = StringIO()

        subs = list(tinysrt.parse(''))
        num_written = tinysrt.compose_file(subs, srt_out_f)

        eq(0, num_written)
