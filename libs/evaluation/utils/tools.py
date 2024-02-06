"""
Scripts for various utils
Created in 2023
@author: Forschungszentrum Jülich GmbH, Nico Röttcher
"""

import pandas as pd
import itertools


def check_type(
    name,
    value,
    allowed_None=False,
    allowed_types=None,
    str_int_to_list=False,
):
    """
    check the type of a varibale and raise error if type is not matched.
    :param name: str
        name of the variable, used for the error message
    :param value: Any
        value of the variable to be checked in type
    :param allowed_None: bool
        whether None type is allowed or not
    :param allowed_types: list of types
        list of allwoed types
    :param str_int_to_list: bool
        whether to transform variable of type str or int to a list
    :return: value
    """
    if allowed_types is None:
        allowed_types = []
    if allowed_None:
        if not (value is None or type(value) in allowed_types):
            raise ValueError(
                f"{name} must be None or of type: "
                + ", ".join([str(dtype) for dtype in allowed_types])
            )
    else:
        if not (type(value) in allowed_types):
            raise ValueError(
                f"{name} must be of type: "
                + ", ".join([str(dtype) for dtype in allowed_types])
            )
    if str_int_to_list and type(value) in [str, int]:
        if type(list()) not in allowed_types:
            raise Exception(
                f"{name} is transformed to list although not given in allowed_types."
            )
        value = list([value])
    return value


# pandas related tools
def singleindex_to_multiindex_list(index):
    """
    Takes pandas index or multiindex and transform it to list of tuples and the name of the index columns as list
    :param index: pandas.Index or pandas.MultiIndex
        pandas Index or MultiIndex
    :return: index, names
        index as list of tuples
        names as list
    """
    names = index.names
    if type(index) == pd.MultiIndex:
        index = index.tolist()
    else:
        index = [(val,) for val in index.tolist()]
    return index, names


def multiindex_from_product_indices(index1, index2):
    """
    Creates a pandas.MultiIndex from the product of two indices (index1, index2). These can be both Index or MultiIndex
    :param index1: pandas.Index or pandas.MultiIndex
        pandas Index or MultiIndex
    :param index2: pandas.Index or pandas.MultiIndex
        pandas Index or MultiIndex
    :return: pandas.MultiIndex
        product of both indices
    """
    index1, name1 = singleindex_to_multiindex_list(index1)
    index2, name2 = singleindex_to_multiindex_list(index2)

    print(index1, index2)
    product_index = list(itertools.product(index1, index2))
    print([row for row in product_index])
    # print(product_index[0])
    tuples = [sum(row, ()) for row in product_index]

    index = pd.MultiIndex.from_tuples(tuples, names=name1 + name2)

    return index
