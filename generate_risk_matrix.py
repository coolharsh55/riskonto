#!/usr/bin/env python3

import itertools
import re
from rdflib.term import Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, SKOS
from rdflib import Namespace, Graph
DPV = Namespace('https://w3id.org/dpv#')
RISK = Namespace('https://w3id.org/dpv/risk/matrix#')

graph = Graph()
graph.namespace_manager.bind('dpv', DPV)
graph.namespace_manager.bind('', RISK)

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
            node = RISK[f'RM{n}x{n}R{row}C{col}']
            graph.add((node, RDF.type, SKOS.Concept))
            risk_label = labels[risk_level]
            pref_label = ' '.join(x for x in re.split(r'([A-Z][a-z]*)', risk_label) if x)
            description = f'Node (row: {row} col: {col}) in {n}x{n} risk matrix with Risk Level: {risk_label} Severity: {labels[col-1]} and Likelihood: {labels[row-1]}'
            graph.add((node, SKOS.prefLabel, 
                Literal(f'{pref_label} Risk', lang='en')))
            graph.add((node, SKOS.definition,
                Literal(description, lang='en')))
            graph.add((node, DPV.hasRiskLevel, RISK[f'{risk_label}Risk']))
            graph.add((node, DPV.hasSeverity, 
                RISK[f'{labels[col-1]}Severity']))
            graph.add((node, DPV.hasLikelihood, 
                RISK[f'{labels[row-1]}Likelihood']))
            graph.add((node, SKOS.broader, RISK[f'RiskMatrix{n}x{n}']))
            # print(f'row: {row} col: {col} risk: {risk_label}')
            print(f"{RISK[f'RM{n}x{n}R{row}C{col}']},{pref_label} Risk,{description},{RISK[f'RiskMatrix{n}x{n}']}")


generate_nodes(3)
generate_nodes(5)
generate_nodes(7)
graph.serialize('risk-matrix-nodes.ttl', format='ttl')

