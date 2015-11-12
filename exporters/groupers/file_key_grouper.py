from exporters.groupers.base_grouper import BaseGrouper


class FileKeyGrouper(BaseGrouper):
    """
    Groups items depending on their keys. It adds the group membership information to items.

        - keys (list)
            A list of keys to group by
    """
    supported_options = {
        'keys': {'type': list}
    }

    def __init__(self, options):
        super(FileKeyGrouper, self).__init__(options)
        self.keys = self.read_option('keys', [])

    def _get_nested_value(self, item, key):
        if '.' in key:
            first_key, rest = key.split('.', 1)
            return self._get_nested_value(item.get(first_key, {}), rest)
        else:
            membership = item.get(key, 'unknown')
            if membership is None:
                membership = 'unknown'
            return membership

    def group_batch(self, batch):
        print '************'
        print self.keys
        print '************'
        for item in batch:
            item.group_key = self.keys
            membership = []
            for key in self.keys:
                membership.append(self._get_nested_value(item, key))
            print '************'
            print membership
            print '************'
            item.group_membership = tuple(membership)
            yield item
