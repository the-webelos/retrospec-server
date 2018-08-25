import logging

from typing import List

from retro.store.store import Store, Group

_logger = logging.getLogger(__name__)


class GroupEngine(object):
    def __init__(self, store: Store):
        self.store = store

    def get_group(self, group_id: str) -> Group:
        return self.store.get_group(group_id)

    def get_groups(self) -> List[Group]:
        return self.store.get_groups()

    def create_group(self, name: str) -> Group:
        group_id = self.store.next_group_id()

        return self.store.upsert_group(group_id, name)

    def update_group(self, group_id: str, name: str) -> Group:
        return self.store.upsert_group(group_id, name)

    def remove_group(self, group_id: str) -> bool:
        return self.store.remove_group(group_id)
