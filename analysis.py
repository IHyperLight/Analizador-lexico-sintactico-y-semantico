import ply.lex as lex
import ply.yacc as yacc
import re

lexical_errors = []
syntax_errors = []
lexical_error_occurred = False
syntax_error_occurred = False

tokens = (
    'CREATE', 'DATABASE', 'USE', 'TABLE', 'INSERT', 'INTO', 'UPDATE', 'DELETE',
    'ID', 'COMMA', 'SEMICOLON', 'LPAREN', 'RPAREN', 'ASTERISK', 'SET', 'VALUES',
    'WHERE', 'AND', 'OR', 'NOT', 'NULL', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES',
    'INT', 'FLOAT', 'VARCHAR', 'TEXT', 'DATETIME', 'TIMESTAMP', 'DATE', 'TIME',
    'UNSIGNED', 'AUTO_INCREMENT', 'EQUALS', 'PLUS', 'MINUS', 'DIVIDE', 'MOD',
    'GREATER', 'LESS', 'GREATER_EQ', 'LESS_EQ', 'NOT_EQ', 'LIKE', 'STRING', 'FROM', 'NUMBER',
)

reserved = {
    'create': 'CREATE',
    'database': 'DATABASE',
    'use': 'USE',
    'table': 'TABLE',
    'insert': 'INSERT',
    'into': 'INTO',
    'update': 'UPDATE',
    'delete': 'DELETE',
    'set': 'SET',
    'values': 'VALUES',
    'where': 'WHERE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'null': 'NULL',
    'primary': 'PRIMARY',
    'key': 'KEY',
    'foreign': 'FOREIGN',
    'references': 'REFERENCES',
    'int': 'INT',
    'float': 'FLOAT',
    'varchar': 'VARCHAR',
    'text': 'TEXT',
    'datetime': 'DATETIME',
    'timestamp': 'TIMESTAMP',
    'date': 'DATE',
    'time': 'TIME',
    'unsigned': 'UNSIGNED',
    'auto_increment': 'AUTO_INCREMENT',
    'equals': 'EQUALS',
    'plus': 'PLUS',
    'minus': 'MINUS',
    'divide': 'DIVIDE',
    'mod': 'MOD',
    'greater': 'GREATER',
    'less': 'LESS',
    'greater_eq': 'GREATER_EQ',
    'less_eq': 'LESS_EQ',
    'not_eq': 'NOT_EQ',
    'like': 'LIKE',
    'from': 'FROM',
}


def t_NUMBER(t):
    r'\d+'
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    return t


t_COMMA = r','
t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ASTERISK = r'\*'
t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_DIVIDE = r'/'
t_MOD = r'%'
t_GREATER = r'>'
t_LESS = r'<'
t_GREATER_EQ = r'>='
t_LESS_EQ = r'<='
t_NOT_EQ = r'<>|!='
t_STRING = r'\'[^\']*\'|\"[^\"]*\"'

t_ignore = ' \t\n'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    global lexical_error_occurred
    error_message = f"Invalid character '{t.value[0]}' at position {t.lexpos}"
    lexical_errors.append(error_message)
    t.lexer.skip(1)
    lexical_error_occurred = True


lexer = lex.lex()


def p_start(p):
    '''start : create_database
             | use
             | create_table
             | insert_into
             | update
             | delete
    '''
    p[0] = p[1]


def p_create_database(p):
    '''create_database : CREATE DATABASE ID SEMICOLON
                       | CREATE DATABASE ID'''
    p[0] = {'action': 'create_database', 'name': p[3]}


def p_use(p):
    '''use : USE ID SEMICOLON
           | USE ID'''
    p[0] = {'action': 'use', 'name': p[2]}


def p_create_table(p):
    '''create_table : CREATE TABLE ID LPAREN column_definitions RPAREN SEMICOLON
                    | CREATE TABLE ID LPAREN column_definitions RPAREN'''
    p[0] = {'action': 'create_table', 'name': p[3], 'columns': p[5]}


def p_column_definitions(p):
    '''column_definitions : column_definition
                          | column_definitions COMMA column_definition
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_column_definition(p):
    'column_definition : ID data_type column_constraints'
    p[0] = {'name': p[1], 'data_type': p[2], 'constraints': p[3]}


def p_data_type(p):
    '''data_type : INT
                 | FLOAT
                 | VARCHAR LPAREN NUMBER RPAREN
                 | TEXT
                 | DATETIME
                 | TIMESTAMP
                 | DATE
                 | TIME
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f'{p[1]}({p[3]})'


def p_column_constraints(p):
    '''column_constraints : column_constraint
                          | column_constraints column_constraint
                          | empty
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    elif p[1] is None:
        p[0] = []
    else:
        p[0] = p[1] + [p[2]]


def p_column_constraint(p):
    '''column_constraint : NULL
                         | NOT NULL
                         | PRIMARY KEY
                         | FOREIGN KEY REFERENCES ID
                         | UNSIGNED
                         | AUTO_INCREMENT
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = f'{p[1]} {p[2]}'
    else:
        p[0] = f'{p[1]} {p[2]} {p[3]} {p[4]}'


def p_insert_into(p):
    '''insert_into : INSERT INTO ID LPAREN column_names RPAREN VALUES LPAREN values RPAREN SEMICOLON
                   | INSERT INTO ID LPAREN column_names RPAREN VALUES LPAREN values RPAREN'''
    p[0] = {'action': 'insert_into', 'table': p[3],
            'columns': p[5], 'values': p[9]}


def p_column_names(p):
    '''column_names : ID
                    | column_names COMMA ID
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_values(p):
    '''values : value
              | values COMMA value
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_value(p):
    '''value : INT
             | FLOAT
             | STRING
             | NULL
    '''
    p[0] = p[1]


def p_update(p):
    '''update : UPDATE ID SET assignments WHERE where_conditions SEMICOLON
              | UPDATE ID SET assignments WHERE where_conditions'''
    p[0] = {'action': 'update', 'table': p[2],
            'assignments': p[4], 'where_conditions': p[6]}


def p_assignments(p):
    '''assignments : assignment
                   | assignments COMMA assignment
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_assignment(p):
    'assignment : ID EQUALS value'
    p[0] = {'column': p[1], 'value': p[3]}


def p_delete(p):
    '''delete : DELETE FROM ID WHERE where_conditions SEMICOLON
              | DELETE FROM ID WHERE where_conditions'''
    p[0] = {'action': 'delete', 'table': p[3], 'where_conditions': p[5]}


def p_where_conditions(p):
    '''where_conditions : where_condition
                        | where_conditions AND where_condition
                        | where_conditions OR where_condition
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [{'operator': p[2], 'condition': p[3]}]


def p_where_condition(p):
    '''where_condition : ID comparison_operator value
                       | NOT where_condition
                       | LPAREN where_conditions RPAREN
    '''
    if len(p) == 2:
        p[0] = {'not': p[1], 'condition': p[2]}
    elif len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = {'column': p[1], 'operator': p[2], 'value': p[3]}


def p_comparison_operator(p):
    '''comparison_operator : EQUALS
                           | NOT_EQ
                           | GREATER
                           | LESS
                           | GREATER_EQ
                           | LESS_EQ
                           | LIKE
    '''
    p[0] = p[1]


def p_empty(p):
    'empty :'
    pass


def p_error(p):
    global syntax_error_occurred
    if p:
        error_message = f"Syntax error at token: {p.type}, value: {p.value}, position: {p.lineno}, {p.lexpos}"
        syntax_errors.append(error_message)
    else:
        syntax_errors.append(
            "Syntax error, the structure of your sentence is invalid.")
    syntax_error_occurred = True


parser = yacc.yacc()


def semantic_analyzer(p, connection):
    result = parser.parse(p, lexer=lexer)
    print(result)

    if result is None:
        return False, "Error: Parsing error detected"

    action = result['action']
    message = ""

    if action == 'create_database':
        success = not check_database_exists(result['name'], connection)
        message = "Database created successfully" if success else "Error: Database already exists"
    elif action == 'use':
        success = check_database_exists(result['name'], connection)
        message = "Using database" if success else "Error: Database does not exist"
    elif action == 'create_table':
        success = check_database_exists(get_current_database(
            connection), connection) and not check_table_exists(result['name'], connection)
        message = "Table created successfully" if success else "Error: Table already exists or database does not exist"
    elif action == 'insert_into':
        success = check_database_exists(get_current_database(
            connection), connection) and check_table_exists(result['table'], connection)
        message = "Insert operation successful" if success else "Error: Table or database does not exist"
    elif action == 'update':
        success = check_database_exists(get_current_database(
            connection), connection) and check_table_exists(result['table'], connection)
        message = "Update operation successful" if success else "Error: Table or database does not exist"
    elif action == 'delete':
        success = check_database_exists(get_current_database(
            connection), connection) and check_table_exists(result['table'], connection)
        message = "Delete operation successful" if success else "Error: Table or database does not exist"
    else:
        return False, "Error: Invalid action"

    return success, message


def check_database_exists(database_name, connection):
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    cursor.close()

    return any(database_name in db for db in databases)


def get_current_database(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT DATABASE();")
    current_database = cursor.fetchone()
    cursor.close()

    return current_database[0] if current_database else None


def check_table_exists(table_name, connection):
    current_database = get_current_database(connection)
    if not current_database:
        return False

    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES IN {current_database};")
    tables = cursor.fetchall()
    cursor.close()

    return any(table_name in table for table in tables)


def run_lexical_analyzer(query):
    lexer.input(query)
    tokens = []
    for token in lexer:
        tokens.append(token)

    error_occurred = bool(lexical_errors)
    result_string = "Tokens:\n" + "\n".join(str(token) for token in tokens)
    if error_occurred:
        result_string += "\n\nLexical Errors:\n" + "\n".join(lexical_errors)

    lexical_errors.clear()
    return result_string, error_occurred


def run_syntax_analyzer(query):
    syntax_result = parser.parse(query, lexer=lexer)

    error_occurred = bool(syntax_errors)
    result_string = "AST:\n" + str(syntax_result)
    if error_occurred:
        result_string += "\n\nSyntax Errors:\n" + "\n".join(syntax_errors)

    syntax_errors.clear()
    return result_string, error_occurred


def run_semantic_analyzer(connection, query):
    result, text = semantic_analyzer(query, connection)
    error_occurred = not result
    result_string = "Semantic Result: " + \
        ("Valid - " if result else "Invalid - ") + text
    return result_string, error_occurred
