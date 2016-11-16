#!/usr/bin/python3

#
# Copyright (C) 2016 Julien Desfossez <jdesfossez@efficios.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 2 as
# published by the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import json
from bokeh.charts import Bar, Histogram, output_file, show
from bokeh.models import HoverTool, BoxSelectTool
from bokeh.plotting import show, figure, ColumnDataSource
from bokeh.models import Range1d


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

    def barchart(self, values, x_names, tooltips, color="SteelBlue"):
        order = range(1, len(values) + 1)
        y_range = Range1d(0, max(values))
        data_dict = {'x': order,
                     'y': [val/2.0 for val in values],
                     'heights': values}
        tooltip_list = []
        for t in tooltips.keys():
            data_dict[t] = tooltips[t]
            tooltip_list.append(("%s" % t,
                                 "@%s" % t))
        hover = HoverTool(tooltips=tooltip_list)
        source = ColumnDataSource(data=data_dict)
        p = figure(x_range=x_names, y_range=y_range, tools=[hover])
        p.rect(x='x', y='y', source=source, width=0.5, height='heights',
               color = color)
        # pi/4
        p.xaxis.major_label_orientation = 0.78
        return p


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
        values = []
        x_labels = []
        tooltips = {'Migrations': [],
                    'Priorities': []}
        #for line in table['data']:
        for line in sorted(table['data'], key=lambda k: k[ratio_col]['value']):
            _name = '%s (%d)' % (line[process_col]['name'],
                                line[process_col]['tid'])
            _ratio = line[ratio_col]['value'] * 100
            _prio = line[prio_col]['value']
            _migration = line[migrations_col]['value']
            x_labels.append(_name)
            tooltips['Migrations'].append(_migration)
            tooltips['Priorities'].append(_prio)
            values.append(_ratio)

        p = self.barchart(values, x_labels, tooltips)
#        p = Bar(data, 'process', values='ratio',
#                title=self.get_table_title('per-process'),
#                color='SteelBlue',
#                ylabel='Usage (%)')

        output_file("bar.html")

        show(p)

#        print(data)

l = CPU('cputop-metadata.json', 'cputop.json')
l.per_process()

