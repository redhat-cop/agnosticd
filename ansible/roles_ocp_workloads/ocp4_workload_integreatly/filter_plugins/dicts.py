'''Custom ansible filters for dicts'''

import copy

class FilterModule(object):
    def filters(self):
        return {
            'csv_filter_spec': self.csv_filter_spec
        }

    def csv_filter_spec(self, target_csv, to_remove):
        '''Remove keys specified in to_remove from target_csv'''
        filtered_csv = copy.deepcopy(target_csv)
        print(filtered_csv['spec'])
        for item in to_remove:
            print(item)
            if item in filtered_csv['spec']:
                del filtered_csv['spec'][item]
        return filtered_csv