import pickle


def pickle_wrapper(data,type):
    pickle_data = pickle.dumps(data)
    return type.parse_raw(
        pickle_data, content_type='application/pickle', allow_pickle=True
    )
