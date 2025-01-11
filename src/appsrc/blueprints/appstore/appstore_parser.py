# A basic python object for parsing the appstore json into lists per category
# Copyright ForTheUsers (4TU.org) 2019
# Licensed under GPL3

import os
import json
from datetime import datetime


class AppstoreParser:
    """Simple python object to hold Homebrew Appstore Data"""

    def __init__(self, name:str) -> None:
        self.name = name
        self.init()

    @classmethod
    def from_json(cls, name:str, data:dict) -> None:
        """Loads appstore parser object from json"""
        obj = cls(name)
        obj.load_json(data)
        return obj

    def init(self) -> None:
        """Init or re-init object"""
        self.all = []
        self.advanced = []
        self.emus = []
        self.games = []
        self.loaders = []
        self.themes = []
        self.tools = []
        self.misc = []
        self.legacy = []
        self.uncategorized = []

        self.map = {
            "all": self.all,
            "advanced": self.advanced,
            "concept": self.misc,
            "emu": self.emus,
            "game": self.games,
            "loader": self.loaders,
            "theme": self.themes,
            "tool": self.tools,
            "misc": self.misc,
            "media": self.misc,
            "misc": self.misc,
            "legacy": self.legacy,
            "uncategorized": self.uncategorized
        }

        # Holds full appstore json
        self.packages = {}

    @property
    def popular(self):
        """Return the top 100 apps based on app_dls."""
        return sorted(self.all, key=lambda app: app.get("app_dls", 0), reverse=True)[:100]

    @property
    def recent(self):
        """Return the 100 most recently updated apps based on app_dls."""
        return sorted(self.all, key=lambda x: datetime.strptime(x['updated'], "%d/%m/%Y"), reverse=True)[:100]
    
    @property
    def newly_added(self):
        """Return the 100 most recently added apps based on app_dls."""
        return sorted(self.all, key=lambda x: datetime.strptime(x['appCreated'], "%d/%m/%Y"), reverse=True)[:100]

    def load_file(self, path:os.PathLike) -> None:
        """Loads appstore json as a large list of dicts from file"""
        if not path:
            raise
        self.init()
        try:
            self.all.clear()
            with open(path, encoding="utf-8") as repojson:
                self.all.extend(json.load(repojson)["packages"])
        except Exception as e:
            print(f"Exception loading appstore json {e}")
        self._sort()
        num_entries = len(self.all)
        print(f"Loaded {num_entries} appstore entries")

    def load_json(self, data:dict) -> None:
        """Loads appstore dict as a large list of dicts from object"""
        if not data:
            raise
        self.init()
        self.all.clear()
        self.all.extend(data["packages"])
        self._sort()
        num_entries = len(self.all)
        print(f"Loaded {num_entries} appstore entries")

    def get_package_dict(self, name:str) -> dict:
        """
        Get package dictionary
        Returns None on package not found.
        """
        return self.packages.get(name, None)
    
    def _sort(self) -> None:
        """
        Sorts list into categories
        Calling multiple times after init will result in
        duplicate entries in the categories list.
        """
        if not self.all:
            raise ValueError("Appstore object data is empty")
        
        for entry in self.all:
            if not entry["category"]:
                self.map["uncategorized"].append(entry)
                continue
            else:
                try:
                    self.map[entry["category"]].append(entry)
                except:
                    pkg = entry["name"]
                    print(f"Error sorting {pkg}")
            self.packages[entry["name"]] = entry