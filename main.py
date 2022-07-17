import sudoku
import time

debugTimer = time.perf_counter()

def try_variants(sdk):
    sdk: sudoku.Sudoku

    sdk.process_allowed_values()

    undefined_cells = sdk.get_udefined_cells()
    if len(undefined_cells) == 0:
        if sdk.is_solved():
            return sdk
        else:
            raise sudoku.Sudoku.NoValidSolutions('')
    variants = {(r, c): cell.get_allowed_values() for (r, c), cell in undefined_cells.items()}

    minimum = 100  # search of an undefined cell wih minimum choice
    for (r, c), vls in variants.items():
        if len(vls) < minimum:
            (row, column), allowed_values = (r, c), vls
            minimum = len(vls)

    for var in allowed_values:
        sdk_copy = sdk.copy()
        sdk_copy.set_cell_value(var, row, column)
        try:
            result = try_variants(sdk_copy)
        except sudoku.Sudoku.NoValidSolutions:
            continue
        return result
    else:
        raise sudoku.Sudoku.NoValidSolutions('')


with open('p096_sudoku.txt', 'r') as src:
    lines = [line.strip() for line in src.readlines()]

sudoku_list = []
lines.insert(0, '')  # for convinient line numbering
line_number = 1
solved_sudokus = []
while line_number < len(lines):
    if lines[line_number][0] == 'G':
        line_number += 1
        sdk = sudoku.Sudoku(id=line_number)
        for row in range(9):
            l = list(lines[line_number + row])
            sdk2 = [int(x) for x in l]
            for i in range(0, 9):
                sdk.set_cell_value(sdk2[i], row + 1, i + 1)
        sudoku_list.append(sdk)
    line_number += 9

for sdk in sudoku_list:
    try:
        solved_sdk = try_variants(sdk.copy())
        solved_sudokus.append(solved_sdk)
    except sudoku.Sudoku.NoValidSolutions:
        print('No solutions found for\n')
        print(sdk)

sigantures = [sdk.get_signature() for sdk in solved_sudokus]
print(sum(sigantures))

debugTimer = time.perf_counter() - debugTimer
print(debugTimer, ' sec')
with open('output.txt', 'w') as ou:
    for i in range(0, 50):
        ou.write(f'Sudoku from source line { sudoku_list[i].get_id()}\n')
        ou.write(str(sudoku_list[i]))
        ou.write('\n')
        ou.write(str(solved_sudokus[i].is_solved()) + '\n')
        ou.write(str(solved_sudokus[i]))
        ou.write('\n\n\n\n')
print('Check output.txt for solutions.')

