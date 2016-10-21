#!/usr/bin/python3

import json
from bokeh.charts import Bar, Histogram, output_file, show
from bokeh.models import HoverTool, BoxSelectTool


class LAMIChart:
    def __init__(self, data, metadata):
        self._data = self._import(data)
        self._metadata = self._import(metadata)

    def _import(self, filename):
        file = open(filename)
        j = json.loads(file.read())
        file.close()
        return j

    def get_title(self):
        return self._metadata['title']

    def get_description(self):
        return self._metadata['description']

    def get_table_title(self, table):
        return self._metadata['table-classes'][table]['title']

    def get_table_column_descriptions(self, table):
        return self._metadata['table-classes'][table]['column-descriptions']

    def get_data_table(self, name):
        for i in self._data['results']:
            if i['class'] == name:
                return i

    def get_column_index_from_title(self, table, column_title):
        columns = self._metadata['table-classes'][table]['column-descriptions']
        for id in range(len(columns)):
            if columns[id]['title'] == column_title:
                return id


class CPU(LAMIChart):
    def __init__(self, metadata, data):
        super().__init__(data, metadata)
    
    def per_process(self):
        table = self.get_data_table('per-process')
        process_col = self.get_column_index_from_title(
            'per-process', 'Process')
        ratio_col = self.get_column_index_from_title(
            'per-process', 'CPU usage')
        prio_col = self.get_column_index_from_title(
            'per-process', 'Chronological priorities')
        migrations_col = self.get_column_index_from_title(
                'per-process', 'Migration count')
        data = []
        #for line in sorted(table['data'], key=lambda k: k[ratio_col]['value']):
        for line in table['data']:
            _name = '%s (%d)' % (line[process_col]['name'],
                                line[process_col]['tid'])
            _ratio = line[ratio_col]['value'] * 100
            _prio = line[prio_col]['value']
            _migration = line[migrations_col]['value']
            data.append({'process': _name,
                         'ratio': _ratio,
                         'prio': _prio,
                         'migrations': _migration})

        p = Bar(data, 'process', values='ratio',
                title=self.get_table_title('per-process'),
                color='SteelBlue',
                ylabel='Usage (%)')

        output_file("bar.html")

        show(p)

#        print(data)

l = CPU('cputop-metadata.json', 'cputop.json')
l.per_process()

