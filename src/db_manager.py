import os
import pandas as pd
from map_categories import get_categories_df_n
from map_strain import get_strain_df
from map_info import get_map_info_df
from sqlalchemy import create_engine, exists, ForeignKey, Column, String, Integer, CHAR, FLOAT, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()
db_path = 'maps_data.db'


class MapsInfo(Base):
    __tablename__ = 'maps_info'
    id = Column(Integer, primary_key=True)
    map_id = Column('map_id', Integer)
    length = Column('length', FLOAT)
    bpm = Column('bpm', FLOAT)
    aim_rating = Column('aim_rating', FLOAT)

    def __init__(self, map_id, length, bpm, aim_rating):
        self.map_id = map_id
        self.length = length
        self.bpm = bpm
        self.aim_rating = aim_rating

        def __repr__(self):
            return f'({self.map_id}): {self.length}, {self.bpm}, {self.aim_rating}'


class MapsTappingData(Base):
    __tablename__ = 'maps_tapping_data'
    id = Column(Integer, primary_key=True)
    map_id = Column('map_id', Integer, ForeignKey('maps_info.map_id'))
    maps_info = relationship('MapsInfo', backref='tapping_data_entries')
    divisor = Column('divisor', FLOAT)
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
            if not session.query(exists().where(MapsInfo.map_id == map_id)).scalar():
                map_info_df = get_map_info_df(map_id)
                map_info_df.to_sql('maps_info', con=engine, if_exists='append', index=False)

            if not session.query(exists().where(MapsTappingData.map_id == map_id)).scalar() or update_entry:
                strain_df = get_strain_df(map_id, update_entry=True)
                categories_df = get_categories_df_n(map_id, strain_type='perceived_strain')
                categories_df = categories_df.rename(columns={
                    'total_strain_n': 'total_strain',  
                    'finger_control_strain_n': 'finger_control_strain',
                    'burst_strain_n': 'burst_strain',
                    'stream_strain_n': 'stream_strain',  
                    'deathstream_strain_n': 'deathstream_strain',  
                    'total_groups_n': 'total_groups',
                    'finger_control_groups_n': 'finger_control_groups',
                    'burst_groups_n': 'burst_groups',
                    'stream_groups_n': 'stream_groups',
                    'deathstream_groups_n': 'deathstream_groups'
                })
                # print(session.query(MapsInfo.map_id == map_id))
                # categories_df['maps_id'] = session.query(MapsInfo.map_id == map_id)
                categories_df.to_sql('maps_tapping_data', con=engine, if_exists='append', index=False)
        except Exception as e:
            print(e)


def read_maps_from_db():
	engine = create_engine(f'sqlite:///{db_path}', echo=False)
	df = pd.read_sql_query(sql=text('''SELECT maps_info.map_id, maps_info.bpm, maps_tapping_data.divisor, 
                                            round(maps_tapping_data.total_strain, 2) as total_strain,
                                            round(maps_tapping_data.finger_control_strain, 2) as finger_control_strain, 
                                            round(maps_tapping_data.burst_strain, 2) as burst_strain, 
                                            round(maps_tapping_data.stream_strain, 2) as stream_strain, 
                                            round(maps_tapping_data.deathstream_strain, 2) as dstream_strain,
                                            round(maps_tapping_data.total_groups / maps_info.length, 2) as total_groups,
                                            round(maps_tapping_data.finger_control_groups / maps_info.length, 2) as finger_control_groups,
                                            round(maps_tapping_data.burst_groups / maps_info.length, 2) as burst_groups,
                                            round(maps_tapping_data.stream_groups / maps_info.length, 2) as stream_groups,
                                            round(maps_tapping_data.deathstream_groups / maps_info.length, 2) as dstream_groups
                                    FROM maps_info JOIN maps_tapping_data 
                                    ON maps_info.map_id == maps_tapping_data.map_id'''), \
                        con=engine.connect())
	return df #pd.read_sql_table(table_name='maps_tapping_data', con=engine.connect(), index_col='id')


def read_maps_info_from_db():
	engine = create_engine(f'sqlite:///{db_path}', echo=False)
	#df = pd.read_sql_query(sql=text('SELECT * FROM maps_data'), con=engine.connect())
	return pd.read_sql_table(table_name='maps_info', con=engine.connect(), index_col='id')