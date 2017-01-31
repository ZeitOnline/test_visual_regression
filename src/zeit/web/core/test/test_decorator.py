import pytest
import pyramid.exceptions

import zeit.web.core.decorator


def test_host_restrictions_should_not_be_allowed_on_view_defaults():
    with pytest.raises(pyramid.exceptions.ConfigurationError):
        zeit.web.core.decorator.view_defaults(host_restriction='foo')

    with pytest.raises(pyramid.exceptions.ConfigurationError):
        zeit.web.core.decorator.view_defaults(request_method='foo')
