import sqlite3
import sqlalchemy
import unittest
import inspect
import marshmallow
import json
from bs4 import BeautifulSoup


class DataBaseTestsMixin:
    """
    Includes methods for Tests with DB Models and Queries
    """

    STRING = "String"
    INTEGER = "Integer"
    DATE = "Date"

    def get_query_info(self, query):
        from_sql_checker = self._sql_checker(query)
        from_cursor = self._get_cursor_info(query)
        return {"query_info": from_sql_checker, "cursor_info": from_cursor}

    def _get_db_cursor(self, query):
        con = sqlite3.connect("../netflix.db")
        cur = con.cursor()
        cur.execute(query)
        return cur

    def _get_cursor_info(self, query):
        """
        Creates dict with info from SQL query string
        """
        cur = self._get_db_cursor(query)
        return self.get_cursor_info(cur)

    def get_cursor_info(self, cursor):
        """
        Returns dict with info about current cursor with query
        """
        columns = cursor.description
        columns_len = len(columns)
        names_of_columns = []
        query_result = cursor.fetchall()
        rows_count = len(query_result)
        for name in columns:
            names_of_columns.append(name[0])
        return {
            "columns": names_of_columns,
            "columns_count": columns_len,
            "query_result": query_result,
            "rows_count": rows_count,
        }

    def _sql_checker(self, query: str):
        """
        returns blocks with SQL keyword
        and keyword value
        """
        query = query.lower()
        keywords = self._get_key_words(query)
        select_ind = query.find("select ")
        from_ind = query.find("from ")
        where_ind = query.find("where ")
        and_ind = query.find(" and ")
        select_block = query[select_ind:from_ind]
        from_block = query[from_ind:where_ind]
        where_block = query[where_ind:]
        and_block = None
        if and_ind:
            where_block = query[where_ind:and_ind]
            and_block = query[and_ind:]
        blocks = {
            "??????????????": select_block,
            "??????????????": from_block,
            "??????????????": where_block,
            "?????? ??????????????": and_block,
        }
        for key, value in blocks.items():
            blocks[key] = self._cleaner(blocks[key])
        blocks["keywords"] = keywords
        return blocks

    def _cleaner(self, lst):
        lst = lst.split(" ")
        key_words = ["select", "from", "where", "like", "distinct", "and", ""]
        for value in key_words:
            if value in lst:
                lst.remove(value)
        for value in lst:
            if "," in value:
                devided_value = value.split(",")
                try:
                    devided_value.remove("")
                except:  # noqa: E722
                    pass
                lst.remove(value)
                lst += devided_value
        return lst

    def _get_key_words(self, query):
        keywords = [
            "select",
            "from",
            "where",
            "like",
            "group by",
            "distinct",
            "limit",
            "order by",
        ]
        lst = []
        for keyword in keywords:
            if keyword in query:
                lst.append(keyword)
        return lst

    def field_name_checker(self, student_columns, author_columns):
        self.assertEqual(
            student_columns,
            author_columns,
            (
                r"%@??????????????????, ?????? ?????????????????? ???????????????????? "
                "???????? ???????????? Author. "
                f"???? ?????????????? {student_columns}, ?????????? "
                f"?????? ???????????????????? {author_columns}"
            ),
        )

    def field_type_checker(
        self, module=None, model_name: str = None, type_name: str = None, fields=None
    ):  # field.name (field.name, field.name)
        correct_field_type = getattr(sqlalchemy, type_name)
        model = getattr(module, model_name)
        fields = (getattr(model, field_name) for field_name in fields)
        for field in fields:
            name = field.property.key
            self.assertTrue(
                isinstance(field.type, correct_field_type),
                f"%@?????????????????? ?????????? ???? ???????? {name} ???????????? {model_name} "
                f"?????? {type_name}",
            )


class ResponseTestsMixin:
    def _required_args_checker(self, *args, **kwargs):
        """
        for usage in module.
        Checks that all arguments in functions is defined
        required arguments can be added to this func as string
        and as list
        if arg is list checks that any of list element is in required
        """
        for test_arg in args:  # required args
            if isinstance(test_arg, list):
                if not {*test_arg}.intersection({*kwargs.keys()}):
                    raise ValueError(
                        f"key argument '{test_arg}' must be defined."
                        f"look at testMethod= here:{self.__eq__}"
                    )
            elif not kwargs.get(test_arg):
                raise ValueError(
                    f"key argument '{test_arg}' must be defined."
                    f"look at testMethod= here:{self.__eq__}"
                )

    def check_status_code_jsonify_and_expected(self: unittest.TestCase, **kwargs):
        """
        compex check that testing:
        - response status code
        - is_json type
        - optional expected_obj (if arg expected is not None)
        - optional answer_obj - check what's returned
        """
        code: list = kwargs.get("code")
        url: str = kwargs.get("url")
        response = kwargs.get("response") or kwargs.get("student_response")
        expected: object = kwargs.get("expected")
        method: str = kwargs.get("method")
        answer = kwargs.get("answer")
        additional_text_on_code_test = kwargs.get("text")
        if additional_text_on_code_test is None:
            additional_text_on_code_test = ""
        self._required_args_checker(
            "url", ["response", "student_response"], "method", **kwargs
        )
        if code:
            self.assertIn(
                response.status_code,
                code,
                (
                    f"%@??????????????????, ?????? {additional_text_on_code_test} ??????????"
                    f" {url} ????????????????, ?? {method}-???????????? "
                    f"???????????????????? ?????? {code}"
                ),
            )
        else:
            self.assertNotIn(
                response.status_code,
                [404, 500],
                (
                    f"%@??????????????, ???? ?????????????? ?????????????????? ????????????."
                    f"??????????????????, ?????? ?????????? {url} ????????????????."
                ),
            )
            self.assertNotIn(
                response.status_code,
                [405],
                (
                    f"%@??????????????????, ?????? ?????? {method}-?????????????? ???? ?????????? "
                    f"{url} ???????????????????????? ???????????????????? http-??????????"
                ),
            )
        # self.assertTrue(  # json_fix
        #     response.is_json,
        #     (f"%@??????????????????, ?????? ?? ?????????? ???? {method}-???????????? "
        #      f"???? ???????????? {url} ?????????????????? ???????????? ?? ?????????????? json."
        #      " ???????????????????? ???????????????????????? ?????????????? jsonify ???? ???????????????????? flask."))
        if expected:
            expected_json = response.json or json.loads(response.data)  # json_fix
            self.assertFalse(
                expected_json == {},
                (
                    f"%@?????????????????? ?????? ?? ?????????? ???? {method}-???????????? ???? ???????????? {url} "
                    f"???????????????????????? ???? ???????????? ??????????"
                ),
            )
            self.assertTrue(
                isinstance(expected_json, expected),
                f"%@?????????????????? ?????? ?? ?????????? ???? {method}-???????????? ???? ???????????? {url}"
                f" ???????????????????????? {expected}",
            )
        if answer:
            answer_json = response.json or json.loads(response.data)  #
            self.assertTrue(
                answer == answer_json,
                f"%@??????????????????, ?????? ?? ???????????? ???? {method}-???????????? ???? ???????????? {url}"
                f" ???????????????????????? ???????????????????? ??????????",
            )
        return response

    def compare_result_fields_with_author_solution(self, many=False, **kwargs):
        """
        Compare student response.data with author sulution.
        - Note:* (response.data must be not None)
        - Use `many=true` for inspecting response.data which contains list
        """
        self._required_args_checker(
            "method", "url", "student_response", "author_response", **kwargs
        )
        method = kwargs.get("method")
        url = kwargs.get("url")
        student_response = kwargs.get("student_response")
        student_response = student_response.json or json.loads(
            student_response.data
        )  # json_fix
        author_response = kwargs.get("author_response").json
        if author_response == "":
            raise ValueError(
                "In this Case response returns None"
                " so no one field can be checked, "
                "delete this function from testCase"
            )
        if many:
            author_data = author_response[0]
            data = student_response[0]
        else:
            author_data = author_response
            data = student_response
        if (
            author_data == data == []  # Ec???? ?????????? ?????????? ???????????? ??????????
            or author_data == data == {}
        ):  # ???????? ???? ??????????????????
            return  # ?????????????????????? ???????????????? ??????????
        if not many and isinstance(author_response, list):
            raise ValueError(
                "check `response.data` maybe many" " arg must have True value"
            )
        if not many:
            self.assertFalse(
                isinstance(student_response, list),
                (
                    f"%@??????????????????, ?????? ?????? {method}-?????????????? ???? ?????????? {url} "
                    f"?????????? ???????????????????????? {dict}"
                ),
            )
        student_keys = data.keys()
        for key, value in author_data.items():
            self.assertIn(
                key,
                student_keys,
                f"%@ ??????????????????, ?????? ?????????? ???? {method}-???????????? ???? ???????????? {url} "
                f"???????????????? ???????? {key}",
            )
            self.assertEqual(
                value,
                data[key],
                f"%@ ??????????????????, ?????? ?????????? ???? {method}-???????????? ???? ???????????? {url} "
                f"?? ???????? {key} ???????????????????? ???????????????????? ????????????????",
            )


class SchemaTestsMixin(ResponseTestsMixin):
    def schema_is_valid(self, **kwargs):
        """
        Simple test that Schema is valid:
        - Schema exists
        - Schema is class
        - Schema is class of marshmallow.Schema
        """
        self._required_args_checker("main", "schema_name", **kwargs)
        main = kwargs.get("main")
        schema_name = kwargs.get("schema_name")
        self.assertTrue(
            hasattr(main, schema_name),
            f"%@??????????????????, ?????? ?????????? {schema_name} ??????????????????" " ?? ????????????",
        )
        student_schema = getattr(main, schema_name)
        self.assertTrue(
            inspect.isclass(student_schema),
            f"%@??????????????????, ?????? {student_schema} ?????? ??????????",
        )
        self.assertTrue(
            issubclass(student_schema, marshmallow.Schema),
            (
                "%@??????????????????, ?????????????????? ???? ???????????? ???????????????????????? ?????????? ?? "
                f"???????????? {student_schema}"
            ),
        )

    def compare_schema_with_author_solution(self, **kwargs):
        """
        Compare field names and types
        between author and student solutions
        """
        self._required_args_checker("student_schema", "author_schema", **kwargs)
        author_schema = kwargs.get("author_schema")
        author_fields_dict = author_schema._declared_fields
        student_schema = kwargs.get("student_schema")
        student_fields_dict = student_schema._declared_fields
        student_fields = student_fields_dict.keys()
        # compare fields and their types
        for field, type in author_fields_dict.items():
            self.assertIn(
                field,
                student_fields,
                (f"%@??????????????????, ?????? ?????????? {student_schema}" f" ???????????????? ???????? {field}"),
            )
            self.assertTrue(
                isinstance(student_fields_dict[field], type.__class__),
                f"%@??????????????????, ?????? ?????????????????? ?????????????????? ?????? "
                f"?? ???????? {field} ?????????? {student_schema}."
                f"???????????????????? ???????????????????????? {type.__class__}",
            )


class TemplateMixin(ResponseTestsMixin):
    def check_code_and_get_soup(self, url, code):
        response = self.app.get(url)
        self.assertTrue(
            response.status_code == code,
            f"%@??????????????????, ?????? ?????????? 127.0.0.1:5000'{url}' ???????????????? ???? ????????????????",
        )

        soup = BeautifulSoup(response.get_data(True), "html.parser")
        return