from typing import Any, Collection, Dict, Tuple, Union

import numpy as np
import pandas as pd
import scipy.stats as ss
from scipy.linalg import LinAlgError


def is_collection(obj: Any) -> bool:
    return isinstance(obj, tuple) or isinstance(obj, list)


def calc_pvalue(nulldist: Collection[float],
                stat: float,
                how: str = 'right') -> float:
    if len(nulldist) < 2:
        raise ValueError('`nulldist` must have multiple elements.')
    if how not in ('right', 'left'):
        raise ValueError("how is not one of 'left', 'right'")
    try:
        kde = ss.gaussian_kde(nulldist)
        if how == 'right':
            pvalue = kde.integrate_box_1d(stat, np.inf)
        else:
            pvalue = kde.integrate_box_1d(np.NINF, stat)
            
    except LinAlgError:
        mean_value = nulldist.mean()
        if stat < mean_value:
            if how == 'right':
                pvalue = 1
            else:
                pvalue = 0
        else:
            if how == 'right':
                pvalue = 0
            else:
                pvalue = 1
    return pvalue


def parse_spaces(present_subspaces: Collection[str],
                 spaces: Collection[str] = None,
                 subspaces: Collection[str] = None,
                 whole: bool = True) -> Tuple[Tuple[str], Dict[str, Tuple[str]]]:
    """
    subspaces:
        If list, then leave untouched. Or check that subspaces match chromosomes or other grouping variable.
        If None, use chromosome names.
    spaces:
        If list, must be list of names of subspaces. Check consistency of subspace names!
        If dict, must be mapping of space name to the collection of subspaces names. Check consistency of subspace names!
        Other formats are not acceptable.
    """
    if subspaces is None:
        subspaces = tuple(present_subspaces)
    elif is_collection(subspaces):
        extra_subspaces = set(subspaces) - set(present_subspaces)
        if len(extra_subspaces) > 0:
            raise ValueError(f"`subspaces` contains the following extra items: {extra_subspaces}.")
    else:
        raise ValueError("`subspaces` is not an iterable nor None.")
    
    if spaces is None:
        spaces = {subspace: (subspace, ) for subspace in subspaces}
    elif is_collection(spaces):
        extra_subspaces = set(spaces) - set(subspaces)
        if len(extra_subspaces) > 0:
            raise ValueError(f"`spaces` contains the following extra items: {extra_subspaces}.")
        spaces = {subspace: (subspace, ) for subspace in spaces}
    elif isinstance(spaces, dict):
        for space_name, space_subspaces in spaces.items():
            extra_subspaces = set(space_subspaces) - set(subspaces)
            if len(extra_subspaces) > 0:
                raise ValueError(f"`spaces` contains the following extra items: {extra_subspaces} under the key {space_name}.")
        spaces = {space_name: tuple(space_subspaces) for space_name, space_subspaces in spaces.items()}
    else:
        raise ValueError(f"`spaces` is not an iterable, dict or None.")
    if whole:
        spaces['whole'] = subspaces
    return subspaces, spaces


def process_result(result_df: pd.DataFrame, output: str = 'full', simple_cols: Union[Collection, None] = None) -> pd.DataFrame:
    if output == 'full':
        return result_df
    elif output == 'simple':
        if simple_cols is None:
            raise ValueError("Supply simple_cols in case `output`='simple'.")

        inconsistent_cols = [col for col in simple_cols if col not in result_df.columns]
        if len(inconsistent_cols) > 0:
            raise ValueError(f"`simple_cols` contains columns that are not in `result_df`: {simple_cols}.")

        return result_df.loc[:, simple_cols]
    else:
        raise ValueError('`output` must be one of "full", "simple".')
