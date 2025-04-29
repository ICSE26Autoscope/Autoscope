import os
from pathlib import Path
from shutil import rmtree



def normal_soot_sig_transfer(origin:str)->str:
    origin = origin.strip()

    if '(' not in origin or ')' not in origin:
        raise ValueError(f"Invalid method signature: {origin}")

    before_paren, param_str = origin.split('(', 1)
    param_str = param_str.rstrip(') ')

    tokens = before_paren.strip().split()
    if len(tokens) < 2:
        raise ValueError(f"Cannot parse return type and method name from: {before_paren}")

    return_type = tokens[0]
    method_name = tokens[1]

    param_list = [p.strip() for p in param_str.split(',') if p.strip()]
    formatted_params = ",".join(param_list)

    return f"{return_type} {method_name}({formatted_params})"
