from rx.subject import Subject


class RxBus:
    """
    This uses rx.subject to emulate pyee.EventEmitter.
    This way, we can ditch the pyee dependency, because anyway we need rx for its ReplaySubject which pyee doesn't support.
    """
    def __init__(self):
        self.subject = Subject()

    def on(self, event_type, callback):
        self.subject.subscribe(
            lambda value: callback(value['payload']) if value['type'] == event_type else None
        )

    def emit(self, event_type, payload):
        self.subject.on_next({'type': event_type, 'payload': payload})
