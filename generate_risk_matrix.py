#!/usr/bin/env python3

import itertools
import re
from rdflib.term import Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, SKOS
from rdflib import Namespace, Graph
DPV = Namespace('https://w3id.org/dpv#')
RISK = Namespace('https://w3id.org/dpv/risk#')
DPV_SKOS = Namespace('https://w3id.org/dpv/dpv-skos#')
RISK_SKOS = Namespace('https://w3id.org/dpv/risk/skos#')
DPV_OWL = Namespace('https://w3id.org/dpv/dpv-owl#')
RISK_OWL = Namespace('https://w3id.org/dpv/risk/owl#')

DPV_Serialisations = (
    ('', Graph(), DPV, RISK),
    ('-skos', Graph(), DPV_SKOS, RISK_SKOS),
    ('-owl', Graph(), DPV_OWL, RISK_OWL),
)

import itertools

def generate_permutations(max, min=1, size=None):
    '''generate and return combinations from min(1) to max of size each'''
    if size is None:
        size = max
    data = tuple(n for n in range(min, max+1))
    # print("range n", data)
    data = tuple(itertools.product(data,repeat=2))
    # print("permute", data)
    data = sorted(data, key=lambda x:x[0]*x[1])
    # print("sorted", data)
    data = [data[n:n+size] for n in range(0,len(data),size)]
    return data


def select_labels(n):
    '''Select n middle labels from risk labels'''
    LEVELS = ('ExtremelyLow', 'VeryLow', 'Low', 
        'Moderate', 
        'High', 'VeryHigh', 'ExtremelyHigh', )
    # We need n middle labels from the set
    # e.g. for 3, it should be from index 2 to 4
    # e.g. for 5, it should be from index 1 to 5
    # e.g. for 7, it should be from index 0 to 6
    # NOTE: highest index of LEVELS is len() - 1
    # By dividing the highest index with n, we get the starting position
    # Then we take a slice of n elements starting from mid
    mid = (len(LEVELS)-1)//n
    return LEVELS[mid:mid+n]

def generate_nodes(n):
    '''Generate risk matrix of nxn with labels'''
    labels = select_labels(n)
    data = tuple(generate_permutations(n))
    # print(data)
    for risk_level, node_list in enumerate(data):
        for row, col in node_list:
            risk_score = (row * col) / (n * n)
            risk_label = labels[risk_level]
            pref_label = ' '.join(x for x in re.split(r'([A-Z][a-z]*)', risk_label) if x)
            pref_label = f'{pref_label} Risk (S:{col} L:{row})'
            description = f'Node in a {n}x{n} Risk Matrix with Risk Severity: {labels[col-1]}; Likelihood: {labels[row-1]}; and Risk Level: {risk_label}'

            # Output for importing into spreadsheets
            # print(f'risk:RM{n}x{n}S{col}L{row},{pref_label},{description},risk:RiskMatrix{n}x{n},a,"{risk_score:.2f},xsd:decimal"')

            # Output for importing into/as RDF

            # General definitions and descriptions will get added via spreadsheet
            # Additional properties: risk severity, likelihood, level
            for _, graph, nm_dpv, nm_risk in DPV_Serialisations:
                node = nm_risk[f'RM{n}x{n}S{col}L{row}']
                graph.add((node, nm_dpv['hasRiskLevel'], nm_risk[f'{risk_label}Risk']))
                graph.add((node, nm_dpv['hasSeverity'], nm_risk[f'{labels[col-1]}Severity']))
                graph.add((node, nm_dpv['hasLikelihood'], nm_risk[f'{labels[row-1]}Likelihood']))

generate_nodes(3)
generate_nodes(5)
generate_nodes(7)

for suffix, graph, *_ in DPV_Serialisations:
    graph.serialize(f'risk-matrix-nodes{suffix}.ttl', format='ttl')

