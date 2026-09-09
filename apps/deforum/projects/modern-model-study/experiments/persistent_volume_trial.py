"""Two real Krea requests to measure first-use and warm execution on a trial Pod."""
import argparse
import json
import time
import turbo_schedule as t


def run(label):
    a = t.d.a
    a.transport.DEPLOYMENT = a.APP/'work/persistent-model-volume/deployment.json'
    (a.PROJECT/'runs').mkdir(exist_ok=True)
    records = []
    for index in range(2):
        graph = t.repaint_graph('turbo-tail', t.d.opening.SEED+1+index)
        graph['11']['inputs']['filename_prefix'] = 'persistent-volume/' + label
        started = time.monotonic()
        folder = a.transport.submit(a.PROJECT, 'volume-trial-'+label+'-'+str(index), graph, 1,
                                    source=t.d.SOURCE,
                                    lineage={'study': 'persistent-model-volume', 'motion': 'none',
                                             'purpose': 'startup and model reuse measurement'})
        history = json.loads((folder/'history.json').read_text())
        if 'status' not in history:
            history = next(iter(history.values()))
        messages = history['status']['messages']
        begin = next(data['timestamp'] for name, data in messages if name == 'execution_start')
        end = next(data['timestamp'] for name, data in messages if name == 'execution_success')
        records.append({'run': str(folder.relative_to(a.PROJECT)), 'request_index': index,
                        'wall_seconds': round(time.monotonic()-started, 3),
                        'graph_seconds': (end-begin)/1000})
        path = a.APP/'work/persistent-model-volume'/f'{label}-renders.json'
        path.write_text(json.dumps(records, indent=2)+'\n')
        print(records[-1], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label')
    run(parser.parse_args().label)
