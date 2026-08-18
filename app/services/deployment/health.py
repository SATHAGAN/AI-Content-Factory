from __future__ import annotations


class ComponentHealth:
    def __init__(self):
        self.components={}

    def set(self,name: str,status: str,detail: str = ""):
        self.components[name]={"status":status,"detail":detail}

    def snapshot(self) -> dict:
        overall="ok" if all(
            item["status"]=="ok" for item in self.components.values()
        ) else "degraded"
        return {"status":overall,"components":self.components}
