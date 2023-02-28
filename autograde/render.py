import os
from common_datamodels import test_result, exit_code


def to_html(results, filename="results.html", embed_style=True):
    # create an html file with the results in a table format
    # one row per student, use the variable names in the dataclass as the column headers
    # use the result and exit_code variables in the test_result dataclass as the values
    # use the exit_code enum to determine the color of the cell
    # green for success, light red for error, yellow for not attempted
    results = sorted(results, key=lambda x: x.student_name)
    headers = results[0].__annotations__.keys()
    with open(filename, 'w') as f:
        # import style sheet freeze.css
        if embed_style:
            f.write('<style>\n')
            print(os.getcwd())
            with open('../../autograde/freeze.css', 'r') as style:
                f.write(style.read())
            f.write('</style>\n')
        else:
            f.write('<link rel="stylesheet" href="../../autograde/freeze.css">\n')
        f.write('<html><body><table>\n')
        f.write('<tr>')
        for header in headers:
            f.write(f'<th>{header}</th>')
        f.write('</tr>\n')
        for result in results:
            f.write('<tr>')
            for header in headers:
                value = getattr(result, header)
                if isinstance(value, test_result):
                    # strip all non utf-8 characters
                    value.result = value.result.encode('ascii', 'ignore').decode('ascii')
                    # replace newlines with <br> so they are displayed correctly
                    value.result = value.result.replace('\n', '<br>')
                    if value.exit_code == exit_code.SUCCESS.value:
                        f.write(
                            f'<td style="background-color:lightgreen"><div class=scrollable>{value.result}</div></td>')
                    elif value.exit_code == exit_code.ERROR.value:
                        f.write(
                            f'<td style="background-color:lightcoral"><div class=scrollable>{value.result}</div></td>')
                    elif value.exit_code == exit_code.NOT_ATTEMPTED.value:
                        f.write(
                            f'<td style="background-color:lightyellow"><div class=scrollable>{value.result}</div></td>')
                else:
                    f.write(f'<td>{value}</td>')
            f.write('</tr>\n')
        f.write('</table></body></html>')


def print_progress_bar(
        iteration, total, prefix='', suffix='', decimals=1, length=os.get_terminal_size()[0], fill='█',
        printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r)
    """
    length -= len(prefix) + len(suffix) + 11
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
