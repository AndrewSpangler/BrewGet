from flask import render_template

def create_table(
    name:str,
    columns:list[str] = [],
    rows:list[str] = []
) -> str:
    """Creates table and associated script html"""
    return render_template(
        "datatables/table.html",
        table_name = name,
        columns = columns,
        rows = rows
    )

def create_table_page(
    name:str,
    columns:list[str] = [],
    rows:list[str] = [],
    title:str = None,
    header_elements:list[str] = None,
    body_elements:list[str] = None
) -> str:
    """
    Creates a table page from a list of columns and rows
    """
    return render_template(
        "datatables/table_page.html",
        title = title or name,
        table = create_table(
            name,
            columns = columns,
            rows = rows
        ),
        header_elements = header_elements,
        body_elements = body_elements
    )

def create_table_page_dict(
    name:str,
    data:dict[str:list[str]] = {},
    title:str = None,
    header_elements:list[str] = None,
    body_elements:list[str] = None
) -> str:
    """
    Creates a table page from a dict of lists
    Assumes keys are column names and lists are columns
    """
    columns = [k for k in data.keys()]
    rows = [
        (data[k][i] for k in data)
        for i in 
        range(len(data[columns[0]]))
    ]
    return create_table_page(
        name,
        columns = columns,
        rows = rows,
        title = title,
        header_elements = header_elements,
        body_elements = body_elements
    )

def create_table_page_list(
    name:str,
    data:list[list[str]],
    title:str = None,
    header_elements:list[str]=None,
    body_elements:list[str] = None
) -> str:
    """
    Creates a table page from a list of lists
    Assumes the first row is table headers
    """
    if not data: data = ([], [])
    return create_table_page(
        name,
        columns = data[0],
        rows = data[1:],
        title = title,
        header_elements = header_elements,
        body_elements = body_elements
    )