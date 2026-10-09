import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
import unittest
from test_history_websocket import handler_namespace


class PilotApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_review_identity_and_revision_are_forwarded(self):
        handlers = handler_namespace()
        manager = SimpleNamespace(async_set_usage_approval=AsyncMock(), async_set_usb_comparison=AsyncMock())
        hass = SimpleNamespace(data={'battery_charge_manager':{'entry':manager}})
        results = []
        connection = SimpleNamespace(user=SimpleNamespace(id='reviewer'), send_result=lambda *v:results.append(v), send_error=lambda *v:results.append(v))
        await handlers['ws_set_usage_approval'](hass, connection, dict(id=1, record_type='rest',record_id='r',approved=True,reason='review',expected_analysis_revision=3,expected_fingerprint='decision',expected_usage_revision=0))
        manager.async_set_usage_approval.assert_awaited_once_with('rest','r',True,'review',3,actor_id='reviewer',expected_fingerprint='decision',expected_usage_revision=0)
        await handlers['ws_set_usb_comparison'](hass, connection, dict(id=2,record_id='r',energy_wh=4.590,reason='Full run end',expected_analysis_revision=3))
        manager.async_set_usb_comparison.assert_awaited_once_with('r',4.590,'Full run end',3,actor_id='reviewer')
        self.assertEqual(results, [(1,), (2,)])

    def test_pilot_mutations_require_admin_and_are_registered(self):
        text = Path('custom_components/battery_charge_manager/websocket_api.py').read_text()
        tree = ast.parse(text)
        for name in ('ws_prepare_rest_reference','ws_confirm_rest_reference','ws_set_usage_approval','ws_set_usb_comparison'):
            node = next(n for n in tree.body if getattr(n,'name',None) == name)
            self.assertIn('websocket_api.require_admin', [ast.unparse(d) for d in node.decorator_list])
            register = next(n for n in tree.body if getattr(n,'name',None) == 'async_register_websocket_api')
            self.assertIn(name, ast.unparse(register))
