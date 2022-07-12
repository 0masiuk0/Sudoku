import itertools


class Cell:
    def __init__(self):
        self.TryoutValue = 0
        self.__value = 0
        self.__allowed_values = set(range(1, 10))

    def get_value(self):
        return self.__value

    def set_value(self, value=None):
        if value is None:
            self.__value = self.TryoutValue
        elif value not in self.__allowed_values and value != 0:
            raise ValueError("Value no allowed")
        else:
            self.__value = value
            self.TryoutValue = value

    def get_allowed_values(self):
        return self.__allowed_values.copy()

    def value_is_set(self):
        return self.__value != 0

    def forbid_values(self, values):
        v = (x for x in values if x != self.__value and x != 0)
        self.__allowed_values.difference_update(v)
        if len(self.__allowed_values) == 1:
            found_new = self.__value == 0
            self.set_value(next(iter(self.__allowed_values)))
            if found_new:
                return True
            else:
                return False
        elif len(self.__allowed_values) == 0:
            raise Sudoku.NoValidSolutions('')
        else:
            return False

    def __repr__(self):
        return str(self.__value) + ':' + str(self.TryoutValue)


class Sudoku:
    def __init__(self):
        self.__cells = {}
        for i in range(1, 10):
            for j in range(1, 10):
                self.__cells[i, j] = Cell()
        self.__rows = tuple(Sudoku.Row(self, row_num) for row_num in range(1, 10))
        self.__columns = tuple(Sudoku.Column(self, col_num) for col_num in range(1, 10))
        self.__squares = {(r, c): Sudoku.Square(self, r, c) for r, c in itertools.product(range(1, 4), range(1, 4))}
        self.__cell_sets = lambda: itertools.chain(self.__rows, self.__columns, self.__squares.values())

    def process_allowed_values(self):
        foundNewValue = True
        while foundNewValue:
            foundNewValue = False
            for (row, column), cell in self.__cells.items():
                foundNewValue |= cell.forbid_values(self.get_row(row).get_non_zero_values_set())
                foundNewValue |= cell.forbid_values(self.get_column(column).get_non_zero_values_set())
                foundNewValue |= cell.forbid_values(self.get_square_of_a_cell(row, column).get_non_zero_values_set())

    def get_cell(self, row, column):
        return self.__cells[row, column]

    def get_row(self, n):
        return self.__rows[n - 1]

    def get_column(self, n):
        return self.__columns[n - 1]

    def get_square_of_a_cell(self, row, column):
        r = ((row - 1) // 3) + 1
        c = ((column - 1) // 3) + 1
        return self.__squares[r, c]

    def set_cell_value(self, value, row, column):
        return self.__cells[row, column].set_value(value)

    def get_cell_value(self, row, column):
        return self.__cells[row, column].get_value()

    def get_signature(self):
        return 100 * self.get_cell_value(1, 1) + 10 * self.get_cell_value(1, 2) + self.get_cell_value(1, 3)

    def get_udefined_cells(self):
        return {(r, c): cell for (r, c), cell in self.__cells.items() if not cell.value_is_set()}

    def project_tryout_values_to_undefined_cells(self, values):
        undefined = self.get_udefined_cells().values()
        undefinedIndexed = dict(zip(range(0, len(undefined)), undefined))
        if len(values) != len(undefined):
            raise ValueError('Bad values for tryout')
        for i in range(0, len(values)):
            undefinedIndexed[i].TryoutValue = values[i]

    def check_if_tryout_solves_it(self):
        ok = False not in (x.is_tryout_valid() for x in self.__cell_sets())
        return ok

    def set_values_from_tryouts(self):
        for cell in self.__cells.values():
            cell.set_value()

    def copy(self):
        cpy = Sudoku()
        for (i, j), cell in self.__cells.items():
            cpy.set_cell_value(cell.get_value(), i, j)
            forbidden_values = set(range(1, 10)) - cell.get_allowed_values()
            cpy.__cells[i, j].forbid_values(forbidden_values)
        return cpy

    def __repr__(self):
        s = ''
        for row in self.__rows:
            s += str(row) + '\n'
        return s

    class CellSet:
        def __init__(self, sudoku):
            self._cells = ()
            self.__sudoku = sudoku

        def get_values_set(self, tryout=False):
            if tryout:
                return set(x.TryoutValue for x in self._cells)
            else:
                return set(x.get_value() for x in self._cells)

        def get_non_zero_values_set(self, tryout=False):
            if tryout:
                return set(x.TryoutValue for x in self._cells if x.TryoutValue != 0)
            else:
                return set(x.get_value() for x in self._cells if x.get_value() != 0)

        def get_values(self, tryout=False):
            if tryout:
                return [c.TryoutValue for c in self._cells]
            else:
                return [c.get_value() for c in self._cells]

        def is_valid_so_far(self):
            for i in range(0, 9):
                if i < 0 or i > 9:
                    return False
                if self._cells[i].get_value() != 0:
                    for j in itertools.chain(range(0, i), range(i + 1, 9)):
                        if self._cells[i].get_value() == j:
                            return False
            return True

        def is_valid(self):
            values_set = self.get_values_set()
            cond1 = False in (x in values_set for x in range(1, 10))
            cond2 = False in (x > 0 and x <= 9 for x in values_set)
            return not (cond1 or cond2)

        def is_tryout_valid(self):
            values_set = self.get_values_set(tryout=True)
            cond1 = len(values_set) != 9
            cond2 = False in (x > 0 and x <= 9 for x in values_set)
            return not (cond1 or cond2)

        def __repr__(self):
            return str([str(c.get_value()) for c in self._cells])

    class Row(CellSet):
        def __init__(self, sudoku, row_number):
            super().__init__(sudoku)
            c = []
            for column in range(1, 10):
                c.append(sudoku.get_cell(row_number, column))
            self._cells = tuple(c)
            self.row_number = row_number

    class Column(CellSet):
        def __init__(self, sudoku, column_number):
            super().__init__(sudoku)
            c = []
            for row in range(1, 10):
                c.append(sudoku.get_cell(row, column_number))
            self._cells = tuple(c)
            self.column_number = column_number

    class Square(CellSet):
        def __init__(self, sudoku, square_row, square_column):
            super().__init__(sudoku)
            c = []
            for row in range((square_row - 1) * 3 + 1, square_row * 3 + 1):
                for column in range((square_column - 1) * 3 + 1, square_column * 3 + 1):
                    c.append(sudoku.get_cell(row, column))
            self._cells = tuple(c)
            self.row_of_squares = square_row
            self.column_of_squares = square_column

    class NoValidSolutions(Exception):
        def __init__(self, message):
            super().__init__(message)
