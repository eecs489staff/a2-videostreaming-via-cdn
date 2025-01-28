import argparse
import asyncio
import os
import sys

from loguru import logger
import numpy as np

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sanic.response import html, text, redirect

from sanic import HTTPResponse, Sanic
from sanic.response import file
from sanic.worker.loader import AppLoader

VIDEO_NAMES = ["michigan-hype-video", "tears-of-steel"]
WEBSERVER_DIR = Path(__file__).parent

MIN_BANDWIDTH = 100
MAX_BANDWIDTH = 100000

MIN_STD = 0
MAX_STD = 1000

logger.remove()
logger.add(sys.stderr, format="<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</> <blue> - PID {process} - </> <green>{level}:</> <lvl>{message}</>")

def prettify_video_name(video_name):
    return video_name.replace('-', ' ').title()

def check_video_exists(video_name):
    if video_name not in VIDEO_NAMES:
        return html(f"Video <b>{prettify_video_name(video_name)}</b> not found", status=404)
    return None

@dataclass
class BandwidthLimit:
    mean: float # kbps
    std: float # kbps

class VideoServer:
    def __init__(self):
        self.app = Sanic("eecs-489-videoserver")
        self.bandwidth_limit: BandwidthLimit = BandwidthLimit(10000, 0)
        self.init_app()
    
    
    def set_bandwidth_limit(self, mean: float, std: float):
        if (MIN_BANDWIDTH <= mean <= MAX_BANDWIDTH) and (MIN_STD <= std <= MAX_STD): 
            self.bandwidth_limit = BandwidthLimit(mean, std)
    
        
    def init_app(self):        
        self.app.config.TEMPLATING_PATH_TO_TEMPLATES = WEBSERVER_DIR / 'templates'
        
        self.app.static('/', WEBSERVER_DIR / 'static/index.html')
        self.app.static('/index.html', WEBSERVER_DIR / 'static/index.html', name='index')
        self.app.static('/favicon.ico', WEBSERVER_DIR / 'static/favicon.ico', name='favicon')
        
        
        @self.app.get('/set_bandwidth.html')
        @self.app.ext.template("set_bandwidth.html")
        async def get_bandwidth(_):
            return {"bandwidth": self.bandwidth_limit.mean, "std": self.bandwidth_limit.std}

        @self.app.post("/set_bandwidth")
        async def set_bandwidth(request):
            mean = float(request.form.get('bandwidth'))
            std = float(request.form.get('bandwidth_var', 0))
            self.set_bandwidth_limit(mean, std)
            
            return redirect("/set_bandwidth.html")
            
        
        @self.app.get('videos/<video_name:slug>')
        @self.app.ext.template("video_player.html")
        async def get_video(_, video_name):
            invalid_error = check_video_exists(video_name)
            if invalid_error:
                return invalid_error
    
            return {"name": prettify_video_name(video_name), "slug": video_name}
        

        @self.app.route('videos/<video_name:slug>/<video_file:path>')
        async def get_video_file(_, video_name, video_file):
            file_path = f"{WEBSERVER_DIR}/static/videos/{video_name}/{video_file}"
            if (not os.path.exists(file_path)) :
                return text(f"File {video_file} for video {video_name} not found",  status=404)
            
            if self.bandwidth_limit is None:
                return await file(file_path)
                    
            file_size = os.path.getsize(file_path) * 8  # in bits
            bandwidth = np.random.normal(self.bandwidth_limit.mean, self.bandwidth_limit.std) * 1000 # bits per second
            bandwidth = max(MIN_BANDWIDTH, bandwidth)
            
            download_time = file_size / bandwidth
            logger.debug(f"Downloading {file_path} should take {download_time} seconds at current bandwidth {bandwidth / 1000}, sampled from N({self.bandwidth_limit.mean}, {self.bandwidth_limit.std})")
            
            await asyncio.sleep(download_time)
            
            return await file(file_path)


        @self.app.on_response
        async def prevent_caching(_, response):
            response.headers["Cache-Control"] = "no-store, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            logger.info(f"Response: {response.status}")

        
        @self.app.on_request
        async def log_request(request):
            logger.info(f"Request: {request.method} {request.url}", )
            
            


    def run(self, port):
        self.app.run(host="127.0.0.1", port=port)


server = VideoServer()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple web server for serving videos.")
    parser.add_argument(
        "port",
        type=int,
        help="The port number to use (e.g., 8080)"
    )
    
     # Parse the command-line arguments
    args = parser.parse_args()
    
    # Validate the port number
    if args.port < 1024 or args.port > 65535:
        print("Error: Port number must be in the interval [1024, 65535]", file=sys.stderr)
        sys.exit(1)
        
    server.run(args.port)