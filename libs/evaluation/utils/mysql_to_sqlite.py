"""
Scripts for translating MySQL to SQLite syntax
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

from collections import deque


def time_intervals(create_view_statement, debug=False):
    """
    Translates time interval syntax form MySQL to SQLite syntax
    :param create_view_statement: str
        sql query to create a view in MySQL
    :param debug: bool
        print additional debug info
    :return: str
        sql query to create a view in SQLite
    """
    # for example in data_ec_analysis, exp_icpms_sfc_batch_expanded, ...
    str_find_interval = " interval "
    str_find_second = " second)"
    # str_find_as = " AS"
    if str_find_interval in create_view_statement:
        while str_find_interval in create_view_statement:
            idx_find_interval = create_view_statement.find(str_find_interval)
            print("interval found: ", idx_find_interval) if debug else ""
            idx_begin = (
                -create_view_statement[:idx_find_interval][::-1].find(",")
                + idx_find_interval
            )
            idx_end = (
                idx_begin
                + create_view_statement[idx_begin:].find(str_find_second)
                + len(str_find_second)
            )
            str_mysql = create_view_statement[idx_begin:idx_end]
            # print(str_mysql)
            col_timestamp = str_mysql.split(str_find_interval)[0].strip(
                "( +-"
            )  # str_mysql.split('+')[0].strip('( ')
            if str_mysql.split(str_find_interval)[1].find("-(") != -1:
                print(str_mysql)
                raise Exception(
                    'Error please use simplified syntax for time interval in mysql. "(a - interval b second)"'
                )
            plus_minus = str_mysql.split(str_find_interval)[0][
                -1
            ]  # '-' if 'interval -' in str_mysql.split('+')[1] else '+'
            if plus_minus not in ["+", "-"]:
                print(str_mysql)
                raise Exception("Error converting plus/minus sign for time interval")
            col_add_seconds = (
                str_mysql.split(str_find_interval)[1]
                .split(str_find_second)[0]
                .strip("-()")
            )

            modifier = ['"%s" || %s || " seconds"' % (plus_minus, col_add_seconds)]
            # print(create_view_statement[idx_end:].strip('+- ')[:8])
            while (
                create_view_statement[idx_end:].strip("+- ")[:8] == "interval"
            ):  # .find(str_find_interval) < create_view_statement[idx_end:].find(str_find_as):
                idx_end_new = (
                    idx_end
                    + create_view_statement[idx_end:].find(str_find_second)
                    + len(str_find_second)
                )
                str_mysql_add = create_view_statement[idx_end:idx_end_new]
                # print(str_mysql_add)
                plus_minus = str_mysql_add.split(str_find_interval)[0][-1]
                col_add_seconds = (
                    str_mysql_add.split(str_find_interval)[1]
                    .split(str_find_second)[0]
                    .strip("-()")
                )
                modifier.append(
                    '"%s" || %s || " seconds"' % (plus_minus, col_add_seconds)
                )
                str_mysql += str_mysql_add
                idx_end = idx_end_new
                # raise Exception()

            str_sqlite = '(STRFTIME("%%Y-%%m-%%d %%H:%%M:%%f",%s, %s))' % (
                col_timestamp,
                ", ".join(modifier),
            )

            create_view_statement = (
                create_view_statement[:idx_begin]
                + str_sqlite
                + create_view_statement[idx_end:]
            )
            # print()

            print(
                "Converted timeinterval: \n\t", str_mysql, "\n\t-->\t", str_sqlite
            ) if debug else ""
        print("All time intervals converted") if debug else ""

    return create_view_statement


def timestampdiff(create_view_statement, debug=False):
    """
    Translates syntax for timestamp difference function  form MySQL to SQLite syntax
    :param create_view_statement: str
        sql query to create a view in MySQL
    :param debug: bool
        print additional debug info
    :return: str
        sql query to create a view in SQLite
    """
    # for example in data_ec_analysis, exp_icpms_sfc_batch_expanded, ...
    str_find_timestampdiff = "timestampdiff("
    # str_find_as = " AS"
    if str_find_timestampdiff in create_view_statement:
        while str_find_timestampdiff in create_view_statement:
            idx_find_timestampdiff = create_view_statement.find(str_find_timestampdiff)
            print("Timestampdiff found: ", idx_find_timestampdiff) if debug else ""
            idx_begin = idx_find_timestampdiff
            idx_end = (
                idx_begin
                + find_closing_bracket(
                    create_view_statement[idx_begin:],
                    create_view_statement[idx_begin:].find("("),
                )
                + 1
            )
            str_mysql = create_view_statement[idx_begin:idx_end]
            # print(str_mysql)
            timestampdiff_arguments = str_mysql.replace(str_find_timestampdiff, "")[
                :-1
            ].split(
                ","
            )  # remove timestampdiff( and )
            if len(timestampdiff_arguments) > 3:
                raise Exception(
                    "Conversion Error: Cannot handle more than 3 arguments", str_mysql
                )
            if timestampdiff_arguments[0] != "SECOND":
                raise Exception(
                    "Conversion Error: Can only hanlde difference in seconds! "
                    "- You would just need to change the multiplicator (days --> desired unit) in code",
                    str_mysql,
                )
            timestamp_col_early = timestampdiff_arguments[1]
            timestamp_col_late = timestampdiff_arguments[2]

            # julianday returns the fractional number of days since noon in Greenwich on November 24, 4714 B.C.
            # https://stackoverflow.com/questions/17708167/difference-in-seconds-between-timestamps-in-sqlite3
            # thus conversion:  days = 86400 seconds
            str_sqlite = "((julianday(%s) - julianday(%s)) * 86400.0)" % (
                timestamp_col_late,
                timestamp_col_early,
            )

            create_view_statement = (
                create_view_statement[:idx_begin]
                + str_sqlite
                + create_view_statement[idx_end:]
            )
            #

            print(
                "Converted timeinterval: \n\t", str_mysql, "\n\t-->\t", str_sqlite
            ) if debug else ""

        print("All time diffs converted") if debug else ""
        # print(create_view_statement)
    return create_view_statement


def functions(create_view_statement):
    """
    Translates syntax for basic functions (IF, STD,) from MySQL to SQLite syntax
    :param create_view_statement:str
        create view statement
    :return: str
        SQLite syntaxed query
    """
    return (
        create_view_statement.replace(" if(", " IIF(")
        .replace(",if(", ",IIF(")
        .replace(",std(", ",stdv(")
        .replace(" std(", " stdv(")
    )


def view_header(create_view_statement):
    """
    Removes create view header specific to MySQL syntax for compatibility with SQLite syntax
    :param create_view_statement: str
        create view statement
    :return: str
        SQLite syntaxed query
    """
    # create_view_statement.replace(' ALGORITHM=UNDEFINED DEFINER=`work_root`@`localhost` SQL SECURITY DEFINER', '')
    header = create_view_statement.split(" select ")[0]
    idx_begin = header.find(" ALGORITHM")
    idx_end = header.find(" VIEW")
    create_view_statement = (
        create_view_statement[:idx_begin] + create_view_statement[idx_end:]
    )
    return create_view_statement


def redundant_brackets(create_view_statement, debug=False):
    """
    Removes unnnecessary brackets automatically added by MSQL Workbench when createing a view with multiple join.
    Query with a certain number of brackets cannot be executed with SQlite. If there are more than 10 opening brackets
    sequentially, they are removed (ideally) without compromising logic of statement.
    :param create_view_statement: str
        create view statement
    :param debug: bool
        print additional debug info
    :return: str
        SQLite syntaxed query
    """
    str_split_from = " from "
    from_statement = create_view_statement.split(str_split_from)[1]
    count_redundant_brackets_found = len(from_statement) - len(
        from_statement.strip("(")
    )

    if count_redundant_brackets_found > 10:  # multiple brackets after from
        print(
            "Found ",
            count_redundant_brackets_found,
            " redundant brackets in statement of ",
            create_view_statement,
        ) if debug else ""
        # print(len(create_view_statement.split('left join')[1:]))
        # display(create_view_statement.split('left join'))

        count_redundant_bracket = 0
        join_statements = []
        for join_statement in create_view_statement.split("left join")[1:]:
            # print(join_statement)
            if ")" in join_statement:
                count_redundant_bracket += 1
                idx_redundant_bracket = -join_statement[::-1].find(")") - 1
                join_statements.append(
                    join_statement[:idx_redundant_bracket]
                    + (
                        join_statement[idx_redundant_bracket + 1:]
                        if idx_redundant_bracket < -1
                        else ""
                    )
                )
            else:
                print("no ) found in:", join_statement)
                join_statements.append(join_statement)

        print(
            "Removed", count_redundant_bracket, "redundant brackets."
        ) if debug else ""
        create_view_statement = "left join".join(
            [
                create_view_statement.split("left join")[0].replace(
                    "(" * count_redundant_bracket, ""
                )
            ]
            + join_statements
        )
    return create_view_statement


def query_params(query):
    """
    Translates dummy string in query which marks position of a parameter in a query from MySQL ('%s') to ('?')
    :param query: str
        SQL query in MySQL syntax
    :return: str
        SQL query in SQLite
    """
    return query.replace("%s", "?")


def database_name(query, debug):
    """
    Removes database name (hte_data) prepended to the table name. There is no equivalent for this notation in SQLite.
    :param query: str
        SQL query in MySQL syntax
    :param debug: bool
        print additional debug info
    :return: str
        SQL query in SQLite
    """
    str_replace_databasename = "hte_data."
    if query.find(str_replace_databasename) != -1 and debug:
        print(
            "Please remove database names from your query. In sqlite there is no such conecpt as database names"
        )
    return query.replace(str_replace_databasename, "")


def find_closing_bracket(s, i):
    """
    find position of a closing bracket for a given opening bracket at position i in string s
    :param s: str
        given string to search for bracket pair
    :param i: int
        position of the opening bracket
    :return: int
        position of closing bracket
    """
    brackets = {"[": "]", "(": ")", "{": "}", '"': '"', "'": "'"}
    # If input is invalid.
    if s[i] in brackets.keys():  # != '[':
        bracket_open = s[i]
        bracket_close = brackets[s[i]]
    else:
        return -1

    # Create a deque to use it as a stack.
    d = deque()

    # Traverse through all elements
    # starting from i.
    for k in range(i, len(s)):

        # Pop a starting bracket
        # for every closing bracket
        if s[k] == bracket_close:
            d.popleft()

        # Push all starting brackets
        elif s[k] == bracket_open:
            d.append(s[i])

        # If deque becomes empty
        if not d:
            return k

    return -1


def find_closing_quote(s, i):
    """
    find position of a closing quote for a given opening quote at position i in string s.
    Triple quotes are not supported.
    :param s: str
        given string to search for quotes pair
    :param i: int
        position of the opening bracket
    :return: int
        position of closing bracket
    """
    quotes = ['"', "'"]
    # If input is invalid.
    if s[i] in quotes:  # != '[':
        quote = s[i]
    else:
        return -1

    if quote in s[i + 1:]:
        return i + 1 + s[i + 1:].find(quote)
    else:
        return -1


def substitute_quoted_comment(
    line,
    sign_comment="#",
    sign_comment_replace="**hashtag**",
    sign_quotes=None,
    debug=False,
):
    """
    Internal function to substitute comment signs (MySQL; '#') with a dummy to avoid their substitution by comments()
    :param line: str
        line in a SQL query
    :param sign_comment: str
        letter to start a comment in SQL
    :param sign_comment_replace: str
        str to which sign_comment should be replaced
    :param sign_quotes: list of str
        list of quotes which should be considered
    :param debug: bool
        print additional debug info
    :return: str
        string with all sign_comment within quotes replaced with sign_comment_replace
    """
    if sign_quotes is None:
        sign_quotes = ['"', "'"]
    if sign_comment in line:
        for sign_quote in sign_quotes:
            if sign_quote in line:
                print("Found quote at: ", line.find(sign_quote)) if debug else ""
                # print(line[find_closing_quote(line, line.find(sign_quote))]) # check if this closing quote
                idx_closing_quote = find_closing_quote(line, line.find(sign_quote))
                if line.find(sign_quote) < line.find(sign_comment) < idx_closing_quote:
                    line = str(
                        line[: line.find(sign_comment)]
                        + sign_comment_replace
                        + line[line.find("#") + 1: idx_closing_quote + 1]
                        + substitute_quoted_comment(
                            line[idx_closing_quote + 1:],
                            sign_comment=sign_comment,
                            sign_comment_replace=sign_comment_replace,
                            sign_quotes=sign_quotes,
                        )
                    )
                    print("comment sign in quotes: ", line) if debug else ""
    return line


def comments(query, debug=False):
    """
    Translate comments syntax from MySQL to SQLite. Replacement of '#' in quotes is not performed.
    :param query: str
        query in MySQL syntax
    :param debug: bool
        print additional debug info
    :return: str
        query in SQLite syntax
    """
    sign_comment = "#"
    sign_comment_replace = "**hashtag**"
    sign_comment_sqlite_open = "/*"
    sign_comment_sqlite_close = "*/"
    split_newline = "\n"
    query_replaced = ""
    if sign_comment in query:
        for line in query.split(split_newline):
            while sign_comment_replace in line:
                sign_comment_replace += "*"
            line_substituted = substitute_quoted_comment(
                line,
                sign_comment=sign_comment,
                sign_comment_replace=sign_comment_replace,
                sign_quotes=['"', "'"],
                debug=debug,
            )
            if sign_comment in line_substituted:
                line = str(
                    line_substituted.replace("#", sign_comment_sqlite_open)
                    + sign_comment_sqlite_close
                ).replace(sign_comment_replace, sign_comment)
            print(line) if debug else ""
            query_replaced += line + split_newline
            # print(line.replace('#', '\\*')+'*\\')
        return query_replaced
    else:
        return query
