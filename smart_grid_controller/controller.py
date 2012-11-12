import urllib2
import json
import time
import urlparse

import csp_solver

from smart_grid_actor.actor import (
    AbstractActor, ConnectionError, NotSolvable
)


def get_actor_value(actor):
    try:
        time_before_request = time.time()
        actor_value = actor.get_value()
        time_after_request = time.time()
        return time_before_request, time_after_request, actor_value
    except KeyboardInterrupt:
        pass


def get_actor_vr(actor):
    return actor.get_value_range()


def set_actor_value(args):
    actor, new_value = args
    return actor.set_value(new_value)


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

        self.actors_cls = None
        for actor in actors:
            if not isinstance(actor, AbstractActor):
                raise Exception("Please pass a valid "
                                "AbstractActor instance, not '%s'"
                % actor
                )

            if (self.actors_cls
                and not actor.__class__ == self.actors_cls):
                raise Exception("Controller "
                    "can only handle Actors of "
                    "the same class."
                )
            self.actors_cls = actor.__class__

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

    def _parallel_apply_for_actors_n_wait(
            self,
            fct,
            iterable=None
            ):
        if self.multiprocessing_pool:
            pool = self.multiprocessing_pool
        else:
            self.log("multiprocessing_pool is unset. "
                "Switching to slow get implementation")
            import multiprocessing
            pool = multiprocessing.Pool()

        if fct == set_actor_value:
            assert iterable

        if iterable == None:
            iterable = self._actors

        query_results_p = pool.map_async(
            fct,
            iterable
        )

        # pass a timeout to multiprocessing to fix bug
        query_results = query_results_p.get(9999999)

        # part of the ad hoc pool workaround
        if not self.multiprocessing_pool:
            pool.terminate()
            pool.join()

        return query_results

    def get_value(self):
        query_results = self._parallel_apply_for_actors_n_wait(
            get_actor_value
        )

        result = sum([
            int(body)
            for _t, _t, body in query_results
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

        query_results = self._parallel_apply_for_actors_n_wait(
            get_actor_vr
        )

        for actor_value_range in query_results:
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

        all_actor_ranges = list(self._parallel_apply_for_actors_n_wait(
            get_actor_vr
        ))

        csp_result = csp_solver.do_solve(
            variables=all_actor_ranges,
            reference_value=set_value,
            csp_solver_config=self._csp_solver_config
        )

        if ('satisfiable_bool' in csp_result
            and csp_result['satisfiable_bool'] == True):

            # Using a subprocess will pickle the used objects
            # --> the "set" values are lost.
            # RemoteActor manipulates outside of
            # context actors --> ok.
            if self.actors_cls in [
                    ControllerActor, RemoteActor
                    ]:
                iterable = [
                    (self._actors[index], assigned_value)
                    for index, assigned_value \
                        in enumerate(csp_result['solution_list'])
                ]
                query_results = self._parallel_apply_for_actors_n_wait(
                    set_actor_value,
                    iterable
                )
            else:
                for index, assigned_value in enumerate(
                        csp_result['solution_list']):
                    set_actor_value(
                        (self._actors[index], assigned_value)
                    )

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
