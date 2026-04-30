# magic_coder/shared/src/magicc_shared/data_access/config/share_database_config.py

from magic_base.data_access.config.base_database_config import MagicDatabaseConfig
from magic_base.data_access.manager.base_database_manager import MagicDatabaseManager


class SharedDatabaseManager(MagicDatabaseManager):
    def __init__(self, main_config=None):
        # 直接使用 MagicDatabaseConfig
        if main_config:
            # 从主配置读取数据库类型
            db_type = main_config.get("database.type", "sqlite")
            self.db_config = MagicDatabaseConfig(db_type=db_type)
        else:
            # 使用默认 SQLite 配置
            self.db_config = MagicDatabaseConfig()
        
        super().__init__(self.db_config)
    
    