#!/usr/bin/env python3

from rdflib.term import Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, SKOS
from rdflib import Namespace, Graph
DPV = Namespace('https://w3id.org/dpv#')
RISK = Namespace('https://w3id.org/dpv/risk/matrix#')

graph = Graph()
graph.namespace_manager.bind('dpv', DPV)
graph.namespace_manager.bind('', RISK)

import itertools

def generate_combinations(max, min=1, size=None):
    '''generate and return combinations from min(1) to max of size each'''
    if size is None:
        size = max
    data = tuple(n for n in range(min, max+1))
    data = tuple(itertools.product(data, data))
    data = sorted(data, key=lambda x:sum(x))
    data = [data[n:n+size] for n in range(0,size)]
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
    data = tuple(generate_combinations(n))
    for index, level in enumerate(data):
        for index2, element in enumerate(level):
            node_index = index*n + index2 + 1
            node = RISK[f'RM{n}x{n}N{node_index}']
            graph.add((node, RDF.type, SKOS.Concept))
            graph.add((node, SKOS.prefLabel, 
                Literal(f'Node {node_index} (row: {index2+1} col: {index+1}) in Risk Matrix {n} x {n}', lang='en')))

            risk_level = abs(index+index2+1)//((n+1)//2)
            # print(f'row: {index2} col: {index} risk: {risk_level}')
            risk_level = labels[risk_level]
            graph.add((node, DPV.hasRiskLevel, RISK[f'{risk_level}Risk']))
            graph.add((node, DPV.hasSeverity, 
                RISK[f'{labels[element[0]-1]}Severity']))
            graph.add((node, DPV.hasLikelihood, 
                RISK[f'{labels[element[1]-1]}Likelihood']))
            graph.add((node, SKOS.broader, RISK[f'RiskMatrix{n}x{n}']))
            print(f'row: {index2} col: {index} risk: {risk_level}')


generate_nodes(3)
# generate_nodes(5)
# generate_nodes(7)
# print(select_labels(7))
graph.serialize('risk-matrix-nodes.ttl', format='ttl')

