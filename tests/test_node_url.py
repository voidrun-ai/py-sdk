from unittest.mock import MagicMock

from voidrun.api_client.configuration import Configuration
from voidrun.api_client.models.sandbox import Sandbox as SandboxModel
from voidrun.node_url import api_base_domain_from_host, node_api_base_url
from voidrun.sandbox import Sandbox, api_client_for_node, fleet_api_client


def test_api_base_domain_strips_ten_char_handle():
    assert api_base_domain_from_host("p8txyu0nq8-api.void-run.com") == "api.void-run.com"
    assert api_base_domain_from_host("api.void-run.com") == "api.void-run.com"


def test_node_api_base_url_pins_handle():
    assert (
        node_api_base_url("https://api.void-run.com/api", "p8txyu0nq8")
        == "https://p8txyu0nq8-api.void-run.com/api"
    )


def test_node_api_base_url_idempotent_when_already_pinned():
    pinned = "https://p8txyu0nq8-api.void-run.com/api"
    assert node_api_base_url(pinned, "p8txyu0nq8") == pinned


def test_node_api_base_url_empty_node_keeps_fleet():
    fleet = "https://api.void-run.com/api"
    assert node_api_base_url(fleet, None) == fleet
    assert node_api_base_url(fleet, "") == fleet
    assert node_api_base_url(fleet, "  ") == fleet


def test_node_api_base_url_adds_https_when_scheme_missing():
    assert (
        node_api_base_url("api.void-run.com/api", "p8txyu0nq8")
        == "https://p8txyu0nq8-api.void-run.com/api"
    )


def test_node_api_base_url_keeps_port_and_query():
    assert (
        node_api_base_url("https://api.example.com:8443/api?x=1", "abcdefghij")
        == "https://abcdefghij-api.example.com:8443/api?x=1"
    )


def test_node_api_base_url_custom_fleet_domain():
    assert (
        node_api_base_url("https://dev-ee-api.vrsbx.icu/api", "u1l7jj57l4")
        == "https://u1l7jj57l4-dev-ee-api.vrsbx.icu/api"
    )


def test_sandbox_pins_exec_client_to_owner_node():
    cfg = Configuration(host="https://api.void-run.com/api", api_key={"ApiKeyAuth": "k"})
    fleet = MagicMock()
    fleet.configuration = cfg
    fleet.default_headers = {"User-Agent": "VoidRun-Python-SDK/0.1.0"}
    client = MagicMock()
    client._api_client = fleet
    model = SandboxModel(
        id="s1",
        name="n",
        cpu=1,
        mem=1024,
        org_id="o",
        status="running",
        node_id="p8txyu0nq8",
    )
    sb = Sandbox(client, model)
    assert (
        sb._api_client.configuration.host
        == "https://p8txyu0nq8-api.void-run.com/api"
    )
    assert sb._exec_api.api_client is sb._api_client
    assert sb.fs._api.api_client is sb._api_client
    assert sb.commands._api.api_client is sb._api_client
    assert sb.pty._api.api_client is sb._api_client
    assert sb.interpreter._api.api_client is sb._api_client


def test_api_client_for_node_reuses_fleet_when_host_unchanged():
    cfg = Configuration(host="https://api.void-run.com/api", api_key={"ApiKeyAuth": "k"})
    fleet = MagicMock()
    fleet.configuration = cfg
    fleet.default_headers = {}
    client = MagicMock(_api_client=fleet)
    assert api_client_for_node(client, None) is fleet
    assert fleet_api_client(client) is fleet


def test_sandbox_remove_uses_pinned_sandboxes_api():
    cfg = Configuration(host="https://api.void-run.com/api", api_key={"ApiKeyAuth": "k"})
    fleet = MagicMock()
    fleet.configuration = cfg
    fleet.default_headers = {}
    client = MagicMock(_api_client=fleet)
    model = SandboxModel(
        id="s1",
        name="n",
        cpu=1,
        mem=1024,
        org_id="o",
        status="running",
        node_id="p8txyu0nq8",
    )
    sb = Sandbox(client, model)
    api = MagicMock()
    sb._sandboxes_api = lambda: api
    sb.remove()
    api.delete_sandbox_with_http_info.assert_called_once_with(id="s1")
