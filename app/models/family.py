import enum
from datetime import datetime
from ..extensions import db


class FamilyRole(str, enum.Enum):
    OWNER = 'OWNER'
    ADMIN = 'ADMIN'
    MEMBER = 'MEMBER'
    RESTRICTED = 'RESTRICTED'


class FamilyMemberStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    INVITED = 'INVITED'
    REMOVED = 'REMOVED'


class Family(db.Model):
    __tablename__ = 'families'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='BRL')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    members = db.relationship('FamilyMember', back_populates='family', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f'<Family {self.name}>'


class FamilyMember(db.Model):
    __tablename__ = 'family_members'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default=FamilyRole.MEMBER)
    status = db.Column(db.String(20), nullable=False, default=FamilyMemberStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    family = db.relationship('Family', back_populates='members')
    user = db.relationship('User', back_populates='family_memberships')

    __table_args__ = (
        db.UniqueConstraint('family_id', 'user_id', name='uq_family_member'),
    )

    def __repr__(self) -> str:
        return f'<FamilyMember user={self.user_id} family={self.family_id} role={self.role}>'
