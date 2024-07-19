#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import check_certmanager

IMG_VERSION = "1.10.1"
CHART_VERSION = IMG_VERSION


# Our k8s harness is a module scoped fixture, so each rock version
# needs to be tested in a separate module in order to have a
# clean, isolated k8s environment.
def test_certmanager_integration():
    check_certmanager.check_certmanager(IMG_VERSION, CHART_VERSION)
