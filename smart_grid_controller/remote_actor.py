import urllib2
import json
import urlparse

from smart_grid_actor.actor import (
    AbstractActor, ConnectionError, NotSolvable
)

class RemoteActor(AbstractActor):
    _uri = None

    def __init__(
            self,
            uri,
            get_timeout=5,
            **kwargs
    ):
        self._uri = uri

        self._get_value_uri = urlparse.urljoin(self._uri, '/')
        self._set_value_uri = self._get_value_uri
        self._get_value_range_uri = urlparse.urljoin(self._uri, '/vr/')

        self.get_timeout = get_timeout
        AbstractActor.__init__(self, **kwargs)

    def get_configuration(self):
        return dict(
            id=self.id,
            uri=self._uri,
            cls=self.__class__.__name__
        )

    def get_value(self):
        try:
            request_result = urllib2.urlopen(
                self._get_value_uri,
                timeout=self.get_timeout
            ).read()
        except urllib2.URLError as exc:
            raise ConnectionError(
                '{0} {1}'.format(self._get_value_uri, exc.reason))

        actor_value = json.loads(request_result)['value']
        return actor_value

    def get_value_range(self):
        try:
            request_result = urllib2.urlopen(
                self._get_value_range_uri,
                timeout=self.get_timeout
            ).read()
        except urllib2.HTTPError as exc:
            raise NotSolvable('400 %s' % exc)
        except urllib2.URLError as exc:
            raise ConnectionError(
                '{0} {1}'.format(self._get_value_range_uri, exc.reason))

        json_result = json.loads(request_result)
        self.log(u"request result: {0}".format(json_result))
        actor_value_range = set(
            json_result['value_range']
        )
        return actor_value_range

    def set_value(self, new_value):
        set_value = self.validate(new_value)

        try:
            data = str(set_value)
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(
                self._set_value_uri,
                data=data
            )
            request.add_header('Content-Type', 'application/json')
            request.get_method = lambda: 'PUT'
            request_response = opener.open(
                request, timeout=self.get_timeout)
            request_result = request_response.read()
        except urllib2.HTTPError as exc:
            raise NotSolvable('400 %s' % exc)
        except urllib2.URLError as exc:
            raise ConnectionError(
                '{0} {1}'.format(self._set_value_uri, exc.reason))

        actor_value = json.loads(request_result)['value']
        return actor_value
