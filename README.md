# redis-py

The Python interface to the Redis key-value store.

## Installation

    $ sudo pip install redis

or alternatively (you really should be using pip though):

    $ sudo easy_install redis

From source:

    $ sudo python setup.py install


## Getting Started

    >>> import redis
    >>> r = redis.StrictRedis(host='localhost', port=6379, db=0)
    >>> r.set('foo', 'bar')
    True
    >>> r.get('foo')
    'bar'

## API Reference

The official Redis documentation does a great job of explaining each command in
detail (http://redis.io/commands). redis-py exposes two client classes that
implement these commands. The StrictRedis class attempts to adhere to the
official official command syntax. There are a few exceptions:

* SELECT: Not implemented. See the explanation in the Thread Safety section
  below.
* DEL: 'del' is a reserved keyword in the Python syntax. Therefore redis-py
  uses 'delete' instead.
* CONFIG GET|SET: These are implemented separately as config_get or config_set.
* MULTI/EXEC: These are implemented as part of the Pipeline class. Calling
  the pipeline method and specifying use_transaction=True will cause the
  pipeline to be wrapped with the MULTI and EXEC statements when it is executed.
  See more about Pipelines below.
* SUBSCRIBE/LISTEN: Similar to pipelines, PubSub is implemented as a separate
  class as it places the underlying connection in a state where it can't
  execute non-pubsub commands. Calling the pubsub method from the Redis client
  will return a PubSub instance where you can subscribe to channels and listen
  for messages. You can call PUBLISH from both classes.

In addition to the changes above, the Redis class, a subclass of StrictRedis,
overrides several other commands to provide backwards compatibility with older
versions of redis-py:

* LREM: Order of 'num' and 'value' arguments reversed such that 'num' can
  provide a default value of zero.
* ZADD: Redis specifies the 'score' argument before 'value'. These were swapped
  accidentally when being implemented and not discovered until after people
  were already using it. The Redis class expects *args in the form of:
      name1, score1, name2, score2, ...
* SETEX: Order of 'time' and 'value' arguments reversed.

