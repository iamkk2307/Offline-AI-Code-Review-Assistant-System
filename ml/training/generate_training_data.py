"""
Synthetic Training Data Generator
====================================
Generates realistic synthetic feature vectors with ground-truth labels
for training all 6 ML models. No internet connection or external datasets required.

The synthetic data is created by:
1. Defining code quality archetypes (excellent, good, average, poor, terrible)
2. Sampling features from realistic distributions for each archetype
3. Assigning ground truth labels based on the archetype + noise

This approach produces ~10,000 training samples that capture the real
relationships between code metrics and quality outcomes.
"""

import numpy as np
import pandas as pd
from dataclasses import asdict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from parsers.base_plugin import Features

RANDOM_SEED = 42
N_SAMPLES = 10000

FEATURE_NAMES = Features.feature_names()


def _sample_features(rng: np.random.Generator, archetype: str) -> dict:
    """
    Sample a plausible feature vector for a given code quality archetype.
    
    Archetypes: excellent, good, average, poor, terrible
    """
    presets = {
        'excellent': dict(
            loc_range=(20, 200),
            comment_ratio_range=(0.15, 0.35),
            function_count_range=(3, 15),
            cyclomatic_range=(1.0, 8.0),
            magic_numbers_range=(0, 2),
            nested_loops_range=(0, 1),
            eval_usage_range=(0, 0),
            hardcoded_creds_range=(0, 0),
            sql_inj_range=(0, 0),
            maintainability_range=(75.0, 100.0),
            naming_violations_range=(0, 2),
            duplicate_ratio_range=(0.0, 0.05),
            long_methods_range=(0, 1),
            exception_handling_range=(1, 5),
        ),
        'good': dict(
            loc_range=(50, 500),
            comment_ratio_range=(0.10, 0.25),
            function_count_range=(5, 25),
            cyclomatic_range=(3.0, 12.0),
            magic_numbers_range=(1, 5),
            nested_loops_range=(0, 2),
            eval_usage_range=(0, 0),
            hardcoded_creds_range=(0, 0),
            sql_inj_range=(0, 1),
            maintainability_range=(55.0, 80.0),
            naming_violations_range=(0, 5),
            duplicate_ratio_range=(0.02, 0.10),
            long_methods_range=(0, 3),
            exception_handling_range=(1, 8),
        ),
        'average': dict(
            loc_range=(100, 1000),
            comment_ratio_range=(0.05, 0.15),
            function_count_range=(5, 40),
            cyclomatic_range=(8.0, 20.0),
            magic_numbers_range=(3, 15),
            nested_loops_range=(1, 4),
            eval_usage_range=(0, 1),
            hardcoded_creds_range=(0, 1),
            sql_inj_range=(0, 2),
            maintainability_range=(35.0, 60.0),
            naming_violations_range=(3, 15),
            duplicate_ratio_range=(0.05, 0.20),
            long_methods_range=(1, 8),
            exception_handling_range=(0, 5),
        ),
        'poor': dict(
            loc_range=(200, 2000),
            comment_ratio_range=(0.0, 0.08),
            function_count_range=(3, 60),
            cyclomatic_range=(15.0, 40.0),
            magic_numbers_range=(10, 40),
            nested_loops_range=(2, 8),
            eval_usage_range=(0, 3),
            hardcoded_creds_range=(0, 3),
            sql_inj_range=(1, 5),
            maintainability_range=(15.0, 40.0),
            naming_violations_range=(10, 30),
            duplicate_ratio_range=(0.10, 0.35),
            long_methods_range=(3, 15),
            exception_handling_range=(0, 3),
        ),
        'terrible': dict(
            loc_range=(500, 5000),
            comment_ratio_range=(0.0, 0.03),
            function_count_range=(1, 5),
            cyclomatic_range=(25.0, 80.0),
            magic_numbers_range=(20, 100),
            nested_loops_range=(3, 15),
            eval_usage_range=(1, 10),
            hardcoded_creds_range=(1, 10),
            sql_inj_range=(2, 15),
            maintainability_range=(0.0, 20.0),
            naming_violations_range=(20, 80),
            duplicate_ratio_range=(0.20, 0.60),
            long_methods_range=(5, 30),
            exception_handling_range=(0, 2),
        ),
    }
    
    p = presets[archetype]
    
    def r(key, as_int=False):
        lo, hi = p[key + '_range']
        v = rng.uniform(lo, hi)
        return int(v) if as_int else float(v)
    
    loc          = r('loc', as_int=True)
    comment_ratio = r('comment_ratio')
    comment_lines = int(loc * comment_ratio)
    blank_lines   = int(loc * rng.uniform(0.05, 0.20))
    sloc          = max(1, loc - blank_lines - comment_lines)
    func_count    = r('function_count', as_int=True)
    cyclomatic    = r('cyclomatic')
    maintainability = r('maintainability')
    
    halstead_volume = float(sloc * np.log2(max(cyclomatic * 2, 2)))
    halstead_difficulty = float(cyclomatic / 2)
    halstead_effort = halstead_volume * halstead_difficulty
    halstead_length = float(sloc * 2)
    
    avg_func_len = rng.uniform(loc / max(func_count, 1) * 0.5, loc / max(func_count, 1) * 1.5)
    
    features = {
        'loc': loc,
        'sloc': sloc,
        'blank_lines': blank_lines,
        'comment_lines': comment_lines,
        'comment_ratio': comment_ratio,
        'function_count': func_count,
        'class_count': r('function_count', as_int=True) // 4,
        'method_count': func_count,
        'import_count': int(rng.uniform(1, 30)),
        'global_variables': int(rng.uniform(0, 10)),
        'constants': int(rng.uniform(0, 15)),
        'parameter_count': func_count * int(rng.uniform(1, 5)),
        'return_statements': func_count,
        'exception_handling': r('exception_handling', as_int=True),
        'loop_count': int(rng.uniform(0, cyclomatic * 0.5)),
        'nested_loops': r('nested_loops', as_int=True),
        'conditional_count': int(cyclomatic * 0.7),
        'recursion_count': int(rng.uniform(0, 3)),
        'switch_statements': int(rng.uniform(0, 5)),
        'cyclomatic_complexity': cyclomatic,
        'halstead_length': halstead_length,
        'halstead_volume': halstead_volume,
        'halstead_difficulty': halstead_difficulty,
        'halstead_effort': halstead_effort,
        'maintainability_index': maintainability,
        'max_nesting_depth': r('nested_loops', as_int=True) + 1,
        'avg_function_length': float(avg_func_len),
        'avg_class_size': float(rng.uniform(3, 20)),
        'avg_identifier_length': float(rng.uniform(4.0, 12.0)),
        'naming_violations': r('naming_violations', as_int=True),
        'duplicate_lines': int(sloc * r('duplicate_ratio')),
        'duplicate_ratio': r('duplicate_ratio'),
        'dead_code_lines': int(rng.uniform(0, sloc * 0.15)),
        'todo_count': r('magic_numbers', as_int=True) // 3,
        'fixme_count': r('magic_numbers', as_int=True) // 5,
        'long_methods': r('long_methods', as_int=True),
        'large_classes': int(rng.uniform(0, 3)),
        'long_parameter_lists': int(rng.uniform(0, 5)),
        'magic_numbers': r('magic_numbers', as_int=True),
        'hardcoded_credentials': r('hardcoded_creds', as_int=True),
        'sql_queries': r('sql_inj', as_int=True),
        'shell_executions': int(rng.uniform(0, r('eval_usage'))),
        'eval_usage': r('eval_usage', as_int=True),
        'file_operations': int(rng.uniform(0, 10)),
        'network_operations': int(rng.uniform(0, 5)),
        'memory_allocations': int(rng.uniform(0, 20)),
        'nested_iterations': r('nested_loops', as_int=True),
        'redundant_calculations': int(rng.uniform(0, 10)),
        'object_creations': int(rng.uniform(0, 30)),
        'collection_usage': int(rng.uniform(0, 20)),
        'expensive_operations': int(rng.uniform(0, 10)),
    }
    
    return features


def _archetype_labels(archetype: str, rng: np.random.Generator) -> dict:
    """Assign ground truth labels for each ML target based on archetype."""
    noise = rng.normal(0, 0.05)
    
    base_quality = {
        'excellent': 88.0,
        'good':      70.0,
        'average':   50.0,
        'poor':      28.0,
        'terrible':  12.0,
    }[archetype]
    
    base_security = {
        'excellent': 95.0,
        'good':      78.0,
        'average':   55.0,
        'poor':      30.0,
        'terrible':  10.0,
    }[archetype]
    
    base_maintainability = {
        'excellent': 85.0,
        'good':      68.0,
        'average':   48.0,
        'poor':      25.0,
        'terrible':  8.0,
    }[archetype]
    
    base_readability = {
        'excellent': 90.0,
        'good':      72.0,
        'average':   52.0,
        'poor':      28.0,
        'terrible':  10.0,
    }[archetype]
    
    bug_prob = {
        'excellent': 0.05,
        'good':      0.15,
        'average':   0.35,
        'poor':      0.65,
        'terrible':  0.90,
    }[archetype]
    
    security_risk = {
        'excellent': 0.02,
        'good':      0.10,
        'average':   0.30,
        'poor':      0.65,
        'terrible':  0.92,
    }[archetype]
    
    severity_map = {
        'excellent': 'INFO',
        'good':      'LOW',
        'average':   'MEDIUM',
        'poor':      'HIGH',
        'terrible':  'CRITICAL',
    }
    
    return {
        'quality_score':        max(0, min(100, base_quality + rng.normal(0, 5))),
        'security_score':       max(0, min(100, base_security + rng.normal(0, 5))),
        'maintainability_score': max(0, min(100, base_maintainability + rng.normal(0, 5))),
        'readability_score':    max(0, min(100, base_readability + rng.normal(0, 5))),
        'bug_probability':      max(0.0, min(1.0, bug_prob + rng.normal(0, 0.05))),
        'security_risk':        max(0.0, min(1.0, security_risk + rng.normal(0, 0.05))),
        'has_bug':              int(bug_prob + rng.normal(0, 0.1) > 0.5),
        'has_security_risk':    int(security_risk + rng.normal(0, 0.1) > 0.5),
        'severity_label':       severity_map[archetype],
    }


def generate_training_data(n_samples: int = N_SAMPLES) -> pd.DataFrame:
    """
    Generate a complete synthetic training dataset.
    
    Args:
        n_samples: Total number of training examples to generate.
    
    Returns:
        DataFrame with feature columns + target label columns.
    """
    rng = np.random.default_rng(RANDOM_SEED)
    
    archetypes = ['excellent', 'good', 'average', 'poor', 'terrible']
    weights    = [0.15, 0.25, 0.30, 0.20, 0.10]  # Realistic distribution
    
    records = []
    for _ in range(n_samples):
        archetype = rng.choice(archetypes, p=weights)
        features  = _sample_features(rng, archetype)
        labels    = _archetype_labels(archetype, rng)
        records.append({**features, **labels, 'archetype': archetype})
    
    df = pd.DataFrame(records)
    print(f"Generated {len(df)} training samples")
    print(f"Archetype distribution:\n{df['archetype'].value_counts()}")
    print(f"Feature columns: {len(FEATURE_NAMES)}")
    return df


if __name__ == '__main__':
    df = generate_training_data()
    output_path = os.path.join(os.path.dirname(__file__), 'training_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Saved training data to: {output_path}")
