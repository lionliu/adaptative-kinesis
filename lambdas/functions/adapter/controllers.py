import math
from typing import Dict

DELTA_TIME = 1


class PIDController:

    def __init__(
            self,
            kp: float,
            ki: float,
            kd: float,
            min_val: int,
            max_val: int,
            setpoint: int,
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_val = min_val
        self.max_val = max_val
        self.setpoint = setpoint
        self.out = 0

    def update(self, goal: int, plant_output: int, shared_dict: Dict[str, float]) -> int:
        error = (goal - plant_output) * self.setpoint

        proportional = self.kp * error

        integral = shared_dict["sum_prev_errors"] * self.ki * DELTA_TIME

        diff = self.kd * (error - shared_dict["prev_error"]) / DELTA_TIME

        self.out = proportional + integral + diff

        print("Error: ", error)
        print("Prev Error: ", shared_dict["prev_error"])
        print("Sum Prev Errors: ", shared_dict["sum_prev_errors"])
        print("Proportional: ", proportional)
        print("Integral: ", integral)
        # print("Diff: ", diff)

        print("Output before limits")
        print(self.out)

        self.out = max(min(self.out, self.max_val), self.min_val)

        shared_dict["prev_error"] = error
        shared_dict["sum_prev_errors"] += error

        self.out = round(self.out)

        return self.out


class HPAController:
    def __init__(
        self,
        #  controlled_factor: int,
        min_val: int, max_val: int
    ):
        # self.controlled_factor = controlled_factor
        self.min_val = min_val
        self.max_val = max_val

    def update(self, goal: int, plant_output: int, current_controlled_factor: int) -> int:

        controlled_factor = current_controlled_factor * (plant_output / goal)

        controlled_factor = math.ceil(controlled_factor)

        controlled_factor = max(
            min(controlled_factor, self.max_val),
            self.min_val
        )

        return controlled_factor
