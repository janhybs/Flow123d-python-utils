#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from pymongo.mongo_client import MongoClient
import re

db = MongoClient('localhost').get_database('bench')
hostname_regex = re.compile(r'([a-zA-Z]+).*')


def get_field_set(col, field_name, regex=None):
    result = set()
    for value in db.get_collection(col).aggregate([
        {
            '$group': {
                '_id': ('$'+field_name)
            }
        }
    ]):
        if regex:
            result.add(
                regex.findall(value['_id'])[0]
            )
        else:
            result.add(value['_id'])
    return sorted(list(result))

hostnames = get_field_set('nodes', 'hostname', hostname_regex)
casenames = get_field_set('bench', 'case-name')
testnames = get_field_set('bench', 'test-name')


result = db.get_collection('bench').aggregate([
    # {
    #     '$match': {
    #         'case-name': '01'
    #     }
    # },
    {
        '$project': {
            'nproc': '$nproc',
            'node_id': '$node_id',
            'test-name': '$test-name',
            'case-name': '$case-name',
            'task-size': '$task-size',
            'overall-duration': '$duration',
            'duration': {'$arrayElemAt': ['$children', 0]}
        }
    },
    {
      '$limit': 500*1000
    },
    {
        '$project': {
            'nproc': '$nproc',
            'node_id': '$node_id',
            'test-name': '$test-name',
            'case-name': '$case-name',
            'task-size': '$task-size',
            'overall-duration': '$overall-duration',
            'time-sum': '$duration.cumul-time-sum',
            'time-min': '$duration.cumul-time-min',
            'time-max': '$duration.cumul-time-max'
        }
    },
    {
        '$lookup': {
            'from': 'nodes',
            'localField': 'node_id',
            'foreignField': '_id',
            'as': 'nodes'
        }
    },
    {
        '$project': {
            'nproc': 1,
            'node_id': 1,
            'test-name': 1,
            'case-name': 1,
            'task-size': 1,
            'overall-duration': 1,
            'time-sum': 1,
            'time-min': 1,
            'time-max': 1,
            'nodes': {'$arrayElemAt': ['$nodes', 0]}
        }
    },
    {
        '$project': {
            'nproc': 1,
            'node_id': 1,
            'test-name': 1,
            'case-name': 1,
            'task-size': 1,
            'overall-duration': 1,
            'time-sum': 1,
            'time-min': 1,
            'time-max': 1,
            'frequency': '$nodes.frequency',
            'hostname': '$nodes.hostname',
            'l1i': '$nodes.l1i',
            'l1d': '$nodes.l1d',
            'l2': '$nodes.l2',
            'l3': '$nodes.l3',
            'vendor': '$nodes.vendor'
        }
    },
])

data = list()
for item in result:
    if 'l3' not in item:
        item['l3'] = 0
    item['task-size'] = int(item['task-size'])
    item['intel'] = str(item['vendor']).find('intel') != -1
    item['hostname'] = hostnames.index(hostname_regex.findall(item['hostname'])[0])
    item['case-name'] = casenames.index(item['case-name'])
    item['test-name'] = testnames.index(item['test-name'])
    del item['vendor']
    # del item['_id']
    data.append(item)

# import json
#
# import formic
# import os
#
# artifact_folder = '/var/lib/mongodb/artifacts'
# artifact_folder_rule = '.artifacts-'
#
# artifact_rule_profiler = '**/profiler_*.json'
# artifact_rule_lscpu = 'lscpu_*.json'
# artifact_rule_benchmark = 'benchmark_*.json'
#
#
#
# def read_json(f):
#     """
#     :rtype: dict
#     """
#     with open(f, 'r') as fp:
#         return json.load(fp)
#
#
# for folder in os.listdir(artifact_folder):
#     if folder.startswith(artifact_folder_rule):
#         artifact_folder_path = os.path.join(artifact_folder, folder)
#         try:
#             benchmark_json = read_json(list(formic.FileSet(
#                 include=artifact_rule_benchmark,
#                 directory=artifact_folder_path))[0])
#
#             lscpu_json = read_json(list(formic.FileSet(
#                 include=artifact_rule_lscpu,
#                 directory=artifact_folder_path))[0])
#         except Exception as e:
#             print 'Ignoring folder {}'.format(artifact_folder_path), e
#             continue
#
#         print 'Processing folder {}'.format(artifact_folder_path)
#
#         # profiler_json = list(formic.FileSet(
#         #     include=artifact_rule_profiler,
#         #     directory=artifact_folder_path))
#
#
#         document = lscpu_json.copy()
#         del document['modes']
#         break

