""" Written programmatically by Benjamin Jack Cullen """

""" Source and credits to: https://fileinfo.com/ """

import codecs
import os

tag0 = '""" Written programmatically by Benjamin Jack Cullen """'
tag1 = '""" Source and credits to: https://fileinfo.com/ """'

for d, s, fl in os.walk('./'):
    for f in fl:
        print(f)
        _lines = []
        with codecs.open(f, 'r', encoding='utf8') as fo:
            for line in fo:
                # line = line.strip()
                _lines.append(line)
        fo.close()

        # with codecs.open(f, 'w', encoding='utf8') as fo:
        #     fo.write(tag0+'\n\n')
        #     fo.write(tag1+'\n\n')
        #     for _line in _lines:
        #         fo.write(_line)
        # fo.close()

