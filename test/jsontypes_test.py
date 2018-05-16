from cacahuate.jsontypes import SortedMap


def test_sorted_map():
    sm = SortedMap([
        {
            'id': '1',
            'name': 'la',
        },
        {
            'id': '2',
            'name': 'le',
        },
    ], key='id')

    assert sm.to_json() == {
        '_type': ':sorted_map',
        'items': {
            '1': {
                'id': '1',
                'name': 'la',
            },
            '2': {
                'id': '2',
                'name': 'le',
            },
        },
        'item_order': ['1', '2'],
    }

    assert list(sm) == [
        {
            'id': '1',
            'name': 'la',
        },
        {
            'id': '2',
            'name': 'le',
        },
    ]

    assert sm['2'] == {
        'id': '2',
        'name': 'le',
    }

    assert sm[0] == {
        'id': '1',
        'name': 'la',
    }
