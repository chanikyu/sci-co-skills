"""aggregate.py — collapse ARG abundances to drug classes / resistance mechanisms via a mapping
(ARO / CARD categories). Pure Python — testable."""
import pandas as pd


def to_drug_class(arg_table, arg_to_class):
    """arg_table: ARG × samples. arg_to_class: {ARG: drug_class}. Returns drug_class × samples (summed).
    ARGs without a mapping go to 'unclassified' (reported, not dropped)."""
    cls = pd.Series(arg_to_class).reindex(arg_table.index).fillna("unclassified")
    return arg_table.groupby(cls).sum()


def class_summary(drug_class_table):
    """Total abundance per drug class across samples — which resistance classes dominate the resistome."""
    return drug_class_table.sum(axis=1).sort_values(ascending=False).rename("total_abundance").to_frame()


def unclassified_count(arg_table, arg_to_class):
    """How many ARGs had no drug-class mapping (a large bucket means the mapping is stale — report it)."""
    cls = pd.Series(arg_to_class).reindex(arg_table.index).fillna("unclassified")
    return int((cls == "unclassified").sum())
