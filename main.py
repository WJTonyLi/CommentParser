import sys
from enum import Enum


class State(Enum):
    CODE = 1
    SINGLE_LINE_COMMENT = 2
    MULTI_LINE_COMMENT = 3


def parseCStyleComments(file):
    lines, commentLines, singleLineComments, blockLines, blockComments, todoCount = 0, 0, 0, 0, 0, 0
    state = State.CODE
    todoCount = 0
    while True:
        hasCode, hasComment, hasBlockComment = False, False, False
        line = file.readline()
        if not line:
            break
        if state == State.SINGLE_LINE_COMMENT:
            state = State.CODE
        index = 0
        while True:
            if index == len(line):
                break
            if state == State.CODE:
                if line[index: index + 2] == '//':
                    state = State.SINGLE_LINE_COMMENT
                    singleLineComments += 1
                    index += 2
                    hasComment = True
                elif line[index: index + 2] == '/*':
                    state = State.MULTI_LINE_COMMENT
                    blockComments += 1
                    index += 2
                    hasComment = True
                    hasBlockComment = True
                elif not line[index: index + 1].isspace():
                    hasCode = True
                    index += 1
                else:
                    index += 1
            elif state == State.MULTI_LINE_COMMENT:
                hasComment = True
                hasBlockComment = True
                if line[index: index + 4] == 'TODO':
                    todoCount += 1
                    index += 4
                elif line[index: index + 2] == '*/':
                    state = State.CODE
                    index += 2
                else:
                    index += 1
            elif state == State.SINGLE_LINE_COMMENT:
                if line[index: index + 4] == 'TODO':
                    todoCount += 1
                    index += 4
                else:
                    index += 1
        lines += 1
        if hasComment:
            commentLines += 1
        if hasBlockComment:
            blockLines += 1
    return (lines, commentLines, singleLineComments, blockLines, blockComments, todoCount)


def parsePythonStyleComments(file):
    lines, commentLines, singleLineComments, blockLines, blockComments, todoCount = 0, 0, 0, 0, 0, 0
    singleLineCommentOnlyPrev, singleLineCommentOnlyPrev2 = False, False
    state = State.CODE
    todoCount = 0
    while True:
        singleLineCommentOnly = False
        hasCode, hasComment = False, False
        line = file.readline()
        if not line:
            break
        if state == State.SINGLE_LINE_COMMENT:
            state = State.CODE
        index = 0
        while True:
            if index == len(line):
                break
            if state == State.CODE:
                if line[index: index + 1] == '#':
                    if not hasCode:
                        singleLineCommentOnly = True
                    if not singleLineCommentOnlyPrev or hasCode:
                        singleLineComments += 1
                    state = State.SINGLE_LINE_COMMENT
                    index += 2
                    hasComment = True
                elif not line[index: index + 1].isspace():
                    hasCode = True
                    index += 1
                else:
                    index += 1
            elif state == State.SINGLE_LINE_COMMENT:
                if line[index: index + 4] == 'TODO':
                    todoCount += 1
                    index += 4
                else:
                    index += 1
        lines += 1
        if hasComment:
            commentLines += 1
        if singleLineCommentOnly and singleLineCommentOnlyPrev:
            blockLines += 1
            if not singleLineCommentOnlyPrev2:
                singleLineComments -= 1
                blockComments += 1
                blockLines += 1
        singleLineCommentOnlyPrev2 = singleLineCommentOnlyPrev
        singleLineCommentOnlyPrev = singleLineCommentOnly
    return (lines, commentLines, singleLineComments, blockLines, blockComments, todoCount)


try:
    file_name = sys.argv[1]
    file = open(file_name)
except IndexError:
    raise Exception("No file provided")

extension = file_name.split('.')[1]
if extension in ['c', 'cpp', 'java', 'js']:
    result = parseCStyleComments(file)
elif extension in ['py']:
    result = parsePythonStyleComments(file)
else:
    raise Exception("unknown file extension", extension)

print("Total # of lines:", result[0])
print("Total # of comment lines:", result[1])
print("Total # of single line comments:", result[2])
print("Total # of comment lines within block comments:", result[3])
print("Total # of block line comments:", result[4])
print("Total # of TODO’s:", result[5])
