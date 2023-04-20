class Token():
    string = 0
    number = 1
    arithmetic_op = 2
    left_branket = 3
    right_branket = 4
    compare_op = 5
    def __init__(self, pair) -> None:
        [num, input] = pair
        self.num = num
        self.input = input
    def __str__(self) -> str:
        return self.input
    def value(self):
        return [self.num, self.input]
    def __repr__(self) -> str:
        num = str(self.num)
        display = self.input if self.num == Token.number else repr(self.input)
        return '[' + num + ', ' + display + ']'

class BinaryOperation():
    def __init__(self, op, lhs, rhs) -> None:
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

class GroupingOperation():
    def __init__(self, content) -> None:
        self.content = content

class CompareOperation():
    def __init__(self, op, lhs, rhs) -> None:
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

class String():
    def __init__(self, string) -> None:
        self.string = string
    def __str__(self) -> str:
        self.string
    def value(self) -> str:
        self.string

class Number():
    def __init__(self, value) -> None:
        self.value = value
    def __str__(self) -> str:
        return self.value
    def value(self):
        return float(self.value)

class Call():
    def __init__(self, string, parameters) -> None:
        self.string = string
        self.parameters = parameters



class DigitStatusStart():
    pass
class DigitStatusAfterDot():
    pass

digit_status_start = DigitStatusStart()
digit_status_after_dot = DigitStatusAfterDot()

class Lexing():
    def lex(source):
        digit_buffer = ""
        string_buffer = ""
        digit_status = digit_status_start
        ret = []
        skip_once = False
        for offset in range(0, len(source)):
            if skip_once:
                skip_once = False
                continue
            char = str(source[offset])
            if char == '(':
                if len(digit_buffer) > 0:
                    digit_status = digit_status_start
                    ret.append(Token([Token.number, digit_buffer]))
                    digit_buffer = ""
                if len(string_buffer) > 0:
                    ret.append(Token([Token.string, string_buffer]))
                    string_buffer = ""
                ret.append(Token([Token.left_branket, "("]))
            elif char == ')':
                if len(digit_buffer) > 0:
                    digit_status = digit_status_start
                    ret.append(Token([Token.number, digit_buffer]))
                    digit_buffer = ""
                if len(string_buffer) > 0:
                    ret.append(Token([Token.string, string_buffer]))
                    string_buffer = ""
                ret.append(Token([Token.right_branket, ")"]))
            elif char in ['+', '-', '*', '/']:
                if len(digit_buffer) > 0:
                    digit_status = digit_status_start
                    ret.append(Token([Token.number, digit_buffer]))
                    digit_buffer = ""
                if len(string_buffer) > 0:
                    ret.append(Token([Token.string, string_buffer]))
                    string_buffer = ""
                ret.append(Token([Token.arithmetic_op, char]))
            elif char.isdigit():
                if digit_buffer == "0":
                    raise ValueError("unexpected character '" + char + "'")
                digit_buffer += char
            elif char == '.':
                if digit_status == digit_status_start:
                    digit_buffer += '.'
                    digit_status = digit_status_after_dot
                else:
                    raise ValueError("unexpected character '.'")
            elif char.isalpha() or u'\u4e00' <= char <= u'\u9fff':
                string_buffer += char
            elif char in ['>', '<']:
                if len(source) > offset + 1 and source[offset + 1] == '=':
                    if len(digit_buffer) > 0:
                        digit_status = digit_status_start
                        ret.append(Token([Token.number, digit_buffer]))
                        digit_buffer = ""
                    if len(string_buffer) > 0:
                        ret.append(Token([Token.string, string_buffer]))
                        string_buffer = ""
                    ret.append(Token([Token.compare_op, char + '=']))
                    skip_once = True
                    continue
                if len(digit_buffer) > 0:
                    digit_status = digit_status_start
                    ret.append(Token([Token.number, digit_buffer]))
                    digit_buffer = ""
                if len(string_buffer) > 0:
                    ret.append(Token([Token.string, string_buffer]))
                    string_buffer = ""
                ret.append(Token([Token.compare_op, char]))
            elif char == '=':
                ret.append(Token([Token.compare_op, char]))
            elif char.isspace():
                if len(digit_buffer) > 0:
                    digit_status = digit_status_start
                    ret.append(Token([Token.number, digit_buffer]))
                    digit_buffer = ""
                if len(string_buffer) > 0:
                    ret.append(Token([Token.string, string_buffer]))
                    string_buffer = ""
            else:
                raise ValueError("unexpected character '" + char + "'")
        if len(digit_buffer) > 0:
            digit_status = digit_status_start
            ret.append(Token([Token.number, digit_buffer]))
            digit_buffer = ""
        if len(string_buffer) > 0:
            ret.append(Token([Token.string, string_buffer]))
            string_buffer = ""
        return ret

    def serialize_tokens(tokens) -> str:
        ret = ""
        ret += "["
        for offset in range(0, len(tokens)):
            if offset > 0:
                ret += ", "
            ret += repr(tokens[offset])
        ret += "]"
        return ret

class Ast():
    def parse(tokens):
        (tree, num_consumed) = Ast.parse_helper(tokens)
        if num_consumed != len(tokens):
            raise ValueError("unexpected tokens " + repr(tokens[num_consumed:]))
        return tree

    def parse_number(tokens):
        if len(tokens) == 0:
            return None
        if tokens[0].num == Token.number:
            return (Number(tokens[0].input), 1)
        return None

    def parse_string(tokens):
        if len(tokens) == 0:
            return None
        if tokens[0].num == Token.string:
            return (String(tokens[0].input), 1)

    def parse_atom(tokens):
        rslt_number = Ast.parse_number(tokens)
        if rslt_number is not None:
            return rslt_number
        rslt_call = Ast.parse_call(tokens)
        if rslt_call is not None:
            return rslt_call
        rslt_grouping = Ast.parse_grouping_operation(tokens)
        return rslt_grouping

    def parse_binary_operation_1st_partial_ext(tokens):
        offset = 0
        acc = []
        while True:
            op = tokens[offset]
            if op.num != Token.arithmetic_op or op.input not in ['*', '/']:
                return None if len(acc) == 0 else (acc, offset)
            rslt_rhs = Ast.parse_atom(tokens[offset + 1:])
            if rslt_rhs is None:
                raise ValueError("unexpected tokens " + repr(tokens[offset + 1:]) + ", expected atom after " + repr(['*', '/']))
            (rhs, rhs_num_consumed) = rslt_rhs
            offset = rhs_num_consumed + 1 + offset
            acc.append((op, rhs))

    def parse_binary_operation_1st(tokens):
        rslt_head = Ast.parse_atom(tokens)
        if rslt_head is None:
            return None
        (head, head_consumed) = rslt_head
        rslt_tail = Ast.parse_binary_operation_1st_partial_ext(tokens[head_consumed:])
        if rslt_tail is None:
            return rslt_head
        (tail, tail_consumed) = rslt_tail
        acc = head
        for (op, rhs) in tail:
            acc = BinaryOperation(op.input, acc, rhs)
        return (acc, head_consumed + tail_consumed)

    def parse_binary_operation_2nd_ext(tokens):
        rslt_lhs = Ast.parse_atom(tokens)
        if rslt_lhs is None:
            return None
        (lhs, lhs_num_consumed) = rslt_lhs
        if len(tokens) == lhs_num_consumed:
            return (lhs, lhs_num_consumed)
        while True:
            rslt_tail = Ast.parse_binary_operation_1st_partial_ext(tokens[lhs_num_consumed:])
            if rslt_tail is not None:
                (tail, tail_consumed) = rslt_tail
                acc = lhs
                for (op, rhs) in tail:
                    acc = BinaryOperation(op.input, acc, rhs)
                return (acc, lhs_num_consumed + tail_consumed)
            op = tokens[lhs_num_consumed]
            if op.num != Token.arithmetic_op or op.input not in ['+', '-']:
                return rslt_lhs
            rslt_rhs = Ast.parse_binary_operation_1st(tokens[lhs_num_consumed + 1:])
            if rslt_rhs is None:
                raise ValueError("unexpected tokens " + repr(tokens[lhs_num_consumed + 1:]) + ", expected atom after " + repr(['+', '-']))
            (rhs, rhs_num_consumed) = rslt_rhs
            lhs_num_consumed = rhs_num_consumed + 1 + lhs_num_consumed
            lhs = BinaryOperation(op.input, lhs, rhs)
            rslt_lhs = (lhs, lhs_num_consumed)

    def parse_binary_operation(tokens):
        return Ast.parse_binary_operation_2nd_ext(tokens)

    def parse_grouping_operation_ext(tokens):
        offset = 0
        acc = None
        depth = 0
        def check_tailing(tokens, depth):
            for i in range(0, depth):
                if tokens[i].input != ')':
                    return False
            return True
        while True:
            if offset >= len(tokens) or tokens[offset].input != '(':
                if acc is None:
                    return None
                return (acc, offset + depth) if check_tailing(tokens[offset:], depth) else None
            rslt_value = Ast.parse_binary_operation(tokens[1:])
            if rslt_value is None:
                return None
            (value, num_consumed) = rslt_value
            offset += 1 + num_consumed
            acc = GroupingOperation(value)
            depth += 1

    def parse_grouping_operation(tokens):
        return Ast.parse_grouping_operation_ext(tokens)

    def parse_call(tokens):
        rslt_string = Ast.parse_string(tokens)
        if rslt_string is not None:
            (string, _) = rslt_string
            rslt_parameters = Ast.parse_grouping_operation(tokens[1:])
            if rslt_parameters is not None:
                (parameters, num_consumed) = rslt_parameters
                return (Call(string.string, parameters), num_consumed + 1)
        return None

    def parse_compare_operation(tokens):
        rslt_lhs = Ast.parse_binary_operation(tokens)
        if rslt_lhs is None:
            return None
        (lhs, num_consumed) = rslt_lhs
        if len(tokens) == num_consumed or tokens[num_consumed].num != Token.compare_op:
            return None
        op = tokens[num_consumed]
        offset = num_consumed + 1
        rslt_rhs = Ast.parse_binary_operation(tokens[offset:])
        if rslt_rhs is None:
            return None
        (rhs, num_consumed) = rslt_rhs
        return (CompareOperation(op.input, lhs, rhs), offset + num_consumed)

    def parse_helper(tokens):
        return Ast.parse_compare_operation(tokens)

    def format_tree(ast_node):
        lines = []        
        Ast.format_tree_helper(ast_node, lines);
        return '\n'.join(lines)

    def format_tree_helper_append(value, lines = [], ptr = (0, 0)):
        (x, y) = ptr
        for _ in range(len(lines), x + 1):
            lines.append("")
        for _ in range(len(lines[x]), y):
            lines[x] += " "
        for i in range(0, len(value)):
            cursor = i + y
            if cursor < len(lines[x]):
                lines[x] = lines[x][:cursor] + value[i] + lines[x][cursor + 1:]
            else:
                lines[x] += value[i]
            
        return (x, y + len(value))

    def format_tree_helper(ast_node, lines = [], ptr = (0, 0)):
        (x, y) = ptr
        if isinstance(ast_node, GroupingOperation):
            (_, y) = Ast.format_tree_helper_append("{(", lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(Ast.format_tree(ast_node.content), lines, (x, y))
            Ast.format_tree_helper_append(")}", lines, (x, y))
        elif isinstance(ast_node, Call):
            (_, y) = Ast.format_tree_helper_append("{", lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(ast_node.string, lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(Ast.format_tree(ast_node.parameters), lines, (x, y))
            Ast.format_tree_helper_append("}", lines, (x, y))
        elif isinstance(ast_node, BinaryOperation):
            (_, y) = Ast.format_tree_helper_append("{", lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(Ast.format_tree(ast_node.lhs), lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(str(ast_node.op), lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(Ast.format_tree(ast_node.rhs), lines, (x, y))
            Ast.format_tree_helper_append("}", lines, (x, y))
        elif isinstance(ast_node, CompareOperation):
            (_, y) = Ast.format_tree_helper_append("{", lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(Ast.format_tree(ast_node.lhs), lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(str(ast_node.op), lines, (x, y))
            (_, y) = Ast.format_tree_helper_append(Ast.format_tree(ast_node.rhs), lines, (x, y))
            Ast.format_tree_helper_append("}", lines, (x, y))
        else:
            Ast.format_tree_helper_append('{' + str(ast_node) + '}', lines, (x, y))


source = '1>2'
tokens = Lexing.lex(source)
assert(Lexing.serialize_tokens(tokens) == "[[1, 1], [5, '>'], [1, 2]]")
tree = Ast.parse(tokens)
print(Ast.format_tree(tree))

print()

source = '1+2>0'
tokens = Lexing.lex(source)
assert(Lexing.serialize_tokens(tokens) == "[[1, 1], [2, '+'], [1, 2], [5, '>'], [1, 0]]")
tree = Ast.parse(tokens)
print(Ast.format_tree(tree))

print()

source = '(1+2)>0'
tokens = Lexing.lex(source)
tree = Ast.parse(tokens)
print(Ast.format_tree(tree))

print()

source = '(1)/2>0'
tokens = Lexing.lex(source)
tree = Ast.parse(tokens)
print(Ast.format_tree(tree))

print()

source = '(折线顶(0) - 折线底(0)) / 折线底(0) >= 0.02'
tokens = Lexing.lex(source)
assert(Lexing.serialize_tokens(tokens) == "[[3, '('], [0, '折线顶'], [3, '('], [1, 0], [4, ')'], [2, '-'], [0, '折线底'], [3, '('], [1, 0], [4, ')'], [4, ')'], [2, '/'], [0, '折线底'], [3, '('], [1, 0], [4, ')'], [5, '>='], [1, 0.02]]")
tree = Ast.parse(tokens)
print(Ast.format_tree(tree))
