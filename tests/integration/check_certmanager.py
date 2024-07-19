#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

from pathlib import Path

from config import MANIFESTS_DIR
from k8s_test_harness import harness
from k8s_test_harness.util import constants, env_util, k8s_util
from k8s_test_harness.util.k8s_util import HelmImage

IMG_PLATFORM = "amd64"
IMG_VERSION = "1.10.1"
CHART_VERSION = IMG_VERSION
INSTALL_NAME = "cert-manager"


def _get_rock_image(name: str, verson: str):
    rock = env_util.get_build_meta_info_for_rock_version(
        "cert-manager-%s", IMG_VERSION, IMG_PLATFORM
    )
    return rock.image


def check_certmanager(
    module_instance: harness.Instance, img_version: str, chart_version: str
):
    images = [
        HelmImage(uri=_get_rock_image("controller", img_version)),
        HelmImage(uri=_get_rock_image("webhook", img_version), prefix="webhook"),
        HelmImage(uri=_get_rock_image("cainjector", img_version), prefix="cainjector"),
        HelmImage(uri=_get_rock_image("acmesolver", img_version), prefix="acmesolver"),
    ]

    helm_command = k8s_util.get_helm_install_command(
        name=INSTALL_NAME,
        chart_name="cert-manager",
        images=[k8s_util.HelmImage(uri=rock.image)],
        namespace=constants.K8S_NS_KUBE_SYSTEM,
        chart_version=chart_version,
        repository="https://charts.jetstack.io",
    )
    helm_command += ["--set", "installCRDs=true"]
    module_instance.exec(helm_command)

    manifest = MANIFESTS_DIR / "cert-manager-test.yaml"
    module_instance.exec(
        ["k8s", "kubectl", "apply", "-f", "-"],
        input=Path(manifest).read_bytes(),
    )

    k8s_utils.wait_for_resource(
        module_instance,
        resource_type="certificate",
        name="selfsigned-cert",
        namespace="cert-manager-test",
    )

    exec_util.stubbornly(retries=5, delay_s=10).on(module_instance).until(
        lambda p: "selfsigned-cert-tls" in p.stdout.decode()
    ).exec(
        [
            "k8s",
            "kubectl",
            "get",
            "secret",
            "--namespace",
            "cert-manager-test",
            "-o",
            "json",
        ]
    )
