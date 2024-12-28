import asyncio
import os

from loguru import logger
import numpy as np

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sanic import HTTPResponse, Sanic
from sanic.response import file
from sanic.worker.loader import AppLoader

webserver_dir = Path(__file__).parent

@dataclass
class BandwidthLimit:
    mean: float
    std: float

class P2Server:
    def __init__(self):
        self.app = Sanic("P2Server")
        self.bandwidth_limit: Optional[BandwidthLimit] = None
        
        self.init_app()
        
        
    async def get_file(self, request, path):
        # Construct the file path
        file_path = Path("static/vod") / path

        # Check if the file exists
        if not os.path.isfile(file_path):
            HTTPResponse(status=404, body="File not found")
        
        response = await file(file_path)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    async def get_file_with_bandwidth_limit(self, request, path):
        if self.bandwidth_limit is None:
            return await self.get_file(request, path)
        
        file_path = Path("static/vod") / path
        file_size = os.path.getsize(file_path)
        bandwidth = np.random.normal(self.bandwidth_limit.mean, self.bandwidth_limit.std) * 1024
        bandwidth = max(100, bandwidth)
        
        
        download_time = file_size / bandwidth
        logger.info(f"Downloading {file_path} should take {download_time} seconds")
        
        await asyncio.sleep(download_time)
        
        return await self.get_file(request, path)
    
    async def handle_set_bandwidth_limit(self, request):
        mean = float(request.form.get('bandwidth')) / 8
        std = float(request.form.get('bandwidth_var', 0)) / 8
        
        self.set_bandwidth_limit(mean, std)
        
        return HTTPResponse(status=200, body=f"Bandwidth limit set to {mean * 8} kbps with variance {std * 8} kbps")
    
    def set_bandwidth_limit(self, mean: float, std: float):
        self.bandwidth_limit = BandwidthLimit(mean, std)
        
    def init_app(self):        
        self.app.static('/', webserver_dir / 'static/index.html')
        self.app.static('/index.html', webserver_dir / 'static/index.html', name='index')
        self.app.static('/favicon.ico', webserver_dir / 'static/favicon.ico', name='favicon')
        self.app.static('/set_bandwidth.html', webserver_dir / 'static/set_bandwidth.html', name='set_bandwidth')
        self.app.add_route(self.get_file_with_bandwidth_limit, "/vod/<path:path>", methods=['GET'])
        self.app.add_route(self.handle_set_bandwidth_limit, "/set_bandwidth", methods=['POST'])

    def run(self):
        self.app.prepare(host="0.0.0.0", port=80)
        self.app.run()


server = P2Server()
app = server.app