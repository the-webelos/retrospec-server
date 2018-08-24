import logging

from typing import List

from retro.store import Store, Group
from retro.utils import get_store
from retro.utils.config import Config

_logger = logging.getLogger(__name__)


class GroupEngine(object):
    def __init__(self, config: Config=None, store: Store=None):
        self.store = store if store else get_store(config)

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
