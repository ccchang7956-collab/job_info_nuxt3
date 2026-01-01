from typing import List, Optional

from sqlalchemy import CHAR, DateTime, ForeignKeyConstraint, Index, String, Text, text, Integer, SmallInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class JobAllData(Base):
    __tablename__ = 'job_all_data'
    __table_args__ = (
        Index('idx_date_to', 'date_to'),
        Index('idx_job_all_data_date_from_desc', 'date_from'),
        Index('idx_job_all_data_date_sysnam', 'date_to', 'sysnam', 'date_from'),
        Index('idx_job_all_data_org_name', 'org_name'),
        Index('idx_job_all_data_rank', 'rank'),
        Index('idx_job_all_data_title', 'title'),
        Index('idx_job_all_data_work_place_type', 'work_place_type'),
        Index('idx_org_workitem', 'org_name', 'work_item'),
        Index('idx_sysnam', 'sysnam'),
        Index('idx_title', 'title'),
        Index('idx_work_place_type', 'work_place_type')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    announce_date: Mapped[Optional[str]] = mapped_column(String(10))
    org_id: Mapped[Optional[str]] = mapped_column(String(20))
    org_name: Mapped[Optional[str]] = mapped_column(String(100))
    person_kind: Mapped[Optional[str]] = mapped_column(String(50))
    rank: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String(100))
    sysnam: Mapped[Optional[str]] = mapped_column(String(255))
    number_of: Mapped[Optional[int]] = mapped_column(Integer)
    reserve_num: Mapped[Optional[str]] = mapped_column(String(10))
    gender_type: Mapped[Optional[str]] = mapped_column(String(20))
    work_place_type: Mapped[Optional[str]] = mapped_column(Text)
    date_from: Mapped[Optional[str]] = mapped_column(String(10))
    date_to: Mapped[Optional[str]] = mapped_column(String(10))
    is_handicap: Mapped[Optional[str]] = mapped_column(CHAR(1))
    is_original: Mapped[Optional[str]] = mapped_column(CHAR(1))
    is_local_original: Mapped[Optional[str]] = mapped_column(CHAR(1))
    is_traning: Mapped[Optional[str]] = mapped_column(CHAR(1))
    type: Mapped[Optional[str]] = mapped_column(String(50))
    vitae_email: Mapped[Optional[str]] = mapped_column(String(100))
    work_quality: Mapped[Optional[str]] = mapped_column(Text)
    work_item: Mapped[Optional[str]] = mapped_column(Text)
    work_address: Mapped[Optional[str]] = mapped_column(Text)
    contact_method: Mapped[Optional[str]] = mapped_column(Text)
    url_link: Mapped[Optional[str]] = mapped_column(String(200))
    view_url: Mapped[Optional[str]] = mapped_column(String(200))
    work_type: Mapped[Optional[int]] = mapped_column(Integer)
    is_transfer: Mapped[Optional[str]] = mapped_column(CHAR(1))


class JobComments(Base):
    __tablename__ = 'job_comments'
    __table_args__ = (
        Index('fk_comments_user_id', 'user_id'),
        Index('idx_comments_job_opening_id', 'is_deleted')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    initial: Mapped[str] = mapped_column(CHAR(1))
    message: Mapped[str] = mapped_column(Text)
    color: Mapped[str] = mapped_column(CHAR(7))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('current_timestamp()'))
    email: Mapped[str] = mapped_column(String(100))
    is_deleted: Mapped[int] = mapped_column(SmallInteger, server_default=text('0'), comment='是否刪除，0=未刪除，1=已刪除')
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    job_all_data_id: Mapped[Optional[int]] = mapped_column(Integer)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, comment='父留言的ID，為NULL表示是父留言')
    deletion_reason: Mapped[Optional[str]] = mapped_column(String(255))


class JobDataUpdateLog(Base):
    __tablename__ = 'job_data_update_log'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(255))
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    new_records: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    updated_records: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'成功'"))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    remarks: Mapped[Optional[str]] = mapped_column(Text)


class JobOpenings(Base):
    __tablename__ = 'job_openings'
    __table_args__ = (
        Index('idx_date_to', 'date_to'),
        Index('idx_job_openings_date_from_desc', 'date_from'),
        Index('idx_job_openings_date_sysnam', 'date_to', 'sysnam', 'date_from'),
        Index('idx_job_openings_org_name', 'org_name'),
        Index('idx_job_openings_rank', 'rank'),
        Index('idx_job_openings_title', 'title'),
        Index('idx_job_openings_work_place_type', 'work_place_type'),
        Index('idx_org_workitem', 'org_name', 'work_item'),
        Index('idx_sysnam', 'sysnam'),
        Index('idx_title', 'title'),
        Index('idx_work_place_type', 'work_place_type'),
        Index('idx_announce_date', 'announce_date') # Added index
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    announce_date: Mapped[Optional[str]] = mapped_column(String(10))
    org_id: Mapped[Optional[str]] = mapped_column(String(20))
    org_name: Mapped[Optional[str]] = mapped_column(String(100))
    person_kind: Mapped[Optional[str]] = mapped_column(String(50))
    rank: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String(100))
    sysnam: Mapped[Optional[str]] = mapped_column(String(50))
    number_of: Mapped[Optional[int]] = mapped_column(Integer)
    reserve_num: Mapped[Optional[str]] = mapped_column(String(10))
    gender_type: Mapped[Optional[str]] = mapped_column(String(20))
    work_place_type: Mapped[Optional[str]] = mapped_column(Text)
    date_from: Mapped[Optional[str]] = mapped_column(String(10))
    date_to: Mapped[Optional[str]] = mapped_column(String(10))
    is_handicap: Mapped[Optional[str]] = mapped_column(CHAR(1))
    is_original: Mapped[Optional[str]] = mapped_column(CHAR(1))
    is_local_original: Mapped[Optional[str]] = mapped_column(CHAR(1))
    is_traning: Mapped[Optional[str]] = mapped_column(CHAR(1))
    type: Mapped[Optional[str]] = mapped_column(String(50))
    vitae_email: Mapped[Optional[str]] = mapped_column(String(100))
    work_quality: Mapped[Optional[str]] = mapped_column(Text)
    work_item: Mapped[Optional[str]] = mapped_column(Text)
    work_address: Mapped[Optional[str]] = mapped_column(Text)
    contact_method: Mapped[Optional[str]] = mapped_column(Text)
    url_link: Mapped[Optional[str]] = mapped_column(String(200))
    view_url: Mapped[Optional[str]] = mapped_column(String(200))
    work_type: Mapped[Optional[int]] = mapped_column(Integer)
    is_transfer: Mapped[Optional[str]] = mapped_column(CHAR(1))

    comments: Mapped[List['Comments']] = relationship('Comments', foreign_keys='[Comments.job_opening_id]', back_populates='job_opening')


class JobSysnam(Base):
    __tablename__ = 'job_sysnam'
    __table_args__ = (
        Index('unique_sysnam', 'sysnam', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50))
    sysnam: Mapped[Optional[str]] = mapped_column(String(255))


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        Index('email', 'email', unique=True),
        Index('email_2', 'email', unique=True),
        Index('email_3', 'email', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    is_verified: Mapped[Optional[int]] = mapped_column(SmallInteger, server_default=text('0'))
    registration_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('current_timestamp()'))
    is_disabled: Mapped[Optional[int]] = mapped_column(SmallInteger, server_default=text('0'))

    comments: Mapped[List['Comments']] = relationship('Comments', back_populates='user')


class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = (
        ForeignKeyConstraint(['job_opening_id'], ['job_openings.id'], ondelete='CASCADE', name='fk_job_opening'),
        ForeignKeyConstraint(['job_opening_id'], ['job_openings.id'], name='fk_job_opening_id'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_comments_user_id'),
        Index('fk_comments_user_id', 'user_id'),
        Index('idx_comments_job_opening_id', 'job_opening_id', 'is_deleted')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    initial: Mapped[str] = mapped_column(CHAR(1))
    message: Mapped[str] = mapped_column(Text)
    color: Mapped[str] = mapped_column(CHAR(7))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('current_timestamp()'))
    email: Mapped[str] = mapped_column(String(100))
    job_opening_id: Mapped[int] = mapped_column(Integer)
    is_deleted: Mapped[int] = mapped_column(SmallInteger, server_default=text('0'), comment='是否刪除，0=未刪除，1=已刪除')
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, comment='父留言的ID，為NULL表示是父留言')
    deletion_reason: Mapped[Optional[str]] = mapped_column(String(255))

    job_opening: Mapped['JobOpenings'] = relationship('JobOpenings', foreign_keys=[job_opening_id], back_populates='comments')
    user: Mapped[Optional['Users']] = relationship('Users', back_populates='comments')
