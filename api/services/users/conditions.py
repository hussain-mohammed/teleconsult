from sutoppu import Specification

from constants import LocalConstants
from utils.constants import Roles, Tables


class UserRole:
    def __init__(self, role):
        self.role = role


class RoleIsPat(Specification):
    description = "The given role must be a patient role."

    def is_satisfied_by(self, user_role):
        if user_role.role == Roles.PATIENT:
            return {"index": Tables.APTS_PATIENT, "col": LocalConstants.PATIENT_ID}


class RoleIsDoc(Specification):
    description = "The given role must be a doctor role."

    def is_satisfied_by(self, user_role):
        if user_role.role == Roles.DOCTOR:
            return {"index": Tables.APTS_DOCTOR, "col": LocalConstants.DOCTOR_ID}


patient_cond = RoleIsPat()
doctor_cond = RoleIsDoc()
