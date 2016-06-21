#!/usr/bin/env python

import srt
import datetime
import utils


def timedelta_to_milliseconds(delta):
    return delta.days * 86400000 + \
           delta.seconds * 1000 + \
           delta.microseconds / 1000

def parse_args():
    def srt_timestamp_to_milliseconds(parser, arg):
        try:
            delta = srt.srt_timestamp_to_timedelta(arg)
        except ValueError:
            parser.error('not a valid SRT timestamp: %s' % arg)
        else:
            return timedelta_to_milliseconds(delta)

    parser = utils.basic_parser()
    parser.add_argument(
        '--from-start',
        '--f1',
        type=lambda arg: srt_timestamp_to_milliseconds(parser, arg),
        required=True,
        help='the first desynchronised timestamp',
    )
    parser.add_argument(
        '--to-start',
        '--t1',
        type=lambda arg: srt_timestamp_to_milliseconds(parser, arg),
        required=True,
        help='the first synchronised timestamp',
    )
    parser.add_argument(
        '--from-end',
        '--f2',
        type=lambda arg: srt_timestamp_to_milliseconds(parser, arg),
        required=True,
        help='the second desynchronised timestamp',
    )
    parser.add_argument(
        '--to-end',
        '--t2',
        type=lambda arg: srt_timestamp_to_milliseconds(parser, arg),
        required=True,
        help='the second synchronised timestamp',
    )
    return parser.parse_args()


def calc_correction(to_start, to_end, from_start, from_end):
    angular = (to_end - to_start) / (from_end - from_start)
    linear = to_end - angular * from_end
    return angular, linear


def correct_time(current_msecs, angular, linear):
    return round(current_msecs * angular + linear)


def correct_timedelta(bad_delta, angular, linear):
    bad_msecs = timedelta_to_milliseconds(bad_delta)
    good_msecs = correct_time(bad_msecs, angular, linear)
    good_delta = datetime.timedelta(milliseconds=good_msecs)
    return good_delta


def linear_correct_subs(subtitles, angular, linear):
    for subtitle in subtitles:
        subtitle.start = correct_timedelta(subtitle.start, angular, linear)
        subtitle.end = correct_timedelta(subtitle.end, angular, linear)
        yield subtitle


def main():
    args = parse_args()
    angular, linear = calc_correction(
        args.to_start, args.to_end,
        args.from_start, args.from_end,
    )
    subtitles_in = srt.parse(args.input.read())
    corrected_subs = linear_correct_subs(subtitles_in, angular, linear)
    output = srt.compose(corrected_subs, strict=args.strict)
    args.output.write(output)


if __name__ == '__main__':
    main()
