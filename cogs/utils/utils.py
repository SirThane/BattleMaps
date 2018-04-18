"""Utility functions and classes.
"""

import redis


class Paginator:

    def __init__(self, page_limit: int=1000, trunc_limit: int=2000, headers=None, header_extender=u'\u200b'):
        self.page_limit = page_limit
        self.trunc_limit = trunc_limit
        self._pages = None
        self._header_extender = header_extender
        self.set_headers(headers)

    @property
    def pages(self):
        if self._headers:
            self._extend_headers(len(self._pages))
            headers, self._headers = self._headers, None
            return [(headers[i], self._pages[i]) for i in range(len(self._pages))]
        else:
            return self._pages

    def set_headers(self, headers=None):
        self._headers = headers

    def set_header_extender(self, header_extender: str=u'\u200b'):
        self._header_extender = header_extender

    def _extend_headers(self, length: int):
        while len(self._headers) < length:
            self._headers.append(self._header_extender)

    def set_trunc_limit(self, limit: int=2000):
        self.trunc_limit = limit

    def set_page_limit(self, limit: int=1000):
        self.page_limit = limit

    def paginate(self, value):
        """
        To paginate a string into a list of strings under
        `self.page_limit` characters. Total len of strings
        will not exceed `self.trunc_limit`.
        :param value: string to paginate
        :return list: list of strings under 'page_limit' chars
        """
        spl = str(value).split('\n')
        ret = []
        page = ''
        total = 0
        for i in spl:
            if total + len(page) < self.trunc_limit:
                if (len(page) + len(i)) < self.page_limit:
                    page += '\n{}'.format(i)
                else:
                    if page:
                        total += len(page)
                        ret.append(page)
                    if len(i) > (self.page_limit - 1):
                        tmp = i
                        while len(tmp) > (self.page_limit - 1):
                            if total + len(tmp) < self.trunc_limit:
                                total += len(tmp[:self.page_limit])
                                ret.append(tmp[:self.page_limit])
                                tmp = tmp[self.page_limit:]
                            else:
                                ret.append(tmp[:self.trunc_limit - total])
                                break
                        else:
                            page = tmp
                    else:
                        page = i
            else:
                ret.append(page[:self.trunc_limit - total])
                break
        else:
            ret.append(page)
        self._pages = ret
        return self.pages


def bool_str(arg):
    if arg == 'True':
        return True
    elif arg == 'False':
        return False
    else:
        return arg


def bool_transform(arg):
    if isinstance(arg, str):
        return bool_str(arg)
    elif isinstance(arg, list):
        for i in range(len(arg)):
            arg[i] = bool_str(arg[i])
        return arg
    elif isinstance(arg, dict):
        for i in arg.keys():
            arg[i] = bool_str(arg[i])
        return arg


class StrictRedis(redis.StrictRedis):
    """Turns 'True' and 'False' values returns
    in redis to bool values"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Bool transforms will be performed on these redis commands
    command_list = ['HGET', 'HGETALL', 'GET', 'LRANGE']

    def parse_response(self, connection, command_name, **options):
        ret = super().parse_response(connection, command_name, **options)
        # ret = eval(compile(ret, '<string>', 'eval'))
        if command_name in self.command_list:
            return bool_transform(ret)
        else:
            return ret
