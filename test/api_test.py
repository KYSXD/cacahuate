from flask import json

from .context import *

def test_continue_process_requires(client):
    res = client.post('/v1/pointer')

    assert res.status_code == 400
    assert json.loads(res.data) == {
        'errors': [
            {
                'detail': 'execution_id is required',
                'i18n': 'errors.execution_id.required',
                'field': 'execution_id',
            },
            {
                'detail': 'node_id is required',
                'i18n': 'errors.node_id.required',
                'field': 'node_id',
            },
        ],
    }

def test_continue_process_asks_living_objects(client):
    ''' the app must validate that the ids sent are real objects '''
    res = client.post('/v1/pointer', data={
        'node_id': 'nada',
        'execution_id': 'verde',
    })

    assert res.status_code == 400
    assert json.loads(res.data) == {
        'errors': [
            {
                'detail': 'execution_id is invalid',
                'i18n': 'errors.execution_id.invalid',
                'field': 'execution_id',
            },
            {
                'detail': 'node_id is invalid',
                'i18n': 'errors.node_id.invalid',
                'field': 'node_id',
            },
        ],
    }

def test_can_continue_process(client):
    res = client.post('/v1/pointer')

    assert res.status_code == 200
    assert json.loads(res.data) == {
        'data': [
            {
                '_type': 'pointer',
                'id': '',
                'node_id': '',
            },
        ]
    }

def test_can_query_process_status(client):
    res = client.get('/v1/node/{}')

    assert res.status_code == 200
    assert res.data == {
        'data': [
            {
                '_type': 'node',
                'id': '',
                'data': {},
            },
        ]
    }

def test_execution_start(client, models):
    assert lib.models.Execution.count() == 0
    assert lib.models.Pointer.count() == 0

    res = client.post('/v1/execution')

    assert res.status_code == 201
    assert res.json() == {
        'data': {
            '_type': 'execution',
            'id': '',
            'process_name': 'simple',
        },
    }

    assert lib.models.Execution.count() == 1
    assert lib.models.Pointer.count() == 1
