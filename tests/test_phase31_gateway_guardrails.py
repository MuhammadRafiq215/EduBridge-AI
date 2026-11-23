import unittest
from unittest.mock import patch

from src.ai_teacher import build_provider_from_settings


BASE = "https://api.cloudflare.com/client/v4/accounts/1234567890abcdef1234567890abcdef/ai/v1"


class Phase31GatewayGuardrailsTests(unittest.TestCase):
    def settings(self, **extra):
        values = {
            "enabled": True,
            "provider": "cloudflare_workers_ai",
            "model": "@cf/meta/llama-3.1-8b-instruct",
            "api_key": "synthetic-test-token",
            "base_url": BASE,
        }
        values.update(extra)
        return values

    def test_cloudflare_fails_closed_without_gateway_and_guardrails_attestation(self):
        provider = build_provider_from_settings(self.settings())
        with patch("src.ai_teacher.urllib.request.urlopen") as network:
            with self.assertRaisesRegex(RuntimeError, "AI Gateway Guardrails"):
                provider.answer([{"role": "user", "content": "Explain photosynthesis"}])
        network.assert_not_called()

    def test_cloudflare_fails_closed_if_gateway_id_missing(self):
        provider = build_provider_from_settings(self.settings(guardrails_enabled=True))
        with patch("src.ai_teacher.urllib.request.urlopen") as network:
            with self.assertRaisesRegex(RuntimeError, "AI Gateway Guardrails"):
                provider.answer([{"role": "user", "content": "Explain photosynthesis"}])
        network.assert_not_called()

    def test_cloudflare_sends_non_streaming_request_through_configured_gateway(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self):
                return b'{"choices":[{"message":{"content":"A safe explanation."}}]}'

        provider = build_provider_from_settings(self.settings(
            safety_gateway_id="default", guardrails_enabled=True
        ))
        with patch("src.ai_teacher.urllib.request.urlopen", return_value=FakeResponse()) as network:
            answer = provider.answer([{"role": "user", "content": "Explain photosynthesis"}])
        request = network.call_args.args[0]
        self.assertEqual(answer, "A safe explanation.")
        self.assertEqual(request.get_header("Cf-aig-gateway-id"), "default")
        import json
        payload = json.loads(request.data.decode("utf-8"))
        self.assertIs(payload["stream"], False)
        self.assertLessEqual(payload["max_tokens"], 900)

    def test_cloudflare_gate_never_exposes_credentials(self):
        secret = "synthetic-secret-token"
        provider = build_provider_from_settings(self.settings(
            api_key=secret, safety_gateway_id="default", guardrails_enabled=True
        ))
        with patch("src.ai_teacher.urllib.request.urlopen", side_effect=OSError("network offline")):
            with self.assertRaises(RuntimeError) as caught:
                provider.answer([{"role": "user", "content": "Explain algebra"}])
        self.assertNotIn(secret, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
