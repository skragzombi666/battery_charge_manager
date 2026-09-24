"""Actual aiohttp streaming; HA user authorization is supplied by test middleware."""
from __future__ import annotations
import importlib
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from test_core import manager_module
from test_retention_completion import setup_manager

try:
    from aiohttp import web
    from aiohttp.test_utils import TestClient, TestServer
except ImportError:
    web = None

@unittest.skipIf(web is None, 'aiohttp runtime is required for HTTP transport tests')
class ArchiveHttpTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.assertTrue((Path(__file__).parents[1]/'custom_components/battery_charge_manager/export.py').exists(),
                        'Archive download view is missing')
        self.manager, self.hass, _ = setup_manager()
        self.hass.data['battery_charge_manager'] = {'entry':self.manager}
        stubs = {'homeassistant.components.http':SimpleNamespace(HomeAssistantView=object),
                 'homeassistant.components.http.const':SimpleNamespace(KEY_HASS_USER='hass_user'),
                 'homeassistant.helpers.http':SimpleNamespace(KEY_HASS='hass')}
        with patch.dict(sys.modules, stubs):
            self.module = importlib.import_module(manager_module.__package__+'.export')
        self.tmp = tempfile.TemporaryDirectory()
        RawArchive=importlib.import_module(manager_module.__package__+'.archive').RawArchive
        self.manager.archive=RawArchive(Path(self.tmp.name)/'a.db');self.manager.archive.initialize({})
        @web.middleware
        async def auth(request, handler):
            request['hass_user'] = SimpleNamespace(is_admin=request.headers.get('X-Admin')=='yes')
            return await handler(request)
        app=web.Application(middlewares=[auth]); app['hass']=self.hass
        view=self.module.BatteryChargeManagerExportView()
        async def handler(request):
            return await view.get(request,request.match_info['entry_id'])
        app.router.add_get(view.url,handler)
        self.client=TestClient(TestServer(app));await self.client.start_server()

    async def asyncTearDown(self):
        if hasattr(self,'client'):await self.client.close()
        if hasattr(self,'tmp'):self.tmp.cleanup()

    async def test_admin_download_and_denial(self):
        response=await self.client.get('/api/battery_charge_manager/export/entry')
        self.assertEqual(response.status,403)
        response=await self.client.get('/api/battery_charge_manager/export/missing',headers={'X-Admin':'yes'})
        self.assertEqual(response.status,404)
        response=await self.client.get('/api/battery_charge_manager/export/entry',headers={'X-Admin':'yes'})
        self.assertEqual(response.status,200)
        data=await response.json()
        self.assertEqual(len(data['raw_archive']['traces'][0]['samples']),2)
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        self.assertIn('attachment',response.headers['Content-Disposition'])
        self.assertTrue(self.module.BatteryChargeManagerExportView.requires_auth)

    async def test_close_export_generator_on_client_failure(self):
        closed=[]
        def broken():
            try:
                yield '{'
                raise OSError('read failure')
            finally: closed.append(True)
        async def export():return broken()
        self.manager.async_archive_export=export
        response=await self.client.get('/api/battery_charge_manager/export/entry',headers={'X-Admin':'yes'})
        # Failure before headers is a readable error; after headers must abort, never a valid truncated JSON.
        self.assertEqual(response.status,500)
        self.assertEqual(closed,[True])
