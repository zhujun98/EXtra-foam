"""
Distributed under the terms of the BSD 3-Clause License.

The full license is in the file LICENSE, distributed with this software.

Author: Jun Zhu <jun.zhu@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
from itertools import chain

from .db_utils import redis_except_handler
from ..ipc import ProcessLogger, RedisConnection


class _AbstractProxy(ProcessLogger):
    """_AbstractProxy.

    Base class for communicate with Redis server.
    """
    _db = RedisConnection()
    _db_nodecode = RedisConnection(decode_responses=False)

    def pubsub(self):
        return self._db.pubsub()

    def reset(self):
        _AbstractProxy.__dict__["_db"].reset()
        _AbstractProxy.__dict__["_db_nodecode"].reset()

    def pipeline(self):
        return self._db.pipeline()

    def execute_command(self, *args, **kwargs):
        return self._db.execute_command(*args, **kwargs)

    @redis_except_handler
    def hset(self, name, key, value):
        """Set a key-value pair of a hash.

        :returns: None if the connection failed;
                  1 if created a new field;
                  0 if set on an old field.
        """
        return self._db.execute_command('HSET', name, key, value)

    @redis_except_handler
    def hmset(self, name, mapping):
        """Set a mapping of a hash.

        :return: None if the connection failed;
                 True if set.
        """
        return self._db.execute_command(
            'HSET', name, *chain.from_iterable(mapping.items()))

    @redis_except_handler
    def hget(self, name, key):
        """Get the value for a given key of a hash.

        :return: None if the connection failed or key was not found;
                 otherwise, the value.
        """
        return self._db.execute_command('HGET', name, key)

    @redis_except_handler
    def hmget(self, name, keys):
        """Get values for a list of keys of a hash.

        :return: None if the connection failed;
                 otherwise, a list of values.
        """
        return self._db.hmget(name, keys)

    @redis_except_handler
    def hdel(self, name, *keys):
        """Delete a number of keys of a hash.

        :return: None if the connection failed;
                 number of keys being found and deleted.
        """
        return self._db.execute_command('HDEL', name, *keys)

    @redis_except_handler
    def hget_all(self, name):
        """Get all key-value pairs of a hash.

        :return: None if the connection failed;
                 otherwise, a dictionary of key-value pairs. If the hash
                 does not exist, an empty dictionary will be returned.
        """
        return self._db.execute_command('HGETALL', name)

    @redis_except_handler
    def hget_all_multi(self, name_list):
        """Get all key-value pairs of a list of hash.

        :return: None if the connection failed;
                 otherwise, a list of dictionaries of key-value pairs.
                 If the hash does not exist, an empty dictionary will
                 be returned.
        """
        pipe = self._db.pipeline()
        for name in name_list:
            pipe.execute_command('HGETALL', name)
        return pipe.execute()

    @redis_except_handler
    def hincrease_by(self, name, key, amount=1):
        """Increase the value of a key in a hash by the given amount.

        :return: None if the connection failed;
                 value after the increment if the initial value is an integer;
                 amount if key does not exist (set initial value to 0).

        :raise: redis.exceptions.ResponseError if value is not an integer.
        """
        return self._db.execute_command('HINCRBY', name, key, amount)

    @redis_except_handler
    def hincrease_by_float(self, name, key, amount=1.0):
        """Increase the value of a key in a hash by the given amount.

        :return: None if the connection failed;
                 value after the increment if the initial value can be
                 converted to a float;
                 amount if key does not exist (set initial value to 0).

        :raise: redis.exceptions.ResponseError if value is not a float.
        """
        return self._db.execute_command('HINCRBYFLOAT', name, key, amount)
