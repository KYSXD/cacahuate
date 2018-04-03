class BaseUser:

    def get_identifier(self):
        raise NotImplementedError('Must be implemented in subclasses')

    def get_human_name(self):
        raise NotImplementedError('Must be implemented in subclasses')

    def get_x_info(self, notification_backend):
        raise NotImplementedError('Must be implemented in subclasses')


class BaseAuthProvider:

    def __init__(self, config):
        self.config = config

    def authenticate(self, **credentials) -> BaseUser:
        raise NotImplementedError('Must be implemented in subclasses')


class BaseHierarchyProvider:

    def __init__(self, config):
        self.config = config

    def validate_user(self, user, **params):
        ''' given a user, should rise an exception if the user does not match
        the hierarchy conditions required via params '''
        raise NotImplementedError('Must be implemented in subclasses')

    def find_users(self, **params) -> [BaseUser]:
        ''' given the params, retrieves the user identifiers that match them '''
        raise NotImplementedError('Must be implemented in subclasses')
