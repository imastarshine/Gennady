from src.db.message import MessageDB
from src.db.markov import MarkovDB

message = MessageDB()
markov = MarkovDB()

__all__ = ["message", "markov"]