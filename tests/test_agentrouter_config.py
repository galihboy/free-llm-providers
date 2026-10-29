import unittest
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from formats import openai_responses
from tools import smoke_test_all


ROOT = Path(__file__).parents[1]


class AgentRouterConfigTests(unittest.TestCase):
    def test_yaml_uses_verified_formats_and_model(self):
        config = yaml.safe_load(
            (ROOT / "providers" / "agentrouter.yaml").read_text(encoding="utf-8")
        )
        formats = config["formats"]
        self.assertIn("anthropic_messages", formats)
        self.assertIn("openai_responses", formats)
        self.assertEqual(formats["openai_responses"]["endpoint"], "/responses")
        self.assertEqual(
            formats["anthropic_messages"]["models"],
            ["gpt-6.1-sol", "gpt-6-astra", "gpt-5.6-sol"],
        )

    @patch("formats.openai_responses.get_api_key", return_value="test-key")
    @patch("formats.openai_responses.requests.post")
    def test_responses_client_parses_output_text(self, post, _key):
        response = Mock(status_code=200)
        response.json.return_value = {
            "output_text": "OK",
            "usage": {"input_tokens": 4, "output_tokens": 1},
        }
        post.return_value = response
        result = openai_responses.chat(
            {
                "base_url": "https://ps.air-outer.com/v1",
                "endpoint": "/responses",
                "key_env": "AGENTROUTER_API_KEY",
            },
            "gpt-6.1-sol",
            "Reply exactly OK",
        )
        self.assertEqual(result["answer"], "OK")
        request = post.call_args
        self.assertEqual(request.args[0], "https://ps.air-outer.com/v1/responses")
        self.assertEqual(request.kwargs["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(request.kwargs["json"]["model"], "gpt-6.1-sol")
        self.assertEqual(request.kwargs["json"]["max_output_tokens"], 512)

    @patch("formats.openai_responses.get_api_key", return_value="test-key")
    @patch("formats.openai_responses.requests.post")
    def test_responses_client_parses_output_blocks(self, post, _key):
        response = Mock(status_code=200)
        response.json.return_value = {
            "output": [
                {"content": [{"type": "output_text", "text": "OK"}]},
                {"content": [{"type": "output_text", "text": "!"}]},
            ]
        }
        post.return_value = response
        result = openai_responses.chat(
            {"base_url": "https://ps.air-outer.com/v1", "key_env": "AGENTROUTER_API_KEY"},
            "gpt-6.1-sol",
            "Reply exactly OK",
        )
        self.assertEqual(result["answer"], "OK!")

    @patch("formats.openai_responses.get_api_key", return_value="test-key")
    @patch("formats.openai_responses.requests.post")
    def test_responses_client_returns_sanitized_shape_on_http_error(self, post, _key):
        response = Mock(status_code=503, text="no available channel")
        post.return_value = response
        result = openai_responses.chat(
            {"base_url": "https://ps.air-outer.com/v1", "key_env": "AGENTROUTER_API_KEY"},
            "gpt-6.1-sol",
            "Reply exactly OK",
        )
        self.assertIsNone(result["answer"])
        self.assertEqual(result["status"], 503)
        self.assertIn("no available channel", result["error"])

    @patch("formats.openai_responses.get_api_key", return_value="test-key")
    @patch("formats.openai_responses.requests.post")
    def test_responses_client_handles_invalid_json(self, post, _key):
        response = Mock(status_code=200)
        response.json.side_effect = ValueError
        post.return_value = response
        result = openai_responses.chat(
            {"base_url": "https://ps.air-outer.com/v1", "key_env": "AGENTROUTER_API_KEY"},
            "gpt-6.1-sol",
            "Reply exactly OK",
        )
        self.assertIsNone(result["answer"])
        self.assertEqual(result["status"], 200)
        self.assertIn("JSON", result["error"])

    def test_smoke_runner_main_exit_code_reflects_mocked_failures(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            providers_dir = Path(temp_dir) / "providers"
            providers_dir.mkdir()
            (providers_dir / "mock.yaml").write_text(
                "name: Mock\nformats:\n  openai_responses:\n    models: [mock-model]\n",
                encoding="utf-8",
            )
            with patch.object(smoke_test_all, "ROOT", temp_dir), patch.object(
                smoke_test_all, "smoke_one",
                return_value={"status": "FAIL", "detail": "mock failure"},
            ), patch.object(sys, "argv", ["smoke_test_all.py"]):
                self.assertEqual(smoke_test_all.main(), 1)

            with patch.object(smoke_test_all, "ROOT", temp_dir), patch.object(
                smoke_test_all, "smoke_one",
                return_value={"status": "OK", "model": "mock-model", "latency_ms": 1},
            ), patch.object(sys, "argv", ["smoke_test_all.py"]):
                self.assertEqual(smoke_test_all.main(), 0)

    def test_smoke_entrypoint_process_exit_codes_without_network(self):
        script = ROOT / "tools" / "smoke_test_all.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            providers_dir = Path(temp_dir) / "providers"
            providers_dir.mkdir()
            provider = providers_dir / "mock.yaml"
            provider.write_text(
                "name: Mock\nformats:\n  openai_responses:\n"
                "    base_url: invalid://offline\n"
                "    key_env: SMOKE_TEST_KEY\n"
                "    models: [mock-model]\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["SMOKE_ROOT"] = temp_dir
            env["SMOKE_TEST_KEY"] = "test-key"
            failed = subprocess.run(
                [sys.executable, str(script)],
                env=env,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                text=True,
                check=False,
            )
            self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)

            env.pop("SMOKE_TEST_KEY")
            passed = subprocess.run(
                [sys.executable, str(script)],
                env=env,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                text=True,
                check=False,
            )
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)


if __name__ == "__main__":
    unittest.main()
