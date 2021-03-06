#!/usr/bin/env/python3
"""
Project moved to git@github.com:archgroove/json2ddl.git

Convert json to DDL.
Everything in the json is assumed to be a struct, an array or a string.
Arrays are assumed to contain items all of the same schema.
Treats items in lists as string if they are not the same type.
"""
import json
import argparse

DEFAULT_TYPE = 'string'

def get_keystring(key):
    """
    If a key name starts with an underscore the name must be escaped with
    backticks for Athena to parse it.
    """
    if str(key).startswith('_'):
        return '`{}`:'.format(key)
    return '{}:'.format(key)

def helper_json_value_to_struct_entry(key, val):
    """
    If a key, val pair are nested inside another json field, this generates
    one entry in the list of struct fields generated by `json_value_to_struct`.
    One of those entries could be another struct generated by
    `json_value_to_struct` if there is another layer of nesting.
    """
    keystring = get_keystring(key)
    if isinstance(val, dict):
        string = keystring + json_value_to_struct(val)
    elif isinstance(val, list):
        string = keystring + 'array<' + get_list_type(val) + '>'
    else:
        string = keystring + DEFAULT_TYPE
    return string

def get_list_type(lst):
    """Assumes that all members of a list are the same type"""
    # If there is no element in the list assume the type is string
    try:
        first_element = lst[0]
    except IndexError:
        return DEFAULT_TYPE
    # TODO: check whether then elements are the same before trying to generated
    # the inner element type here, and possibly create a new column for each Type
    # in the list.
    if not all(isinstance(element, type(first_element)) for element in lst):
        return DEFAULT_TYPE
    # TODO if the elements are structs, check whether they all have the same schema
    if isinstance(first_element, dict):
        string = json_value_to_struct(first_element)
    elif isinstance(first_element, list):
        string = 'array<' + get_list_type(first_element) + '>'
    else:
        string = DEFAULT_TYPE
    return string

def json_value_to_struct(structkeyvals):
    """
    If a json field is a nested dict of other fields, this generates the ddl
    struct corresponding to those nested fields. It calls
    `helper_json_value_to_struct` to construct the either a `DEFAULT_TYPE entry
    or another struct. `helper_json_value_to_struct` calls this function again
    if it is another struct.

    Example: struct<field1:string, field2:string>
    Example: struct<field1:string, field2:struct<field3:string, field4:string>>
    """
    assert isinstance(structkeyvals, dict), 'structkeyvals must be a dict'
    string = 'struct<'
    ordered_dict_items = list(structkeyvals.items())
    for key, val in ordered_dict_items[:-1]:
        string += helper_json_value_to_struct_entry(key, val)
        string += ', '
    key, val = ordered_dict_items[-1]
    string += helper_json_value_to_struct_entry(key, val)
    string += '>'
    return string

def json_field_to_string(key, value):
    if isinstance(value, dict):
        return '`{}` {}'.format(key, json_value_to_struct(value))
    elif isinstance(value, list):
        return '`{}` '.format(key) + 'array<' + get_list_type(value) + '>'.format(key)
    return '`{}` string'.format(key)

def json2ddl(jsonfile, encoding=None):
    with open(jsonfile) as fp:
        if encoding == None:
            jsondata = json.load(fp)
        elif encoding.lower() in ['utf8', 'utf-8']:
            jsondata = json.load(fp, encoding='utf-8')
        elif encoding.lower() in ['ascii']:
            jsondata = json.load(fp)
        else:
            jsondata = json.load(fp, encoding=encoding)
    ddl = 'CREATE EXTERNAL TABLE `<table_name>`(\n'
    ordered_jsondata = list(jsondata.items())
    for key, val in ordered_jsondata[:-1]:
        ddl += json_field_to_string(key, val) + ',' + '\n'
    key, val = ordered_jsondata[-1]
    ddl += json_field_to_string(key, val) + '\n'
    ddl += ')'
    return ddl

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert JSON to a DDL schema")
    parser.add_argument('--encoding', help="Only 'utf-8' or 'ascii' is supported")
    parser.add_argument('jsonfile')
    args = parser.parse_args()
    encoding = args.encoding if args.encoding else None
    ddl = json2ddl(args.jsonfile, encoding)
    print('Formatted ddl:')
    print(ddl)
    print('\n')
    print('No newlines ddl:')
    print(' '.join(ddl.split('\n')))
