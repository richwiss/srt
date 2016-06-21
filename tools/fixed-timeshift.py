#!/usr/bin/env python

import srt
import datetime
import utils


def parse_args():
    parser = utils.basic_parser()
    parser.add_argument(
        '--seconds',
        type=float,
        required=True,
        help='how many seconds to shift',
    )
    return parser.parse_args()


def scalar_correct_subs(subtitles, seconds_to_shift):
    td_to_shift = datetime.timedelta(seconds=seconds_to_shift)
    for subtitle in subtitles:
        subtitle.start += td_to_shift
        subtitle.end += td_to_shift
        yield subtitle


def main():
    args = parse_args()
    subtitles_in = srt.parse(args.input.read())
    corrected_subs = scalar_correct_subs(subtitles_in, args.seconds)
    output = srt.compose(corrected_subs, strict=args.strict)
    args.output.write(output)


if __name__ == '__main__':
    main()
