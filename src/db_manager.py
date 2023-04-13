import os
import pandas as pd
from map_categories import get_categories_df_n
from sqlalchemy import create_engine, exists, ForeignKey, Column, String, Integer, CHAR, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
db_path = 'maps_data.db'


class MapData(Base):
    __tablename__ = 'maps_data'
    map_id = Column('map_id', Integer, primary_key=True)
    divisor = Column('divisor', FLOAT, primary_key=True)
    total_strain = Column('total_strain', FLOAT)
    finger_control_strain = Column('finger_control_strain', FLOAT)
    burst_strain = Column('burst_strain', FLOAT)
    stream_strain = Column('stream_strain', FLOAT)
    deathstream_strain = Column('deathstream_strain', FLOAT)
    total_groups = Column('total_groups', FLOAT)
    finger_control_groups = Column('finger_control_groups', FLOAT)
    burst_groups = Column('burst_groups', FLOAT)
    stream_groups = Column('stream_groups', FLOAT)
    deathstream_groups = Column('deathstream_groups', FLOAT)

    def __init__(self, map_id, divisor, total_strain, finger_control_strain, burst_strain, stream_strain, deathstream_strain, \
		                            total_groups, finger_control_groups, burst_groups, stream_groups, deathstream_groups):
        self.map_id = map_id
        self.divisor = divisor
        self.total_strain = total_strain
        self.finger_control_strain = finger_control_strain
        self.burst_strain = burst_strain
        self.stream_strain = stream_strain
        self.deathstream_strain = deathstream_strain
        self.total_groups = total_groups
        self.finger_control_groups = finger_control_groups
        self.burst_groups = burst_groups
        self.stream_groups = stream_groups
        self.deathstream_groups = deathstream_groups
	
    def __repr__(self):
	    return f'({self.map_id}, {self.divisor}):  {self.total_strain}, {self.finger_control_strain}, {self.burst_strain}, {self.stream_strain}, {self.deathstream_strain}'


def init_db(recreate_db=False):
    if recreate_db and os.path.exists(db_path):
        os.remove(db_path)
    if not os.path.exists(db_path):
        engine = create_engine(f'sqlite:///{db_path}', echo=True)
        Base.metadata.create_all(bind=engine)


def add_maps_to_db(map_ids=[], update_entry=False):
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    for map_id in map_ids:
        try:
            # print(session.query(MapData).filter(MapData.map_id == map_id).scalar())
            if not session.query(exists().where(MapData.map_id == map_id)).scalar() or update_entry:
                categories_df = get_categories_df_n(map_id, strain_type='perceived_strain')
                # categories_df = categories_df.loc[(categories_df['divisor'] == 2) | (categories_df['divisor'] == 4)]
                categories_df.to_sql('maps_data', con=engine, if_exists='append', index=False)
        except Exception as e:
            print(e)


def read_maps_from_db():
	engine = create_engine(f'sqlite:///{db_path}', echo=False)
	#df = pd.read_sql_query(sql=text('SELECT * FROM maps_data'), con=engine.connect())
	return pd.read_sql_table(table_name='maps_data', con=engine.connect())