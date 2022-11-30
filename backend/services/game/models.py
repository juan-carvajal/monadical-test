from sqlalchemy import CheckConstraint, Column, ForeignKeyConstraint, Integer, Text, UniqueConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Game(Base):
    __tablename__ = 'game'
    __table_args__ = (
        CheckConstraint('(line_target <= width) AND (line_target <= height)'),
        UniqueConstraint('game_id', 'width', 'height')
    )

    game_id = Column(Integer, primary_key=True, server_default=text(
        "nextval('game_game_id_seq'::regclass)"))
    width = Column(Integer, nullable=False, server_default=text("7"))
    height = Column(Integer, nullable=False, server_default=text("7"))
    line_target = Column(Integer, nullable=False, server_default=text("4"))
    host = Column(Text, nullable=False)
    enemy = Column(Text, nullable=True)

    tiles = relationship('GameTile', back_populates='game')


class GameTile(Base):
    __tablename__ = 'game_tile'
    __table_args__ = (
        CheckConstraint(
            '(x < game_width) AND (x >= 0) AND (y < game_height) AND (y >= 0)'),
        ForeignKeyConstraint(['game_id', 'game_width', 'game_height'], [
                             'game.game_id', 'game.width', 'game.height'])
    )

    game_id = Column(Integer, primary_key=True, nullable=False, server_default=text(
        "nextval('game_tile_game_id_seq'::regclass)"))
    game_width = Column(Integer, nullable=False)
    game_height = Column(Integer, nullable=False)
    x = Column(Integer, primary_key=True, nullable=False)
    y = Column(Integer, primary_key=True, nullable=False)
    value = Column(Text, nullable=False)

    game = relationship('Game', back_populates='tiles')
