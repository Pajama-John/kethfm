import uuid

class Article:
    def __init__(self, title, youtube_link=None, thumbnail_path: str=None) -> None:
        self.title = title
        self.youtube_link = youtube_link
        self.thumbnail_path = thumbnail_path
        
        self.uuid = uuid.uuid4()