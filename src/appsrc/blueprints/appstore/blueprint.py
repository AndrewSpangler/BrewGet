import os
from flask import (
    Blueprint,
    flash,
    redirect,
    url_for,
    render_template
)
from ...main import app, db
from ...modules.etag import EFile
from .appstore_parser import AppstoreParser

class AppstoreHandler(AppstoreParser):
    """High-level appstore data handler"""
    def __init__(self, name:str, base_url:str):
        AppstoreParser.__init__(self, name)
        self.base_url = base_url
        self.repo_url = base_url.rstrip("/") + "/repo.json"

    @classmethod
    def from_json(cls, name:str, base_url:str, data:dict) -> None:
        """Loads appstore handler object from json object"""
        obj = cls(name, base_url)
        obj.load_json(data)
        return obj

    def get_package_data(self, package) -> dict:
        pass

    def get_package_icon_url(self, package) -> list:
        pass

    def get_package_screenshot_urls(self, package) -> list:
        pass

    def get_package_zip_url(self, package) -> list:
        pass

    def search_by_author(self, author:str) -> list:
        return [p for p in self.all if author.lower() in p["author"].lower()]

class MultiShopHandler:
    """
    Handler to parse multiple appstore repositories
    Repos are specified with the "config" argument as such:
    config = {
        "REPO_NAME": "REPO_BASE_URL",
        "wiiu": "https://wiiubru.com/appstore/",
        "switch": "https://switchbru.com/appstore/"
    }
    """
    def __init__(self, config:dict):
        self.shops = {}

        for name, base_url in config.items():
            data = EFile(base_url+"repo.json", f"{name}.json").read_json()
            shop = AppstoreHandler.from_json(name, base_url, data)
            self.shops[name] = shop

    def refresh(self):
        for name, shop in self.shops.items():
            data = EFile(shop.repo_url, f"{name}.json").read_json()
            shop.load_json(data)

blueprint = Blueprint(
    'appstore',
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__),"static"),
    url_prefix='/appstore'
)

shops = MultiShopHandler({
    "WiiU": "https://wiiubru.com/appstore/",
    "Switch": "https://switchbru.com/appstore/"
})


def render_tile_list(appstore, packages, message):
    return render_template(
        "tiles.html",
        appstore=appstore,
        packages=packages,
        message=message,
        nav_enabled=False
    )

def render_tile_page(appstore, endpoint:str):
    return render_template("tile_page.html", endpoint=endpoint)

@blueprint.route("/<console>/popular")
def popular(console:str):
    return render_tile_page(
        shops.shops[console],
        endpoint=url_for("appstore.popular_embed", console=console)
    )
@blueprint.route("/<console>/popular_embed")
def popular_embed(console:str):
    return render_tile_list(
        appstore=shops.shops[console],
        packages=shops.shops[console].popular,
        message=f"Top 100 {console} homebrew apps"
    )

@blueprint.route("/<console>/<path:author>")
def author(console:str, author:str):
    return render_tile_page(
        shops.shops[console],
        endpoint=url_for("appstore.author_embed", console=console, author=author)
    )
@blueprint.route("/<console>/<path:author>_embed")
def author_embed(console:str, author:str):
    return render_tile_list(
        appstore=shops.shops[console],
        packages=(packages:=shops.shops[console].search_by_author(author)),
        message=f"Found {len(packages)} packages for console {console} by author {author}"
    )

@blueprint.route("/<console>/recent")
def recent(console:str):
    return render_tile_page(
        shops.shops[console],
        endpoint=url_for("appstore.recent_embed", console=console)
    )
@blueprint.route("/<console>/recent_embed")
def recent_embed(console:str):
    return render_tile_list(
        appstore=shops.shops[console],
        packages=shops.shops[console].recent,
        message=f"Recently Updated {console} homebrew apps"
    )

@blueprint.route("/<console>/new")
def newly_added(console:str):
    return render_tile_page(
        shops.shops[console],
        endpoint=url_for("appstore.newly_added_embed", console=console)
    )
@blueprint.route("/<console>/new_embed")
def newly_added_embed(console:str):
    return render_tile_list(
        appstore=shops.shops[console],
        packages=shops.shops[console].newly_added,
        message=f"New {console} homebrew apps"
    )


app.task_manager.create_task(
    name = "REFRESH_APPSTORES",
    task = shops.refresh,
    interval = 15*60,
    enabled = True,
    delay_startup = True
)