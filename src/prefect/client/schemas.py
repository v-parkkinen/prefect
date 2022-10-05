import datetime
from typing import TYPE_CHECKING, Generic, Optional, Type, TypeVar, Union, overload

from pydantic import Field

from prefect.orion import schemas

if TYPE_CHECKING:
    from prefect.deprecated.data_documents import DataDocument
    from prefect.results import BaseResult

R = TypeVar("R")


class State(schemas.states.State.subclass(exclude_fields=["data"]), Generic[R]):
    """
    The state of a run.

    This client-side extension adds a `result` interface.
    """

    data: Optional[Union["BaseResult[R]", "DataDocument[R]"]] = Field(
        default=None,
    )

    @overload
    def result(self: "State[R]", raise_on_failure: bool = True) -> R:
        ...

    @overload
    def result(self: "State[R]", raise_on_failure: bool = False) -> Union[R, Exception]:
        ...

    def result(self, raise_on_failure: bool = True):
        """
        Convenience method for access the data on the state's data document.

        Args:
            raise_on_failure: a boolean specifying whether to raise an exception
                if the state is of type `FAILED` and the underlying data is an exception

        Raises:
            TypeError: if the state is failed but without an exception

        Returns:
            The underlying decoded data

        Examples:
            >>> from prefect import flow, task
            >>> @task
            >>> def my_task(x):
            >>>     return x

            Get the result from a task future in a flow

            >>> @flow
            >>> def my_flow():
            >>>     future = my_task("hello")
            >>>     state = future.wait()
            >>>     result = state.result()
            >>>     print(result)
            >>> my_flow()
            hello

            Get the result from a flow state

            >>> @flow
            >>> def my_flow():
            >>>     return "hello"
            >>> my_flow().result()
            hello

            Get the result from a failed state

            >>> @flow
            >>> def my_flow():
            >>>     raise ValueError("oh no!")
            >>> state = my_flow()  # Error is wrapped in FAILED state
            >>> state.result()  # Raises `ValueError`

            Get the result from a failed state without erroring

            >>> @flow
            >>> def my_flow():
            >>>     raise ValueError("oh no!")
            >>> state = my_flow()
            >>> result = state.result(raise_on_failure=False)
            >>> print(result)
            ValueError("oh no!")
        """
        from prefect.deprecated.data_documents import (
            DataDocument,
            result_from_state_with_data_document,
        )
        from prefect.results import BaseResult

        if isinstance(self.data, DataDocument):
            return result_from_state_with_data_document(
                self, raise_on_failure=raise_on_failure
            )
        elif isinstance(self.data, BaseResult):
            return self.data.load()
        else:
            raise ValueError(
                f"State data is of unknown result type {type(self.data).__name__!r}."
            )


def Scheduled(
    cls: Type[State] = State, scheduled_time: datetime.datetime = None, **kwargs
) -> State:
    """Convenience function for creating `Scheduled` states.

    Returns:
        State: a Scheduled state
    """
    return schemas.states.Scheduled(cls=cls, scheduled_time=scheduled_time, **kwargs)


def Completed(cls: Type[State] = State, **kwargs) -> State:
    """Convenience function for creating `Completed` states.

    Returns:
        State: a Completed state
    """
    return schemas.states.Completed(cls=cls, **kwargs)


def Running(cls: Type[State] = State, **kwargs) -> State:
    """Convenience function for creating `Running` states.

    Returns:
        State: a Running state
    """
    return schemas.states.Running(cls=cls, **kwargs)


def Failed(cls: Type[State] = State, **kwargs) -> State:
    """Convenience function for creating `Failed` states.

    Returns:
        State: a Failed state
    """
    return schemas.states.Failed(cls=cls, **kwargs)


def Crashed(cls: Type[State] = State, **kwargs) -> State:
    """Convenience function for creating `Crashed` states.

    Returns:
        State: a Crashed state
    """
    return schemas.states.Crashed(cls=cls, **kwargs)


def Cancelled(cls: Type[State] = State, **kwargs) -> State:
    """Convenience function for creating `Cancelled` states.

    Returns:
        State: a Cancelled state
    """
    return schemas.states.Cancelled(cls=cls, **kwargs)


def Pending(cls: Type[State] = State, **kwargs) -> State:
    """Convenience function for creating `Pending` states.

    Returns:
        State: a Pending state
    """
    return schemas.states.Pending(cls=cls, **kwargs)


def AwaitingRetry(
    cls: Type[State] = State, scheduled_time: datetime.datetime = None, **kwargs
) -> State:
    """Convenience function for creating `AwaitingRetry` states.

    Returns:
        State: a AwaitingRetry state
    """
    return schemas.states.AwaitingRetry(
        cls=cls, scheduled_time=scheduled_time, **kwargs
    )


def Retrying(cls: Type[State] = State, **kwargs) -> State:
    """Convenience function for creating `Retrying` states.

    Returns:
        State: a Retrying state
    """
    return schemas.states.Retrying(cls=cls, **kwargs)


def Late(
    cls: Type[State] = State, scheduled_time: datetime.datetime = None, **kwargs
) -> State:
    """Convenience function for creating `Late` states.

    Returns:
        State: a Late state
    """
    return schemas.states.Late(cls=cls, scheduled_time=scheduled_time, **kwargs)


class FlowRun(schemas.core.FlowRun.subclass()):
    state: Optional[State] = Field(default=None)


class TaskRun(schemas.core.TaskRun.subclass()):
    state: Optional[State] = Field(default=None)


class OrchestrationResult(schemas.responses.OrchestrationResult.subclass()):
    state: Optional[State]
