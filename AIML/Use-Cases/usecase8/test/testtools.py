from src.tools.sql_tools import execute_sql

print(execute_sql.invoke(
    {"query": "SELECT * FROM users"}
))