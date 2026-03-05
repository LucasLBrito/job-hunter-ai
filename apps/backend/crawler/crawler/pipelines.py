import os
import logging
from datetime import datetime, timezone

class MongoPipeline:
    collection_name = 'raw_jobs'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
            mongo_db=os.getenv("MONGO_DB_NAME", "job_lake")
        )

    def open_spider(self, spider):
        # Usamos pymongo síncrono no Scrapy Pipelines (por padrão)
        import pymongo
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        
        # Garante indice único pelo URL (upsert)
        self.db[self.collection_name].create_index("url", unique=True)

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        # Prepara o documento
        document = dict(item)
        document['collected_at'] = datetime.now(timezone.utc)
        document['status'] = 'pending_processing'
        
        url_key = document.get('url')
        if not url_key:
            logging.warning("Skipping item without URL")
            return item

        try:
            # Tenta dar um upsert pela URL
            self.db[self.collection_name].update_one(
                {"url": url_key},
                {"$set": document},
                upsert=True
            )
            spider.logger.debug(f"Saved/Updated raw job to Mongo: {url_key}")
        except Exception as e:
            spider.logger.error(f"Error saving to Mongo: {e}")

        return item
