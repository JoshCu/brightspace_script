import subprocess
import os
# the b means bytes so we can use the \n
INPUT = b"3\n10\n10\n7\n12\n5\n8\n"
# timeout in seconds for the subprocess
TIMEOUT = 1


def to_csv(results):
    # write the results to a csv file
    # convert results to a grid on a webpage
    # if success then make the cell green
    # if failure then make the cell red
    # add border to the table
    with open("run_results.html", "w") as f:
        f.write("<table border=\"1\">")
        for student in sorted(results.keys()):
            f.write("<tr>")
            f.write("<td>" + student + "</td>")
            for result in results[student]:
                if str(result[0]) == "Compilation":
                    if str(result[1]) == "SUCCESS":
                        f.write("<td bgcolor=\"green\">" + str(result[1]) + "</td>")
                    else:
                        f.write("<td bgcolor=\"red\">" + str(result[1]) + "</td>")
                elif str(result[0]) == "Mixed Files":
                    if str(result[1]) == "True":
                        f.write("<td bgcolor=\"blue\">" + str(result[1]) + "</td>")
                    else:
                        f.write("<td bgcolor=\"white\">" + str(result[1]) + "</td>")
                elif str(result[0]) == "Runtime":
                    if str(result[1]) == "True":
                        f.write("<td bgcolor=\"green\">" + str(result[1]) + "</td>")
                        f.write("<td bgcolor=\"green\">" + str(result[2]) + "</td>")
                    else:
                        f.write("<td bgcolor=\"red\">" + str(result[1]) + "</td>")
                        f.write("<td bgcolor=\"red\">" + str(result[2]) + "</td>")
            f.write("</tr>")
        f.write("</table>")

# Open results.csv load all of the students


students = {}
with open("results.csv", "r") as f:
    for line in f:
        metrics = []
        line = line.strip()
        if line and (len(line.split(',')) > 3):
            surname, forename, mixed, build_status = line.split(",")[:4]
            metrics.append(("Compilation", build_status))
            metrics.append(("Mixed Files", mixed))

        students[surname + "," + forename] = metrics
# loop through the students and run their code if successfuly built
for student in students:
    for metric in students[student]:
        if metric[0] == "Compilation" and metric[1] == "SUCCESS":
            binary_path = os.path.join(os.getcwd(), student, "bin", "out.exe")
            try:

                result = subprocess.run([binary_path], check=True, capture_output=True, input=INPUT, timeout=TIMEOUT)
                students[student].append(("Runtime", "True", result.stdout.decode("utf-8")))

            except subprocess.CalledProcessError as e:
                # get the error message
                students[student].append(("Runtime", "False", result.stderr.decode("utf-8")))
            except subprocess.TimeoutExpired as e:
                students[student].append(("Runtime", "False", "Timeout"))
            # p = subprocess.Popen(binary_path, shell=True,
            #                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # out, err = p.communicate(input=INPUT)
            # p.wait(timeout=1)
            # if err:
            #     students[student].append(("Runtime", "False", err.decode("utf-8")))
            # # get just the last two lines of output
            # if out:
            #     students[student].append(("Runtime", "True", out.decode("utf-8")))


to_csv(students)
