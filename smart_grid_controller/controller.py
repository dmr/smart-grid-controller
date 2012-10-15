import urllib2
import json
import time

import csp_solver

from smart_grid_actor.actor import AbstractActor, ConnectionError, NotSolvable
from smart_grid_actor.server import CustomPool


def get_actor_value(actor):
    try:
        time_before_request = time.time()
        actor_value = actor.get_value()
        time_after_request = time.time()
        return time_before_request, time_after_request, actor_value
    except KeyboardInterrupt:
        pass



class ControllerActor(AbstractActor):
    _actors=None

    def __init__(
            self,
            actors,
            csp_solver_config,
            multiprocessing_pool=None,
            **kwargs
            ):
        self.multiprocessing_pool = multiprocessing_pool

        for actor in actors:
            if not isinstance(actor, AbstractActor):
                raise Exception("Please pass a valid "
                                "AbstractActor instance, not '%s'"
                % actor
                )
            # actors needs to be a list
        assert isinstance(actors, list)
        self._actors = actors
        AbstractActor.__init__(self)

        self._csp_solver_config = csp_solver_config

    def get_configuration(self):
        return dict(
            id=self.id,
            actors=[actor.get_configuration()
                    for actor in self._actors],
            cls=self.__class__.__name__
        )

    def get_value(self):
        if self.multiprocessing_pool:
            query_results_p = self.multiprocessing_pool.map_async(
                get_actor_value,
                self._actors
            )
            try:
                query_results = query_results_p.get(9999999)
            except KeyboardInterrupt as exc:
                return

        else:
            self.log("multiprocessing_pool is unset. "
                "Switching to slow get implementation")
            pool = CustomPool(4)

            query_results_p = pool.map_async(
                get_actor_value,
                self._actors
            )
            try:
                query_results = query_results_p.get(9999999)
            except KeyboardInterrupt as exc:
                return

            pool.terminate()
            pool.join()

        result = sum([
        int(body)
        for _t, _t, body in query_results
        # pass a timeout to multiprocessing to fix bug
        ])
        return result

    def get_value_range(self):
        # alternative algorithm: try every possible answer. This is
        # not an option as there might be infinity possibilities
        # --> calculate a few small problems by trying out every
        # possibility is solvable and faster

        range_min = 0
        range_max = 0
        all_actor_ranges = []

        for actor in self._actors:
            actor_value_range = actor.get_value_range()
            all_actor_ranges.append(actor_value_range)
            actor_min = min(actor_value_range)
            range_min += actor_min
            actor_max = max(actor_value_range)
            range_max += actor_max

        range_theo_max = range(range_min, range_max+1)
        range_theo_max_length = len(range_theo_max)

        if range_theo_max_length > 500:
            self.log('warning: big interval to check: {0}'.format(
                range_theo_max_length))
            raise ValueError(
                'please improve algorithm for large numbers')

        own_value_range = set()

        for possibly_a_value_range_value in range_theo_max:
            csp_result = csp_solver.do_solve(
                variables=all_actor_ranges,
                reference_value=possibly_a_value_range_value,
                csp_solver_config=self._csp_solver_config
            )
            if ('satisfiable_bool' in csp_result
                and csp_result['satisfiable_bool'] == True):
                own_value_range.add(possibly_a_value_range_value)
            else:
                self.log('not a solution: {0}'.format(
                    possibly_a_value_range_value))

        return own_value_range

    def set_value(self, new_value):
        set_value = self.validate(new_value)

        all_actor_ranges = []
        for actor in self._actors:
            actor_value_range = actor.get_value_range()
            all_actor_ranges.append(actor_value_range)

        csp_result = csp_solver.do_solve(
            variables=all_actor_ranges,
            reference_value=set_value,
            csp_solver_config=self._csp_solver_config
        )

        if ('satisfiable_bool' in csp_result
            and csp_result['satisfiable_bool'] == True):

            for index, assigned_value in enumerate(
                csp_result['solution_list']):
                self.log('Setting value {0} for Actor {1} (id {2})'.format(
                    assigned_value, index, self._actors[index]
                ))
                self._actors[index].set_value(assigned_value)
            return set_value

        else:
            raise NotSolvable(
                '{0} is not an satisfiable'.format(set_value)
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
            url = self._uri + '/'
            request_result = urllib2.urlopen(url,
                timeout=self.get_timeout).read()
        except urllib2.URLError as exc:
            raise ConnectionError(
                '{0} {1}'.format(self._uri, exc.reason))

        actor_value = json.loads(request_result)['value']
        return actor_value

    def get_value_range(self):
        try:
            url = self._uri + '/vr/'
            request_result = urllib2.urlopen(url,
                timeout=self.get_timeout).read()
        except urllib2.HTTPError as exc:
            raise NotSolvable('400 %s' % exc)
        except urllib2.URLError as exc:
            raise ConnectionError(
                '{0} {1}'.format(self._uri, exc.reason))

        actor_value_range = set(
            json.loads(request_result)['value_range']
        )
        return actor_value_range

    def set_value(self, new_value):
        set_value = self.validate(new_value)

        try:
            url = self._uri + '/'
            data = str(set_value)
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(url, data=data)
            request.add_header('Content-Type', 'application/json')
            request.get_method = lambda: 'PUT'
            request_response = opener.open(
                request, timeout=self.get_timeout)
            request_result = request_response.read()
        except urllib2.HTTPError as exc:
            raise NotSolvable('400 %s' % exc)
        except urllib2.URLError as exc:
            raise ConnectionError(
                '{0} {1}'.format(self._uri, exc.reason))

        actor_value = json.loads(request_result)['value']
        return actor_value
